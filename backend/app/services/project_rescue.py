"""project_rescue.py — Project Rescue & Health Intelligence Service.

Detects project risk early using explainable signals from actual workspace data:
- Overdue milestones
- Approaching / missed overall project deadline
- Unresolved revision requests
- Creator inactivity / stalled communication
- Repeated Buzz Check failures or low delivery readiness
- Multiple revision cycles

Provides:
- 0–100 Explainable Project Health score & status (ON TRACK / AT RISK / RESCUE RECOMMENDED)
- Deterministic plan recovery suggestions
- Protected Budget simulation (approved milestones earned by Creator A, only remaining balance transferred)
- Project Handoff Pack so replacement creators do not restart from zero
- Replacement creator recommendations reusing the existing matching engine (excluding current creator)
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.workspaces import (
    Workspace,
    WorkspaceMilestone,
    RevisionRequest,
    SharedFile,
    WorkspaceMessage,
    DeliveryCheckResult,
    ProjectRescueLog,
)
from app.models.creators import CreatorProfile
from app.models.users import User
from app.services.matching import recommend_top_creators


def _safe_utc_now() -> datetime:
    """Returns naive UTC datetime matching database timestamps."""
    return datetime.utcnow()


def calculate_project_health(workspace: Workspace, db: Session) -> Dict[str, Any]:
    """Calculates an explainable 0–100 project health score and status for a workspace."""
    now = _safe_utc_now()
    score = 100
    reasons: List[str] = []
    adjust_suggestions: List[str] = []

    # 1. Milestone Status & Overdue Checks
    milestones = workspace.milestones or []
    unfinished_milestones = [m for m in milestones if m.status not in ("approved", "released")]
    completed_milestones = [m for m in milestones if m.status in ("approved", "released")]

    overdue_count = 0
    severe_overdue_count = 0
    for m in unfinished_milestones:
        if m.estimated_date:
            est = m.estimated_date.replace(tzinfo=None) if m.estimated_date.tzinfo else m.estimated_date
            if est < now:
                days_overdue = max(1, (now - est).days)
                overdue_count += 1
                if days_overdue >= 3:
                    severe_overdue_count += 1
                    score -= 20
                    reasons.append(f"Milestone '{m.title}' is critically overdue by {days_overdue} days")
                else:
                    score -= 10
                    reasons.append(f"Milestone '{m.title}' is overdue by {days_overdue} day(s)")

    if overdue_count > 0:
        adjust_suggestions.append("Extend remaining milestone deadlines by 3–5 business days")
        adjust_suggestions.append("Prioritize the current milestone before beginning subsequent deliverables")

    # 2. Overall Brief Deadline
    brief = workspace.brief
    if brief and brief.deadline:
        dl = brief.deadline.replace(tzinfo=None) if brief.deadline.tzinfo else brief.deadline
        if dl < now and workspace.status != "completed":
            score -= 25
            over_days = max(1, (now - dl).days)
            reasons.append(f"Overall project deadline was missed {over_days} day(s) ago")
            adjust_suggestions.append("Renegotiate or reset the project completion target date")
        elif (dl - now).days <= 2 and len(unfinished_milestones) >= 2:
            score -= 15
            reasons.append("Overall project deadline is in less than 48 hours with multiple unfinished deliverables")
            adjust_suggestions.append("Scope down non-essential deliverable variants to hit core deadline")

    # 3. Unresolved Revision Requests
    revisions = workspace.revisions or []
    unresolved_revs = [
        r for r in revisions if r.status in ("requested", "in_progress", "open")
    ]
    if len(unresolved_revs) >= 2:
        score -= 20
        reasons.append(f"{len(unresolved_revs)} unresolved revision requests pending creator action")
        adjust_suggestions.append("Schedule a brief review call or message exchange to clarify revision requirements")
    elif len(unresolved_revs) == 1:
        score -= 10
        reasons.append("1 active revision request currently awaiting creator resubmission")

    # 4. Multiple Revision Cycles on Same Milestone
    if len(revisions) >= 3:
        score -= 10
        reasons.append(f"High revision volume ({len(revisions)} total revision requests logged)")
        adjust_suggestions.append("Consolidate feedback into a single definitive revision checklist")

    # 5. Creator Inactivity in Active Production
    if workspace.status in ("production", "review") and workspace.creator_user_id:
        # Find latest activity from creator (message or file upload)
        creator_msgs = [m for m in (workspace.messages or []) if m.sender_id == workspace.creator_user_id]
        creator_files = [f for f in (workspace.files or []) if f.uploader_id == workspace.creator_user_id]

        latest_creator_time: Optional[datetime] = None
        for m in creator_msgs:
            mt = m.created_at.replace(tzinfo=None) if m.created_at and m.created_at.tzinfo else m.created_at
            if mt and (latest_creator_time is None or mt > latest_creator_time):
                latest_creator_time = mt
        for f in creator_files:
            ft = f.created_at.replace(tzinfo=None) if f.created_at and f.created_at.tzinfo else f.created_at
            if ft and (latest_creator_time is None or ft > latest_creator_time):
                latest_creator_time = ft

        # If no activity recorded yet, compare to workspace creation
        if latest_creator_time is None:
            latest_creator_time = workspace.created_at.replace(tzinfo=None) if workspace.created_at and workspace.created_at.tzinfo else workspace.created_at

        if latest_creator_time:
            hours_idle = (now - latest_creator_time).total_seconds() / 3600.0
            if hours_idle >= 120:  # 5+ days
                score -= 25
                reasons.append(f"Severe creator inactivity: no updates or uploads in over {int(hours_idle // 24)} days")
            elif hours_idle >= 72:  # 3–4 days
                score -= 15
                reasons.append(f"Creator has been inactive for {int(hours_idle)} hours without a status update")
                adjust_suggestions.append("Send a check-in ping to confirm creator availability and workload")

    # 6. Buzz Check Readiness on Latest Deliverable
    files = workspace.files or []
    if files:
        latest_file = sorted(files, key=lambda x: (x.version or 1, x.created_at or datetime.min), reverse=True)[0]
        latest_bc = (
            db.query(DeliveryCheckResult)
            .filter(DeliveryCheckResult.file_id == latest_file.id)
            .order_by(DeliveryCheckResult.id.desc())
            .first()
        )
        if latest_bc:
            if latest_bc.overall_status == "blocked":
                score -= 20
                reasons.append(
                    f"Latest deliverable (v{latest_file.version}) blocked Buzz Check (Readiness: {latest_bc.readiness_score}%)"
                )
                adjust_suggestions.append("Apply suggested Buzz Check fixes (format, aspect ratio, duration) before resubmission")
            elif latest_bc.overall_status == "needs_attention":
                score -= 10
                reasons.append(
                    f"Latest deliverable (v{latest_file.version}) needs attention ({latest_bc.readiness_score}% readiness)"
                )

    # Normalize final score between 0 and 100
    final_score = max(0, min(100, score))

    # Determine health status
    if final_score >= 75:
        health_status = "ON TRACK"
    elif final_score >= 45:
        health_status = "AT RISK"
    else:
        health_status = "RESCUE RECOMMENDED"

    if not reasons:
        reasons = [
            "All project milestones are progressing on schedule",
            "Creator communication and uploads are actively verified",
            "Automated delivery compliance checks passing",
        ]

    if not adjust_suggestions:
        adjust_suggestions = [
            "Maintain current production cadence",
            "Review next milestone deliverables in advance",
        ]

    # Protected Budget Simulation
    total_budget = sum(m.amount for m in milestones)
    if total_budget <= 0 and brief:
        total_budget = brief.budget_max or brief.budget_min or 50000.0

    approved_amount = sum(m.amount for m in completed_milestones)
    remaining_balance = max(0.0, total_budget - approved_amount)

    protected_budget = {
        "total_budget": total_budget,
        "approved_amount": approved_amount,
        "remaining_protected_balance": remaining_balance,
        "disclaimer": (
            "Protected Budget — Demo Simulation. Completed and approved milestone earnings "
            "are preserved for Creator A; only the remaining protected balance is allocated to a replacement engagement."
        ),
    }

    return {
        "health_score": final_score,
        "health_status": health_status,
        "reasons": reasons,
        "adjust_plan_suggestions": adjust_suggestions,
        "protected_budget": protected_budget,
    }


def generate_handoff_pack(workspace: Workspace, db: Session) -> Dict[str, Any]:
    """Builds a complete, portable Project Handoff Pack so replacement creators don't restart from zero."""
    brief = workspace.brief
    milestones = workspace.milestones or []
    files = workspace.files or []
    revisions = workspace.revisions or []

    completed_ms = [
        {
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "amount": m.amount,
            "status": m.status,
            "completed_at": m.completed_at.isoformat() if m.completed_at else None,
        }
        for m in milestones
        if m.status in ("approved", "released")
    ]

    remaining_ms = [
        {
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "amount": m.amount,
            "status": m.status,
            "estimated_date": m.estimated_date.isoformat() if m.estimated_date else None,
        }
        for m in milestones
        if m.status not in ("approved", "released")
    ]

    # Deliverables history with Buzz Check metadata
    deliverable_history = []
    for f in sorted(files, key=lambda x: (x.version or 1), reverse=True):
        bc = (
            db.query(DeliveryCheckResult)
            .filter(DeliveryCheckResult.file_id == f.id)
            .order_by(DeliveryCheckResult.id.desc())
            .first()
        )
        deliverable_history.append({
            "version": f.version or 1,
            "filename": f.filename,
            "file_type": f.file_type,
            "file_size": f.file_size,
            "status": f.status,
            "client_feedback": getattr(f, "client_feedback", None),
            "buzz_check_status": bc.overall_status if bc else "not_evaluated",
            "buzz_readiness_score": bc.readiness_score if bc else None,
            "created_at": f.created_at.isoformat() if f.created_at else None,
        })

    # Recruiter feedback summary
    feedback_notes = [
        f"V{f.version}: {f.client_feedback}"
        for f in files
        if getattr(f, "client_feedback", None)
    ]

    # Unresolved revisions
    unresolved_revisions = [
        {
            "id": r.id,
            "milestone_id": r.milestone_id,
            "description": r.description,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in revisions
        if r.status in ("requested", "in_progress", "open")
    ]

    # Agreed licensing terms
    brief_lic = getattr(brief, "licensing", None) if brief else None
    licensing_data = {
        "commercial_use": getattr(brief_lic, "commercial_use_required", True) if brief_lic else True,
        "usage_types": getattr(brief_lic, "usage_types", ["paid_ads", "organic_social"]) if brief_lic else ["paid_ads", "organic_social"],
        "territory": getattr(brief_lic, "territory", "worldwide") if brief_lic else "worldwide",
        "duration_months": getattr(brief_lic, "usage_duration_months", 12) if brief_lic else 12,
        "platforms": getattr(brief_lic, "platforms", ["instagram", "youtube", "website"]) if brief_lic else ["instagram", "youtube", "website"],
    }

    # Remaining deadline
    deadline_str = "Flexible"
    if brief and brief.deadline:
        dl = brief.deadline.replace(tzinfo=None) if brief.deadline.tzinfo else brief.deadline
        days_left = (dl - _safe_utc_now()).days
        deadline_str = f"{days_left} days remaining ({dl.strftime('%b %d, %Y')})"

    return {
        "workspace_id": workspace.id,
        "project_title": workspace.title,
        "brief_overview": {
            "title": brief.title if brief else workspace.title,
            "content_type": brief.content_type if brief else "video",
            "style": brief.style if brief else "Cinematic",
            "aspect_ratio": getattr(brief, "aspect_ratio", "9:16"),
            "duration": getattr(brief, "duration", "30 seconds"),
            "tools_suggested": getattr(brief, "tools_suggested", []),
            "deliverables_required": getattr(brief, "deliverables", []),
        },
        "agreed_licensing": licensing_data,
        "completed_milestones": completed_ms,
        "remaining_milestones": remaining_ms,
        "deliverable_history": deliverable_history,
        "recruiter_feedback_summary": feedback_notes,
        "unresolved_revisions": unresolved_revisions,
        "remaining_deadline": deadline_str,
        "remaining_scope": (
            f"{len(remaining_ms)} milestone(s) remaining. "
            f"{len(unresolved_revisions)} unresolved revision(s) require completion."
        ),
    }


def find_replacement_creators(
    workspace: Workspace, db: Session, limit: int = 3
) -> List[Dict[str, Any]]:
    """
    Finds the strongest 3 replacement creators using the existing matching engine.
    Strictly excludes the currently assigned creator from candidates.
    """
    brief = workspace.brief
    current_creator_user_id = workspace.creator_user_id

    # Query active creators excluding the current creator
    query = (
        db.query(CreatorProfile)
        .join(User)
        .filter(
            User.is_active == True,
            CreatorProfile.user_id != current_creator_user_id,
        )
    )

    candidate_profiles = query.all()
    if not candidate_profiles:
        return []

    # Calculate remaining budget for replacement
    milestones = workspace.milestones or []
    completed_amount = sum(m.amount for m in milestones if m.status in ("approved", "released"))
    total_budget = sum(m.amount for m in milestones)
    if total_budget <= 0 and brief:
        total_budget = brief.budget_max or 50000.0
    remaining_budget = max(0.0, total_budget - completed_amount)

    # Use brief requirements to score replacement candidates
    category = brief.content_type if brief else "video"
    style = brief.style if brief else ""
    tools = brief.tools_suggested if brief else []
    desc = brief.description if brief else workspace.title

    results = recommend_top_creators(
        category=category,
        content_type=category,
        style=style,
        tools_suggested=tools,
        budget=remaining_budget,
        budget_min=0.0,
        budget_max=remaining_budget,
        timeline_days=7,
        description=desc,
        creators=candidate_profiles,
        limit=limit,
    )

    formatted_replacements = []
    for item in results:
        creator: CreatorProfile = item["creator"]
        user = creator.user
        formatted_replacements.append({
            "creator_profile_id": creator.id,
            "creator_user_id": creator.user_id,
            "name": creator.display_name or (user.full_name if user else "Verified Creator"),
            "handle": f"@{creator.display_name.lower().replace(' ', '')}" if creator.display_name else "@creator",
            "primary_category": getattr(creator, "core_category", None) or "AI Video",
            "specialization": creator.specialization,
            "rating": creator.rating,
            "hourly_rate": getattr(creator, "starting_rate", 500.0),
            "match_score": item["match_score"],
            "recommendation_reason": item["recommendation_reason"],
            "match_reasons": item.get("match_reasons", []),
            "score_breakdown": item.get("score_breakdown", {}),
            "avatar_url": user.avatar_url if user else None,
        })

    return formatted_replacements
