"""Phase 5 Test Suite: Buzz Check / Delivery Intelligence.

Tests all 12 Phase 5 requirements:
1.  Upload triggers automatic Buzz Check result creation
2.  Buzz Check result is embedded in FileResponse (GET workspace detail)
3.  Buzz Check result is retrievable via dedicated endpoint
4.  Format check: video brief + MP4 upload -> passed
5.  Format check: video brief + PDF upload -> failed
6.  Aspect ratio check: matching dimensions -> passed
7.  Aspect ratio check: wrong dimensions -> failed
8.  Aspect ratio check: no metadata -> not_verified (not failed)
9.  Duration check: within limit -> passed
10. Duration check: over limit -> failed + suggested fix
11. Upload without a brief still succeeds (no checks run, score=100)
12. Unauthorized user cannot access delivery-check endpoint (403)
"""

import io
import sys
import os
import json
import pytest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.models.users import User
from app.models.briefs import Brief
from app.models.licensing import BriefLicensing
from app.models.workspaces import SharedFile, DeliveryCheckResult
from app.dependencies import create_access_token, get_password_hash
from app.services.delivery_check import (
    run_delivery_check,
    extract_file_metadata,
    _parse_aspect_ratio,
    _parse_duration_seconds,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def other_user(db_session):
    u = User(
        email="buzz_intruder@maccall.demo",
        password_hash=get_password_hash("password123"),
        full_name="Buzz Intruder",
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
def video_brief(db_session, brand_user):
    """Brief with video, 9:16 aspect, 15s duration requirement."""
    brief = Brief(
        brand_user_id=brand_user.id,
        title="Reel Campaign Brief",
        description="Short-form vertical reel for Instagram and TikTok",
        content_type="video",
        style="Cinematic",
        aspect_ratio="9:16",
        duration="15 seconds",
        deliverables=["Instagram Reel", "TikTok Clip"],
        budget_min=5000.0,
        budget_max=15000.0,
        status="published",
    )
    db_session.add(brief)
    db_session.commit()
    db_session.refresh(brief)
    return brief


@pytest.fixture
def workspace_with_brief(db_session, brand_user, creator_user, brand_token, creator_token, client, video_brief):
    """Creates a workspace backed by the video brief."""
    brand_hdr = {"Authorization": f"Bearer {brand_token}"}
    res = client.post(
        "/api/workspaces",
        headers=brand_hdr,
        json={
            "brief_id": video_brief.id,
            "creator_user_id": creator_user.id,
            "title": "Reel Campaign Workspace",
        },
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


@pytest.fixture
def workspace_no_brief(db_session, brand_user, creator_user, brand_token, client):
    """Creates a workspace with NO brief attached."""
    brand_hdr = {"Authorization": f"Bearer {brand_token}"}
    res = client.post(
        "/api/workspaces",
        headers=brand_hdr,
        json={
            "creator_user_id": creator_user.id,
            "title": "Freeform Workspace (No Brief)",
        },
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


# ── Pure unit tests for service helpers ───────────────────────────────────────

def test_parse_aspect_ratio_valid():
    assert _parse_aspect_ratio("9:16") == (9, 16)
    assert _parse_aspect_ratio("16:9") == (16, 9)
    assert _parse_aspect_ratio("1:1") == (1, 1)


def test_parse_aspect_ratio_invalid():
    assert _parse_aspect_ratio(None) is None
    assert _parse_aspect_ratio("") is None
    assert _parse_aspect_ratio("widescreen") is None


def test_parse_duration_seconds():
    assert _parse_duration_seconds("15 seconds") == 15.0
    assert _parse_duration_seconds("15s") == 15.0
    assert _parse_duration_seconds("30") == 30.0
    assert _parse_duration_seconds("1:30") == 90.0
    assert _parse_duration_seconds("2 min") == 120.0
    assert _parse_duration_seconds(None) is None


# ── Integration tests ─────────────────────────────────────────────────────────

def _upload_mp4(client, ws_id: int, creator_token: str, filename: str = "reel.mp4") -> dict:
    creator_hdr = {"Authorization": f"Bearer {creator_token}"}
    content = b"fake mp4 binary content"
    res = client.post(
        f"/api/workspaces/{ws_id}/deliverables",
        headers=creator_hdr,
        data={"description": "Test upload"},
        files={"file": (filename, io.BytesIO(content), "video/mp4")},
    )
    assert res.status_code == 201, res.text
    return res.json()


def _upload_pdf(client, ws_id: int, creator_token: str) -> dict:
    creator_hdr = {"Authorization": f"Bearer {creator_token}"}
    content = b"%PDF-1.4 fake pdf content"
    res = client.post(
        f"/api/workspaces/{ws_id}/deliverables",
        headers=creator_hdr,
        data={"description": "Wrong file type"},
        files={"file": ("brief_doc.pdf", io.BytesIO(content), "application/pdf")},
    )
    assert res.status_code == 201, res.text
    return res.json()


def test_1_upload_triggers_buzz_check(client, db_session, workspace_with_brief, creator_token):
    """Upload should automatically create a DeliveryCheckResult record."""
    file_data = _upload_mp4(client, workspace_with_brief, creator_token)
    file_id = file_data["id"]

    bc = db_session.query(DeliveryCheckResult).filter(
        DeliveryCheckResult.file_id == file_id
    ).first()
    assert bc is not None, "Buzz Check result should be created on upload"
    assert bc.overall_status in {"ready", "needs_attention", "blocked"}
    assert 0 <= bc.readiness_score <= 100
    print(f"[PASS] 1. Buzz Check auto-created: status={bc.overall_status}, score={bc.readiness_score}")


def test_2_buzz_check_embedded_in_file_response(client, workspace_with_brief, brand_token, creator_token):
    """Workspace detail endpoint must include buzz_check on each FileResponse."""
    _upload_mp4(client, workspace_with_brief, creator_token)

    brand_hdr = {"Authorization": f"Bearer {brand_token}"}
    ws_res = client.get(f"/api/workspaces/{workspace_with_brief}", headers=brand_hdr)
    assert ws_res.status_code == 200
    files = ws_res.json()["files"]
    assert len(files) >= 1
    file_item = files[0]
    assert "buzz_check" in file_item
    assert file_item["buzz_check"] is not None
    bc = file_item["buzz_check"]
    assert "overall_status" in bc
    assert "readiness_score" in bc
    assert "check_details" in bc
    print(f"[PASS] 2. buzz_check embedded in file response: status={bc['overall_status']}")


def test_3_dedicated_delivery_check_endpoint(client, workspace_with_brief, brand_token, creator_token):
    """GET /workspaces/{id}/deliverables/{fid}/delivery-check must return BuzzCheckResult."""
    file_data = _upload_mp4(client, workspace_with_brief, creator_token)
    file_id = file_data["id"]

    brand_hdr = {"Authorization": f"Bearer {brand_token}"}
    bc_res = client.get(
        f"/api/workspaces/{workspace_with_brief}/deliverables/{file_id}/delivery-check",
        headers=brand_hdr,
    )
    assert bc_res.status_code == 200, bc_res.text
    bc = bc_res.json()
    assert bc["file_id"] == file_id
    assert bc["overall_status"] in {"ready", "needs_attention", "blocked"}
    assert isinstance(bc["check_details"], list)
    print(f"[PASS] 3. Dedicated delivery-check endpoint works: {bc['overall_status']}")


def test_4_format_check_video_mp4_passes(db_session):
    """Video brief + MP4 file -> format check passed."""
    result = run_delivery_check(
        file_id=1, workspace_id=1, version=1,
        filename="reel.mp4", mime_type="video/mp4", file_type="video",
        width=None, height=None, duration_seconds=None, deliverable_type=None,
        brief_content_type="video",
    )
    format_checks = [c for c in result["check_details"] if c["name"] == "format"]
    assert len(format_checks) == 1
    assert format_checks[0]["status"] == "passed"
    print(f"[PASS] 4. Format check: MP4 for video brief -> passed")


def test_5_format_check_video_brief_pdf_fails(db_session):
    """Video brief + PDF upload -> format check failed."""
    result = run_delivery_check(
        file_id=2, workspace_id=1, version=1,
        filename="doc.pdf", mime_type="application/pdf", file_type="document",
        width=None, height=None, duration_seconds=None, deliverable_type=None,
        brief_content_type="video",
    )
    format_checks = [c for c in result["check_details"] if c["name"] == "format"]
    assert len(format_checks) == 1
    assert format_checks[0]["status"] == "failed"
    assert len(result["suggested_fixes"]) >= 1
    print(f"[PASS] 5. Format check: PDF for video brief -> failed with fix suggestion")


def test_6_aspect_ratio_matching_dimensions_passes(db_session):
    """Correct 9:16 dimensions -> aspect ratio check passed."""
    result = run_delivery_check(
        file_id=3, workspace_id=1, version=1,
        filename="reel.mp4", mime_type="video/mp4", file_type="video",
        width=1080, height=1920, duration_seconds=None, deliverable_type=None,
        brief_aspect_ratio="9:16",
    )
    ar_checks = [c for c in result["check_details"] if c["name"] == "aspect_ratio"]
    assert len(ar_checks) == 1
    assert ar_checks[0]["status"] == "passed"
    print(f"[PASS] 6. Aspect ratio 9:16 with matching 1080x1920 -> passed")


def test_7_aspect_ratio_wrong_dimensions_fails(db_session):
    """16:9 file uploaded for 9:16 brief -> aspect ratio check failed."""
    result = run_delivery_check(
        file_id=4, workspace_id=1, version=1,
        filename="landscape.mp4", mime_type="video/mp4", file_type="video",
        width=1920, height=1080, duration_seconds=None, deliverable_type=None,
        brief_aspect_ratio="9:16",
    )
    ar_checks = [c for c in result["check_details"] if c["name"] == "aspect_ratio"]
    assert len(ar_checks) == 1
    assert ar_checks[0]["status"] == "failed"
    assert len(result["suggested_fixes"]) >= 1
    print(f"[PASS] 7. Aspect ratio: wrong 1920x1080 for 9:16 brief -> failed")


def test_8_aspect_ratio_no_metadata_not_verified(db_session):
    """No dimension metadata -> not_verified (must NOT count as failed in score)."""
    result = run_delivery_check(
        file_id=5, workspace_id=1, version=1,
        filename="reel.mp4", mime_type="video/mp4", file_type="video",
        width=None, height=None, duration_seconds=None, deliverable_type=None,
        brief_aspect_ratio="9:16",
    )
    ar_checks = [c for c in result["check_details"] if c["name"] == "aspect_ratio"]
    assert len(ar_checks) == 1
    assert ar_checks[0]["status"] == "not_verified"
    # Score must NOT be penalised for unverifiable checks
    # The score should be 100 (no scoreable check ran for aspect ratio)
    assert result["readiness_score"] == 100
    print(f"[PASS] 8. Aspect ratio not_verified -> score not penalised (score={result['readiness_score']})")


def test_9_duration_within_limit_passes(db_session):
    """14s video for 15s limit -> duration check passed."""
    result = run_delivery_check(
        file_id=6, workspace_id=1, version=1,
        filename="reel.mp4", mime_type="video/mp4", file_type="video",
        width=None, height=None, duration_seconds=14.0, deliverable_type=None,
        brief_duration="15 seconds",
    )
    dur_checks = [c for c in result["check_details"] if c["name"] == "duration"]
    assert len(dur_checks) == 1
    assert dur_checks[0]["status"] == "passed"
    print(f"[PASS] 9. Duration 14s within 15s limit -> passed")


def test_10_duration_over_limit_fails_with_fix(db_session):
    """19s video for 15s limit -> failed + suggested fix with trim amount."""
    result = run_delivery_check(
        file_id=7, workspace_id=1, version=1,
        filename="reel.mp4", mime_type="video/mp4", file_type="video",
        width=None, height=None, duration_seconds=19.0, deliverable_type=None,
        brief_duration="15 seconds",
    )
    dur_checks = [c for c in result["check_details"] if c["name"] == "duration"]
    assert len(dur_checks) == 1
    assert dur_checks[0]["status"] == "failed"
    assert len(result["suggested_fixes"]) >= 1
    fix_text = result["suggested_fixes"][0]
    # Should mention approximate trim amount (19 - 15 = 4s, within tolerance)
    assert "trim" in fix_text.lower() or "seconds" in fix_text.lower()
    print(f"[PASS] 10. Duration 19s for 15s limit -> failed, fix: '{fix_text[:60]}...'")


def test_11_upload_without_brief_succeeds_score_100(client, workspace_no_brief, creator_token, db_session):
    """No brief -> no checks run, readiness_score = 100, overall_status = ready."""
    file_data = _upload_mp4(client, workspace_no_brief, creator_token)
    file_id = file_data["id"]

    bc = db_session.query(DeliveryCheckResult).filter(
        DeliveryCheckResult.file_id == file_id
    ).first()
    assert bc is not None, "Buzz Check should still be created"
    assert bc.readiness_score == 100
    assert bc.overall_status == "ready"
    assert bc.check_details == []
    print(f"[PASS] 11. No brief -> score=100, status=ready, no checks run")


def test_12_unauthorized_user_cannot_access_delivery_check(
    client, workspace_with_brief, creator_token, other_token
):
    """Non-member must receive 403 on the delivery-check endpoint."""
    file_data = _upload_mp4(client, workspace_with_brief, creator_token)
    file_id = file_data["id"]

    other_hdr = {"Authorization": f"Bearer {other_token}"}
    res = client.get(
        f"/api/workspaces/{workspace_with_brief}/deliverables/{file_id}/delivery-check",
        headers=other_hdr,
    )
    assert res.status_code == 403
    print(f"[PASS] 12. Unauthorized user gets 403 on delivery-check endpoint")
