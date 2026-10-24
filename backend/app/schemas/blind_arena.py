"""Schemas for KreatorBuzz Blind Arena hiring mode."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.comparison import CreatorCompareCard


class BlindPortfolioSample(BaseModel):
    """Anonymous portfolio sample with work quality signals intact."""
    title: str
    category: str
    image_url: str
    tools_used: List[str] = []


class BlindCreatorCard(BaseModel):
    """Anonymized creator card preserving work quality while hiding reputation signals."""
    anonymous_id: str  # "Creator A", "Creator B", "Creator C"
    blind_token: str   # Opaque session token to reveal later
    specialization: str
    core_category: Optional[str] = None
    match_score: int
    starting_rate: float
    delivery_days: int
    ai_tools: List[str] = []
    portfolio_samples: List[BlindPortfolioSample] = []
    licensing_status: str
    licensing_summary: str
    is_rising_creator: bool
    strengths: List[str] = []
    things_to_consider: List[str] = []


class BlindArenaRequest(BaseModel):
    """Request to initiate Blind Arena evaluation."""
    creator_ids: List[int]
    brief_id: Optional[int] = None
    target_category: Optional[str] = None
    budget: Optional[float] = None
    timeline_days: Optional[int] = None


class BlindArenaResponse(BaseModel):
    """Response payload containing anonymized creator cards."""
    blind_arena_id: str
    tagline: str = "Choose the work. Then meet the creator."
    candidates: List[BlindCreatorCard]


class BlindRevealRequest(BaseModel):
    """Request to reveal the identity of the chosen blind creator."""
    blind_token: str
    all_tokens: List[str] = []


class WhatOthersDidBetter(BaseModel):
    """Transparent comparison note on what non-selected candidates excelled at."""
    anonymous_id: str
    strengths: List[str]


class BlindRevealResponse(BaseModel):
    """Revealed creator identity and fairness decision breakdown."""
    revealed_creator: CreatorCompareCard
    why_this_creator_won: str
    what_others_did_better: List[WhatOthersDidBetter] = []
