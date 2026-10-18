from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.users import UserResponse
from app.schemas.creators import CreatorProfileResponse


class BriefBase(BaseModel):
    title: str
    description: str
    prompt_text: Optional[str] = None
    content_type: str = "video"
    style: Optional[str] = None
    target_audience: Optional[str] = None
    platform: List[str] = []
    duration: Optional[str] = None
    aspect_ratio: str = "9:16"
    deliverables: List[str] = []
    tools_suggested: List[str] = []
    budget_min: float = 1000.0
    budget_max: float = 3000.0
    deadline: Optional[datetime] = None
    commercial_rights_required: bool = True
    status: str = "published"
    visual_reference_url: Optional[str] = None


class BriefCreate(BriefBase):
    pass


class BriefUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    prompt_text: Optional[str] = None
    content_type: Optional[str] = None
    style: Optional[str] = None
    target_audience: Optional[str] = None
    platform: Optional[List[str]] = None
    duration: Optional[str] = None
    aspect_ratio: Optional[str] = None
    deliverables: Optional[List[str]] = None
    tools_suggested: Optional[List[str]] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    deadline: Optional[datetime] = None
    commercial_rights_required: Optional[bool] = None
    status: Optional[str] = None
    visual_reference_url: Optional[str] = None


class BriefResponse(BriefBase):
    id: int
    brand_user_id: int
    created_at: datetime
    brand_user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class BriefGenerateRequest(BaseModel):
    prompt: str
    additional_notes: Optional[str] = None


class BriefGenerateResponse(BaseModel):
    title: str
    description: str
    content_type: str
    style: str
    target_audience: str
    platform: List[str]
    duration: str
    aspect_ratio: str
    deliverables: List[str]
    tools_suggested: List[str]
    budget_min: float
    budget_max: float
    suggested_timeline_days: int
    raw_prompt: str
    recommended_creator_category: str = "AI Videos"


class ScoreBreakdown(BaseModel):
    style_match: float
    tools_match: float
    skills_match: float
    availability_match: float
    delivery_match: float
    rights_match: float
    portfolio_match: float


class CreatorMatchItem(BaseModel):
    creator: CreatorProfileResponse
    match_score: int
    match_reasons: List[str]
    score_breakdown: ScoreBreakdown


class BriefMatchResponse(BaseModel):
    brief_id: int
    brief_title: str
    total_candidates: int
    matches: List[CreatorMatchItem]


class CreatorRecommendationRequest(BaseModel):
    category: Optional[str] = None
    content_type: Optional[str] = None
    style: Optional[str] = None
    tools_suggested: Optional[List[str]] = []
    budget: Optional[float] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    timeline_days: Optional[int] = None
    description: Optional[str] = None


class RecommendedCreatorItem(BaseModel):
    creator: CreatorProfileResponse
    match_score: int
    recommendation_reason: str
    match_reasons: List[str]
    score_breakdown: Optional[ScoreBreakdown] = None


class RecommendedCreatorsResponse(BaseModel):
    recommended_category: str
    total_matches: int
    creators: List[RecommendedCreatorItem]

