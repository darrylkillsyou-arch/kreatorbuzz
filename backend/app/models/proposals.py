from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    brand_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    creator_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True)
    project_title = Column(String(255), nullable=False)
    project_requirement = Column(Text, nullable=False)
    budget_in_rupees = Column(Float, nullable=False)
    deadline = Column(String(100), nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    brand_user = relationship("User", foreign_keys=[brand_user_id])
    creator_user = relationship("User", foreign_keys=[creator_user_id])
    workspace = relationship("Workspace", foreign_keys=[workspace_id])
