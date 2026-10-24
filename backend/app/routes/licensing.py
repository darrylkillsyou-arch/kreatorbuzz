"""Licensing management routes for KreatorBuzz Phase 2A."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User
from app.models.creators import CreatorProfile
from app.models.briefs import Brief
from app.models.licensing import CreatorLicensing, BriefLicensing
from app.schemas.licensing import (
    CreatorLicensingCreate,
    CreatorLicensingUpdate,
    CreatorLicensingResponse,
    BriefLicensingCreate,
    BriefLicensingUpdate,
    BriefLicensingResponse,
    LicensingCompatibilityResult,
)
from app.dependencies import get_current_user
from app.services.licensing import check_licensing_compatibility, build_licensing_explanation

router = APIRouter(prefix="/licensing", tags=["licensing"])


# --- Creator Licensing ---

@router.get("/creator/{creator_profile_id}", response_model=CreatorLicensingResponse)
def get_creator_licensing(creator_profile_id: int, db: Session = Depends(get_db)):
    """Get a creator's licensing offer."""
    lic = db.query(CreatorLicensing).filter(
        CreatorLicensing.creator_profile_id == creator_profile_id
    ).first()
    if not lic:
        raise HTTPException(status_code=404, detail="Creator licensing data not found")
    return lic


@router.post("/creator/{creator_profile_id}", response_model=CreatorLicensingResponse, status_code=201)
def set_creator_licensing(
    creator_profile_id: int,
    data: CreatorLicensingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Set or replace a creator's licensing offer."""
    profile = db.query(CreatorProfile).filter(CreatorProfile.id == creator_profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Creator profile not found")
    if profile.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    existing = db.query(CreatorLicensing).filter(
        CreatorLicensing.creator_profile_id == creator_profile_id
    ).first()

    if existing:
        for field, value in data.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    lic = CreatorLicensing(creator_profile_id=creator_profile_id, **data.model_dump())
    db.add(lic)
    db.commit()
    db.refresh(lic)
    return lic


@router.patch("/creator/{creator_profile_id}", response_model=CreatorLicensingResponse)
def update_creator_licensing(
    creator_profile_id: int,
    data: CreatorLicensingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update specific fields of a creator's licensing offer."""
    profile = db.query(CreatorProfile).filter(CreatorProfile.id == creator_profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Creator profile not found")
    if profile.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    lic = db.query(CreatorLicensing).filter(
        CreatorLicensing.creator_profile_id == creator_profile_id
    ).first()
    if not lic:
        raise HTTPException(status_code=404, detail="Creator licensing data not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lic, field, value)
    db.commit()
    db.refresh(lic)
    return lic


# --- Brief Licensing ---

@router.get("/brief/{brief_id}", response_model=BriefLicensingResponse)
def get_brief_licensing(brief_id: int, db: Session = Depends(get_db)):
    """Get a brief's licensing requirements."""
    lic = db.query(BriefLicensing).filter(BriefLicensing.brief_id == brief_id).first()
    if not lic:
        raise HTTPException(status_code=404, detail="Brief licensing data not found")
    return lic


@router.post("/brief/{brief_id}", response_model=BriefLicensingResponse, status_code=201)
def set_brief_licensing(
    brief_id: int,
    data: BriefLicensingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Set licensing requirements for a brief."""
    brief = db.query(Brief).filter(Brief.id == brief_id).first()
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    if brief.brand_user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    existing = db.query(BriefLicensing).filter(BriefLicensing.brief_id == brief_id).first()
    if existing:
        for field, value in data.model_dump().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    lic = BriefLicensing(brief_id=brief_id, **data.model_dump())
    db.add(lic)
    db.commit()
    db.refresh(lic)
    return lic


@router.patch("/brief/{brief_id}", response_model=BriefLicensingResponse)
def update_brief_licensing(
    brief_id: int,
    data: BriefLicensingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update specific fields of a brief's licensing requirements."""
    brief = db.query(Brief).filter(Brief.id == brief_id).first()
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    if brief.brand_user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    lic = db.query(BriefLicensing).filter(BriefLicensing.brief_id == brief_id).first()
    if not lic:
        raise HTTPException(status_code=404, detail="Brief licensing data not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lic, field, value)
    db.commit()
    db.refresh(lic)
    return lic


# --- Compatibility Check ---

@router.get("/check/{brief_id}/{creator_profile_id}", response_model=LicensingCompatibilityResult)
def check_compatibility(
    brief_id: int,
    creator_profile_id: int,
    db: Session = Depends(get_db),
):
    """Check licensing compatibility between a brief and a creator."""
    brief_lic = db.query(BriefLicensing).filter(BriefLicensing.brief_id == brief_id).first()
    creator_lic = db.query(CreatorLicensing).filter(
        CreatorLicensing.creator_profile_id == creator_profile_id
    ).first()

    result = check_licensing_compatibility(brief_lic, creator_lic)
    explanation = build_licensing_explanation(result)

    return LicensingCompatibilityResult(
        licensing_status=result["licensing_status"],
        licensing_score=result["licensing_score"],
        licensing_strengths=result["licensing_strengths"],
        licensing_conflicts=result["licensing_conflicts"],
        explanation=explanation,
    )
