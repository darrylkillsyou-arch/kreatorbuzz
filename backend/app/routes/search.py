"""Creator discovery and multi-parameter advanced search route."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, cast, String
from app.database import get_db
from app.models.users import User
from app.models.creators import CreatorProfile
from app.schemas.creators import CreatorProfileResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/creators", response_model=List[CreatorProfileResponse])
def search_creators(
    q: Optional[str] = Query(None, description="Free text search on name, tagline, bio, tools"),
    skills: Optional[str] = Query(None, description="Comma separated skill filters"),
    specialization: Optional[str] = Query(None, description="Specialization keyword"),
    tools: Optional[str] = Query(None, description="Comma separated AI tool names"),
    content_type: Optional[str] = Query(None, description="Preferred content type"),
    availability: Optional[str] = Query(None, description="available, busy, booked"),
    delivery_days: Optional[int] = Query(None, description="Max delivery turnaround days"),
    commercial_rights: Optional[bool] = Query(None, description="Requires full commercial rights"),
    max_rate: Optional[float] = Query(None, description="Maximum starting rate"),
    db: Session = Depends(get_db),
):
    """Advanced search and filtering for AI creators across tools, styles, ratings, and rates."""
    query = db.query(CreatorProfile).join(User).filter(User.is_active == True)

    if q:
        term = f"%{q.lower()}%"
        query = query.filter(
            or_(
                CreatorProfile.display_name.ilike(term),
                CreatorProfile.tagline.ilike(term),
                CreatorProfile.specialization.ilike(term),
                CreatorProfile.location.ilike(term),
                cast(CreatorProfile.skills, String).ilike(term),
                cast(CreatorProfile.ai_tools, String).ilike(term),
            )
        )

    if specialization:
        query = query.filter(CreatorProfile.specialization.ilike(f"%{specialization}%"))

    if availability:
        query = query.filter(CreatorProfile.availability_status == availability)

    if delivery_days is not None:
        query = query.filter(CreatorProfile.delivery_days <= delivery_days)

    if commercial_rights is not None:
        query = query.filter(CreatorProfile.commercial_rights == commercial_rights)

    if max_rate is not None:
        query = query.filter(CreatorProfile.starting_rate <= max_rate)

    results = query.order_by(CreatorProfile.rating.desc(), CreatorProfile.sla_score.desc()).all()

    # In-memory filter for JSON arrays (tools, skills, content_type)
    filtered = []
    for creator in results:
        match = True
        if tools:
            req_tools = [t.strip().lower() for t in tools.split(",") if t.strip()]
            creator_tools = [t.lower() for t in (creator.ai_tools or [])]
            if not any(rt in ct or ct in rt for rt in req_tools for ct in creator_tools):
                match = False

        if skills and match:
            req_skills = [s.strip().lower() for s in skills.split(",") if s.strip()]
            creator_skills = [s.lower() for s in (creator.skills or [])]
            if not any(rs in cs or cs in rs for rs in req_skills for cs in creator_skills):
                match = False

        if content_type and match:
            ct_lower = content_type.lower()
            spec_lower = creator.specialization.lower()
            tag_lower = (creator.tagline or "").lower()
            if ct_lower not in spec_lower and ct_lower not in tag_lower:
                match = False

        if match:
            filtered.append(creator)

    return filtered
