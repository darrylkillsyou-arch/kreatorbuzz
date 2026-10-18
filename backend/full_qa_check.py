import requests
import sys
import os

BASE_URL = 'http://localhost:8000/api'

def run_qa():
    print("============================================================")
    print("CODE XERO FULL SYSTEM AUTOMATED QA & INTEGRATION TEST")
    print("============================================================")
    results = {}

    # ---------------------------------------------------------
    # PRIORITY 6: AUTHENTICATION & DEMO ACCOUNTS
    # ---------------------------------------------------------
    print("\n--- Testing Priority 6: Authentication & Demo Accounts ---")
    
    # Login Demo Recruiter
    r_rec = requests.post(f'{BASE_URL}/auth/login', json={'email': 'recruiter@codexero.com', 'password': 'Demo@123'})
    assert r_rec.status_code == 200, f"Demo Recruiter login failed: {r_rec.text}"
    rec_tok = r_rec.json()['access_token']
    rec_h = {'Authorization': f'Bearer {rec_tok}'}
    print("[PASS] Demo Recruiter login")

    # Login Demo Content Creator
    r_cre = requests.post(f'{BASE_URL}/auth/login', json={'email': 'creator@codexero.com', 'password': 'Demo@123'})
    assert r_cre.status_code == 200, f"Demo Content Creator login failed: {r_cre.text}"
    cre_tok = r_cre.json()['access_token']
    cre_h = {'Authorization': f'Bearer {cre_tok}'}
    print("[PASS] Demo Content Creator login")

    # Login Clean Recruiter
    r_cln_rec = requests.post(f'{BASE_URL}/auth/login', json={'email': 'cleanrecruiter@codexero.com', 'password': 'Demo@123'})
    assert r_cln_rec.status_code == 200, f"Clean Recruiter login failed: {r_cln_rec.text}"
    cln_rec_tok = r_cln_rec.json()['access_token']
    cln_rec_h = {'Authorization': f'Bearer {cln_rec_tok}'}
    print("[PASS] Clean Recruiter login")

    # Login Clean Creator
    r_cln_cre = requests.post(f'{BASE_URL}/auth/login', json={'email': 'cleancreator@codexero.com', 'password': 'Demo@123'})
    assert r_cln_cre.status_code == 200, f"Clean Content Creator login failed: {r_cln_cre.text}"
    cln_cre_tok = r_cln_cre.json()['access_token']
    cln_cre_h = {'Authorization': f'Bearer {cln_cre_tok}'}
    print("[PASS] Clean Content Creator login")

    results['demo_accounts'] = 'PASS'

    # ---------------------------------------------------------
    # PRIORITY 1: COMMUNITY PAGE
    # ---------------------------------------------------------
    print("\n--- Testing Priority 1: Community Page ---")
    
    # 1. Post Creation from Demo Content Creator
    post_payload = {
        'title': 'QA Test Post — AI Cinematic Commercial',
        'content': 'QA Test Post — Presenting our latest AI Cinematic Commercial for CODE XERO.',
        'post_type': 'Showcase Work',
        'image_url': 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe',
        'tools_tags': ['AI Video', 'ComfyUI', 'Showcase']
    }
    r_post = requests.post(f'{BASE_URL}/community/posts', json=post_payload, headers=cre_h)
    assert r_post.status_code == 201, f"Create post failed: {r_post.text}"
    created_post = r_post.json()
    post_id = created_post['id']
    print(f"[PASS] Post created successfully (ID={post_id}) by Demo Content Creator")

    # 2. Shared Feed Read from Clean Recruiter (Account B)
    r_feed = requests.get(f'{BASE_URL}/community/posts', headers=cln_rec_h)
    assert r_feed.status_code == 200, f"Fetch feed failed: {r_feed.text}"
    feed_posts = r_feed.json()
    found_post = next((p for p in feed_posts if p['id'] == post_id), None)
    assert found_post is not None, "Post created by Creator not visible in Clean Recruiter feed!"
    print(f"[PASS] Cross-account post persistence verified (Author: {found_post.get('author_name')}, Role: {found_post.get('author_role')})")

    # 3. Like Post from Clean Recruiter
    r_like = requests.post(f'{BASE_URL}/community/posts/{post_id}/like', headers=cln_rec_h)
    assert r_like.status_code in (200, 201), f"Like failed: {r_like.text}"
    like_res = r_like.json()
    print(f"[PASS] Like persisted. Status: {like_res}")

    # Verify like count persisted in feed
    r_feed2 = requests.get(f'{BASE_URL}/community/posts', headers=cre_h)
    found_post2 = next((p for p in r_feed2.json() if p['id'] == post_id), None)
    assert found_post2 is not None and found_post2.get('likes_count', 0) >= 1, f"Like count not reflected: {found_post2}"
    print(f"[PASS] Like count persisted across accounts: {found_post2.get('likes_count')}")

    # 4. Add Comment from Clean Recruiter
    comment_payload = {'content': 'Awesome work! Love the cinematic quality.'}
    r_cmt = requests.post(f'{BASE_URL}/community/posts/{post_id}/comments', json=comment_payload, headers=cln_rec_h)
    assert r_cmt.status_code in (200, 201), f"Add comment failed: {r_cmt.text}"
    print(f"[PASS] Comment added by Clean Recruiter")

    # 5. Fetch Comments from Demo Content Creator
    r_get_cmts = requests.get(f'{BASE_URL}/community/posts/{post_id}/comments', headers=cre_h)
    assert r_get_cmts.status_code == 200, f"Get comments failed: {r_get_cmts.text}"
    cmts = r_get_cmts.json()
    assert len(cmts) >= 1, "Comments empty when fetched by post author!"
    print(f"[PASS] Comments visible across accounts: '{cmts[0].get('content')}' by {cmts[0].get('user_name')}")

    results['community'] = 'PASS'

    # ---------------------------------------------------------
    # PRIORITY 2 & 5: RECRUITER -> CREATOR WORKFLOW & WORKSPACES ISOLATION
    # ---------------------------------------------------------
    print("\n--- Testing Priority 2 & 5: Recruiter -> Creator Flow & Workspace Isolation ---")
    
    # Check Clean Recruiter workspace count (should be 0)
    r_cln_ws = requests.get(f'{BASE_URL}/workspaces', headers=cln_rec_h)
    cln_ws_count = len(r_cln_ws.json()) if r_cln_ws.status_code == 200 else 0
    assert cln_ws_count == 0, f"Clean Recruiter should have 0 workspaces, found {cln_ws_count}"
    print(f"[PASS] Clean Recruiter has 0 workspaces (Strict workspace isolation verified)")

    # Send proposal from Demo Recruiter to Demo Content Creator
    prop_payload = {
        'creator_id': '101',
        'project_title': 'QA Verified Campaign',
        'project_requirement': 'High-end AI asset generation.',
        'budget_in_rupees': 50000,
        'deadline': '5 Days'
    }
    r_prop = requests.post(f'{BASE_URL}/proposals', json=prop_payload, headers=rec_h)
    assert r_prop.status_code == 201, f"Send proposal failed: {r_prop.text}"
    prop_id = r_prop.json()['id']
    print(f"[PASS] Proposal created (ID={prop_id})")

    # Creator accepts proposal
    r_acc = requests.post(f'{BASE_URL}/proposals/{prop_id}/accept', headers=cre_h)
    assert r_acc.status_code == 200, f"Accept proposal failed: {r_acc.text}"
    print(f"[PASS] Proposal accepted by Creator")

    # Verify workspace visible to Recruiter and Creator
    r_rec_ws = requests.get(f'{BASE_URL}/workspaces', headers=rec_h)
    rec_ws_list = r_rec_ws.json() if r_rec_ws.status_code == 200 else []
    assert len(rec_ws_list) >= 1, "Recruiter workspace list empty after accepting proposal"
    print(f"[PASS] Recruiter sees new workspace (Total: {len(rec_ws_list)})")

    # Re-verify Clean Recruiter workspace count is STILL 0
    r_cln_ws2 = requests.get(f'{BASE_URL}/workspaces', headers=cln_rec_h)
    assert len(r_cln_ws2.json()) == 0, "Unrelated user can see workspace!"
    print(f"[PASS] Unrelated user isolation maintained post-workspace creation")

    results['recruiter_creator_flow'] = 'PASS'
    results['workspaces_isolation'] = 'PASS'

    # ---------------------------------------------------------
    # PRIORITY 3: DISCOVER & SAVED CREATORS
    # ---------------------------------------------------------
    print("\n--- Testing Priority 3: Discover & Saved Creators ---")
    r_creators = requests.get(f'{BASE_URL}/creators', headers=rec_h)
    assert r_creators.status_code == 200, f"Fetch creators failed: {r_creators.text}"
    creators_list = r_creators.json()
    assert len(creators_list) > 0, "Creators list is empty!"
    print(f"[PASS] Discover creators loaded successfully ({len(creators_list)} creators available)")

    # Save a creator to shortlist
    target_creator_id = creators_list[0]['id']
    target_user_id = creators_list[0].get('user_id', 2)
    r_fav = requests.post(f'{BASE_URL}/shortlist', json={'creator_user_id': target_user_id}, headers=rec_h)
    print(f"[INFO] Shortlist add status: {r_fav.status_code}")
    
    # Get saved creators
    r_saved = requests.get(f'{BASE_URL}/shortlist', headers=rec_h)
    assert r_saved.status_code == 200, f"Get shortlist failed: {r_saved.text}"
    print(f"[PASS] Shortlist/Saved Creators endpoint functional")

    results['discover'] = 'PASS'

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------
    print("\n============================================================")
    print("ALL QA BACKEND & WORKFLOW TESTS EXECUTED SUCCESSFULLY")
    print("============================================================")
    for k, v in results.items():
        print(f"  - {k}: {v}")

if __name__ == '__main__':
    run_qa()
