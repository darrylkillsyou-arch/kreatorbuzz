from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.users import UserResponse


class PortfolioItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: str
    category: str = "video"
    tools_used: List[str] = []


class PortfolioItemCreate(PortfolioItemBase):
    pass


class PortfolioItemResponse(PortfolioItemBase):
    id: int
    creator_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AchievementResponse(BaseModel):
    id: int
    creator_id: int
    title: str
    description: Optional[str] = None
    badge_type: str
    awarded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VerificationResponse(BaseModel):
    id: int
    creator_id: int
    verification_type: str
    status: str
    verified_at: datetime
    details: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CreatorProfileBase(BaseModel):
    display_name: str
    tagline: Optional[str] = None
    specialization: str
    skills: List[str] = []
    ai_tools: List[str] = []
    starting_rate: float = 500.0
    delivery_days: int = 7
    commercial_rights: bool = True
    availability_status: str = "available"
    rating: float = 5.0
    total_briefs: int = 0
    sla_score: float = 98.0
    on_time_percentage: float = 100.0
    is_verified: bool = False
    location: Optional[str] = None
    core_category: Optional[str] = None
    sub_specializations: List[str] = []
    style_tags: List[str] = []


class CreatorProfileCreate(CreatorProfileBase):
    pass


class CreatorProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    tagline: Optional[str] = None
    specialization: Optional[str] = None
    skills: Optional[List[str]] = None
    ai_tools: Optional[List[str]] = None
    starting_rate: Optional[float] = None
    delivery_days: Optional[int] = None
    commercial_rights: Optional[bool] = None
    availability_status: Optional[str] = None
    location: Optional[str] = None
    core_category: Optional[str] = None
    sub_specializations: Optional[List[str]] = None
    style_tags: Optional[List[str]] = None


class CreatorProfileResponse(CreatorProfileBase):
    id: int
    user_id: int
    created_at: datetime
    user: Optional[UserResponse] = None
    portfolio_items: List[PortfolioItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class CreatorDetailResponse(CreatorProfileResponse):
    achievements: List[AchievementResponse] = []
    verifications: List[VerificationResponse] = []

    model_config = ConfigDict(from_attributes=True)
