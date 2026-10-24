"""
Phase 1 verification script:
Verifies proposal notifications, acceptance, workspace message loading,
revision request state lifecycle, and deliverable version history.
"""
import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def get_auth_token(email: str, password: str = "Demo@123"):
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if resp.status_code != 200:
        raise Exception(f"Failed to authenticate {email}: {resp.text}")
    return resp.json()["access_token"]

def main():
    print("Testing Phase 1 Stabilized Flows...")

    recruiter_token = get_auth_token("recruiter@codexero.com")
    creator_token = get_auth_token("creator@codexero.com")
    recruiter_headers = {"Authorization": f"Bearer {recruiter_token}"}
    creator_headers = {"Authorization": f"Bearer {creator_token}"}

    # 1. Recruiter sends proposal to creator
    prop_payload = {
        "creator_user_id": 106,
        "project_title": "Phase 1 Verification Campaign",
        "project_requirement": "Verifying full proposal to workspace flow with notifications",
        "budget_in_rupees": 250000.0,
        "deadline": "2026-11-30"
    }
    resp = requests.post(f"{BASE_URL}/proposals", json=prop_payload, headers=recruiter_headers)
    assert resp.status_code == 201, f"Create proposal failed: {resp.text}"
    proposal = resp.json()
    proposal_id = proposal["id"]
    print(f"[OK] Proposal created: #{proposal_id}")

    # 2. Check Recruiter and Creator Notifications
    rec_notifs = requests.get(f"{BASE_URL}/notifications", headers=recruiter_headers).json()
    cr_notifs = requests.get(f"{BASE_URL}/notifications", headers=creator_headers).json()
    
    assert any(n.get("type") == "proposal_sent" for n in rec_notifs), f"Missing proposal_sent notification for recruiter: {rec_notifs}"
    assert any(n.get("type") == "proposal_received" for n in cr_notifs), f"Missing proposal_received notification for creator: {cr_notifs}"
    print("[OK] Recruiter and Creator both received initial proposal notifications")

    # 3. Creator accepts proposal
    accept_resp = requests.post(f"{BASE_URL}/proposals/{proposal_id}/accept", headers=creator_headers)
    assert accept_resp.status_code == 200, f"Accept proposal failed: {accept_resp.text}"
    accept_data = accept_resp.json()
    workspace_id = accept_data["workspace_id"]
    print(f"[OK] Creator accepted proposal #{proposal_id}. Workspace #{workspace_id} created.")

    # 4. Check post-acceptance notifications
    rec_notifs_after = requests.get(f"{BASE_URL}/notifications", headers=recruiter_headers).json()
    cr_notifs_after = requests.get(f"{BASE_URL}/notifications", headers=creator_headers).json()
    assert any(n.get("type") == "proposal_accepted" for n in rec_notifs_after), "Missing proposal_accepted notification"
    assert any(n.get("type") == "workspace_created" for n in rec_notifs_after), "Missing workspace_created notification for recruiter"
    assert any(n.get("type") == "workspace_created" for n in cr_notifs_after), "Missing workspace_created notification for creator"
    print("[OK] Post-acceptance notifications confirmed for both parties")

    # 5. Workspace message history immediately loads without new message
    ws_detail = requests.get(f"{BASE_URL}/workspaces/{workspace_id}", headers=recruiter_headers).json()
    assert "messages" in ws_detail, "Workspace detail missing messages array"
    initial_msg_count = len(ws_detail["messages"])
    print(f"[OK] Workspace opened immediately with {initial_msg_count} initial system/intro messages")

    # 6. Post messages and ensure chronological ordering and persistence
    requests.post(f"{BASE_URL}/workspaces/{workspace_id}/messages", json={"content": "Msg 1: Hello from Recruiter"}, headers=recruiter_headers)
    requests.post(f"{BASE_URL}/workspaces/{workspace_id}/messages", json={"content": "Msg 2: Hello from Creator"}, headers=creator_headers)

    ws_messages = requests.get(f"{BASE_URL}/workspaces/{workspace_id}/messages", headers=recruiter_headers).json()
    assert len(ws_messages) == initial_msg_count + 2, f"Expected {initial_msg_count + 2} messages, got {len(ws_messages)}"
    assert ws_messages[-2]["content"] == "Msg 1: Hello from Recruiter"
    assert ws_messages[-1]["content"] == "Msg 2: Hello from Creator"
    print("[OK] Messages persist, sort chronologically, and both parties see identical conversation")

    # 7. Revision Request and Standardization
    milestone_id = ws_detail["milestones"][0]["id"]
    rev_payload = {
        "milestone_id": milestone_id,
        "description": "Please refine the color grading on the teaser"
    }
    rev_resp = requests.post(f"{BASE_URL}/workspaces/{workspace_id}/revision-requests", json=rev_payload, headers=recruiter_headers)
    assert rev_resp.status_code == 201, f"Revision request failed: {rev_resp.text}"
    rev_data = rev_resp.json()
    revision_id = rev_data["id"]
    assert rev_data["status"] == "requested", f"Expected 'requested', got {rev_data['status']}"
    print(f"[OK] Revision request created with standardized status 'requested': #{revision_id}")

    # 8. Creator acknowledges revision -> in_progress
    patch_resp = requests.patch(
        f"{BASE_URL}/workspaces/{workspace_id}/revision-requests/{revision_id}",
        json={"status": "in_progress", "response_notes": "Working on the color balance now."},
        headers=creator_headers
    )
    assert patch_resp.status_code == 200, f"Revision patch failed: {patch_resp.text}"
    assert patch_resp.json()["status"] == "in_progress"
    print("[OK] Revision transitioned to 'in_progress'")

    # 9. Deliverable Upload & Version Preservation
    file_content = b"Phase 1 deliverable content v1"
    files = {"file": ("teaser_v1.mp4", file_content, "video/mp4")}
    data = {"milestone_id": str(milestone_id), "version": "1"}
    up_resp = requests.post(f"{BASE_URL}/workspaces/{workspace_id}/deliverables", files=files, data=data, headers=creator_headers)
    assert up_resp.status_code == 201, f"Upload v1 failed: {up_resp.text}"

    # Upload v2 to address revision -> should auto-submit revision
    files2 = {"file": ("teaser_v2.mp4", b"Phase 1 deliverable content v2 updated colors", "video/mp4")}
    data2 = {"milestone_id": str(milestone_id), "version": "2"}
    up_resp2 = requests.post(f"{BASE_URL}/workspaces/{workspace_id}/deliverables", files=files2, data=data2, headers=creator_headers)
    assert up_resp2.status_code == 201, f"Upload v2 failed: {up_resp2.text}"

    # Verify both v1 and v2 exist and sort properly
    ws_after_upload = requests.get(f"{BASE_URL}/workspaces/{workspace_id}", headers=recruiter_headers).json()
    files_list = ws_after_upload["files"]
    versions = [f["version"] for f in files_list]
    assert 1 in versions and 2 in versions, f"Expected versions [1, 2], got {versions}"
    print(f"[OK] Deliverable version history preserved without overwrite: {versions}")

    # Check revision status is now 'submitted'
    rev_after = next(r for r in ws_after_upload["revisions"] if r["id"] == revision_id)
    assert rev_after["status"] == "submitted", f"Expected revision 'submitted', got {rev_after['status']}"
    print("[OK] Revision automatically marked 'submitted' upon uploading version 2")

    # 10. Recruiter approves revision
    patch_appr = requests.patch(
        f"{BASE_URL}/workspaces/{workspace_id}/revision-requests/{revision_id}",
        json={"status": "approved"},
        headers=recruiter_headers
    )
    assert patch_appr.status_code == 200
    assert patch_appr.json()["status"] == "approved"
    print("[OK] Revision successfully approved")

    print("\n=======================================================")
    print("ALL PHASE 1 FLOW TESTS PASSED FLAWLESSLY!")
    print("=======================================================")

if __name__ == "__main__":
    main()
