import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_full_demo_journey():
    print("=== Step 1: Brand Login ===")
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "brand@maccall.demo",
        "password": "demo1234"
    })
    assert res.status_code in (200, 201), f"Login failed: {res.text}"
    auth_data = res.json()
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[OK] Logged in as: {auth_data['user']['full_name']} (Role: {auth_data['user']['role']})")

    print("\n=== Step 2: Generate Brief via AI Synthesizer ===")
    prompt = "I need a 30-second cinematic product launch video for a luxury automotive brand. Neo-brutalist architecture, dusk illumination, high-fashion silhouettes."
    res = requests.post(f"{BASE_URL}/briefs/generate", json={"prompt": prompt})
    assert res.status_code in (200, 201), f"Brief generation failed: {res.text}"
    gen_data = res.json()
    print(f"[OK] AI Generated Brief Title: {gen_data['title']}")
    print(f"  Visual Style: {gen_data['style']}")
    print(f"  Content Type: {gen_data['content_type']}")
    print(f"  Estimated Budget: ${gen_data['budget_min']} - ${gen_data['budget_max']}")

    print("\n=== Step 3: Save the Generated Brief ===")
    brief_payload = {
        "title": gen_data["title"],
        "description": "Generated from natural language prompt concierge",
        "prompt_text": prompt,
        "content_type": gen_data["content_type"],
        "style": gen_data["style"],
        "target_audience": gen_data.get("target_audience", "Global Luxury Connoisseurs"),
        "platform": gen_data.get("platform", ["Digital Billboard", "Instagram Reels", "YouTube & Web"]),
        "duration": gen_data.get("duration", "30s"),
        "aspect_ratio": gen_data.get("aspect_ratio", "16:9"),
        "deliverables": gen_data.get("deliverables", ["1x 30s Master Cut", "3x 10s Social Platform Cuts", "8x High-Res Still Key Visuals"]),
        "tools_suggested": gen_data.get("tools_suggested", ["Runway Gen-3", "Kling AI", "Premiere Pro"]),
        "budget_min": gen_data.get("budget_min", 3500),
        "budget_max": gen_data.get("budget_max", 6000),
        "commercial_rights_required": True,
        "visual_reference_url": gen_data.get("visual_reference_url", "")
    }
    res = requests.post(f"{BASE_URL}/briefs", json=brief_payload, headers=headers)
    assert res.status_code in (200, 201), f"Save brief failed: {res.text}"
    saved_brief = res.json()
    brief_id = saved_brief["id"]
    print(f"[OK] Brief saved with ID: {brief_id}")

    print("\n=== Step 4: Receive Intelligent Creator Matches ===")
    res = requests.post(f"{BASE_URL}/briefs/{brief_id}/match-creators", headers=headers)
    assert res.status_code in (200, 201), f"Matching failed: {res.text}"
    match_resp = res.json()
    matches_list = match_resp.get("matches", [])
    print(f"[OK] Total Matched Creators: {len(matches_list)}")
    for m in matches_list[:3]:
        creator = m["creator"]
        print(f"  - {creator['display_name']}: MatchScore = {m['match_score']}% | Reasons: {', '.join(m['match_reasons'])}")
    
    top_creator_profile = matches_list[0]["creator"]
    creator_id = top_creator_profile["id"]

    print("\n=== Step 5: Open Creator Profile Folio ===")
    res = requests.get(f"{BASE_URL}/creators/{creator_id}")
    assert res.status_code in (200, 201), f"Get creator failed: {res.text}"
    creator_profile = res.json()
    print(f"[OK] Creator: {creator_profile['display_name']} | SLA: {creator_profile['sla_score']}% | Rating: {creator_profile['rating']}/5.0")

    print("\n=== Step 6: Shortlist & Hire Creator (Auto-create Workspace) ===")
    res = requests.post(f"{BASE_URL}/shortlist", json={
        "creator_user_id": creator_profile["user_id"],
        "brief_id": brief_id
    }, headers=headers)
    assert res.status_code in (200, 201), f"Shortlist failed: {res.text}"
    shortlist_entry = res.json()
    print(f"[OK] Creator shortlisted (ID: {shortlist_entry['id']})")

    res = requests.post(f"{BASE_URL}/shortlist/{shortlist_entry['id']}/hire", json={}, headers=headers)
    assert res.status_code in (200, 201), f"Hire failed: {res.text}"
    workspace_data = res.json()
    workspace_id = workspace_data["id"]
    print(f"[OK] Commission initiated! Dedicated Workspace ID: {workspace_id} (Status: {workspace_data['status']})")

    print("\n=== Step 7: Send Encrypted Message in Workspace ===")
    res = requests.post(f"{BASE_URL}/workspaces/{workspace_id}/messages", json={
        "content": "Welcome to the production vault! Looking forward to the 4K master cuts."
    }, headers=headers)
    assert res.status_code in (200, 201), f"Send message failed: {res.text}"
    print(f"[OK] Sent encrypted message to workspace.")

    res = requests.get(f"{BASE_URL}/workspaces/{workspace_id}/messages", headers=headers)
    assert res.status_code in (200, 201), f"Get messages failed: {res.text}"
    messages = res.json()
    print(f"[OK] Retrieved & decrypted {len(messages)} message(s). Latest: '{messages[-1]['content']}'")

    print("\n=== Step 8: Update Milestone / Request Revision ===")
    # Check workspace milestones
    res = requests.get(f"{BASE_URL}/workspaces/{workspace_id}", headers=headers)
    assert res.status_code in (200, 201), f"Get workspace failed: {res.text}"
    ws_detail = res.json()
    if ws_detail["milestones"]:
        milestone = ws_detail["milestones"][0]
        res = requests.put(f"{BASE_URL}/workspaces/{workspace_id}/milestones/{milestone['id']}", json={
            "status": "in_review"
        }, headers=headers)
        assert res.status_code in (200, 201), f"Update milestone failed: {res.text}"
        print(f"[OK] Updated milestone '{milestone['title']}' to status: in_review")

    print("\n=== Step 9: Visit Community Salon & Interact ===")
    res = requests.get(f"{BASE_URL}/community/posts")
    assert res.status_code in (200, 201), f"Get posts failed: {res.text}"
    posts = res.json()
    print(f"[OK] Loaded {len(posts)} Salon dispatches.")
    
    first_post = posts[0]
    post_id = first_post["id"]
    print(f"  Post #1: '{first_post['title']}' by {first_post['author']['full_name']}")

    # Like post
    res = requests.post(f"{BASE_URL}/community/posts/{post_id}/like", headers=headers)
    assert res.status_code in (200, 201), f"Like failed: {res.text}"
    print(f"[OK] Toggled like on post #{post_id} (Liked: {res.json()['liked']})")

    # Comment on post
    res = requests.post(f"{BASE_URL}/community/posts/{post_id}/comment", json={
        "content": "Stunning volumetric organza lighting. How was the prompt iteration tuned?"
    }, headers=headers)
    assert res.status_code in (200, 201), f"Comment failed: {res.text}"
    print(f"[OK] Added editorial comment to discussion thread.")

    print("\n=== Step 10: View Verified Leaderboard ===")
    res = requests.get(f"{BASE_URL}/leaderboard")
    assert res.status_code in (200, 201), f"Leaderboard failed: {res.text}"
    lb_data = res.json()
    print(f"[OK] Total Ranked Leaderboard Entries: {len(lb_data)}")
    for entry in lb_data[:3]:
        creator = entry.get("creator", {})
        print(f"  - Category: {entry['category']} | Creator: {creator.get('display_name')} | Score: {entry['score']}")

    print("\n==========================================")
    print("SUCCESS: ALL 10 STEPS OF THE DEMO JOURNEY PASSED")
    print("==========================================")

if __name__ == "__main__":
    test_full_demo_journey()
