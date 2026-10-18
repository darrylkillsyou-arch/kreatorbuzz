"""Shortlist and direct hiring routes."""

from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User
from app.models.creators import CreatorProfile
from app.models.briefs import Brief
from app.models.shortlist import Shortlist
from app.models.workspaces import Workspace, WorkspaceMember, WorkspaceMilestone, WorkspaceMessage
from app.schemas.shortlist import ShortlistCreate, ShortlistResponse, HireRequest
from app.schemas.workspaces import WorkspaceResponse
from app.dependencies import get_current_user, get_current_brand_user
from app.services.encryption import encrypt_message

router = APIRouter(prefix="/shortlist", tags=["shortlist"])


def _resolve_creator_user(target: Union[int, str], db: Session) -> Optional[User]:
    """Resolves a User representing a creator from CreatorProfile ID, User ID, or display name."""
    if target is None:
        return None

    target_str = str(target).strip()
    if target_str.isdigit():
        uid = int(target_str)
        # 1. CreatorProfile ID (frontend creator cards use CreatorProfile ID)
        prof = db.query(CreatorProfile).filter(CreatorProfile.id == uid).first()
        if prof and prof.user and prof.user.role == "creator" and prof.user.is_active:
            return prof.user
        # 2. Direct User ID
        user = db.query(User).filter(User.id == uid, User.role == "creator", User.is_active == True).first()
        if user:
            return user
        return None

    # 3. Try string lookup
    clean = target_str.replace("-", " ").strip().lower()
    prof = db.query(CreatorProfile).filter(
        (CreatorProfile.display_name.ilike(f"%{clean}%")) |
        (CreatorProfile.tagline.ilike(f"%{clean}%"))
    ).first()
    if prof and prof.user and prof.user.role == "creator" and prof.user.is_active:
        return prof.user

    user = db.query(User).filter(User.full_name.ilike(f"%{clean}%"), User.role == "creator", User.is_active == True).first()
    if user:
        return user

    return None


@router.post("", response_model=ShortlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_shortlist(
    item_in: ShortlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adds a creator to the user's saved/shortlist collection."""
    creator_user = None

    if item_in.creator_profile_id is not None:
        prof = db.query(CreatorProfile).filter(CreatorProfile.id == item_in.creator_profile_id).first()
        if prof and prof.user and prof.user.role == "creator" and prof.user.is_active:
            creator_user = prof.user

    if not creator_user and item_in.creator_user_id is not None:
        user = db.query(User).filter(User.id == item_in.creator_user_id, User.role == "creator", User.is_active == True).first()
        if user:
            creator_user = user

    if not creator_user and item_in.creator_id is not None:
        creator_user = _resolve_creator_user(item_in.creator_id, db)

    if not creator_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator not found")

    existing = db.query(Shortlist).filter(
        Shortlist.brand_user_id == current_user.id,
        Shortlist.creator_user_id == creator_user.id,
    ).first()

    if existing:
        c_prof = creator_user.creator_profile
        return ShortlistResponse(
            id=existing.id,
            brand_user_id=existing.brand_user_id,
            creator_user_id=existing.creator_user_id,
            brief_id=existing.brief_id,
            created_at=existing.created_at,
            creator_user=existing.creator_user,
            creator_profile=c_prof,
            brief=existing.brief,
        )

    entry = Shortlist(
        brand_user_id=current_user.id,
        creator_user_id=creator_user.id,
        brief_id=item_in.brief_id,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    c_prof = creator_user.creator_profile
    return ShortlistResponse(
        id=entry.id,
        brand_user_id=entry.brand_user_id,
        creator_user_id=entry.creator_user_id,
        brief_id=entry.brief_id,
        created_at=entry.created_at,
        creator_user=entry.creator_user,
        creator_profile=c_prof,
        brief=entry.brief,
    )


@router.get("", response_model=List[ShortlistResponse])
def get_my_shortlist(
    brief_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists creators saved to the logged-in user's shortlist."""
    query = db.query(Shortlist).filter(Shortlist.brand_user_id == current_user.id)
    if brief_id:
        query = query.filter(Shortlist.brief_id == brief_id)
    entries = query.order_by(Shortlist.created_at.desc()).all()

    results = []
    for e in entries:
        c_prof = e.creator_user.creator_profile if e.creator_user else None
        results.append(
            ShortlistResponse(
                id=e.id,
                brand_user_id=e.brand_user_id,
                creator_user_id=e.creator_user_id,
                brief_id=e.brief_id,
                created_at=e.created_at,
                creator_user=e.creator_user,
                creator_profile=c_prof,
                brief=e.brief,
            )
        )
    return results


@router.delete("/{identifier}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_shortlist(
    identifier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Removes a creator from the shortlist by entry ID or creator ID."""
    entry = None
    if identifier.isdigit():
        num_id = int(identifier)
        # 1. Try matching Shortlist.id
        entry = db.query(Shortlist).filter(
            Shortlist.id == num_id,
            Shortlist.brand_user_id == current_user.id,
        ).first()

    if not entry:
        # 2. Try resolving as creator user
        creator_user = _resolve_creator_user(identifier, db)
        if creator_user:
            entry = db.query(Shortlist).filter(
                Shortlist.creator_user_id == creator_user.id,
                Shortlist.brand_user_id == current_user.id,
            ).first()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shortlist entry not found")

    db.delete(entry)
    db.commit()
    return None


@router.post("/{shortlist_id}/hire", response_model=WorkspaceResponse)
def hire_creator_from_shortlist(
    shortlist_id: int,
    hire_data: Optional[HireRequest] = Body(default=None),
    current_user: User = Depends(get_current_brand_user),
    db: Session = Depends(get_db),
):
    """Directly hires a creator from shortlist and provisions a collaboration workspace."""
    entry = db.query(Shortlist).filter(
        Shortlist.id == shortlist_id,
        Shortlist.brand_user_id == current_user.id,
    ).first()

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shortlist entry not found")

    title = None
    if hire_data and hire_data.title:
        title = hire_data.title
    elif entry.brief:
        title = f"{entry.brief.title} - Collaboration"
    else:
        title = f"Project with {entry.creator_user.full_name}"

    workspace = Workspace(
        brief_id=entry.brief_id,
        brand_user_id=current_user.id,
        creator_user_id=entry.creator_user_id,
        title=title,
        status="brief_approved",
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    # Add members
    m1 = WorkspaceMember(workspace_id=workspace.id, user_id=current_user.id, role="brand")
    m2 = WorkspaceMember(workspace_id=workspace.id, user_id=entry.creator_user_id, role="creator")
    db.add_all([m1, m2])

    # Milestone
    initial_amount = 1500.0
    if hire_data and hire_data.initial_milestone_amount:
        initial_amount = hire_data.initial_milestone_amount
    elif entry.brief and entry.brief.budget_min:
        initial_amount = entry.brief.budget_min
    milestone = WorkspaceMilestone(
        workspace_id=workspace.id,
        title="Initial Phase & Concept Development",
        description="Kickoff, storyboard framing, and model finetuning",
        amount=initial_amount,
        status="approved",
    )
    db.add(milestone)

    msg = WorkspaceMessage(
        workspace_id=workspace.id,
        sender_id=current_user.id,
        encrypted_content=encrypt_message(f"Hired via shortlist! Looking forward to working together on '{workspace.title}'."),
    )
    db.add(msg)
    
    # Remove from shortlist after hiring
    db.delete(entry)
    db.commit()
    db.refresh(workspace)

    return workspace
