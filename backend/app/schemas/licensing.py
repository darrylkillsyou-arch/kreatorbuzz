"""Pydantic schemas for licensing data model."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class CreatorLicensingBase(BaseModel):
    commercial_use: bool = True
    usage_types: List[str] = []
    territories: List[str] = ["india"]
    max_duration_months: int = 12
    platforms: List[str] = []
    additional_notes: Optional[str] = None


class CreatorLicensingCreate(CreatorLicensingBase):
    pass


class CreatorLicensingUpdate(BaseModel):
    commercial_use: Optional[bool] = None
    usage_types: Optional[List[str]] = None
    territories: Optional[List[str]] = None
    max_duration_months: Optional[int] = None
    platforms: Optional[List[str]] = None
    additional_notes: Optional[str] = None


class CreatorLicensingResponse(CreatorLicensingBase):
    id: int
    creator_profile_id: int

    model_config = ConfigDict(from_attributes=True)


class BriefLicensingBase(BaseModel):
    commercial_use_required: bool = True
    usage_types: List[str] = []
    territory: str = "india"
    usage_duration_months: int = 12
    platforms: List[str] = []


class BriefLicensingCreate(BriefLicensingBase):
    pass


class BriefLicensingUpdate(BaseModel):
    commercial_use_required: Optional[bool] = None
    usage_types: Optional[List[str]] = None
    territory: Optional[str] = None
    usage_duration_months: Optional[int] = None
    platforms: Optional[List[str]] = None


class BriefLicensingResponse(BriefLicensingBase):
    id: int
    brief_id: int

    model_config = ConfigDict(from_attributes=True)


class LicensingCompatibilityResult(BaseModel):
    licensing_status: str  # full_match | partial_match | mismatch
    licensing_score: float  # 0-25
    licensing_strengths: List[str]
    licensing_conflicts: List[str]
    explanation: str
