"""Phase 4 Test Suite: Workspace 2.0 Production & Collaboration Hub Tests.

Tests all 12 Phase 4 requirements:
1. Workspace opens with messages, milestones, deliverables, agreed licensing, timeline
2. V1 upload
3. V2 upload preserves V1
4. V3 upload preserves V1 and V2
5. Revision requested
6. Creator starts revision (in_progress with response_notes)
7. New version upload sets revision to submitted
8. Recruiter approval of revision
9. Feedback linked to correct version
10. Usage rights display matches project licensing
11. Unauthorized user gets 403
12. Creator cannot approve own deliverable or milestone (403)
"""

import io
import sys
import os
import pytest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.models.users import User
from app.models.briefs import Brief
from app.models.licensing import BriefLicensing, CreatorLicensing
from app.dependencies import create_access_token, get_password_hash


@pytest.fixture
def other_user(db_session):
    """Creates a 3rd user who is not a member of the workspace."""
    u = User(
        email="unauthorized_intruder@maccall.demo",
        password_hash=get_password_hash("password123"),
        full_name="Unauthorized Intruder",
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
def brief_with_licensing(db_session, brand_user):
    """Creates a brief with deterministic licensing terms for testing."""
    brief = Brief(
        brand_user_id=brand_user.id,
        title="Luxury Automotive Cinematic Spot",
        description="High-end video showcase for electric hypercar",
        content_type="video",
        style="Photorealistic Luxury",
        aspect_ratio="16:9",
        duration="30s",
        budget_min=50000.0,
        budget_max=125000.0,
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


def test_phase4_complete_workspace_lifecycle(
    client,
    brand_user,
    creator_user,
    brand_token,
    creator_token,
    other_token,
    brief_with_licensing,
    db_session,
):
    brand_hdr = {"Authorization": f"Bearer {brand_token}"}
    creator_hdr = {"Authorization": f"Bearer {creator_token}"}
    other_hdr = {"Authorization": f"Bearer {other_token}"}

    # Setup Creator Licensing Offer
    creator_lic = CreatorLicensing(
        creator_profile_id=creator_user.creator_profile.id,
        commercial_use=True,
        usage_types=["paid_ads", "organic_social"],
        territories=["worldwide"],
        max_duration_months=12,
        platforms=["instagram", "youtube", "website"],
    )
    db_session.add(creator_lic)
    db_session.commit()

    # Step 0: Create Workspace
    create_res = client.post(
        "/api/workspaces",
        headers=brand_hdr,
        json={
            "brief_id": brief_with_licensing.id,
            "creator_user_id": creator_user.id,
            "title": "Luxury Automotive Spot Collaboration",
        },
    )
    assert create_res.status_code == 201, create_res.text
    ws_id = create_res.json()["id"]

    # Add a Milestone
    ms_res = client.post(
        f"/api/workspaces/{ws_id}/milestones",
        headers=brand_hdr,
        json={
            "title": "Concept Design & Storyboard",
            "description": "Initial 3D animatic and key visual frames",
            "amount": 50000.0,
        },
    )
    assert ms_res.status_code == 201
    ms_id = ms_res.json()["id"]

    # Send a message
    msg_res = client.post(
        f"/api/workspaces/{ws_id}/messages",
        headers=brand_hdr,
        json={"content": "Welcome to the workspace! Please upload V1 concept."},
    )
    assert msg_res.status_code == 201

    # -------------------------------------------------------------
    # 1. Test Workspace Detail: opens with messages, milestones, deliverables, agreed licensing, timeline
    # -------------------------------------------------------------
    ws_detail_res = client.get(f"/api/workspaces/{ws_id}", headers=brand_hdr)
    assert ws_detail_res.status_code == 200
    ws_data = ws_detail_res.json()
    assert len(ws_data["messages"]) >= 1
    assert len(ws_data["milestones"]) >= 1
    assert "agreed_licensing" in ws_data and ws_data["agreed_licensing"] is not None
    assert ws_data["agreed_licensing"]["commercial_use"] is True
    assert ws_data["agreed_licensing"]["territory"] == "Worldwide"
    assert "timeline" in ws_data
    print("[PASS] 1. Workspace detail verified with agreed licensing and timeline.")

    # -------------------------------------------------------------
    # 2. Test V1 upload
    # -------------------------------------------------------------
    v1_file_content = b"Binary stream for deliverable version 1"
    v1_upload_res = client.post(
        f"/api/workspaces/{ws_id}/deliverables",
        headers=creator_hdr,
        data={"milestone_id": ms_id, "description": "V1 Initial concept render"},
        files={"file": ("concept_v1.mp4", io.BytesIO(v1_file_content), "video/mp4")},
    )
    assert v1_upload_res.status_code == 201, v1_upload_res.text
    v1_data = v1_upload_res.json()
    assert v1_data["version"] == 1
    v1_id = v1_data["id"]
    print(f"[PASS] 2. V1 upload succeeded (id={v1_id}, version={v1_data['version']}).")

    # -------------------------------------------------------------
    # 3. Test V2 upload preserves V1
    # -------------------------------------------------------------
    v2_file_content = b"Binary stream for deliverable version 2"
    v2_upload_res = client.post(
        f"/api/workspaces/{ws_id}/deliverables",
        headers=creator_hdr,
        data={"milestone_id": ms_id, "description": "V2 Color graded revision"},
        files={"file": ("concept_v2.mp4", io.BytesIO(v2_file_content), "video/mp4")},
    )
    assert v2_upload_res.status_code == 201
    v2_data = v2_upload_res.json()
    assert v2_data["version"] == 2
    v2_id = v2_data["id"]

    # Verify both V1 and V2 are present
    chk_res = client.get(f"/api/workspaces/{ws_id}", headers=brand_hdr)
    files = chk_res.json()["files"]
    versions = [f["version"] for f in files]
    assert 1 in versions and 2 in versions, f"V1 was not preserved when V2 uploaded: {versions}"
    v2_file_item = next(f for f in files if f["version"] == 2)
    v1_file_item = next(f for f in files if f["version"] == 1)
    assert v2_file_item["is_current"] is True
    assert v1_file_item["is_current"] is False
    print("[PASS] 3. V2 upload preserves V1 and marks V2 as is_current.")

    # -------------------------------------------------------------
    # 4. Test V3 upload preserves V1 and V2
    # -------------------------------------------------------------
    v3_file_content = b"Binary stream for deliverable version 3"
    v3_upload_res = client.post(
        f"/api/workspaces/{ws_id}/deliverables",
        headers=creator_hdr,
        data={"milestone_id": ms_id, "description": "V3 Master render with sound FX"},
        files={"file": ("concept_v3.mp4", io.BytesIO(v3_file_content), "video/mp4")},
    )
    assert v3_upload_res.status_code == 201
    v3_data = v3_upload_res.json()
    assert v3_data["version"] == 3
    v3_id = v3_data["id"]

    chk_res3 = client.get(f"/api/workspaces/{ws_id}", headers=brand_hdr)
    files3 = chk_res3.json()["files"]
    versions3 = [f["version"] for f in files3]
    assert 1 in versions3 and 2 in versions3 and 3 in versions3
    v3_file_item = next(f for f in files3 if f["version"] == 3)
    assert v3_file_item["is_current"] is True
    print("[PASS] 4. V3 upload preserves V1 and V2 (all 3 versions intact).")

    # -------------------------------------------------------------
    # 5. Test Revision requested by Recruiter
    # -------------------------------------------------------------
    rev_res = client.post(
        f"/api/workspaces/{ws_id}/revision-requests",
        headers=brand_hdr,
        json={
            "milestone_id": ms_id,
            "description": "Please brighten lighting on the front bumper and cut 1s from intro.",
        },
    )
    assert rev_res.status_code == 201
    rev_data = rev_res.json()
    assert rev_data["status"] == "requested"
    rev_id = rev_data["id"]
    print(f"[PASS] 5. Revision requested (id={rev_id}, status={rev_data['status']}).")

    # -------------------------------------------------------------
    # 6. Test Creator starts revision (in_progress with response_notes)
    # -------------------------------------------------------------
    start_rev_res = client.patch(
        f"/api/workspaces/{ws_id}/revision-requests/{rev_id}",
        headers=creator_hdr,
        json={
            "status": "in_progress",
            "response_notes": "Working on lighting boost and trimming the first scene now.",
        },
    )
    assert start_rev_res.status_code == 200
    start_rev_data = start_rev_res.json()
    assert start_rev_data["status"] == "in_progress"
    assert "lighting boost" in start_rev_data["response_notes"]
    print("[PASS] 6. Creator moved revision to in_progress with response notes.")

    # -------------------------------------------------------------
    # 7. Test New version upload sets revision to submitted
    # -------------------------------------------------------------
    v4_file_content = b"Binary stream for deliverable version 4"
    v4_upload_res = client.post(
        f"/api/workspaces/{ws_id}/deliverables",
        headers=creator_hdr,
        data={"milestone_id": ms_id, "description": "V4 Addressed lighting and trim"},
        files={"file": ("concept_v4.mp4", io.BytesIO(v4_file_content), "video/mp4")},
    )
    assert v4_upload_res.status_code == 201
    # Check revision status is automatically transitioned to submitted
    chk_rev = client.get(f"/api/workspaces/{ws_id}", headers=brand_hdr)
    matching_rev = next(r for r in chk_rev.json()["revisions"] if r["id"] == rev_id)
    assert matching_rev["status"] == "submitted"
    print("[PASS] 7. Uploading new deliverable version transitioned revision to 'submitted'.")

    # -------------------------------------------------------------
    # 8. Test Recruiter approval of revision
    # -------------------------------------------------------------
    appr_rev_res = client.patch(
        f"/api/workspaces/{ws_id}/revision-requests/{rev_id}",
        headers=brand_hdr,
        json={"status": "approved"},
    )
    assert appr_rev_res.status_code == 200
    assert appr_rev_res.json()["status"] == "approved"
    print("[PASS] 8. Recruiter approved revision successfully.")

    # -------------------------------------------------------------
    # 9. Test Feedback linked to correct version
    # -------------------------------------------------------------
    fb_res = client.post(
        f"/api/workspaces/{ws_id}/deliverables/{v3_id}/feedback",
        headers=brand_hdr,
        json={
            "client_feedback": "Lighting looks much better, but audio still clipped slightly.",
            "status": "feedback_given",
        },
    )
    assert fb_res.status_code == 200
    assert fb_res.json()["client_feedback"] == "Lighting looks much better, but audio still clipped slightly."

    # Verify that V3 has feedback, while V1 does not
    chk_detail = client.get(f"/api/workspaces/{ws_id}", headers=brand_hdr).json()
    f3 = next(f for f in chk_detail["files"] if f["id"] == v3_id)
    f1 = next(f for f in chk_detail["files"] if f["id"] == v1_id)
    assert f3["client_feedback"] is not None
    assert f1["client_feedback"] is None
    print("[PASS] 9. Recruiter feedback is strictly attached to specific version.")

    # -------------------------------------------------------------
    # 10. Test Usage rights display matches project licensing
    # -------------------------------------------------------------
    lic_terms = chk_detail["agreed_licensing"]
    assert lic_terms["commercial_use"] is True
    assert lic_terms["territory"] == "Worldwide"
    assert lic_terms["duration_months"] == 12
    assert "Instagram" in lic_terms["platforms"]
    assert "Paid Ads" in lic_terms["usage_types"]
    print("[PASS] 10. Agreed licensing in workspace accurately mirrors project brief licensing.")

    # -------------------------------------------------------------
    # 11. Test Unauthorized user gets 403
    # -------------------------------------------------------------
    unauth_get = client.get(f"/api/workspaces/{ws_id}", headers=other_hdr)
    assert unauth_get.status_code == 403, f"Expected 403, got {unauth_get.status_code}"

    unauth_post_msg = client.post(
        f"/api/workspaces/{ws_id}/messages",
        headers=other_hdr,
        json={"content": "I am not a member!"},
    )
    assert unauth_post_msg.status_code == 403

    unauth_upload = client.post(
        f"/api/workspaces/{ws_id}/deliverables",
        headers=other_hdr,
        data={"milestone_id": ms_id},
        files={"file": ("hack.mp4", io.BytesIO(b"data"), "video/mp4")},
    )
    assert unauth_upload.status_code == 403
    print("[PASS] 11. Unauthorized access strictly blocked with HTTP 403 Forbidden.")

    # -------------------------------------------------------------
    # 12. Test Creator cannot approve own deliverable or milestone (403)
    # -------------------------------------------------------------
    # Creator tries to approve own milestone
    cr_appr_ms = client.put(
        f"/api/workspaces/{ws_id}/milestones/{ms_id}",
        headers=creator_hdr,
        json={"status": "completed"},
    )
    assert cr_appr_ms.status_code == 403, f"Expected 403, got {cr_appr_ms.status_code}"
    assert "Creators cannot approve" in cr_appr_ms.json()["detail"]

    # Creator tries to approve own deliverable
    cr_appr_del = client.post(
        f"/api/workspaces/{ws_id}/deliverables/{v3_id}/feedback",
        headers=creator_hdr,
        json={"status": "approved"},
    )
    assert cr_appr_del.status_code == 403, f"Expected 403, got {cr_appr_del.status_code}"
    assert "Creators cannot approve" in cr_appr_del.json()["detail"]

    # Creator tries to approve own revision
    cr_appr_rev = client.patch(
        f"/api/workspaces/{ws_id}/revision-requests/{rev_id}",
        headers=creator_hdr,
        json={"status": "approved"},
    )
    assert cr_appr_rev.status_code == 403, f"Expected 403, got {cr_appr_rev.status_code}"
    assert "Creators cannot approve" in cr_appr_rev.json()["detail"]

    print("[PASS] 12. Creator self-approval attempts strictly forbidden with HTTP 403.")
    print("\n=======================================================")
    print("ALL 12 PHASE 4 WORKSPACE 2.0 REQUIREMENTS PASSED!")
    print("=======================================================")
