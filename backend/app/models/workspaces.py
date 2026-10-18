from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    brief_id = Column(Integer, ForeignKey("briefs.id", ondelete="SET NULL"), nullable=True)
    brand_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creator_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="discovery", nullable=False)
    # discovery, brief_approved, production, review, delivered, completed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    brief = relationship("Brief", back_populates="workspaces")
    brand_user = relationship("User", foreign_keys=[brand_user_id])
    creator_user = relationship("User", foreign_keys=[creator_user_id])
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    messages = relationship("WorkspaceMessage", back_populates="workspace", cascade="all, delete-orphan")
    milestones = relationship("WorkspaceMilestone", back_populates="workspace", cascade="all, delete-orphan")
    files = relationship("SharedFile", back_populates="workspace", cascade="all, delete-orphan")
    revisions = relationship("RevisionRequest", back_populates="workspace", cascade="all, delete-orphan")
    review = relationship("Review", back_populates="workspace", uselist=False, cascade="all, delete-orphan")


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # brand, creator, collaborator

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User")


class WorkspaceMessage(Base):
    __tablename__ = "workspace_messages"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    encrypted_content = Column(Text, nullable=False)  # Encrypted string at rest
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    workspace = relationship("Workspace", back_populates="messages")
    sender = relationship("User")


class WorkspaceMilestone(Base):
    __tablename__ = "workspace_milestones"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, default=0.0, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, approved, in_review, released
    estimated_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    workspace = relationship("Workspace", back_populates="milestones")
    revisions = relationship("RevisionRequest", back_populates="milestone", cascade="all, delete-orphan")
    deliverables = relationship("SharedFile", back_populates="milestone")


class SharedFile(Base):
    __tablename__ = "shared_files"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    milestone_id = Column(Integer, ForeignKey("workspace_milestones.id", ondelete="SET NULL"), nullable=True)
    uploader_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    stored_path = Column(String(500), nullable=True)
    mime_type = Column(String(100), nullable=True)
    file_size = Column(String(50), nullable=True)  # e.g., "124 MB"
    file_type = Column(String(50), nullable=True)  # video, image, model, zip, document
    version = Column(Integer, default=1, nullable=False)
    status = Column(String(50), default="submitted", nullable=False)  # submitted, approved, revision_requested, demo
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    workspace = relationship("Workspace", back_populates="files")
    milestone = relationship("WorkspaceMilestone", back_populates="deliverables")
    uploader = relationship("User")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, unique=True)
    recruiter_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creator_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    workspace = relationship("Workspace", back_populates="review")
    recruiter = relationship("User", foreign_keys=[recruiter_user_id])
    creator = relationship("User", foreign_keys=[creator_user_id])


class RevisionRequest(Base):
    __tablename__ = "revision_requests"

    id = Column(Integer, primary_key=True, index=True)
    milestone_id = Column(Integer, ForeignKey("workspace_milestones.id", ondelete="CASCADE"), nullable=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    requester_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="open", nullable=False)  # open, addressed, resolved
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    workspace = relationship("Workspace", back_populates="revisions")
    milestone = relationship("WorkspaceMilestone", back_populates="revisions")
    requester = relationship("User")
