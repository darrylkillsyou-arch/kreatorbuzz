from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, ConfigDict
from app.schemas.users import UserResponse
from app.schemas.creators import CreatorProfileResponse
from app.schemas.briefs import BriefResponse


class ShortlistCreate(BaseModel):
    creator_user_id: Optional[int] = None
    creator_profile_id: Optional[int] = None
    creator_id: Optional[Union[int, str]] = None
    brief_id: Optional[int] = None


class ShortlistResponse(BaseModel):
    id: int
    brand_user_id: int
    creator_user_id: int
    brief_id: Optional[int] = None
    created_at: datetime
    creator_user: Optional[UserResponse] = None
    creator_profile: Optional[CreatorProfileResponse] = None
    brief: Optional[BriefResponse] = None

    model_config = ConfigDict(from_attributes=True)


class HireRequest(BaseModel):
    title: Optional[str] = None
    initial_milestone_amount: Optional[float] = None
