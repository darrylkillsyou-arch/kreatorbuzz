"""Schemas for creator and recruiter trust signals and reliability flags."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class TrustBadge(BaseModel):
    """Individual verified trust badge backed by verifiable platform evidence."""
    id: str  # identity, portfolio, tools, commercial, reviews, delivery
    label: str
    verified: bool
    evidence: str
    icon: Optional[str] = None


class ReliabilityFlags(BaseModel):
    """Explainable creator reliability metrics and overall status."""
    completed_projects: int = 0
    late_deliveries: int = 0
    abandoned_projects: int = 0
    unresolved_disputes: int = 0
    on_time_percentage: float = 100.0
    status: str  # Reliable | Minor Concern | Reliability Concern
    notes: List[str] = []


class CreatorTrustResponse(BaseModel):
    """Full trust profile for a creator."""
    creator_id: int
    user_id: int
    display_name: str
    is_verified: bool
    is_rising_creator: bool
    rising_creator_reason: Optional[str] = None
    badges: List[TrustBadge] = []
    reliability: ReliabilityFlags

    model_config = ConfigDict(from_attributes=True)


class RecruiterTrustResponse(BaseModel):
    """Recruiter trust signals shown to creators."""
    recruiter_user_id: int
    company_name: Optional[str] = None
    is_verified_business: bool = False
    projects_commissioned: int = 0
    projects_completed: int = 0
    completion_rate_pct: float = 100.0
    abandoned_engagements: int = 0
    dispute_count: int = 0
    response_behavior: str = "Prompt (< 2 hours)"
    trust_status: str  # Verified Brand | Established Recruiter | New Brand
