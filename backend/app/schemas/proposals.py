from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ProposalCreate(BaseModel):
    creator_id: Optional[str] = None
    creator_user_id: Optional[int] = None
    creator_profile_id: Optional[int] = None
    project_title: str
    project_requirement: str
    budget_in_rupees: float
    deadline: str


class ProposalResponse(BaseModel):
    id: int
    brand_user_id: int
    creator_user_id: int
    workspace_id: Optional[int] = None
    project_title: str
    project_requirement: str
    budget_in_rupees: float
    deadline: str
    status: str
    created_at: datetime
    recruiter_name: Optional[str] = None
    creator_name: Optional[str] = None
    creator_avatar: Optional[str] = None

    class Config:
        from_attributes = True
