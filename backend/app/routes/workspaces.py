import os
import re
import uuid
import shutil
import logging
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
    DeliveryCheckResult,
    ProjectRescueLog,
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
    RevisionUpdate,
    RevisionResponse,
    FileResponse,
    ReviewCreate,
    ReviewResponse,
    DeliverableFeedbackCreate,
    AgreedLicensingResponse,
    ProductionTimelineItem,
    BuzzCheckResult,
    BuzzCheckItem,
    ProjectHealthResponse,
    ProjectHandoffPackResponse,
    ProtectedBudgetResponse,
    RescueReplacementResponse,
    RescueActionRequest,
)
from app.config import settings
from app.dependencies import get_current_user, get_optional_current_user
from app.services.encryption import encrypt_message, decrypt_message
from app.services.delivery_check import run_delivery_check, extract_file_metadata
from app.services.project_rescue import (
    calculate_project_health,
    generate_handoff_pack,
    find_replacement_creators,
)

log = logging.getLogger(__name__)
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


def _is_workspace_member(workspace: Workspace, user: User, db: Session) -> bool:
    if user.role == "admin":
        return True
    if workspace.brand_user_id == user.id or workspace.creator_user_id == user.id:
        return True
    member = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace.id,
        WorkspaceMember.user_id == user.id
    ).first()
    return member is not None


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

    if not _is_workspace_member(workspace, current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden to this workspace")

    # Decrypt messages deterministically in chronological order
    raw_messages = (
        db.query(WorkspaceMessage)
        .filter(WorkspaceMessage.workspace_id == workspace_id)
        .order_by(WorkspaceMessage.created_at.asc(), WorkspaceMessage.id.asc())
        .all()
    )
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

    # Track highest version per milestone to mark is_current
    highest_v_per_ms = {}
    for f in workspace.files:
        ms_key = f.milestone_id or 0
        if ms_key not in highest_v_per_ms or (f.version or 1) > highest_v_per_ms[ms_key]:
            highest_v_per_ms[ms_key] = f.version or 1

    # Pre-load buzz check results keyed by file_id
    buzz_results_by_file: dict = {}
    for f in workspace.files:
        latest_bc = (
            db.query(DeliveryCheckResult)
            .filter(DeliveryCheckResult.file_id == f.id)
            .order_by(DeliveryCheckResult.id.desc())
            .first()
        )
        if latest_bc:
            buzz_results_by_file[f.id] = latest_bc

    def _make_buzz_check_schema(bc: DeliveryCheckResult) -> BuzzCheckResult:
        return BuzzCheckResult(
            id=bc.id,
            file_id=bc.file_id,
            workspace_id=bc.workspace_id,
            version=bc.version,
            overall_status=bc.overall_status,
            readiness_score=bc.readiness_score,
            check_details=[BuzzCheckItem(**c) for c in (bc.check_details or [])],
            warnings=bc.warnings or [],
            suggested_fixes=bc.suggested_fixes or [],
            generated_at=bc.generated_at,
        )

    # Map files and sort by version descending per milestone, ensuring download_url is set
    files = [
        FileResponse(
            id=f.id,
            workspace_id=f.workspace_id,
            milestone_id=f.milestone_id,
            uploader_id=f.uploader_id,
            filename=f.filename,
            file_size=f.file_size,
            file_type=f.file_type,
            mime_type=f.mime_type,
            version=f.version or 1,
            status=f.status or "submitted",
            description=f.description,
            client_feedback=getattr(f, "client_feedback", None),
            width=getattr(f, "width", None),
            height=getattr(f, "height", None),
            duration_seconds=getattr(f, "duration_seconds", None),
            deliverable_type=getattr(f, "deliverable_type", None),
            is_current=(f.version or 1) == highest_v_per_ms.get(f.milestone_id or 0, 1),
            created_at=f.created_at,
            uploader=f.uploader,
            download_url=f"/api/workspaces/{workspace_id}/files/{f.id}/download",
            buzz_check=_make_buzz_check_schema(buzz_results_by_file[f.id])
            if f.id in buzz_results_by_file
            else None,
        )
        for f in sorted(
            workspace.files,
            key=lambda x: (x.milestone_id or 0, -(x.version or 1), x.created_at or datetime.min),
        )
    ]

    # Standardize revision statuses: requested, in_progress, submitted, approved
    normalized_revisions = []
    for r in workspace.revisions:
        status_val = r.status
        if status_val == "open":
            status_val = "requested"
        elif status_val == "addressed":
            status_val = "submitted"
        elif status_val == "resolved":
            status_val = "approved"
        normalized_revisions.append(
            RevisionResponse(
                id=r.id,
                milestone_id=r.milestone_id,
                workspace_id=r.workspace_id,
                requester_id=r.requester_id,
                description=r.description,
                status=status_val,
                response_notes=getattr(r, "response_notes", None),
                created_at=r.created_at,
                requester=r.requester,
            )
        )

    # Synthesize agreed licensing terms from brief and/or creator profile licensing
    brief_lic = workspace.brief.licensing if (workspace.brief and getattr(workspace.brief, "licensing", None)) else None
    creator_lic = None
    if (
        workspace.creator_user
        and getattr(workspace.creator_user, "creator_profile", None)
        and getattr(workspace.creator_user.creator_profile, "licensing", None)
    ):
        creator_lic = workspace.creator_user.creator_profile.licensing

    commercial_use = True
    if brief_lic is not None:
        commercial_use = getattr(brief_lic, "commercial_use_required", True)
    elif creator_lic is not None:
        commercial_use = getattr(creator_lic, "commercial_use", True)

    usage_types = ["Paid Ads", "Organic Social"]
    if brief_lic and brief_lic.usage_types:
        usage_types = [u.replace("_", " ").title() for u in brief_lic.usage_types]
    elif creator_lic and creator_lic.usage_types:
        usage_types = [u.replace("_", " ").title() for u in creator_lic.usage_types]

    territory = "Worldwide"
    if brief_lic and brief_lic.territory:
        territory = brief_lic.territory.capitalize()
    elif creator_lic and creator_lic.territories:
        territory = ", ".join([t.capitalize() for t in creator_lic.territories])

    duration_months = 12
    if brief_lic and brief_lic.usage_duration_months is not None:
        duration_months = brief_lic.usage_duration_months
    elif creator_lic and creator_lic.max_duration_months is not None:
        duration_months = creator_lic.max_duration_months

    dur_label = f"{duration_months} Months" if duration_months > 0 else "Perpetual"

    platforms = ["Instagram", "YouTube", "Website"]
    if brief_lic and brief_lic.platforms:
        platforms = [p.capitalize() for p in brief_lic.platforms]
    elif workspace.brief and workspace.brief.platform:
        platforms = [p.capitalize() for p in workspace.brief.platform]
    elif creator_lic and creator_lic.platforms:
        platforms = [p.capitalize() for p in creator_lic.platforms]

    agreed_lic = AgreedLicensingResponse(
        commercial_use=commercial_use,
        usage_types=usage_types,
        territory=territory,
        duration_months=duration_months,
        duration_label=dur_label,
        platforms=platforms,
        notes="Verified commercial grant applicable to all approved deliverables.",
    )

    # Build production timeline items
    timeline_items = []
    ms_map = {m.id: m.title for m in (workspace.milestones or [])}

    for f in workspace.files:
        actor = f.uploader.full_name if f.uploader else "Creator"
        role = "creator" if f.uploader_id == workspace.creator_user_id else "brand"
        timeline_items.append(
            ProductionTimelineItem(
                id=f"file-{f.id}",
                item_type="version_upload",
                version=f.version or 1,
                file_id=f.id,
                filename=f.filename,
                download_url=f"/api/workspaces/{workspace_id}/files/{f.id}/download",
                milestone_id=f.milestone_id,
                milestone_title=ms_map.get(f.milestone_id),
                actor_name=actor,
                actor_role=role,
                creator_note=f.description,
                client_feedback=getattr(f, "client_feedback", None),
                status=f.status or "submitted",
                created_at=f.created_at,
            )
        )
        # Attach buzz check timeline item immediately after the upload if available
        if f.id in buzz_results_by_file:
            bc = buzz_results_by_file[f.id]
            timeline_items.append(
                ProductionTimelineItem(
                    id=f"buzz-{bc.id}",
                    item_type="buzz_check",
                    version=f.version or 1,
                    file_id=f.id,
                    filename=f.filename,
                    milestone_id=f.milestone_id,
                    milestone_title=ms_map.get(f.milestone_id),
                    actor_name="Buzz Check",
                    actor_role="system",
                    status=bc.overall_status,
                    buzz_overall_status=bc.overall_status,
                    buzz_readiness_score=bc.readiness_score,
                    created_at=bc.generated_at,
                )
            )

    for r in workspace.revisions:
        actor = r.requester.full_name if r.requester else "Recruiter"
        timeline_items.append(
            ProductionTimelineItem(
                id=f"rev-{r.id}",
                item_type="revision_request",
                version=None,
                file_id=None,
                filename=None,
                download_url=None,
                milestone_id=r.milestone_id,
                milestone_title=ms_map.get(r.milestone_id),
                actor_name=actor,
                actor_role="brand",
                creator_note=None,
                client_feedback=None,
                revision_description=r.description,
                revision_response=getattr(r, "response_notes", None),
                status=r.status,
                created_at=r.created_at,
            )
        )

    for rlog in (workspace.rescue_logs or []):
        actor = rlog.triggered_by.full_name if rlog.triggered_by else "Recruiter"
        action_label = {
            "adjust_plan": "Project Rescue: Plan Adjusted",
            "continue_with_creator": "Project Rescue: Continued with Creator",
            "initiate_replacement": "Project Rescue: Replacement Initiated",
        }.get(rlog.action_type, f"Project Rescue: {rlog.action_type}")
        timeline_items.append(
            ProductionTimelineItem(
                id=f"rescue-{rlog.id}",
                item_type="project_rescue",
                version=None,
                file_id=None,
                filename=None,
                download_url=None,
                milestone_id=None,
                milestone_title=None,
                actor_name=actor,
                actor_role="brand",
                creator_note=None,
                client_feedback=None,
                revision_description=rlog.notes or action_label,
                revision_response=None,
                status=rlog.action_type,
                created_at=rlog.created_at,
            )
        )

    timeline_items.sort(key=lambda x: x.created_at)

    health_data = calculate_project_health(workspace, db)
    health_resp = ProjectHealthResponse(**health_data)

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
        files=files,
        revisions=normalized_revisions,
        review=workspace.review,
        agreed_licensing=agreed_lic,
        timeline=timeline_items,
        health=health_resp,
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

    if not _is_workspace_member(workspace, current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden to this workspace")

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
    """Retrieves decrypted message stream for a workspace in chronological order."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    if not _is_workspace_member(workspace, current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden to this workspace")

    raw_messages = (
        db.query(WorkspaceMessage)
        .filter(WorkspaceMessage.workspace_id == workspace_id)
        .order_by(WorkspaceMessage.created_at.asc(), WorkspaceMessage.id.asc())
        .all()
    )

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
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    if not _is_workspace_member(workspace, current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    milestone = db.query(WorkspaceMilestone).filter(
        WorkspaceMilestone.id == milestone_id,
        WorkspaceMilestone.workspace_id == workspace_id,
    ).first()
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

    update_data = milestone_in.model_dump(exclude_unset=True)

    # Permission check: Creator CANNOT approve or release their own milestone
    if update_data.get("status") in ("released", "completed", "approved"):
        if current_user.id == workspace.creator_user_id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Creators cannot approve or release their own milestones."
            )

    if update_data.get("status") in ("released", "completed") and not milestone.completed_at:
        milestone.completed_at = datetime.utcnow()

    for field, val in update_data.items():
        setattr(milestone, field, val)

    # When a milestone is approved/released, mark all linked revisions as approved
    if update_data.get("status") in ("released", "completed", "approved"):
        milestone_revs = db.query(RevisionRequest).filter(
            RevisionRequest.milestone_id == milestone.id,
            RevisionRequest.status.in_(["requested", "in_progress", "submitted", "open", "addressed"])
        ).all()
        for r in milestone_revs:
            r.status = "approved"

        # Notify creator that milestone has been approved
        db.add(Notification(
            user_id=workspace.creator_user_id,
            title="Milestone Approved",
            message=f"Milestone '{milestone.title}' was approved by recruiter in '{workspace.title}'.",
            link=f"/workspaces?id={workspace.id}",
            type="milestone_approved",
        ))

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

    if not _is_workspace_member(workspace, current_user, db):
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
        status="requested",
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


@router.patch("/{workspace_id}/revision-requests/{revision_id}", response_model=RevisionResponse)
def update_revision_status(
    workspace_id: int,
    revision_id: int,
    rev_in: RevisionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Updates revision status (requested, in_progress, submitted, approved)."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace or not _is_workspace_member(workspace, current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    rev = db.query(RevisionRequest).filter(
        RevisionRequest.id == revision_id,
        RevisionRequest.workspace_id == workspace_id,
    ).first()
    if not rev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revision request not found")

    if rev_in.status:
        valid_statuses = {"requested", "in_progress", "submitted", "approved"}
        if rev_in.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status '{rev_in.status}'. Valid: {', '.join(sorted(valid_statuses))}",
            )
        # Creators cannot approve their own revision requests
        if rev_in.status == "approved" and current_user.id == workspace.creator_user_id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Creators cannot approve their own revision requests."
            )
        rev.status = rev_in.status

    if rev_in.response_notes is not None:
        rev.response_notes = rev_in.response_notes.strip()

    # Notifications based on transitions
    if rev_in.status == "in_progress":
        db.add(Notification(
            user_id=workspace.brand_user_id,
            title="Revision Started",
            message=f"Creator began working on the requested revision in '{workspace.title}'" + (f": {rev.response_notes}" if rev.response_notes else "."),
            link=f"/workspaces?id={workspace.id}",
            type="revision_in_progress",
        ))
    elif rev_in.status == "approved":
        db.add(Notification(
            user_id=workspace.creator_user_id,
            title="Revision Approved",
            message=f"The recruiter approved your revision in '{workspace.title}'.",
            link=f"/workspaces?id={workspace.id}",
            type="revision_approved",
        ))

    db.commit()
    db.refresh(rev)
    return rev


@router.post("/{workspace_id}/deliverables/{file_id}/feedback", response_model=FileResponse)
def submit_deliverable_feedback(
    workspace_id: int,
    file_id: int,
    feedback_in: DeliverableFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Allows recruiter or workspace member to leave feedback and/or update approval status of a deliverable version."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    if not _is_workspace_member(workspace, current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    file_obj = db.query(SharedFile).filter(
        SharedFile.id == file_id,
        SharedFile.workspace_id == workspace_id,
    ).first()
    if not file_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deliverable file not found")

    # Creator cannot approve their own deliverable
    if feedback_in.status == "approved" and current_user.id == workspace.creator_user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Creators cannot approve their own deliverables."
        )

    if feedback_in.client_feedback is not None:
        file_obj.client_feedback = feedback_in.client_feedback.strip()

    if feedback_in.status:
        file_obj.status = feedback_in.status

    # Notify creator of recruiter's feedback/approval
    notif_title = "Deliverable Approved" if feedback_in.status == "approved" else "Feedback Received on Deliverable"
    notif_msg = (
        f"Recruiter approved {file_obj.filename} (v{file_obj.version}) in '{workspace.title}'."
        if feedback_in.status == "approved"
        else f"Recruiter left feedback on {file_obj.filename} (v{file_obj.version}): '{feedback_in.client_feedback}'"
    )
    db.add(Notification(
        user_id=workspace.creator_user_id,
        title=notif_title,
        message=notif_msg,
        link=f"/workspaces?id={workspace.id}",
        type="deliverable_approved" if feedback_in.status == "approved" else "deliverable_feedback",
    ))

    db.commit()
    db.refresh(file_obj)

    # Attach download_url
    file_obj.download_url = f"/api/workspaces/{workspace_id}/files/{file_obj.id}/download"
    return file_obj


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
UPLOAD_DIR_ENV = os.environ.get("UPLOADS_DIR")
if UPLOAD_DIR_ENV:
    UPLOAD_BASE_DIR = Path(UPLOAD_DIR_ENV)
elif os.environ.get("VERCEL"):
    UPLOAD_BASE_DIR = Path("/tmp/uploads/workspaces")
else:
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

    # Check if there is a pending revision request on this milestone: mark as submitted
    if target_milestone:
        open_revs = db.query(RevisionRequest).filter(
            RevisionRequest.milestone_id == target_milestone.id,
            RevisionRequest.status.in_(["requested", "in_progress", "open"]),
        ).all()
        for r in open_revs:
            r.status = "submitted"

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

    # ── Extract file metadata (non-blocking) ──────────────────────────────────
    try:
        meta = extract_file_metadata(str(target_path), file_type)
        if meta.get("width") is not None:
            shared_file.width = meta["width"]
        if meta.get("height") is not None:
            shared_file.height = meta["height"]
        if meta.get("duration_seconds") is not None:
            shared_file.duration_seconds = meta["duration_seconds"]
        db.commit()
        db.refresh(shared_file)
    except Exception as meta_err:
        log.warning("Metadata extraction failed for file %s: %s", shared_file.id, meta_err)

    # ── Run Buzz Check (non-blocking) ─────────────────────────────────────────
    try:
        brief = workspace.brief
        buzz_result = run_delivery_check(
            file_id=shared_file.id,
            workspace_id=workspace.id,
            version=new_version,
            filename=safe_name,
            mime_type=shared_file.mime_type,
            file_type=file_type,
            width=getattr(shared_file, "width", None),
            height=getattr(shared_file, "height", None),
            duration_seconds=getattr(shared_file, "duration_seconds", None),
            deliverable_type=getattr(shared_file, "deliverable_type", None),
            brief_aspect_ratio=brief.aspect_ratio if brief else None,
            brief_duration=brief.duration if brief else None,
            brief_content_type=brief.content_type if brief else None,
            brief_deliverables=brief.deliverables if brief else None,
        )
        bc_record = DeliveryCheckResult(
            file_id=shared_file.id,
            workspace_id=workspace.id,
            version=new_version,
            overall_status=buzz_result["overall_status"],
            readiness_score=buzz_result["readiness_score"],
            check_details=buzz_result["check_details"],
            warnings=buzz_result["warnings"],
            suggested_fixes=buzz_result["suggested_fixes"],
            generated_at=datetime.utcnow(),
        )
        db.add(bc_record)
        db.commit()
    except Exception as bc_err:
        log.warning("Buzz Check failed for file %s: %s", shared_file.id, bc_err)

    # Attach download_url for frontend
    shared_file.download_url = f"/api/workspaces/{workspace_id}/files/{shared_file.id}/download"
    return shared_file


@router.get(
    "/{workspace_id}/deliverables/{file_id}/delivery-check",
    response_model=BuzzCheckResult,
)
def get_delivery_check(
    workspace_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns the latest Buzz Check result for a specific deliverable version."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    if not _is_workspace_member(workspace, current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this workspace")

    shared_file = db.query(SharedFile).filter(
        SharedFile.id == file_id,
        SharedFile.workspace_id == workspace_id,
    ).first()
    if not shared_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deliverable not found")

    bc = (
        db.query(DeliveryCheckResult)
        .filter(DeliveryCheckResult.file_id == file_id)
        .order_by(DeliveryCheckResult.id.desc())
        .first()
    )
    if not bc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Buzz Check result available for this deliverable yet.",
        )

    return BuzzCheckResult(
        id=bc.id,
        file_id=bc.file_id,
        workspace_id=bc.workspace_id,
        version=bc.version,
        overall_status=bc.overall_status,
        readiness_score=bc.readiness_score,
        check_details=[BuzzCheckItem(**c) for c in (bc.check_details or [])],
        warnings=bc.warnings or [],
        suggested_fixes=bc.suggested_fixes or [],
        generated_at=bc.generated_at,
    )


@router.get("/{workspace_id}/files/{file_id}/download")
def download_workspace_file(
    workspace_id: int,
    file_id: int,
    token: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Securely downloads a workspace deliverable with strict membership check."""
    # Allow token query parameter for direct browser anchor tags if needed
    if not current_user and token:
        try:
            from jose import jwt
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id_str = payload.get("sub")
            if user_id_str:
                current_user = db.query(User).filter(User.id == int(user_id_str), User.is_active == True).first()
        except Exception:
            current_user = None

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
# PROJECT RESCUE & HEALTH INTELLIGENCE
# ==========================================

@router.get("/{workspace_id}/health", response_model=ProjectHealthResponse)
def get_project_health(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves real-time explainable project health score, status, and risk signals."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    if not _is_workspace_member(workspace, current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this workspace")

    health_data = calculate_project_health(workspace, db)
    return ProjectHealthResponse(**health_data)


@router.get("/{workspace_id}/rescue", response_model=RescueReplacementResponse)
def get_project_rescue_details(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns project health, the comprehensive Handoff Pack, protected budget, and top 3 replacements."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    if not _is_workspace_member(workspace, current_user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this workspace")

    health_data = calculate_project_health(workspace, db)
    handoff_data = generate_handoff_pack(workspace, db)
    replacements = find_replacement_creators(workspace, db, limit=3)

    return RescueReplacementResponse(
        workspace_id=workspace.id,
        health=ProjectHealthResponse(**health_data),
        handoff_pack=ProjectHandoffPackResponse(**handoff_data),
        replacement_candidates=replacements,
    )


@router.post("/{workspace_id}/rescue/action", status_code=status.HTTP_200_OK)
def handle_rescue_action(
    workspace_id: int,
    action_in: RescueActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Recruiter-only endpoint to execute a Project Rescue action."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    is_recruiter = (
        workspace.brand_user_id == current_user.id
        or current_user.role == "admin"
    )
    if not is_recruiter:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the recruiter can initiate Project Rescue actions",
        )

    health_data = calculate_project_health(workspace, db)
    rescue_log = ProjectRescueLog(
        workspace_id=workspace.id,
        action_type=action_in.action,
        triggered_by_user_id=current_user.id,
        health_score_at_trigger=health_data["health_score"],
        health_status_at_trigger=health_data["health_status"],
        notes=action_in.notes or f"Project Rescue action executed: {action_in.action.replace('_', ' ')}",
        replacement_creator_user_id=action_in.replacement_creator_id,
        created_at=datetime.utcnow(),
    )
    db.add(rescue_log)

    # If replacement creator chosen, notify the replacement creator & recruiter
    if action_in.action == "initiate_replacement" and action_in.replacement_creator_id:
        replacement_user = db.query(User).filter(User.id == action_in.replacement_creator_id).first()
        if replacement_user:
            db.add(Notification(
                user_id=replacement_user.id,
                title="Project Rescue Handoff Opportunity",
                message=f"You have been selected as a top replacement candidate for '{workspace.title}' with protected budget.",
                link=f"/requests",
                type="rescue_handoff",
            ))

    db.add(Notification(
        user_id=workspace.brand_user_id,
        title="Project Rescue Action Executed",
        message=f"Rescue decision '{action_in.action.replace('_', ' ')}' logged for '{workspace.title}'",
        link=f"/workspaces?id={workspace.id}",
        type="rescue_action",
    ))

    db.commit()
    db.refresh(rescue_log)

    return {
        "status": "success",
        "action": action_in.action,
        "log_id": rescue_log.id,
        "health_score": rescue_log.health_score_at_trigger,
        "health_status": rescue_log.health_status_at_trigger,
        "message": f"Project Rescue action '{action_in.action.replace('_', ' ')}' successfully recorded.",
    }


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
        RevisionRequest.status.in_(["requested", "in_progress", "open"]),
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


