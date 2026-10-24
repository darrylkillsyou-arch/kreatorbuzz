"""Licensing data model for creator commercial-use compatibility.

Adds licensing offer fields to CreatorProfile and licensing requirement
fields to Brief, enabling deterministic brand-vs-creator compatibility checks.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class CreatorLicensing(Base):
    """Describes what commercial licensing a creator is willing to provide."""
    __tablename__ = "creator_licensing"

    id = Column(Integer, primary_key=True, index=True)
    creator_profile_id = Column(
        Integer,
        ForeignKey("creator_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    commercial_use = Column(Boolean, default=True, nullable=False)
    usage_types = Column(JSON, default=list, nullable=False)
    # e.g. ["paid_ads", "organic_social", "website", "broadcast", "internal"]
    territories = Column(JSON, default=list, nullable=False)
    # e.g. ["india", "asia", "worldwide"]
    max_duration_months = Column(Integer, default=12, nullable=False)
    # 3, 6, 12, 24, or 0 for perpetual
    platforms = Column(JSON, default=list, nullable=False)
    # e.g. ["instagram", "youtube", "website", "tiktok", "linkedin", "ecommerce"]
    additional_notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    creator_profile = relationship("CreatorProfile", back_populates="licensing")


class BriefLicensing(Base):
    """Describes what commercial licensing a brand requires for a brief."""
    __tablename__ = "brief_licensing"

    id = Column(Integer, primary_key=True, index=True)
    brief_id = Column(
        Integer,
        ForeignKey("briefs.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    commercial_use_required = Column(Boolean, default=True, nullable=False)
    usage_types = Column(JSON, default=list, nullable=False)
    territory = Column(String(100), default="india", nullable=False)
    # "india", "asia", "worldwide", or custom
    usage_duration_months = Column(Integer, default=12, nullable=False)
    # 3, 6, 12, 24, or 0 for perpetual
    platforms = Column(JSON, default=list, nullable=False)

    brief = relationship("Brief", back_populates="licensing")
