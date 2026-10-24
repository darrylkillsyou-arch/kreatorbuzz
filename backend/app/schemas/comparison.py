"""Schemas for side-by-side creator comparison and difference explanations."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.trust import TrustBadge, ReliabilityFlags


class CreatorCompareCard(BaseModel):
    """Normalized metrics for a single creator in side-by-side comparison."""
    creator_id: int
    user_id: int
    display_name: str
    avatar_url: Optional[str] = None
    specialization: str
    core_category: Optional[str] = None
    starting_rate: float
    delivery_days: int
    rating: float
    sla_score: float
    match_score: int = 85
    ai_tools: List[str] = []
    portfolio_count: int = 0
    portfolio_samples: List[Dict[str, Any]] = []
    licensing_status: str = "full_match"
    licensing_summary: str = "Standard Commercial License"
    licensing_territory: str = "Worldwide"
    licensing_duration: str = "12 Months"
    is_rising_creator: bool = False
    reliability: ReliabilityFlags
    badges: List[TrustBadge] = []
    strengths: List[str] = []
    things_to_consider: List[str] = []


class DifferenceItem(BaseModel):
    """Detailed difference item for an individual creator relative to the peers."""
    creator_id: int
    creator_name: str
    unique_advantages: List[str]
    tradeoffs_vs_others: List[str]


class CreatorComparisonRequest(BaseModel):
    """Request payload to compare 2 or 3 creators."""
    creator_ids: List[int]
    brief_id: Optional[int] = None
    target_category: Optional[str] = None
    budget: Optional[float] = None
    timeline_days: Optional[int] = None


class CreatorComparisonResponse(BaseModel):
    """Full side-by-side comparison response with structured difference insights."""
    candidates: List[CreatorCompareCard]
    difference_explanations: List[DifferenceItem]
    summary_verdict: str
