"""Phase 6 / Final Round 2 Suite: Buzz Check + Project Rescue Tests.

Tests all 13 core requirements:
BUZZ CHECK:
1. Correct delivery -> ready
2. Aspect ratio mismatch -> failed + suggested fix
3. Duration mismatch -> failed + suggested fix
4. Unavailable metadata -> not_verified (not penalized)
5. V1 result remains after V2 is uploaded
6. Unauthorized user blocked from Buzz Check (403)

PROJECT RESCUE:
7. Healthy project -> ON TRACK (>=75)
8. Overdue/revision-heavy project -> AT RISK (45-74)
9. Severe delays & inactivity -> RESCUE RECOMMENDED (<45)
10. Current creator strictly excluded from replacement results
11. Handoff Pack includes brief, deliverables history, revisions, licensing
12. Creator cannot initiate rescue / replacement action (HTTP 403 Forbidden)
13. Protected budget excludes already approved milestone amount
"""

import io
import sys
from datetime import datetime, timedelta
import pytest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.models.users import User
from app.models.briefs import Brief
from app.models.licensing import BriefLicensing
from app.models.creators import CreatorProfile
from app.models.workspaces import (
    Workspace,
    WorkspaceMilestone,
    RevisionRequest,
    SharedFile,
    DeliveryCheckResult,
)
from app.dependencies import create_access_token, get_password_hash
from app.services.delivery_check import run_delivery_check
from app.services.project_rescue import (
    calculate_project_health,
    generate_handoff_pack,
    find_replacement_creators,
)


@pytest.fixture
def other_user(db_session):
    u = User(
        email="rescue_intruder@maccall.demo",
        password_hash=get_password_hash("password123"),
        full_name="Rescue Intruder",
        role="brand",
        is_active=True,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture
def other_token(other_user):
    return create_access_token({"sub": str(other_user.id), "role": other_user.role})


@pytest.fixture
def replacement_creator_user(db_session):
    """Creates a distinct 2nd creator profile to verify replacement matching."""
    u = User(
        email="replacement_talent@maccall.demo",
        password_hash=get_password_hash("password123"),
        full_name="Replacement Superstar",
        role="creator",
        is_active=True,
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)

    cp = CreatorProfile(
        user_id=u.id,
        display_name="Replacement Superstar",
        core_category="video",
        specialization="Commercials",
        ai_tools=["Runway Gen-3", "ComfyUI"],
        rating=4.95,
        starting_rate=120.0,
        availability_status="available",
    )
    db_session.add(cp)
    db_session.commit()
    db_session.refresh(cp)
    return u


@pytest.fixture
def video_brief(db_session, brand_user):
    brief = Brief(
        brand_user_id=brand_user.id,
        title="High-End AI Campaign Video",
        description="Luxury product reveal video in 9:16 vertical format",
        content_type="video",
        style="Photorealistic Luxury",
        aspect_ratio="9:16",
        duration="15 seconds",
        deliverables=["15s Reel Master", "Clean Social Cut"],
        tools_suggested=["Runway Gen-3", "Midjourney"],
        budget_min=40000.0,
        budget_max=60000.0,
        deadline=datetime.utcnow() + timedelta(days=10),
        status="published",
    )
    db_session.add(brief)
    db_session.commit()
    db_session.refresh(brief)

    lic = BriefLicensing(
        brief_id=brief.id,
        commercial_use_required=True,
        usage_types=["paid_ads", "organic_social"],
        territory="worldwide",
        usage_duration_months=12,
        platforms=["instagram", "youtube", "website"],
    )
    db_session.add(lic)
    db_session.commit()
    return brief


@pytest.fixture
def workspace_with_brief(client, brand_user, creator_user, brand_token, video_brief):
    brand_hdr = {"Authorization": f"Bearer {brand_token}"}
    res = client.post(
        "/api/workspaces",
        headers=brand_hdr,
        json={
            "brief_id": video_brief.id,
            "creator_user_id": creator_user.id,
            "title": "Luxury AI Campaign Collaboration",
        },
    )
    assert res.status_code == 201
    return res.json()["id"]


# ==============================================================
# PART A: BUZZ CHECK TESTS (1–6)
# ==============================================================

def test_1_buzz_check_correct_delivery_ready():
    """1. Correct delivery (matching format, 9:16 aspect ratio, within 15s) -> ready."""
    result = run_delivery_check(
        file_id=1, workspace_id=10, version=1,
        filename="hero_render.mp4", mime_type="video/mp4", file_type="video",
        width=1080, height=1920, duration_seconds=14.5, deliverable_type=None,
        brief_aspect_ratio="9:16", brief_duration="15 seconds", brief_content_type="video",
    )
    assert result["overall_status"] == "ready"
    assert result["readiness_score"] >= 90
    assert len(result["suggested_fixes"]) == 0
    print(f"[PASS] 1. Correct delivery -> {result['overall_status']} ({result['readiness_score']}%)")


def test_2_buzz_check_aspect_ratio_mismatch():
    """2. Aspect ratio mismatch (16:9 uploaded when 9:16 required) -> failed + suggested fix."""
    result = run_delivery_check(
        file_id=2, workspace_id=10, version=1,
        filename="hero_wide.mp4", mime_type="video/mp4", file_type="video",
        width=1920, height=1080, duration_seconds=14.0, deliverable_type=None,
        brief_aspect_ratio="9:16", brief_duration="15 seconds", brief_content_type="video",
    )
    ar_check = next(c for c in result["check_details"] if c["name"] == "aspect_ratio")
    assert ar_check["status"] == "failed"
    assert any("resize" in f.lower() or "re-crop" in f.lower() for f in result["suggested_fixes"])
    print(f"[PASS] 2. Aspect ratio mismatch -> failed with suggested fix")


def test_3_buzz_check_duration_mismatch():
    """3. Duration mismatch (22s uploaded when 15s max required) -> failed + trim suggested fix."""
    result = run_delivery_check(
        file_id=3, workspace_id=10, version=1,
        filename="hero_long.mp4", mime_type="video/mp4", file_type="video",
        width=1080, height=1920, duration_seconds=22.0, deliverable_type=None,
        brief_aspect_ratio="9:16", brief_duration="15 seconds", brief_content_type="video",
    )
    dur_check = next(c for c in result["check_details"] if c["name"] == "duration")
    assert dur_check["status"] == "failed"
    assert any("trim" in f.lower() for f in result["suggested_fixes"])
    print(f"[PASS] 3. Duration mismatch -> failed with trim suggestion")


def test_4_buzz_check_unavailable_metadata_not_verified():
    """4. Unavailable metadata -> not_verified (not penalized in readiness score)."""
    result = run_delivery_check(
        file_id=4, workspace_id=10, version=1,
        filename="concept.mp4", mime_type="video/mp4", file_type="video",
        width=None, height=None, duration_seconds=None, deliverable_type=None,
        brief_aspect_ratio="9:16", brief_duration="15 seconds", brief_content_type="video",
    )
    ar_check = next(c for c in result["check_details"] if c["name"] == "aspect_ratio")
    dur_check = next(c for c in result["check_details"] if c["name"] == "duration")
    assert ar_check["status"] == "not_verified"
    assert dur_check["status"] == "not_verified"
    # Unverified checks must NOT count as failed; format check passed -> score remains 100
    assert result["readiness_score"] == 100
    print(f"[PASS] 4. Unavailable metadata -> not_verified without score penalty")


def test_5_v1_result_remains_after_v2(client, workspace_with_brief, creator_token):
    """5. V1 Buzz Check result is preserved in database and does not get overwritten when V2 uploaded."""
    creator_hdr = {"Authorization": f"Bearer {creator_token}"}
    
    # Upload V1
    v1_res = client.post(
        f"/api/workspaces/{workspace_with_brief}/deliverables",
        headers=creator_hdr,
        data={"description": "V1 initial draft"},
        files={"file": ("cut_v1.mp4", io.BytesIO(b"binary content v1"), "video/mp4")},
    )
    assert v1_res.status_code == 201
    v1_id = v1_res.json()["id"]

    # Upload V2
    v2_res = client.post(
        f"/api/workspaces/{workspace_with_brief}/deliverables",
        headers=creator_hdr,
        data={"description": "V2 revised cut"},
        files={"file": ("cut_v2.mp4", io.BytesIO(b"binary content v2"), "video/mp4")},
    )
    assert v2_res.status_code == 201
    v2_id = v2_res.json()["id"]

    # Both V1 and V2 have dedicated distinct check results
    bc1 = client.get(f"/api/workspaces/{workspace_with_brief}/deliverables/{v1_id}/delivery-check", headers=creator_hdr)
    bc2 = client.get(f"/api/workspaces/{workspace_with_brief}/deliverables/{v2_id}/delivery-check", headers=creator_hdr)
    assert bc1.status_code == 200
    assert bc2.status_code == 200
    assert bc1.json()["file_id"] == v1_id
    assert bc2.json()["file_id"] == v2_id
    print(f"[PASS] 5. V1 Buzz Check (fid={v1_id}) preserved alongside V2 (fid={v2_id})")


def test_6_unauthorized_user_blocked_from_buzz_check(client, workspace_with_brief, creator_token, other_token):
    """6. Unauthorized user is blocked from viewing Buzz Check results (403)."""
    creator_hdr = {"Authorization": f"Bearer {creator_token}"}
    res = client.post(
        f"/api/workspaces/{workspace_with_brief}/deliverables",
        headers=creator_hdr,
        data={"description": "V1 test"},
        files={"file": ("cut.mp4", io.BytesIO(b"data"), "video/mp4")},
    )
    assert res.status_code == 201
    fid = res.json()["id"]

    other_hdr = {"Authorization": f"Bearer {other_token}"}
    chk = client.get(f"/api/workspaces/{workspace_with_brief}/deliverables/{fid}/delivery-check", headers=other_hdr)
    assert chk.status_code == 403
    print("[PASS] 6. Unauthorized user received 403 on Buzz Check")


# ==============================================================
# PART B: PROJECT RESCUE TESTS (7–13)
# ==============================================================

def test_7_healthy_project_on_track(db_session, workspace_with_brief):
    """7. Healthy project with milestones on schedule -> ON TRACK (>=75)."""
    ws = db_session.query(Workspace).filter(Workspace.id == workspace_with_brief).first()
    
    # Add a healthy milestone with a future estimated date
    m1 = WorkspaceMilestone(
        workspace_id=ws.id,
        title="Styleframes & Direction",
        amount=25000.0,
        status="approved",
        completed_at=datetime.utcnow() - timedelta(days=1),
    )
    m2 = WorkspaceMilestone(
        workspace_id=ws.id,
        title="Final 4K Master",
        amount=35000.0,
        status="pending",
        estimated_date=datetime.utcnow() + timedelta(days=5),
    )
    db_session.add_all([m1, m2])
    db_session.commit()
    db_session.refresh(ws)

    health = calculate_project_health(ws, db_session)
    assert health["health_score"] >= 75
    assert health["health_status"] == "ON TRACK"
    print(f"[PASS] 7. Healthy project -> {health['health_status']} ({health['health_score']}/100)")


def test_8_overdue_revision_heavy_project_at_risk(db_session, workspace_with_brief, brand_user):
    """8. Overdue milestone and multiple unresolved revisions -> AT RISK (45-74)."""
    ws = db_session.query(Workspace).filter(Workspace.id == workspace_with_brief).first()
    
    # Overdue milestone (by 1 day)
    m = WorkspaceMilestone(
        workspace_id=ws.id,
        title="Animatic Pass",
        amount=30000.0,
        status="pending",
        estimated_date=datetime.utcnow() - timedelta(days=1),
    )
    db_session.add(m)
    db_session.commit()

    # 2 unresolved revision requests
    r1 = RevisionRequest(
        workspace_id=ws.id,
        milestone_id=m.id,
        requester_id=brand_user.id,
        description="Fix the pacing in second scene",
        status="requested",
    )
    r2 = RevisionRequest(
        workspace_id=ws.id,
        milestone_id=m.id,
        requester_id=brand_user.id,
        description="Update brand logo placement",
        status="requested",
    )
    db_session.add_all([r1, r2])
    db_session.commit()
    db_session.refresh(ws)

    health = calculate_project_health(ws, db_session)
    assert 45 <= health["health_score"] <= 74
    assert health["health_status"] == "AT RISK"
    assert any("overdue" in r.lower() for r in health["reasons"])
    assert any("revision" in r.lower() for r in health["reasons"])
    print(f"[PASS] 8. Overdue + revisions -> {health['health_status']} ({health['health_score']}/100)")


def test_9_severe_delays_rescue_recommended(db_session, workspace_with_brief, brand_user):
    """9. Multiple overdue milestones, missed deadline, severe inactivity -> RESCUE RECOMMENDED (<45)."""
    ws = db_session.query(Workspace).filter(Workspace.id == workspace_with_brief).first()
    ws.status = "production"
    
    # Set brief deadline in the past
    ws.brief.deadline = datetime.utcnow() - timedelta(days=3)
    
    # 2 severely overdue milestones
    m1 = WorkspaceMilestone(
        workspace_id=ws.id,
        title="Concept 3D Render",
        amount=25000.0,
        status="pending",
        estimated_date=datetime.utcnow() - timedelta(days=4),
    )
    m2 = WorkspaceMilestone(
        workspace_id=ws.id,
        title="Audio Master",
        amount=25000.0,
        status="pending",
        estimated_date=datetime.utcnow() - timedelta(days=4),
    )
    db_session.add_all([m1, m2])

    # Unresolved revisions
    r1 = RevisionRequest(workspace_id=ws.id, requester_id=brand_user.id, description="R1", status="requested")
    r2 = RevisionRequest(workspace_id=ws.id, requester_id=brand_user.id, description="R2", status="requested")
    db_session.add_all([r1, r2])
    db_session.commit()
    db_session.refresh(ws)

    health = calculate_project_health(ws, db_session)
    assert health["health_score"] < 45
    assert health["health_status"] == "RESCUE RECOMMENDED"
    print(f"[PASS] 9. Severe delays -> {health['health_status']} ({health['health_score']}/100)")


def test_10_current_creator_excluded_from_replacement(db_session, workspace_with_brief, replacement_creator_user):
    """10. Replacement matching strictly excludes the current workspace creator."""
    ws = db_session.query(Workspace).filter(Workspace.id == workspace_with_brief).first()
    current_creator_uid = ws.creator_user_id

    replacements = find_replacement_creators(ws, db_session, limit=5)
    assert len(replacements) > 0
    candidate_user_ids = [c["creator_user_id"] for c in replacements]
    assert current_creator_uid not in candidate_user_ids, "Current creator must NOT be in replacement list"
    assert replacement_creator_user.id in candidate_user_ids
    print(f"[PASS] 10. Current creator #{current_creator_uid} excluded from replacements: {candidate_user_ids}")


def test_11_handoff_pack_contains_all_critical_context(db_session, workspace_with_brief, brand_user):
    """11. Handoff Pack includes brief, deliverables history, revisions, licensing, and budget."""
    ws = db_session.query(Workspace).filter(Workspace.id == workspace_with_brief).first()
    
    # Add a completed milestone and an unfinished milestone
    m_done = WorkspaceMilestone(workspace_id=ws.id, title="M1 Done", amount=20000.0, status="approved")
    m_todo = WorkspaceMilestone(workspace_id=ws.id, title="M2 Todo", amount=40000.0, status="pending")
    db_session.add_all([m_done, m_todo])

    # Add a deliverable
    sf = SharedFile(
        workspace_id=ws.id,
        uploader_id=ws.creator_user_id,
        filename="v1_render.mp4",
        version=1,
        status="revision_requested",
        client_feedback="Lighting is too dark in background",
    )
    db_session.add(sf)
    db_session.commit()

    pack = generate_handoff_pack(ws, db_session)
    assert "brief_overview" in pack
    assert "agreed_licensing" in pack
    assert len(pack["completed_milestones"]) >= 1
    assert len(pack["remaining_milestones"]) >= 1
    assert len(pack["deliverable_history"]) >= 1
    assert "recruiter_feedback_summary" in pack
    assert any("too dark" in note for note in pack["recruiter_feedback_summary"])
    assert "remaining_scope" in pack
    print("[PASS] 11. Handoff pack contains brief, deliverables, licensing, feedback, and scope")


def test_12_creator_cannot_initiate_rescue_action(client, workspace_with_brief, creator_token, brand_token):
    """12. Creator cannot trigger rescue replacement/action (HTTP 403 Forbidden). Recruiter can."""
    creator_hdr = {"Authorization": f"Bearer {creator_token}"}
    brand_hdr = {"Authorization": f"Bearer {brand_token}"}

    # Creator attempts replacement -> 403
    creator_res = client.post(
        f"/api/workspaces/{workspace_with_brief}/rescue/action",
        headers=creator_hdr,
        json={"action": "initiate_replacement", "notes": "Creator trying to self-replace"},
    )
    assert creator_res.status_code == 403
    assert "Only the recruiter can initiate Project Rescue" in creator_res.json()["detail"]

    # Recruiter triggers adjust_plan -> 200
    brand_res = client.post(
        f"/api/workspaces/{workspace_with_brief}/rescue/action",
        headers=brand_hdr,
        json={"action": "adjust_plan", "notes": "Extending deadline by 3 days"},
    )
    assert brand_res.status_code == 200
    assert brand_res.json()["status"] == "success"
    print("[PASS] 12. Creator blocked with 403; Recruiter successfully initiated rescue action")


def test_13_protected_budget_excludes_approved_milestone_amount(db_session, workspace_with_brief):
    """13. Protected budget preserves Creator A's approved milestone earnings and only transfers remaining balance."""
    ws = db_session.query(Workspace).filter(Workspace.id == workspace_with_brief).first()
    
    # Remove any default milestones to isolate test scenario
    db_session.query(WorkspaceMilestone).filter(WorkspaceMilestone.workspace_id == ws.id).delete()
    db_session.commit()

    # Milestone 1: Approved / Earned (₹15,000)
    m1 = WorkspaceMilestone(workspace_id=ws.id, title="M1 Concept", amount=15000.0, status="approved")
    # Milestone 2: Pending (₹45,000)
    m2 = WorkspaceMilestone(workspace_id=ws.id, title="M2 Production", amount=45000.0, status="pending")
    db_session.add_all([m1, m2])
    db_session.commit()
    db_session.refresh(ws)

    health = calculate_project_health(ws, db_session)
    budget = health["protected_budget"]

    assert budget["total_budget"] == 60000.0
    assert budget["approved_amount"] == 15000.0
    assert budget["remaining_protected_balance"] == 45000.0
    assert "Protected Budget — Demo Simulation" in budget["disclaimer"]
    print(f"[PASS] 13. Protected budget: Total ₹{budget['total_budget']} - Approved ₹{budget['approved_amount']} = Remaining ₹{budget['remaining_protected_balance']}")
