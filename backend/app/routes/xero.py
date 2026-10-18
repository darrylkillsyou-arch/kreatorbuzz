import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User
from app.models.briefs import Brief, XeroSession
from app.models.creators import CreatorProfile
from app.schemas.briefs import BriefResponse
from app.schemas.xero import (
    XeroChatRequest,
    XeroConversationResponse,
    SaveBriefFromPlanRequest,
    ProjectPlan,
    ChatMessage,
)
from app.dependencies import get_current_user, get_optional_current_user
from app.services.ai import get_ai_provider
from app.services.matching import recommend_top_creators

router = APIRouter(prefix="/xero", tags=["xero"])


def get_recommendations_for_plan(
    plan: ProjectPlan,
    db: Session,
    offset: int = 0,
    limit: int = 3,
) -> Tuple[List[Dict[str, Any]], int]:
    creators = db.query(CreatorProfile).join(User).filter(User.is_active == True).all()
    if not creators:
        return [], 0

    all_scored = recommend_top_creators(
        category=plan.core_category,
        content_type=plan.content_format,
        style=", ".join(plan.style_direction),
        tools_suggested=plan.preferred_tools,
        budget=plan.budget,
        budget_min=plan.budget * 0.8,
        budget_max=plan.budget * 1.2,
        timeline_days=plan.timeline_days,
        description=plan.summary,
        creators=creators,
        limit=100,  # score all
        offset=0,
    )
    total_matches = len(all_scored)
    
    # Handle wrap-around pagination if offset exceeds total
    if total_matches > 0 and offset >= total_matches:
        offset = 0

    page_slice = all_scored[offset:offset + limit]

    serialized = []
    for item in page_slice:
        c = item["creator"]
        serialized.append({
            "creator": {
                "id": c.id,
                "user_id": c.user_id,
                "display_name": c.display_name,
                "tagline": c.tagline,
                "specialization": c.specialization,
                "core_category": c.core_category,
                "skills": c.skills or [],
                "ai_tools": c.ai_tools or [],
                "starting_rate": c.starting_rate,
                "delivery_days": c.delivery_days,
                "rating": c.rating or 5.0,
                "sla_score": c.sla_score or 98.0,
                "is_verified": c.is_verified,
                "avatar_url": c.user.avatar_url if c.user else None,
            },
            "match_score": item["match_score"],
            "recommendation_reason": item["recommendation_reason"],
            "match_reasons": item["match_reasons"],
        })
    return serialized, total_matches


@router.post("/chat", response_model=XeroConversationResponse)
def xero_chat_endpoint(
    req: XeroChatRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):

    """
    Main conversational entry point for Xero AI 2.0 Copilot.
    Maintains session history, supports initial creation and multi-turn refinement,
    returns structured plan, smart follow-ups, and grounded creator recommendations.
    """
    msg_clean = req.message.strip()
    if not msg_clean:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be empty")

    session_id = req.session_id or f"xero_{uuid.uuid4().hex[:12]}"
    session = db.query(XeroSession).filter(XeroSession.id == session_id).first()

    history: List[ChatMessage] = []
    existing_plan: Optional[ProjectPlan] = None
    creator_offset = 0

    if session:
        creator_offset = session.creator_offset or 0
        if session.messages:
            history = [ChatMessage(**m) for m in session.messages]
        if session.project_plan:
            try:
                existing_plan = ProjectPlan(**session.project_plan)
            except Exception:
                existing_plan = None
    else:
        session = XeroSession(
            id=session_id,
            user_id=current_user.id if current_user else None,
            messages=[],
            project_plan=None,
            creator_offset=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(session)
        db.commit()

    # Special intent: "show me different creators" / "show different creators"
    msg_lower = msg_clean.lower()
    is_diff_creators_req = any(p in msg_lower for p in [
        "different creator", "other creator", "show different", "more creator", "next creator", "another creator"
    ])

    if existing_plan and is_diff_creators_req:
        new_offset = creator_offset + 3
        recs, total = get_recommendations_for_plan(existing_plan, db, offset=new_offset, limit=3)
        session.creator_offset = new_offset
        
        reply = (
            f"Here are the next top-ranked creators for your **{existing_plan.project_title}** project, "
            f"selected by matching specialization and style fidelity."
        )
        
        history.append(ChatMessage(role="user", content=msg_clean, timestamp=datetime.utcnow().isoformat()))
        history.append(ChatMessage(role="assistant", content=reply, timestamp=datetime.utcnow().isoformat()))
        session.messages = [m.model_dump() for m in history]
        session.updated_at = datetime.utcnow()
        db.commit()

        return XeroConversationResponse(
            session_id=session_id,
            message=reply,
            plan=existing_plan,
            follow_up_questions=[],
            recommended_creators=recs,
            total_matching_creators=total,
            creator_offset=new_offset,
            ai_provider_used="deterministic_matcher",
            scope_warning=existing_plan.scope_warning,
        )

    # Dispatch to configured AI Provider (Ollama / Gemini with Fallback protection)
    provider = get_ai_provider()
    provider_name = "ollama" if type(provider).__name__ == "OllamaAIProvider" else (
        "gemini" if type(provider).__name__ == "GeminiAIProvider" else "deterministic_fallback"
    )

    plan, reply, follow_ups, scope_warning = provider.generate_project_plan(
        user_message=msg_clean,
        conversation_history=history,
        existing_plan=existing_plan,
    )

    if getattr(provider, "last_used_fallback", False):
        provider_name = "deterministic_fallback"


    recs: List[Dict[str, Any]] = []
    total_matches = 0

    if plan:
        # Match creators from live database using verified matching engine
        recs, total_matches = get_recommendations_for_plan(plan, db, offset=0, limit=3)
        session.project_plan = plan.model_dump()
        session.creator_offset = 0

    # Update conversation history
    history.append(ChatMessage(role="user", content=msg_clean, timestamp=datetime.utcnow().isoformat()))
    history.append(ChatMessage(role="assistant", content=reply, timestamp=datetime.utcnow().isoformat()))
    
    session.messages = [m.model_dump() for m in history]
    session.updated_at = datetime.utcnow()
    if current_user and not session.user_id:
        session.user_id = current_user.id

    db.commit()

    return XeroConversationResponse(
        session_id=session_id,
        message=reply,
        plan=plan,
        follow_up_questions=follow_ups,
        recommended_creators=recs,
        total_matching_creators=total_matches,
        creator_offset=session.creator_offset,
        ai_provider_used=provider_name,
        scope_warning=scope_warning,
    )


@router.get("/sessions/{session_id}", response_model=XeroConversationResponse)
def get_xero_session_endpoint(
    session_id: str,
    db: Session = Depends(get_db),
):
    """Retrieves full persistent state and message history of an active Xero AI session."""
    session = db.query(XeroSession).filter(XeroSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Xero AI session not found")

    plan = ProjectPlan(**session.project_plan) if session.project_plan else None
    recs = []
    total = 0
    if plan:
        recs, total = get_recommendations_for_plan(plan, db, offset=session.creator_offset or 0, limit=3)

    last_reply = "Welcome back to your Xero AI copilot session."
    if session.messages:
        for m in reversed(session.messages):
            if m.get("role") == "assistant":
                last_reply = m.get("content", "")
                break

    return XeroConversationResponse(
        session_id=session.id,
        message=last_reply,
        plan=plan,
        follow_up_questions=[],
        recommended_creators=recs,
        total_matching_creators=total,
        creator_offset=session.creator_offset or 0,
        ai_provider_used="session_restored",
        scope_warning=plan.scope_warning if plan else None,
    )


@router.post("/save-brief", response_model=BriefResponse)
def save_brief_from_plan_endpoint(
    req: SaveBriefFromPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Saves a finalized Xero AI project plan into a persistent, database-backed Brief record.
    Preserves all structured plan fields (category, deliverables, budget, timeline, milestones).
    """
    session = db.query(XeroSession).filter(XeroSession.id == req.session_id).first()
    if not session or not session.project_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session has no active project plan to save"
        )

    plan = ProjectPlan(**session.project_plan)

    deliverable_names = [f"{d.name} (x{d.quantity})" for d in plan.deliverables]

    brief = Brief(
        brand_user_id=current_user.id,
        title=req.title_override or plan.project_title,
        description=plan.summary,
        prompt_text=f"Generated via Xero AI 2.0 (Session: {session.id})\nCreative Direction: {plan.creative_direction}",
        content_type=plan.content_format,
        style=", ".join(plan.style_direction),
        target_audience=plan.target_audience,
        platform=plan.platforms,
        duration=plan.duration,
        aspect_ratio=plan.deliverables[0].aspect_ratio if plan.deliverables else "9:16",
        deliverables=deliverable_names,
        tools_suggested=plan.preferred_tools,
        budget_min=round(plan.budget * 0.85, 2),
        budget_max=round(plan.budget * 1.15, 2),
        deadline=None,
        commercial_rights_required=True,
        status="published",
    )
    db.add(brief)
    db.commit()
    db.refresh(brief)
    return brief
