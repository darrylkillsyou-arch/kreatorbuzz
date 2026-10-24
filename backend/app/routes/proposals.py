from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User
from app.models.creators import CreatorProfile
from app.models.proposals import Proposal
from app.models.workspaces import Workspace, WorkspaceMember, WorkspaceMilestone, WorkspaceMessage
from app.models.notifications import Notification
from app.schemas.proposals import ProposalCreate, ProposalResponse
from app.dependencies import get_current_user
from app.services.encryption import encrypt_message

router = APIRouter(prefix="/proposals", tags=["proposals"])


def _serialize_proposal(p: Proposal, db: Session) -> ProposalResponse:
    brand = db.query(User).filter(User.id == p.brand_user_id).first()
    creator = db.query(User).filter(User.id == p.creator_user_id).first()
    creator_prof = db.query(CreatorProfile).filter(CreatorProfile.user_id == p.creator_user_id).first()

    recruiter_name = brand.full_name if brand else "Recruiter"
    creator_name = (creator_prof.display_name if creator_prof else None) or (creator.full_name if creator else "Creator")
    creator_avatar = (creator.avatar_url if creator else None)

    return ProposalResponse(
        id=p.id,
        brand_user_id=p.brand_user_id,
        creator_user_id=p.creator_user_id,
        workspace_id=p.workspace_id,
        project_title=p.project_title,
        project_requirement=p.project_requirement,
        budget_in_rupees=p.budget_in_rupees,
        deadline=p.deadline,
        status=p.status,
        created_at=p.created_at,
        recruiter_name=recruiter_name,
        creator_name=creator_name,
        creator_avatar=creator_avatar,
    )


@router.post("", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
def create_proposal(
    proposal_in: ProposalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submits a hiring proposal to an explicitly identified creator.
    Validates creator existence, role, and active status.
    Strictly forbids fallback to Creator #1 or current user.
    """
    target_creator_id = proposal_in.creator_id.strip() if proposal_in.creator_id else None

    # Validate presence of creator identifier
    if not target_creator_id and proposal_in.creator_user_id is None and proposal_in.creator_profile_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Creator identifier is required",
        )

    if proposal_in.creator_id is not None and not target_creator_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Creator identifier cannot be empty",
        )

    creator_user = None

    # 1. Resolve by explicit creator_user_id if provided
    if proposal_in.creator_user_id is not None:
        user = db.query(User).filter(
            User.id == proposal_in.creator_user_id,
            User.is_active == True,
        ).first()
        if user:
            if user.role != "creator":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User {user.id} is not registered as a creator",
                )
            creator_user = user

    # 2. Resolve by explicit creator_profile_id if provided
    if not creator_user and proposal_in.creator_profile_id is not None:
        prof = db.query(CreatorProfile).filter(CreatorProfile.id == proposal_in.creator_profile_id).first()
        if prof and prof.user and prof.user.is_active:
            if prof.user.role != "creator":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User linked to creator profile {prof.id} is not a creator",
                )
            creator_user = prof.user

    # 3. Resolve by creator_id string or integer
    if not creator_user and target_creator_id:
        if target_creator_id.isdigit():
            target_int = int(target_creator_id)
            # Check CreatorProfile.id first since frontend cards and routes use profile ID
            prof = db.query(CreatorProfile).filter(CreatorProfile.id == target_int).first()
            if prof and prof.user and prof.user.is_active:
                if prof.user.role == "creator":
                    creator_user = prof.user

            # If not matching a CreatorProfile.id, check direct User.id
            if not creator_user:
                user = db.query(User).filter(
                    User.id == target_int,
                    User.is_active == True,
                ).first()
                if user:
                    if user.role != "creator":
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User {user.id} is not registered as a creator",
                        )
                    creator_user = user
        else:
            # Slug or display name lookup
            clean_name = target_creator_id.replace('-', ' ').strip()
            prof = db.query(CreatorProfile).filter(
                CreatorProfile.display_name.ilike(clean_name)
            ).first()
            if prof and prof.user and prof.user.is_active and prof.user.role == "creator":
                creator_user = prof.user
            else:
                user = db.query(User).filter(
                    User.full_name.ilike(clean_name),
                    User.is_active == True,
                    User.role == "creator",
                ).first()
                if user:
                    creator_user = user

    # 4. Strict validation: no silent fallback is permitted under any circumstances!
    if not creator_user:
        identifier_display = target_creator_id or proposal_in.creator_user_id or proposal_in.creator_profile_id
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Creator with identifier '{identifier_display}' not found",
        )

    # 5. Prevent sending proposal to oneself
    if current_user.id == creator_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send a hiring proposal to yourself",
        )

    # 6. Save proposal strictly with the resolved creator_user.id
    proposal = Proposal(
        brand_user_id=current_user.id,
        creator_user_id=creator_user.id,
        project_title=proposal_in.project_title,
        project_requirement=proposal_in.project_requirement,
        budget_in_rupees=proposal_in.budget_in_rupees,
        deadline=proposal_in.deadline,
        status="pending",
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    # 7. Notify both the recipient creator and the sending recruiter
    notif_creator = Notification(
        user_id=creator_user.id,
        title="New Project Proposal",
        message=f"{current_user.full_name or 'A recruiter'} sent you a proposal for '{proposal.project_title}' (Budget: ₹{proposal.budget_in_rupees:,.0f}).",
        link="/requests",
        type="proposal_received",
    )
    notif_recruiter = Notification(
        user_id=current_user.id,
        title="Proposal Sent Successfully",
        message=f"Your proposal for '{proposal.project_title}' was successfully sent to {creator_user.full_name or 'the creator'}.",
        link="/requests",
        type="proposal_sent",
    )
    db.add_all([notif_creator, notif_recruiter])
    db.commit()

    return _serialize_proposal(proposal, db)


@router.get("", response_model=List[ProposalResponse])
def get_my_proposals(
    role: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists proposals associated with current user (as recruiter or creator)."""
    query = db.query(Proposal)
    if role == "creator" or (role is None and current_user.role == "creator"):
        query = query.filter(Proposal.creator_user_id == current_user.id)
    elif role == "brand":
        query = query.filter(Proposal.brand_user_id == current_user.id)
    else:
        query = query.filter(
            (Proposal.brand_user_id == current_user.id) |
            (Proposal.creator_user_id == current_user.id)
        )
    proposals = query.order_by(Proposal.created_at.desc()).all()
    return [_serialize_proposal(p, db) for p in proposals]


@router.post("/{proposal_id}/accept", response_model=ProposalResponse)
def accept_proposal(
    proposal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creator accepts proposal.
    Updates status to 'accepted', creates workspace linked only to recruiter and creator,
    and dispatches a notification to the recruiter.
    Idempotent: will not create duplicate workspaces if Accept is clicked multiple times.
    """
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")

    if proposal.creator_user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the assigned creator can accept this proposal")

    if proposal.status == "accepted" and proposal.workspace_id:
        # Already accepted and workspace exists — return without duplicating
        return _serialize_proposal(proposal, db)

    proposal.status = "accepted"

    # Check if a workspace already exists for this proposal
    workspace = None
    if proposal.workspace_id:
        workspace = db.query(Workspace).filter(Workspace.id == proposal.workspace_id).first()

    if not workspace:
        # Create a new workspace linked only to that recruiter and creator
        workspace = Workspace(
            brand_user_id=proposal.brand_user_id,
            creator_user_id=proposal.creator_user_id,
            title=proposal.project_title,
            status="discovery",
        )
        db.add(workspace)
        db.commit()
        db.refresh(workspace)

        proposal.workspace_id = workspace.id

        # Add workspace members
        m_brand = WorkspaceMember(workspace_id=workspace.id, user_id=proposal.brand_user_id, role="brand")
        m_creator = WorkspaceMember(workspace_id=workspace.id, user_id=proposal.creator_user_id, role="creator")
        db.add_all([m_brand, m_creator])

        # Add initial milestone with the agreed budget
        milestone = WorkspaceMilestone(
            workspace_id=workspace.id,
            title="Initial Concept & Deliverables Delivery",
            description=proposal.project_requirement[:250],
            amount=proposal.budget_in_rupees,
            status="approved",
        )
        db.add(milestone)

        # Welcome message
        welcome_msg = WorkspaceMessage(
            workspace_id=workspace.id,
            sender_id=current_user.id,
            encrypted_content=encrypt_message(f"Proposal accepted for '{proposal.project_title}'. Welcome to our dedicated workspace!"),
        )
        db.add(welcome_msg)

    # Create notifications for both recruiter and creator
    notif_recruiter_accept = Notification(
        user_id=proposal.brand_user_id,
        title="Creator Accepted Proposal",
        message=f"{current_user.full_name} accepted your proposal for '{proposal.project_title}'.",
        link=f"/workspaces?id={workspace.id}",
        type="proposal_accepted",
    )
    notif_recruiter_ws = Notification(
        user_id=proposal.brand_user_id,
        title="Workspace Created",
        message=f"Collaboration workspace #{workspace.id} is now ready for '{proposal.project_title}'.",
        link=f"/workspaces?id={workspace.id}",
        type="workspace_created",
    )
    notif_creator_ws = Notification(
        user_id=current_user.id,
        title="Proposal Accepted & Workspace Ready",
        message=f"You accepted '{proposal.project_title}'. Collaboration workspace #{workspace.id} is active.",
        link=f"/workspaces?id={workspace.id}",
        type="workspace_created",
    )
    db.add_all([notif_recruiter_accept, notif_recruiter_ws, notif_creator_ws])
    db.commit()
    db.refresh(proposal)

    return _serialize_proposal(proposal, db)


@router.post("/{proposal_id}/decline", response_model=ProposalResponse)
def decline_proposal(
    proposal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creator declines proposal.
    Updates status to 'declined', creates NO workspace, and notifies recruiter.
    """
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")

    if proposal.creator_user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the assigned creator can decline this proposal")

    proposal.status = "declined"

    # Create notifications for recruiter and creator
    notif_recruiter = Notification(
        user_id=proposal.brand_user_id,
        title="Creator Declined Proposal",
        message=f"{current_user.full_name} declined your proposal for '{proposal.project_title}'.",
        link="/requests",
        type="proposal_declined",
    )
    notif_creator = Notification(
        user_id=current_user.id,
        title="Proposal Declined",
        message=f"You declined the proposal for '{proposal.project_title}'.",
        link="/requests",
        type="proposal_declined",
    )
    db.add_all([notif_recruiter, notif_creator])
    db.commit()
    db.refresh(proposal)

    return _serialize_proposal(proposal, db)
