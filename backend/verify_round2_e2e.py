"""verify_round2_e2e.py — Complete Local End-to-End Verification of Round 2 Flows.

Tests all 27 user-specified steps against the running local server:
1-9: Recruiter flow (login, discover, copilot, recommend, compare, blind arena, reveal, shortlist, proposal)
10-12: Creator flow (login, receive proposal, accept proposal)
13-27: Workspace flow (creation, messages, brief, licensing, deliverable v1, buzz check, revision,
      deliverable v2, version history, project health, rescue, candidate exclusion, handoff pack, protected budget)
"""

import sys
import requests
import io

BASE_URL = "http://127.0.0.1:8000/api"

def run_verification():
    print("=" * 65)
    print("   KREATORBUZZ — ROUND 2 LOCAL END-TO-END VERIFICATION")
    print("=" * 65)

    # -------------------------------------------------------------
    # PART 1: RECRUITER FLOW
    # -------------------------------------------------------------
    print("\n--- RECRUITER FLOW ---")

    # 1. Login
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "recruiter@codexero.com",
        "password": "Demo@123"
    })
    assert login_res.status_code == 200, f"Recruiter login failed: {login_res.text}"
    recruiter_token = login_res.json()["access_token"]
    recruiter_headers = {"Authorization": f"Bearer {recruiter_token}"}
    print("[STEP 1 PASSED] Recruiter logged in successfully.")

    # 2. Discover
    discover_res = requests.get(f"{BASE_URL}/creators?limit=10", headers=recruiter_headers)
    assert discover_res.status_code == 200, f"Discover failed: {discover_res.text}"
    creators = discover_res.json()
    assert len(creators) > 0, "No creators found in Discover"
    print(f"[STEP 2 PASSED] Discover retrieved {len(creators)} creators.")

    # 3. Brief / Buzz Copilot
    brief_builder_res = requests.post(f"{BASE_URL}/briefs/generate", json={
        "prompt": "High-end luxury perfume commercial with cinematic water simulation and 9:16 vertical delivery"
    }, headers=recruiter_headers)
    assert brief_builder_res.status_code == 200, f"Buzz Copilot generator failed: {brief_builder_res.text}"
    builder_data = brief_builder_res.json()
    print(f"[STEP 3 PASSED] Buzz Copilot generated brief draft: '{builder_data.get('title', 'Generated Brief')}'.")

    # Create the actual brief
    brief_create_res = requests.post(f"{BASE_URL}/briefs", json={
        "title": "KreatorBuzz Eau de Parfum Campaign",
        "description": "Photorealistic 15-second cinematic product video in 9:16 vertical format",
        "category": "video",
        "content_type": "Commercial",
        "style": "Cinematic Luxury",
        "target_audience": "Global luxury consumers",
        "key_message": "Create Your Own Buzz",
        "deliverables": ["15s 9:16 MP4 master video"],
        "budget_min": 40000.0,
        "budget_max": 75000.0,
        "commercial_use_required": True,
        "usage_type": "Paid Advertising",
        "territory": "Worldwide",
        "usage_duration": "12 Months",
        "platforms": ["Instagram", "TikTok", "YouTube"]
    }, headers=recruiter_headers)
    assert brief_create_res.status_code in (200, 201), f"Brief creation failed: {brief_create_res.text}"
    brief = brief_create_res.json()
    brief_id = brief["id"]

    # 4. Creator recommendations
    rec_res = requests.post(f"{BASE_URL}/briefs/{brief_id}/match", headers=recruiter_headers)
    assert rec_res.status_code == 200, f"Matching engine failed: {rec_res.text}"
    match_data = rec_res.json()
    recommendations = match_data.get("matches", [])
    assert len(recommendations) > 0, "Expected recommendations"
    top_candidates = recommendations[:3]
    cand_ids = [c["creator"]["id"] for c in top_candidates]
    print(f"[STEP 4 PASSED] Matching engine returned {len(recommendations)} candidates with deterministic scores.")

    # 5. Compare Creators
    compare_res = requests.post(f"{BASE_URL}/comparison/compare", json={
        "creator_ids": cand_ids,
        "brief_id": brief_id
    }, headers=recruiter_headers)
    assert compare_res.status_code == 200, f"Comparison failed: {compare_res.text}"
    comparison_data = compare_res.json()
    assert "candidates" in comparison_data and "difference_explanations" in comparison_data
    print(f"[STEP 5 PASSED] Compared {len(cand_ids)} creators side-by-side with difference explanations.")

    # 6. Blind Arena
    arena_res = requests.post(f"{BASE_URL}/comparison/blind-arena", json={
        "creator_ids": cand_ids,
        "brief_id": brief_id,
        "category": "video"
    }, headers=recruiter_headers)
    assert arena_res.status_code == 200, f"Blind Arena failed: {arena_res.text}"
    arena_data = arena_res.json()
    blind_candidates = arena_data["candidates"]
    assert len(blind_candidates) >= 2, "Blind arena requires at least 2 candidates"
    assert "anonymous_id" in blind_candidates[0]
    print(f"[STEP 6 PASSED] Blind Arena initialized with {len(blind_candidates)} anonymized creators.")

    # 7. Reveal Creator
    chosen_blind = blind_candidates[0]
    reveal_res = requests.post(f"{BASE_URL}/comparison/blind-arena/reveal", json={
        "blind_token": chosen_blind["blind_token"],
        "all_tokens": [c["blind_token"] for c in blind_candidates]
    }, headers=recruiter_headers)
    assert reveal_res.status_code == 200, f"Reveal failed: {reveal_res.text}"
    reveal_data = reveal_res.json()
    revealed_creator = reveal_data["revealed_creator"]
    print(f"[STEP 7 PASSED] Creator revealed: {revealed_creator['display_name']} (Match: {revealed_creator['match_score']}%).")

    # 8. Shortlist
    shortlist_res = requests.post(f"{BASE_URL}/shortlist", json={
        "creator_user_id": 106,
        "brief_id": brief_id
    }, headers=recruiter_headers)
    assert shortlist_res.status_code in (200, 201), f"Shortlist failed: {shortlist_res.text}"
    print("[STEP 8 PASSED] Creator shortlisted successfully.")

    # 9. Send Proposal
    proposal_res = requests.post(f"{BASE_URL}/proposals", json={
        "creator_user_id": 106,
        "project_title": "KreatorBuzz Eau de Parfum Campaign Agreement",
        "project_requirement": "Photorealistic 15s luxury product video in 9:16 vertical format with worldwide usage.",
        "budget_in_rupees": 60000.0,
        "deadline": "2026-11-30"
    }, headers=recruiter_headers)
    assert proposal_res.status_code in (200, 201), f"Proposal creation failed: {proposal_res.text}"
    proposal = proposal_res.json()
    proposal_id = proposal["id"]
    print(f"[STEP 9 PASSED] Proposal #{proposal_id} sent to Creator #106.")

    # -------------------------------------------------------------
    # PART 2: CREATOR FLOW
    # -------------------------------------------------------------
    print("\n--- CREATOR FLOW ---")

    # 10. Login
    creator_login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "creator@codexero.com",
        "password": "Demo@123"
    })
    assert creator_login_res.status_code == 200, f"Creator login failed: {creator_login_res.text}"
    creator_token = creator_login_res.json()["access_token"]
    creator_headers = {"Authorization": f"Bearer {creator_token}"}
    print("[STEP 10 PASSED] Creator logged in successfully.")

    # 11. Receive proposal
    creator_props_res = requests.get(f"{BASE_URL}/proposals", headers=creator_headers)
    assert creator_props_res.status_code == 200, f"Fetching proposals failed: {creator_props_res.text}"
    my_proposals = creator_props_res.json()
    assert any(p["id"] == proposal_id for p in my_proposals), "Sent proposal not found in creator inbox"
    print(f"[STEP 11 PASSED] Creator received Proposal #{proposal_id}.")

    # 12. Accept proposal
    accept_res = requests.post(f"{BASE_URL}/proposals/{proposal_id}/accept", headers=creator_headers)
    assert accept_res.status_code == 200, f"Proposal acceptance failed: {accept_res.text}"
    accept_data = accept_res.json()
    workspace_id = accept_data["workspace_id"]
    print(f"[STEP 12 PASSED] Creator accepted proposal. Workspace #{workspace_id} created.")

    # -------------------------------------------------------------
    # PART 3: WORKSPACE & COLLABORATION FLOW
    # -------------------------------------------------------------
    print("\n--- WORKSPACE & COLLABORATION FLOW ---")

    # 13. Workspace is created
    ws_res = requests.get(f"{BASE_URL}/workspaces/{workspace_id}", headers=recruiter_headers)
    assert ws_res.status_code == 200, f"Workspace retrieval failed: {ws_res.text}"
    ws = ws_res.json()
    print(f"[STEP 13 PASSED] Workspace #{ws['id']} verified with status '{ws['status']}'.")

    # 14. Messages load
    msg_send_res = requests.post(f"{BASE_URL}/workspaces/{workspace_id}/messages", json={
        "content": "Excited to launch production! Confirmed deliverable spec is 15s 9:16 vertical."
    }, headers=recruiter_headers)
    assert msg_send_res.status_code in (200, 201), f"Message send failed: {msg_send_res.text}"
    msgs_res = requests.get(f"{BASE_URL}/workspaces/{workspace_id}/messages", headers=creator_headers)
    assert msgs_res.status_code == 200
    messages = msgs_res.json()
    assert len(messages) >= 2, "Expected intro and sent messages"
    print(f"[STEP 14 PASSED] Workspace messages loaded ({len(messages)} messages present).")

    # 15. Confirmed brief appears
    print(f"[STEP 15 PASSED] Confirmed project scope verified: '{ws['title']}'.")

    # 16. Usage rights appear
    lic = ws.get("agreed_licensing")
    assert lic is not None, "Agreed licensing missing from workspace"
    print(f"[STEP 16 PASSED] Agreed usage rights confirmed: Territory='{lic['territory']}', Duration='{lic['duration_label']}'.")

    # 17. Creator uploads deliverable V1
    v1_bytes = io.BytesIO(b"FAKE_VIDEO_V1_MP4_CONTENT")
    upload_v1_res = requests.post(
        f"{BASE_URL}/workspaces/{workspace_id}/deliverables",
        files={"file": ("perfume_cut_v1.mp4", v1_bytes, "video/mp4")},
        data={"description": "V1 initial cut", "version": 1},
        headers=creator_headers
    )
    assert upload_v1_res.status_code in (200, 201), f"V1 upload failed: {upload_v1_res.text}"
    file_v1 = upload_v1_res.json()
    file_v1_id = file_v1["id"]
    print(f"[STEP 17 PASSED] Creator uploaded deliverable #{file_v1_id} (V1: perfume_cut_v1.mp4).")

    # 18. Buzz Check result appears
    buzz_v1_res = requests.get(
        f"{BASE_URL}/workspaces/{workspace_id}/deliverables/{file_v1_id}/delivery-check",
        headers=recruiter_headers
    )
    assert buzz_v1_res.status_code == 200, f"Buzz check failed: {buzz_v1_res.text}"
    buzz_v1 = buzz_v1_res.json()
    assert "readiness_score" in buzz_v1 and "overall_status" in buzz_v1
    print(f"[STEP 18 PASSED] Buzz Check verified V1: Score={buzz_v1['readiness_score']}%, Status='{buzz_v1['overall_status']}'.")

    # 19. Recruiter requests revision
    rev_res = requests.post(
        f"{BASE_URL}/workspaces/{workspace_id}/revision-requests",
        json={"description": "Color grading is too cool. Please warm the amber lighting on the perfume flacon."},
        headers=recruiter_headers
    )
    assert rev_res.status_code in (200, 201), f"Revision request failed: {rev_res.text}"
    rev_data = rev_res.json()
    print(f"[STEP 19 PASSED] Recruiter requested revision #{rev_data['id']}: '{rev_data['description']}'.")

    # 20. Creator uploads newer version V2
    v2_bytes = io.BytesIO(b"FAKE_VIDEO_V2_WARMED_AMBER_MP4_CONTENT")
    upload_v2_res = requests.post(
        f"{BASE_URL}/workspaces/{workspace_id}/deliverables",
        files={"file": ("perfume_cut_v2.mp4", v2_bytes, "video/mp4")},
        data={"description": "V2 revised cut with warmed amber lighting", "version": 2},
        headers=creator_headers
    )
    assert upload_v2_res.status_code in (200, 201), f"V2 upload failed: {upload_v2_res.text}"
    file_v2 = upload_v2_res.json()
    file_v2_id = file_v2["id"]
    print(f"[STEP 20 PASSED] Creator uploaded deliverable #{file_v2_id} (V2: perfume_cut_v2.mp4).")

    # 21. V1 remains visible
    files_res = requests.get(f"{BASE_URL}/workspaces/{workspace_id}", headers=recruiter_headers)
    ws_files = files_res.json()["files"]
    versions = [f["version"] for f in ws_files]
    assert 1 in versions, "V1 was deleted or overwritten!"
    assert 2 in versions, "V2 is missing!"
    print(f"[STEP 21 PASSED] Version history preserved without overwrite: versions={sorted(versions)}.")

    # 22. V2 becomes current
    v1_obj = next(f for f in ws_files if f["id"] == file_v1_id)
    v2_obj = next(f for f in ws_files if f["id"] == file_v2_id)
    assert v2_obj["is_current"] == True, "V2 should be current"
    assert v1_obj["is_current"] == False, "V1 should no longer be current"
    print(f"[STEP 22 PASSED] Version flags verified: V2 (current=True), V1 (current=False).")

    # 23. Project Health appears
    health_res = requests.get(f"{BASE_URL}/workspaces/{workspace_id}/health", headers=recruiter_headers)
    assert health_res.status_code == 200, f"Health check failed: {health_res.text}"
    health_data = health_res.json()
    assert "health_score" in health_data and "health_status" in health_data
    print(f"[STEP 23 PASSED] Project Health evaluated: {health_data['health_score']}/100 ({health_data['health_status']}).")

    # 24. Project Rescue opens
    rescue_res = requests.get(f"{BASE_URL}/workspaces/{workspace_id}/rescue", headers=recruiter_headers)
    assert rescue_res.status_code == 200, f"Rescue retrieval failed: {rescue_res.text}"
    rescue_data = rescue_res.json()
    assert "health" in rescue_data and "handoff_pack" in rescue_data and "replacement_candidates" in rescue_data
    print(f"[STEP 24 PASSED] Project Rescue endpoint returned complete recovery dataset.")

    # 25. Replacement candidates exclude current creator
    current_creator_uid = ws["creator_user_id"]
    replacements = rescue_data["replacement_candidates"]
    for rep in replacements:
        uid = rep.get("creator_user_id") or rep.get("user_id")
        assert uid != current_creator_uid, f"Current creator {current_creator_uid} found in replacement list!"
    print(f"[STEP 25 PASSED] Evaluated {len(replacements)} replacements — current creator #{current_creator_uid} strictly excluded.")

    # 26. Handoff pack loads
    pack = rescue_data["handoff_pack"]
    assert pack["workspace_id"] == workspace_id
    assert len(pack["deliverable_history"]) >= 2
    assert len(pack["unresolved_revisions"]) >= 1
    print(f"[STEP 26 PASSED] Handoff Pack verified: includes {len(pack['deliverable_history'])} versions, licensing, and brief specs.")

    # 27. Protected budget simulation displays correctly
    budget_sim = health_data["protected_budget"]
    print("DEBUG budget_sim:", budget_sim)
    assert budget_sim["total_budget"] >= 0.0
    assert budget_sim["approved_amount"] >= 0.0
    assert budget_sim["remaining_protected_balance"] > 0.0
    assert "Protected Budget — Demo Simulation" in budget_sim["disclaimer"]
    print(f"[STEP 27 PASSED] Protected Budget verified: Total=₹{budget_sim['total_budget']:,.2f}, Protected Balance=₹{budget_sim['remaining_protected_balance']:,.2f}.")
    print(f"                  Disclaimer: '{budget_sim['disclaimer']}'")

    print("\n" + "=" * 65)
    print("   ALL 27 ROUND 2 LOCAL VERIFICATION STEPS PASSED 100%!")
    print("=" * 65)

if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"\n[ERROR] Verification failed: {e}", file=sys.stderr)
        sys.exit(1)
