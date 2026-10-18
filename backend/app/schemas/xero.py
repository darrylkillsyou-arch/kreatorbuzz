from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class DeliverableItem(BaseModel):
    name: str
    type: str = "video"  # video, image, 3d, audio, document
    quantity: int = 1
    duration_seconds: Optional[int] = None
    aspect_ratio: Optional[str] = "9:16"


class BudgetBreakdownItem(BaseModel):
    item: str
    amount: float
    percentage: Optional[float] = None


class MilestoneItem(BaseModel):
    step: int
    title: str
    description: str
    duration_days: int
    deliverable_ids: Optional[List[str]] = []


class ProjectPlan(BaseModel):
    project_title: str
    summary: str
    objective: str
    target_audience: str
    creative_direction: str
    core_category: str  # Valid CODE XERO category
    specializations: List[str] = []
    content_format: str = "video"
    deliverables: List[DeliverableItem] = []
    duration: Optional[str] = "30 seconds"
    platforms: List[str] = []
    timeline_days: int = 7
    budget: float = 60000.0
    budget_breakdown: List[BudgetBreakdownItem] = []
    milestones: List[MilestoneItem] = []
    preferred_tools: List[str] = []
    style_direction: List[str] = []
    risks_and_production_notes: List[str] = []
    creator_requirements: List[str] = []
    scope_warning: Optional[str] = None


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: Optional[str] = None


class XeroConversationResponse(BaseModel):
    session_id: str
    message: str
    plan: Optional[ProjectPlan] = None
    follow_up_questions: List[str] = []
    recommended_creators: List[Dict[str, Any]] = []
    total_matching_creators: int = 0
    creator_offset: int = 0
    ai_provider_used: str  # "gemini" or "deterministic_fallback"
    scope_warning: Optional[str] = None


class XeroChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class SaveBriefFromPlanRequest(BaseModel):
    session_id: str
    title_override: Optional[str] = None
