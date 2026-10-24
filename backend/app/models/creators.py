from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class CreatorProfile(Base):
    __tablename__ = "creator_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    tagline = Column(String(500), nullable=True)
    specialization = Column(String(255), nullable=False)  # e.g., Luxury Fashion, Sci-Fi Film, Cinematic 3D
    skills = Column(JSON, default=list, nullable=False)  # list of strings
    ai_tools = Column(JSON, default=list, nullable=False)  # e.g., ["Midjourney v6", "Runway Gen-3", "ComfyUI", "Sora"]
    starting_rate = Column(Float, default=500.0, nullable=False)
    delivery_days = Column(Integer, default=7, nullable=False)
    commercial_rights = Column(Boolean, default=True, nullable=False)
    availability_status = Column(String(50), default="available", nullable=False)  # available, busy, booked
    rating = Column(Float, default=5.0, nullable=False)
    total_briefs = Column(Integer, default=0, nullable=False)
    sla_score = Column(Float, default=98.0, nullable=False)  # percentage
    on_time_percentage = Column(Float, default=100.0, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    location = Column(String(255), nullable=True)
    core_category = Column(String(100), nullable=True)  # e.g., "AI Video", "AI Images", "3D & CGI"
    sub_specializations = Column(JSON, default=list, nullable=True)  # e.g., ["Cinematic Video", "Automotive"]
    style_tags = Column(JSON, default=list, nullable=True)  # e.g., ["Cinematic", "Luxury", "Photorealistic"]
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="creator_profile")
    portfolio_items = relationship("PortfolioItem", back_populates="creator", cascade="all, delete-orphan")
    achievements = relationship("CreatorAchievement", back_populates="creator", cascade="all, delete-orphan")
    verifications = relationship("Verification", back_populates="creator", cascade="all, delete-orphan")
    leaderboard_entries = relationship("LeaderboardEntry", back_populates="creator", cascade="all, delete-orphan")
    licensing = relationship("CreatorLicensing", back_populates="creator_profile", uselist=False, cascade="all, delete-orphan")


class PortfolioItem(Base):
    __tablename__ = "portfolio_items"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=False)
    category = Column(String(100), default="video", nullable=False)  # video, fashion, 3d, audio, brand
    tools_used = Column(JSON, default=list, nullable=False)  # list of tools
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    creator = relationship("CreatorProfile", back_populates="portfolio_items")


class CreatorAchievement(Base):
    __tablename__ = "creator_achievements"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    badge_type = Column(String(100), nullable=False)  # gold, silver, award, top_rated, verified
    awarded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    creator = relationship("CreatorProfile", back_populates="achievements")


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("creator_profiles.id", ondelete="CASCADE"), nullable=False)
    verification_type = Column(String(100), nullable=False)  # identity, tools, portfolio, workflow, past_work, commercial_rights
    status = Column(String(50), default="verified", nullable=False)  # verified, pending, rejected
    verified_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    details = Column(Text, nullable=True)

    creator = relationship("CreatorProfile", back_populates="verifications")
