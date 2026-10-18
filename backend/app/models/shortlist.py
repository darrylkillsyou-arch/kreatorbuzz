from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Shortlist(Base):
    __tablename__ = "shortlists"

    id = Column(Integer, primary_key=True, index=True)
    brand_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creator_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    brief_id = Column(Integer, ForeignKey("briefs.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("brand_user_id", "creator_user_id", "brief_id", name="unique_brand_creator_brief_shortlist"),
    )

    brand_user = relationship("User", foreign_keys=[brand_user_id], back_populates="shortlists")
    creator_user = relationship("User", foreign_keys=[creator_user_id])
    brief = relationship("Brief", back_populates="shortlists")
