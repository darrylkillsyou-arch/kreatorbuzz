from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Brief(Base):
    __tablename__ = "briefs"

    id = Column(Integer, primary_key=True, index=True)
    brand_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    prompt_text = Column(Text, nullable=True)  # Raw prompt used in brief generator
    content_type = Column(String(100), default="video", nullable=False)  # video, image, 3d, audio, campaign
    style = Column(String(255), nullable=True)  # Cinematic, Luxury, Hyper-real, Cyberpunk
    target_audience = Column(String(255), nullable=True)
    platform = Column(JSON, default=list, nullable=False)  # ["Instagram Reels", "TikTok", "YouTube", "Website"]
    duration = Column(String(100), nullable=True)  # e.g., "30 seconds", "15s reel"
    aspect_ratio = Column(String(50), default="9:16", nullable=False)  # 9:16, 16:9, 1:1, 4:5
    deliverables = Column(JSON, default=list, nullable=False)  # ["4K Master", "Clean Plate", "Sound Mix"]
    tools_suggested = Column(JSON, default=list, nullable=False)  # ["Midjourney", "Runway Gen-3", "ComfyUI"]
    budget_min = Column(Float, default=1000.0, nullable=False)
    budget_max = Column(Float, default=3000.0, nullable=False)
    deadline = Column(DateTime, nullable=True)
    commercial_rights_required = Column(Boolean, default=True, nullable=False)
    status = Column(String(50), default="published", nullable=False)  # draft, published, matched, in_progress, completed
    visual_reference_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    brand_user = relationship("User", back_populates="briefs")
    workspaces = relationship("Workspace", back_populates="brief")
    shortlists = relationship("Shortlist", back_populates="brief", cascade="all, delete-orphan")
    licensing = relationship("BriefLicensing", back_populates="brief", uselist=False, cascade="all, delete-orphan")


class XeroSession(Base):
    __tablename__ = "xero_sessions"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    project_plan = Column(JSON, nullable=True)
    messages = Column(JSON, default=list, nullable=False)
    creator_offset = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User")

