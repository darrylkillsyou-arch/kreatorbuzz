from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class LeaderboardEntry(Base):
    __tablename__ = "leaderboard_entries"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100), nullable=False)  # creator_of_week, most_trusted, best_ai_video, most_helpful, rising
    score = Column(Float, default=0.0, nullable=False)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    creator = relationship("CreatorProfile", back_populates="leaderboard_entries")
