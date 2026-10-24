"""Routes for Creator Comparison, Trust Signals, and Blind Arena."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.creators import CreatorProfile
from app.models.users import User
from app.dependencies import get_current_user, get_optional_current_user
from app.schemas.comparison import (
    CreatorComparisonRequest,
    CreatorComparisonResponse,
)
from app.schemas.trust import (
    CreatorTrustResponse,
    RecruiterTrustResponse,
)
from app.schemas.blind_arena import (
    BlindArenaRequest,
    BlindArenaResponse,
    BlindRevealRequest,
    BlindRevealResponse,
)
from app.services.trust import evaluate_creator_trust, evaluate_recruiter_trust
from app.services.comparison import compare_creators
from app.services.blind_arena import create_blind_arena, reveal_blind_creator

router = APIRouter(prefix="/comparison", tags=["comparison"])


@router.post("/compare", response_model=CreatorComparisonResponse)
def compare_creators_endpoint(
    req: CreatorComparisonRequest,
    db: Session = Depends(get_db),
):
    """Side-by-side comparison of 2 or 3 creators with structured difference explanations."""
    if len(req.creator_ids) < 2 or len(req.creator_ids) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comparison requires selecting 2 or 3 creators.",
        )

    res = compare_creators(
        creator_ids=req.creator_ids,
        db=db,
        brief_id=req.brief_id,
        target_category=req.target_category,
        budget=req.budget or 0.0,
        timeline_days=req.timeline_days or 7,
    )
    return res


@router.get("/trust/{creator_profile_id}", response_model=CreatorTrustResponse)
def get_creator_trust_endpoint(
    creator_profile_id: int,
    db: Session = Depends(get_db),
):
    """Retrieves verified trust badges, reliability flags, and Rising Creator status."""
    creator = db.query(CreatorProfile).filter(CreatorProfile.id == creator_profile_id).first()
    if not creator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator not found")

    return evaluate_creator_trust(creator, db)


@router.get("/recruiter-trust/{user_id}", response_model=RecruiterTrustResponse)
def get_recruiter_trust_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
):
    """Retrieves transparent recruiter reliability signals visible to creators."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return evaluate_recruiter_trust(user, db)


@router.post("/blind-arena", response_model=BlindArenaResponse)
def create_blind_arena_endpoint(
    req: BlindArenaRequest,
    db: Session = Depends(get_db),
):
    """Initiates an anonymized Blind Arena hiring evaluation session."""
    if len(req.creator_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blind Arena requires at least 2 creators to evaluate.",
        )

    return create_blind_arena(
        creator_ids=req.creator_ids,
        db=db,
        brief_id=req.brief_id,
        target_category=req.target_category,
        budget=req.budget or 0.0,
        timeline_days=req.timeline_days or 7,
    )


@router.post("/blind-arena/reveal", response_model=BlindRevealResponse)
def reveal_blind_creator_endpoint(
    req: BlindRevealRequest,
    db: Session = Depends(get_db),
):
    """Reveals the chosen blind creator's real identity with fairness breakdown."""
    try:
        return reveal_blind_creator(
            chosen_token=req.blind_token,
            all_tokens=req.all_tokens,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
