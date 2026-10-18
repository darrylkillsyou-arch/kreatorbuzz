"""Director & Creator Monthly Leaderboard routes (Leaderboard 2.0)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.leaderboard import (
    MonthlyLeaderboardResponse,
    MonthlySummaryStats,
)
from app.services.leaderboard_service import (
    get_monthly_leaderboard,
)

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("", response_model=MonthlyLeaderboardResponse)
def get_monthly_creator_leaderboard(
    month: str = Query("2026-10", description="Selected calendar month formatted as 'YYYY-MM' (e.g. '2026-08', '2026-09', '2026-10')"),
    db: Session = Depends(get_db),
):
    """Retrieves dynamic monthly performance leaderboard for the specified month,

    including Top 10 Creators, Category Champions (Top 3 across all 9 disciplines),
    Monthly Awards, and honest operational summary metrics.
    """
    return get_monthly_leaderboard(db=db, month=month)


@router.get("/summary", response_model=MonthlySummaryStats)
def get_monthly_summary(
    month: str = Query("2026-10", description="Selected calendar month formatted as 'YYYY-MM'"),
    db: Session = Depends(get_db),
):
    """Retrieves operational summary metrics strictly for the specified calendar month."""
    res = get_monthly_leaderboard(db=db, month=month)
    return res.summary
