from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.users import UserResponse
from app.schemas.briefs import BriefResponse


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: int
    workspace_id: int
    sender_id: int
    content: str  # Decrypted content presented to client
    created_at: datetime
    sender: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class RevisionCreate(BaseModel):
    milestone_id: Optional[int] = None
    description: Optional[str] = None
    notes: Optional[str] = None

    @property
    def text(self) -> str:
        return (self.description or self.notes or "").strip()


class RevisionUpdate(BaseModel):
    status: Optional[str] = None  # requested, in_progress, submitted, approved
    response_notes: Optional[str] = None


class RevisionResponse(BaseModel):
    id: int
    milestone_id: Optional[int] = None
    workspace_id: int
    requester_id: int
    description: str
    status: str
    response_notes: Optional[str] = None
    created_at: datetime
    requester: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class MilestoneCreate(BaseModel):
    title: str
    description: Optional[str] = None
    amount: float = 0.0
    estimated_date: Optional[datetime] = None


class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None  # pending, approved, in_review, released
    estimated_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class MilestoneResponse(BaseModel):
    id: int
    workspace_id: int
    title: str
    description: Optional[str] = None
    amount: float
    status: str
    estimated_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    revisions: List[RevisionResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ── Buzz Check schemas ────────────────────────────────────────────────────────

class BuzzCheckItem(BaseModel):
    """A single check line within a Buzz Check result."""
    name: str
    label: str
    status: str   # passed | failed | not_verified
    detail: str


class BuzzCheckResult(BaseModel):
    """Full Buzz Check result for one uploaded deliverable version."""
    id: Optional[int] = None
    file_id: int
    workspace_id: int
    version: int
    overall_status: str          # ready | needs_attention | blocked
    readiness_score: int         # 0–100
    check_details: List[BuzzCheckItem] = []
    warnings: List[str] = []
    suggested_fixes: List[str] = []
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── File / Deliverable schemas ────────────────────────────────────────────────

class FileResponse(BaseModel):
    id: int
    workspace_id: int
    milestone_id: Optional[int] = None
    uploader_id: int
    filename: str
    file_size: Optional[str] = None
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    version: int = 1
    status: str = "submitted"
    description: Optional[str] = None
    client_feedback: Optional[str] = None
    # Buzz Check metadata (may be None for older uploads)
    width: Optional[int] = None
    height: Optional[int] = None
    duration_seconds: Optional[float] = None
    deliverable_type: Optional[str] = None
    is_current: bool = False
    created_at: datetime
    uploader: Optional[UserResponse] = None
    download_url: Optional[str] = None
    buzz_check: Optional[BuzzCheckResult] = None

    model_config = ConfigDict(from_attributes=True)


class DeliverableFeedbackCreate(BaseModel):
    client_feedback: Optional[str] = None
    status: Optional[str] = None  # approved, revision_requested, submitted


class AgreedLicensingResponse(BaseModel):
    commercial_use: bool = True
    usage_types: List[str] = []
    territory: str = "Worldwide"
    duration_months: int = 12
    duration_label: str = "12 Months"
    platforms: List[str] = []
    notes: Optional[str] = None


class ProductionTimelineItem(BaseModel):
    id: str
    item_type: str  # version_upload, revision_request, revision_status, milestone_status, buzz_check
    version: Optional[int] = None
    file_id: Optional[int] = None
    filename: Optional[str] = None
    download_url: Optional[str] = None
    milestone_id: Optional[int] = None
    milestone_title: Optional[str] = None
    actor_name: str
    actor_role: str  # creator, brand, system
    creator_note: Optional[str] = None
    client_feedback: Optional[str] = None
    revision_description: Optional[str] = None
    revision_response: Optional[str] = None
    status: str
    # Buzz Check inline summary (only present on buzz_check items)
    buzz_overall_status: Optional[str] = None
    buzz_readiness_score: Optional[int] = None
    created_at: datetime


class ReviewCreate(BaseModel):
    rating: int  # 1 to 5
    comment: str


class ReviewResponse(BaseModel):
    id: int
    workspace_id: int
    recruiter_user_id: int
    creator_user_id: int
    rating: int
    comment: str
    created_at: datetime
    recruiter: Optional[UserResponse] = None
    creator: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class WorkspaceCreate(BaseModel):
    brief_id: Optional[int] = None
    creator_user_id: int
    title: str
    initial_milestones: Optional[List[MilestoneCreate]] = None


class WorkspaceResponse(BaseModel):
    id: int
    brief_id: Optional[int] = None
    brand_user_id: int
    creator_user_id: int
    title: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    brand_user: Optional[UserResponse] = None
    creator_user: Optional[UserResponse] = None
    brief: Optional[BriefResponse] = None
    milestones: List[MilestoneResponse] = []
    review: Optional[ReviewResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ── Project Rescue schemas ───────────────────────────────────────────────────

class ProtectedBudgetResponse(BaseModel):
    total_budget: float
    approved_amount: float
    remaining_protected_balance: float
    disclaimer: str


class ProjectHealthResponse(BaseModel):
    health_score: int              # 0–100
    health_status: str             # ON TRACK | AT RISK | RESCUE RECOMMENDED
    reasons: List[str] = []
    adjust_plan_suggestions: List[str] = []
    protected_budget: ProtectedBudgetResponse


class ProjectHandoffPackResponse(BaseModel):
    workspace_id: int
    project_title: str
    brief_overview: dict
    agreed_licensing: dict
    completed_milestones: List[dict] = []
    remaining_milestones: List[dict] = []
    deliverable_history: List[dict] = []
    recruiter_feedback_summary: List[str] = []
    unresolved_revisions: List[dict] = []
    remaining_deadline: str
    remaining_scope: str


class RescueReplacementResponse(BaseModel):
    workspace_id: int
    health: ProjectHealthResponse
    handoff_pack: ProjectHandoffPackResponse
    replacement_candidates: List[dict] = []


class RescueActionRequest(BaseModel):
    action: str  # adjust_plan, continue_with_creator, initiate_replacement
    notes: Optional[str] = None
    replacement_creator_id: Optional[int] = None


class WorkspaceDetailResponse(WorkspaceResponse):
    milestones: List[MilestoneResponse] = []
    messages: List[MessageResponse] = []
    files: List[FileResponse] = []
    revisions: List[RevisionResponse] = []
    review: Optional[ReviewResponse] = None
    agreed_licensing: Optional[AgreedLicensingResponse] = None
    timeline: List[ProductionTimelineItem] = []
    health: Optional[ProjectHealthResponse] = None

    model_config = ConfigDict(from_attributes=True)

