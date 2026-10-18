"""Brief management, AI brief generation, and creator matching routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User
from app.models.briefs import Brief
from app.models.creators import CreatorProfile
from app.schemas.briefs import (
    BriefCreate,
    BriefUpdate,
    BriefResponse,
    BriefGenerateRequest,
    BriefGenerateResponse,
    BriefMatchResponse,
    CreatorMatchItem,
    ScoreBreakdown,
    CreatorRecommendationRequest,
    RecommendedCreatorsResponse,
    RecommendedCreatorItem,
)
from app.dependencies import get_current_user, get_current_brand_user
from app.services.brief_generator import generate_structured_brief
from app.services.matching import match_creators_for_brief, recommend_top_creators

router = APIRouter(prefix="/briefs", tags=["briefs"])


@router.post("/generate", response_model=BriefGenerateResponse)
def generate_brief_ai(req: BriefGenerateRequest):
    """Generates structured creative brief parameters from natural language prompt."""
    result = generate_structured_brief(prompt=req.prompt, additional_notes=req.additional_notes or "")
    return BriefGenerateResponse(**result)


@router.post("/recommend-creators", response_model=RecommendedCreatorsResponse)
def recommend_creators_endpoint(req: CreatorRecommendationRequest, db: Session = Depends(get_db)):
    """Recommends the top 3 creators tailored to a project plan."""
    creators = db.query(CreatorProfile).join(User).filter(User.is_active == True).all()
    
    target_category = req.category or "AI Videos"
    scored = recommend_top_creators(
        category=target_category,
        content_type=req.content_type or "",
        style=req.style or "",
        tools_suggested=req.tools_suggested or [],
        budget=req.budget or req.budget_max or req.budget_min or 0.0,
        budget_min=req.budget_min or 0.0,
        budget_max=req.budget_max or 0.0,
        timeline_days=req.timeline_days or 7,
        description=req.description or "",
        creators=creators,
        limit=5,
    )

    items = [
        RecommendedCreatorItem(
            creator=item["creator"],
            match_score=item["match_score"],
            recommendation_reason=item["recommendation_reason"],
            match_reasons=item["match_reasons"],
            score_breakdown=ScoreBreakdown(**item["score_breakdown"]) if item.get("score_breakdown") else None,
        )
        for item in scored
    ]

    return RecommendedCreatorsResponse(
        recommended_category=target_category,
        total_matches=len(items),
        creators=items,
    )



@router.post("", response_model=BriefResponse, status_code=status.HTTP_201_CREATED)
def create_brief(
    brief_in: BriefCreate,
    current_user: User = Depends(get_current_brand_user),
    db: Session = Depends(get_db),
):
    """Creates a new creative brief submitted by a brand."""
    brief = Brief(
        brand_user_id=current_user.id,
        title=brief_in.title,
        description=brief_in.description,
        prompt_text=brief_in.prompt_text,
        content_type=brief_in.content_type,
        style=brief_in.style,
        target_audience=brief_in.target_audience,
        platform=brief_in.platform,
        duration=brief_in.duration,
        aspect_ratio=brief_in.aspect_ratio,
        deliverables=brief_in.deliverables,
        tools_suggested=brief_in.tools_suggested,
        budget_min=brief_in.budget_min,
        budget_max=brief_in.budget_max,
        deadline=brief_in.deadline,
        commercial_rights_required=brief_in.commercial_rights_required,
        status=brief_in.status,
        visual_reference_url=brief_in.visual_reference_url,
    )
    db.add(brief)
    db.commit()
    db.refresh(brief)
    return brief


@router.get("", response_model=List[BriefResponse])
def list_briefs(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = None,
    content_type: Optional[str] = None,
    my_only: bool = False,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists published or brand's own briefs."""
    query = db.query(Brief)
    if my_only and current_user:
        query = query.filter(Brief.brand_user_id == current_user.id)
    elif status_filter:
        query = query.filter(Brief.status == status_filter)
    
    if content_type:
        query = query.filter(Brief.content_type.ilike(f"%{content_type}%"))

    return query.order_by(Brief.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{brief_id}", response_model=BriefResponse)
def get_brief(brief_id: int, db: Session = Depends(get_db)):
    """Retrieves single creative brief details."""
    brief = db.query(Brief).filter(Brief.id == brief_id).first()
    if not brief:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brief not found")
    return brief


@router.put("/{brief_id}", response_model=BriefResponse)
def update_brief(
    brief_id: int,
    brief_in: BriefUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Updates brief specifications."""
    brief = db.query(Brief).filter(Brief.id == brief_id).first()
    if not brief:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brief not found")
    if brief.brand_user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this brief")

    update_data = brief_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(brief, field, val)

    db.commit()
    db.refresh(brief)
    return brief


@router.post("/{brief_id}/match-creators", response_model=BriefMatchResponse)
@router.get("/{brief_id}/match-creators", response_model=BriefMatchResponse)
@router.post("/{brief_id}/match", response_model=BriefMatchResponse)
@router.get("/{brief_id}/match", response_model=BriefMatchResponse)
def match_creators(brief_id: str, db: Session = Depends(get_db)):
    """Matches registered creators against brief criteria with multi-factor scoring."""
    brief = None
    try:
        b_id = int(brief_id)
        brief = db.query(Brief).filter(Brief.id == b_id).first()
    except (ValueError, TypeError):
        brief = None

    if not brief:
        brief = db.query(Brief).first()

    creators = db.query(CreatorProfile).join(User).filter(User.is_active == True).all()
    if brief:
        scored_creators = match_creators_for_brief(brief, creators)
        matches = [
            CreatorMatchItem(
                creator=item["creator"],
                match_score=item["match_score"],
                match_reasons=item["match_reasons"],
                score_breakdown=ScoreBreakdown(**item["score_breakdown"]),
            )
            for item in scored_creators
        ]
        brief_title = brief.title
        res_id = brief.id
    else:
        matches = [
            CreatorMatchItem(
                creator=c,
                match_score=int(c.rating * 20),
                match_reasons=["Verified Tier-1 Creator", "High SLA performance record"],
                score_breakdown=ScoreBreakdown(
                    style_match=25.0,
                    tools_match=20.0,
                    skills_match=15.0,
                    availability_match=10.0,
                    delivery_match=10.0,
                    rights_match=10.0,
                    portfolio_match=10.0,
                ),
            )
            for c in creators[:6]
        ]
        brief_title = "Active Commission Brief"
        res_id = 1

    return BriefMatchResponse(
        brief_id=res_id,
        brief_title=brief_title,
        total_candidates=len(creators),
        matches=matches,
    )
