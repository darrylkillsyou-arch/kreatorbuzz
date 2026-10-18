import os
import re
import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User
from app.models.notifications import Notification
from app.models.workspaces import (
    Workspace,
    WorkspaceMember,
    WorkspaceMessage,
    WorkspaceMilestone,
    SharedFile,
    RevisionRequest,
    Review,
)
from app.models.creators import CreatorProfile
from app.schemas.workspaces import (
    WorkspaceCreate,
    WorkspaceResponse,
    WorkspaceDetailResponse,
    MessageCreate,
    MessageResponse,
    MilestoneCreate,
    MilestoneUpdate,
    MilestoneResponse,
    RevisionCreate,
    RevisionResponse,
    FileResponse,
    ReviewCreate,
    ReviewResponse,
)
from app.dependencies import get_current_user
from app.services.encryption import encrypt_message, decrypt_message

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=List[WorkspaceResponse])
def list_my_workspaces(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Lists all active collaboration workspaces the current user participates in."""
    workspaces = db.query(Workspace).filter(
        (Workspace.brand_user_id == current_user.id) |
        (Workspace.creator_user_id == current_user.id) |
        (Workspace.id.in_(
            db.query(WorkspaceMember.workspace_id).filter(WorkspaceMember.user_id == current_user.id)
        ))
    ).order_by(Workspace.created_at.desc()).all()
    return workspaces


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    ws_in: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Creates a new collaboration workspace between brand and creator."""
    creator_user = db.query(User).filter(User.id == ws_in.creator_user_id).first()
    if not creator_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Creator user not found")

    workspace = Workspace(
        brief_id=ws_in.brief_id,
        brand_user_id=current_user.id,
        creator_user_id=ws_in.creator_user_id,
        title=ws_in.title,
        status="discovery",
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    # Add workspace members
    m1 = WorkspaceMember(workspace_id=workspace.id, user_id=current_user.id, role="brand")
    m2 = WorkspaceMember(workspace_id=workspace.id, user_id=creator_user.id, role="creator")
    db.add_all([m1, m2])

    # Add initial milestones if provided
    if ws_in.initial_milestones:
        for m in ws_in.initial_milestones:
            db.add(WorkspaceMilestone(
                workspace_id=workspace.id,
                title=m.title,
                description=m.description,
                amount=m.amount,
                status="pending",
                estimated_date=m.estimated_date,
            ))
    else:
        # Default milestones
        db.add(WorkspaceMilestone(
            workspace_id=workspace.id,
            title="Discovery & Concept Art",
            description="Initial style frames and prompt tests",
            amount=500.0,
            status="approved",
        ))
        db.add(WorkspaceMilestone(
            workspace_id=workspace.id,
            title="Rough Cut & Motion Pass",
            description="First pass video generation and pacing",
            amount=1000.0,
            status="pending",
        ))
        db.add(WorkspaceMilestone(
            workspace_id=workspace.id,
            title="Final 4K Master & Audio Stems",
            description="Final upscaled render and sound design",
            amount=1000.0,
            status="pending",
        ))

    # Send welcome automated encrypted message
    welcome_msg = WorkspaceMessage(
        workspace_id=workspace.id,
        sender_id=current_user.id,
        encrypted_content=encrypt_message(f"Welcome to the workspace '{workspace.title}'. Brief and milestones are loaded."),
    )
    db.add(welcome_msg)
    db.commit()
    db.refresh(workspace)
    return workspace


@router.get("/{workspace_id}", response_model=WorkspaceDetailResponse)
def get_workspace_detail(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves full details of a workspace, including milestones, decrypted messages, files, and revisions."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    # Authorize member
    is_member = (
        workspace.brand_user_id == current_user.id or
        workspace.creator_user_id == current_user.id or
        current_user.role == "admin"
    )
    if not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden to this workspace")

    # Decrypt messages
    raw_messages = db.query(WorkspaceMessage).filter(WorkspaceMessage.workspace_id == workspace_id).order_by(WorkspaceMessage.created_at.asc()).all()
    decrypted_messages = [
        MessageResponse(
            id=m.id,
            workspace_id=m.workspace_id,
            sender_id=m.sender_id,
            content=decrypt_message(m.encrypted_content),
            created_at=m.created_at,
            sender=m.sender,
        )
        for m in raw_messages
    ]

    return WorkspaceDetailResponse(
        id=workspace.id,
        brief_id=workspace.brief_id,
        brand_user_id=workspace.brand_user_id,
        creator_user_id=workspace.creator_user_id,
        title=workspace.title,
        status=workspace.status,
        created_at=workspace.created_at,
        completed_at=workspace.completed_at,
        brand_user=workspace.brand_user,
        creator_user=workspace.creator_user,
        brief=workspace.brief,
        milestones=workspace.milestones,
        messages=decrypted_messages,
        files=workspace.files,
        revisions=workspace.revisions,
        review=workspace.review,
    )


@router.post("/{workspace_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_workspace_message(
    workspace_id: int,
    msg_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sends an encrypted message in a collaboration workspace."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    encrypted_text = encrypt_message(msg_in.content)
    message = WorkspaceMessage(
        workspace_id=workspace.id,
        sender_id=current_user.id,
        encrypted_content=encrypted_text,
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    return MessageResponse(
        id=message.id,
        workspace_id=message.workspace_id,
        sender_id=message.sender_id,
        content=msg_in.content,
        created_at=message.created_at,
        sender=current_user,
    )


@router.get("/{workspace_id}/messages", response_model=List[MessageResponse])
def get_workspace_messages(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves decrypted message stream for a workspace."""
    raw_messages = db.query(WorkspaceMessage).filter(
        WorkspaceMessage.workspace_id == workspace_id
    ).order_by(WorkspaceMessage.created_at.asc()).all()

    return [
        MessageResponse(
            id=m.id,
            workspace_id=m.workspace_id,
            sender_id=m.sender_id,
            content=decrypt_message(m.encrypted_content),
            created_at=m.created_at,
            sender=m.sender,
        )
        for m in raw_messages
    ]


@router.put("/{workspace_id}/milestones/{milestone_id}", response_model=MilestoneResponse)
@router.patch("/{workspace_id}/milestones/{milestone_id}", response_model=MilestoneResponse)
def update_milestone(
    workspace_id: int,
    milestone_id: int,
    milestone_in: MilestoneUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Updates milestone status (e.g. approved, in_review, released, completed)."""
    milestone = db.query(WorkspaceMilestone).filter(
        WorkspaceMilestone.id == milestone_id,
        WorkspaceMilestone.workspace_id == workspace_id,
    ).first()
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

    update_data = milestone_in.model_dump(exclude_unset=True)
    if update_data.get("status") in ("released", "completed") and not milestone.completed_at:
        milestone.completed_at = datetime.utcnow()

    for field, val in update_data.items():
        setattr(milestone, field, val)

    db.commit()
    db.refresh(milestone)
    return milestone


@router.post("/{workspace_id}/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
def add_milestone(
    workspace_id: int,
    milestone_in: MilestoneCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Adds a new milestone to a workspace."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    milestone = WorkspaceMilestone(
        workspace_id=workspace.id,
        title=milestone_in.title,
        description=milestone_in.description,
        amount=milestone_in.amount,
        status="pending",
        estimated_date=milestone_in.estimated_date,
    )
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


@router.post("/{workspace_id}/revision-requests", response_model=RevisionResponse, status_code=status.HTTP_201_CREATED)
def request_revision(
    workspace_id: int,
    rev_in: RevisionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submits a formal revision request on a milestone or overall workspace."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    # Authorize: only workspace members may create revision requests
    is_member = (
        workspace.brand_user_id == current_user.id
        or workspace.creator_user_id == current_user.id
        or current_user.role == "admin"
    )
    if not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this workspace")

    # Resolve description from either field sent by the client
    description = (rev_in.description or rev_in.notes or "").strip()
    if not description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Revision description cannot be empty")

    # Validate milestone ownership when a milestone_id is provided
    milestone_id = rev_in.milestone_id
    if milestone_id is not None:
        milestone = db.query(WorkspaceMilestone).filter(
            WorkspaceMilestone.id == milestone_id,
            WorkspaceMilestone.workspace_id == workspace_id,
        ).first()
        if not milestone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found in this workspace")

    rev = RevisionRequest(
        workspace_id=workspace.id,
        milestone_id=milestone_id,
        requester_id=current_user.id,
        description=description,
        status="open",
    )
    db.add(rev)

    # Notify the other workspace participant
    recipient_id = (
        workspace.creator_user_id
        if current_user.id == workspace.brand_user_id
        else workspace.brand_user_id
    )
    short_desc = description[:100] + ("..." if len(description) > 100 else "")
    notification = Notification(
        user_id=recipient_id,
        title="Revision Requested",
        message=f"{current_user.full_name or current_user.email} requested a revision on '{workspace.title}': {short_desc}",
        link=f"/workspaces?id={workspace.id}",
        type="revision_requested",
    )
    db.add(notification)

    db.commit()
    db.refresh(rev)
    return rev


# ==========================================
# FILE UPLOAD & DELIVERABLES
# ==========================================

ALLOWED_EXTENSIONS = {
    # Images
    "jpg", "jpeg", "png", "webp",
    # Documents
    "pdf",
    # Video
    "mp4", "mov",
    # Archives
    "zip",
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
UPLOAD_BASE_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "workspaces"


def sanitize_filename(filename: str) -> str:
    """Sanitizes user-supplied filename against path traversal and special characters."""
    clean = os.path.basename(filename)
    clean = re.sub(r'[^a-zA-Z0-9_.-]', '_', clean)
    return clean[:120] if clean else "file"


def format_size(bytes_num: int) -> str:
    """Formats file size into human-readable representation."""
    if bytes_num < 1024:
        return f"{bytes_num} B"
    elif bytes_num < 1024 * 1024:
        return f"{bytes_num / 1024:.1f} KB"
    else:
        return f"{bytes_num / (1024 * 1024):.1f} MB"


@router.post("/{workspace_id}/deliverables", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_deliverable(
    workspace_id: int,
    file: UploadFile = File(...),
    milestone_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Uploads a verified project deliverable into a collaboration workspace."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    # Access control: user must belong to this workspace
    is_member = (
        workspace.brand_user_id == current_user.id
        or workspace.creator_user_id == current_user.id
        or current_user.role == "admin"
    )
    if not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this workspace")

    # Milestone verification if passed
    target_milestone = None
    if milestone_id is not None:
        target_milestone = db.query(WorkspaceMilestone).filter(
            WorkspaceMilestone.id == milestone_id,
            WorkspaceMilestone.workspace_id == workspace_id,
        ).first()
        if not target_milestone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found in this workspace")

    # File validation: extension
    raw_filename = file.filename or "deliverable"
    ext = raw_filename.rsplit(".", 1)[-1].lower() if "." in raw_filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '.{ext}'. Supported formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Sanitize and create safe storage directory
    safe_name = sanitize_filename(raw_filename)
    ws_dir = UPLOAD_BASE_DIR / str(workspace_id)
    ws_dir.mkdir(parents=True, exist_ok=True)

    unique_stored_name = f"{uuid.uuid4().hex[:12]}_{safe_name}"
    target_path = ws_dir / unique_stored_name

    # Stream file to disk and measure size
    size_bytes = 0
    try:
        with open(target_path, "wb") as f_out:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                size_bytes += len(chunk)
                if size_bytes > MAX_FILE_SIZE:
                    target_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"File exceeds maximum upload size limit of {MAX_FILE_SIZE // (1024 * 1024)} MB."
                    )
                f_out.write(chunk)
    except Exception as e:
        target_path.unlink(missing_ok=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to store file: {str(e)}")

    # Determine version: check previous files in this workspace (or for this milestone)
    prev_query = db.query(SharedFile).filter(SharedFile.workspace_id == workspace_id)
    if target_milestone:
        prev_query = prev_query.filter(SharedFile.milestone_id == target_milestone.id)
    highest_v = 0
    for prev in prev_query.all():
        if prev.version and prev.version > highest_v:
            highest_v = prev.version
    new_version = highest_v + 1

    # Map file_type category
    file_type = "document"
    if ext in {"jpg", "jpeg", "png", "webp"}:
        file_type = "image"
    elif ext in {"mp4", "mov"}:
        file_type = "video"
    elif ext == "zip":
        file_type = "zip"

    shared_file = SharedFile(
        workspace_id=workspace.id,
        milestone_id=target_milestone.id if target_milestone else None,
        uploader_id=current_user.id,
        filename=safe_name,
        stored_path=str(target_path),
        mime_type=file.content_type or f"application/{ext}",
        file_size=format_size(size_bytes),
        file_type=file_type,
        version=new_version,
        status="submitted",
        description=description,
    )
    db.add(shared_file)

    # Check if there is an open revision request on this milestone: mark as addressed
    if target_milestone:
        open_revs = db.query(RevisionRequest).filter(
            RevisionRequest.milestone_id == target_milestone.id,
            RevisionRequest.status == "open",
        ).all()
        for r in open_revs:
            r.status = "addressed"

    # Notify recipient
    recipient_id = workspace.brand_user_id if current_user.id == workspace.creator_user_id else workspace.creator_user_id
    notif_msg = f"{current_user.full_name or 'Creator'} uploaded {safe_name} (v{new_version}) in '{workspace.title}'"
    db.add(Notification(
        user_id=recipient_id,
        title=f"Deliverable Uploaded (v{new_version})",
        message=notif_msg,
        link=f"/workspaces?id={workspace.id}",
        type="deliverable_uploaded",
    ))

    db.commit()
    db.refresh(shared_file)

    # Attach download_url for frontend
    shared_file.download_url = f"/api/workspaces/{workspace_id}/files/{shared_file.id}/download"
    return shared_file


@router.get("/{workspace_id}/files/{file_id}/download")
def download_workspace_file(
    workspace_id: int,
    file_id: int,
    token: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Securely downloads a workspace deliverable with strict membership check."""
    # Allow token query parameter for direct browser anchor tags if needed
    if not current_user and token:
        from app.services.auth import decode_token
        payload = decode_token(token)
        if payload and "sub" in payload:
            current_user = db.query(User).filter(User.email == payload["sub"]).first()

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    is_member = (
        workspace.brand_user_id == current_user.id
        or workspace.creator_user_id == current_user.id
        or current_user.role == "admin"
    )
    if not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this workspace asset")

    shared_file = db.query(SharedFile).filter(
        SharedFile.id == file_id,
        SharedFile.workspace_id == workspace_id,
    ).first()
    if not shared_file or not shared_file.stored_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File record or asset not found")

    file_path = Path(shared_file.stored_path)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file asset is not present on disk")

    return FastAPIFileResponse(
        path=str(file_path),
        filename=shared_file.filename,
        media_type=shared_file.mime_type or "application/octet-stream",
    )


# ==========================================
# PROJECT COMPLETION
# ==========================================

@router.post("/{workspace_id}/complete", response_model=WorkspaceDetailResponse)
def complete_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marks a workspace/project as completed once all milestones are approved and no open revisions remain."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    is_member = (
        workspace.brand_user_id == current_user.id
        or workspace.creator_user_id == current_user.id
        or current_user.role == "admin"
    )
    if not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this workspace")

    # Rule 1: Cannot complete an already completed workspace
    if workspace.status == "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project is already completed")

    # Rule 2: All milestones must be released/completed
    milestones = workspace.milestones or []
    if milestones:
        incomplete_milestones = [m for m in milestones if m.status not in ("released", "completed")]
        if incomplete_milestones:
            titles = ", ".join([m.title for m in incomplete_milestones])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot complete project: {len(incomplete_milestones)} milestone(s) are not yet approved/released ({titles})."
            )

    # Rule 3: No unresolved blocking open revisions
    open_revisions = db.query(RevisionRequest).filter(
        RevisionRequest.workspace_id == workspace_id,
        RevisionRequest.status == "open",
    ).all()
    if open_revisions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot complete project: {len(open_revisions)} open revision request(s) must be addressed or resolved first."
        )

    # Mark as completed
    workspace.status = "completed"
    workspace.completed_at = datetime.utcnow()

    # Notify both participants
    for uid in {workspace.brand_user_id, workspace.creator_user_id}:
        db.add(Notification(
            user_id=uid,
            title="Project Completed!",
            message=f"Production workspace '{workspace.title}' has been successfully completed and archived.",
            link=f"/workspaces?id={workspace.id}",
            type="project_completed",
        ))

    db.commit()
    db.refresh(workspace)
    return get_workspace_detail(workspace_id=workspace.id, current_user=current_user, db=db)


# ==========================================
# CREATOR REVIEWS
# ==========================================

@router.post("/{workspace_id}/review", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_creator_review(
    workspace_id: int,
    review_in: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submits a verified recruiter review for a creator upon project completion."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    # Rule 1: Project must be completed
    if workspace.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviews can only be submitted after the project has been fully completed."
        )

    # Rule 2: Only the recruiter/brand of this workspace may submit a review
    if current_user.id != workspace.brand_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the recruiter who commissioned this project may submit a creator review."
        )

    # Rule 3: Cannot review yourself
    if workspace.creator_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Creators cannot review themselves."
        )

    # Rule 4: Rating bounds check (1 to 5)
    if review_in.rating < 1 or review_in.rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be an integer between 1 and 5 stars."
        )

    comment = review_in.comment.strip()
    if len(comment) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review comment must be at least 5 characters long."
        )

    # Rule 5: Duplicate review prevention (one review per workspace)
    existing_review = db.query(Review).filter(Review.workspace_id == workspace_id).first()
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A verified review has already been submitted for this completed project."
        )

    review = Review(
        workspace_id=workspace.id,
        recruiter_user_id=current_user.id,
        creator_user_id=workspace.creator_user_id,
        rating=review_in.rating,
        comment=comment,
    )
    db.add(review)

    # Update creator profile rating without destroying demo credibility:
    # Blend verified reviews with base rating
    creator_prof = db.query(CreatorProfile).filter(CreatorProfile.user_id == workspace.creator_user_id).first()
    if creator_prof:
        # Fetch all verified reviews for this creator
        all_reviews = db.query(Review).filter(Review.creator_user_id == workspace.creator_user_id).all()
        ratings = [r.rating for r in all_reviews] + [review_in.rating]
        avg_verified = sum(ratings) / len(ratings)
        # 80% base rating weight + 20% verified reviews weight
        base = creator_prof.rating or 4.8
        creator_prof.rating = round(base * 0.8 + avg_verified * 0.2, 2)

    # Notify creator of received review
    db.add(Notification(
        user_id=workspace.creator_user_id,
        title="New Verified Review Received",
        message=f"{current_user.full_name or 'Recruiter'} rated your work {review_in.rating}★ on '{workspace.title}': \"{comment[:80]}\"",
        link=f"/workspaces?id={workspace.id}",
        type="review_received",
    ))

    db.commit()
    db.refresh(review)
    return review


@router.get("/creators/{creator_id}/reviews", response_model=List[ReviewResponse])
def get_creator_reviews(
    creator_id: int,
    db: Session = Depends(get_db),
):
    """Fetches all verified reviews for a creator profile."""
    # Find user_id from creator_profiles
    creator_prof = db.query(CreatorProfile).filter(
        (CreatorProfile.id == creator_id) | (CreatorProfile.user_id == creator_id)
    ).first()
    if not creator_prof:
        return []

    reviews = db.query(Review).filter(
        Review.creator_user_id == creator_prof.user_id
    ).order_by(Review.created_at.desc()).all()
    return reviews


