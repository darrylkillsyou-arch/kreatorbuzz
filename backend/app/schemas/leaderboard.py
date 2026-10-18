from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict
from app.schemas.creators import CreatorProfileResponse


class MonthlySummaryStats(BaseModel):
    selected_month: str  # e.g., "2026-10"
    completed_projects: int
    active_creators: int
    verified_reviews: int
    average_verified_rating: float
    deliverables_completed: int
    source: str = "real_database"


class CreatorMonthlyMetrics(BaseModel):
    completed_projects: int
    verified_reviews_count: int
    verified_rating: Optional[float] = None
    released_milestones: int
    revision_requests: int
    revision_efficiency_pct: float
    production_deliverables: int
    community_posts: int


class MonthlyRankedCreator(BaseModel):
    rank: int
    creator_id: int
    user_id: int
    name: str
    avatar: Optional[str] = None
    hero_image: Optional[str] = None
    primary_category: str
    specialization: str
    bio: Optional[str] = None
    monthly_performance_score: float
    rank_movement: str  # "+2", "-1", "=", or "NEW"
    badge: Optional[str] = None
    explanation: str
    profile_strength: float  # Separate 0-100% profile metric
    metrics: CreatorMonthlyMetrics
    creator_profile: Optional[CreatorProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)


class MonthlyAward(BaseModel):
    award_title: str  # "Creator of the Month", "Top Rated", "Most Productive", "Delivery Leader", "Rising Creator"
    creator_id: int
    creator_name: str
    avatar: Optional[str] = None
    category: str
    score: float
    reason: str


class CategoryTopCreators(BaseModel):
    category: str
    creators: List[MonthlyRankedCreator]


class MonthlyLeaderboardResponse(BaseModel):
    selected_month: str  # "2026-10"
    month_name: str      # "October 2026"
    available_months: List[str]  # ["2026-08", "2026-09", "2026-10"]
    summary: MonthlySummaryStats
    top_10: List[MonthlyRankedCreator]
    awards: List[MonthlyAward]
    category_champions: List[CategoryTopCreators]
    total_qualifying_creators: int


# Backward compatibility
PlatformSummaryStats = MonthlySummaryStats
DynamicLeaderboardResponse = MonthlyLeaderboardResponse
LeaderboardResponse = MonthlyLeaderboardResponse
