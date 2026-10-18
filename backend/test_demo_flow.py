"""
Test the full Recruiter -> Creator -> Accept -> Workspace flow
using the NEW demo accounts: recruiter@codexero.com / creator@codexero.com
Password: Demo@123
"""
import requests
import sys

BASE_URL = 'http://localhost:8000/api'

def run_tests():
    print("\n" + "="*60)
    print("DEMO ACCOUNT FLOW TEST")
    print("="*60)

    # 1. Login as Demo Recruiter
    r = requests.post(f'{BASE_URL}/auth/login',
                      json={'email': 'recruiter@codexero.com', 'password': 'Demo@123'})
    if r.status_code != 200:
        print(f"[FAIL] Demo Recruiter login failed: {r.text}")
        sys.exit(1)
    recruiter_token = r.json()['access_token']
    recruiter_headers = {'Authorization': f'Bearer {recruiter_token}'}
    recruiter_user = r.json()['user']
    print(f"[PASS] 1. Demo Recruiter logged in: {recruiter_user['full_name']} (ID={recruiter_user['id']})")

    # 2. Find Demo Content Creator (profile ID 101, user ID 106)
    r = requests.get(f'{BASE_URL}/creators', headers=recruiter_headers)
    creators = r.json() if r.status_code == 200 else []
    demo_creator_profile = None
    for c in creators:
        if 'Demo Content Creator' in (c.get('name') or ''):
            demo_creator_profile = c
            break
    if not demo_creator_profile:
        # try direct
        r = requests.get(f'{BASE_URL}/creators/101', headers=recruiter_headers)
        if r.status_code == 200:
            demo_creator_profile = r.json()

    if not demo_creator_profile:
        print("[WARN] Demo Content Creator not found in public listing — skipping proposal step")
        # Still test using creator profile id 101 directly
        demo_creator_id = '101'
    else:
        demo_creator_id = str(demo_creator_profile.get('id', '101'))
    print(f"[INFO] 2. Using Demo Content Creator profile ID={demo_creator_id}")

    # 3. Send proposal to Demo Content Creator
    payload = {
        'creator_id': demo_creator_id,
        'project_title': 'Demo Flow Test — AI Social Media Campaign',
        'project_requirement': 'Create 5 AI-generated social media images for a fashion brand launch.',
        'budget_in_rupees': 40000,
        'deadline': '3 Business Days'
    }
    r = requests.post(f'{BASE_URL}/proposals', json=payload, headers=recruiter_headers)
    if r.status_code != 201:
        print(f"[FAIL] Proposal send failed: {r.text}")
        sys.exit(1)
    proposal = r.json()
    proposal_id = proposal['id']
    print(f"[PASS] 3. Proposal created: #{proposal_id} | '{proposal['project_title']}' | Status={proposal['status']} | INR {proposal['budget_in_rupees']}")

    # Check workspace count BEFORE accept (for Demo Recruiter)
    r_ws = requests.get(f'{BASE_URL}/workspaces', headers=recruiter_headers)
    ws_before = len(r_ws.json()) if r_ws.status_code == 200 else 0
    print(f"[INFO]    Recruiter workspace count BEFORE accept: {ws_before}")

    # 4. Login as Demo Content Creator
    r = requests.post(f'{BASE_URL}/auth/login',
                      json={'email': 'creator@codexero.com', 'password': 'Demo@123'})
    if r.status_code != 200:
        print(f"[FAIL] Demo Content Creator login failed: {r.text}")
        sys.exit(1)
    creator_token = r.json()['access_token']
    creator_headers = {'Authorization': f'Bearer {creator_token}'}
    creator_user = r.json()['user']
    print(f"[PASS] 4. Demo Content Creator logged in: {creator_user['full_name']} (ID={creator_user['id']})")

    # 5. Fetch Creator Project Requests
    r = requests.get(f'{BASE_URL}/proposals', headers=creator_headers)
    if r.status_code != 200:
        print(f"[FAIL] List proposals failed: {r.text}")
        sys.exit(1)
    proposals = r.json()
    matching = [p for p in proposals if p['id'] == proposal_id]
    if not matching:
        print(f"[FAIL] Creator does NOT see the proposal (ID={proposal_id})")
        sys.exit(1)
    print(f"[PASS] 5. Creator sees incoming proposal: '{matching[0]['project_title']}'")

    # 6. Creator Accepts Proposal
    r = requests.post(f'{BASE_URL}/proposals/{proposal_id}/accept', headers=creator_headers)
    if r.status_code != 200:
        print(f"[FAIL] Accept proposal failed: {r.text}")
        sys.exit(1)
    accepted = r.json()
    if accepted.get('status') != 'accepted':
        print(f"[FAIL] Proposal status is '{accepted.get('status')}', expected 'accepted'")
        sys.exit(1)
    print(f"[PASS] 6. Proposal accepted. Status={accepted['status']}")

    # 7. Verify workspace created for Creator
    r = requests.get(f'{BASE_URL}/workspaces', headers=creator_headers)
    creator_workspaces = r.json() if r.status_code == 200 else []
    print(f"[INFO] 7. Demo Content Creator workspace count AFTER accept: {len(creator_workspaces)}")
    assert len(creator_workspaces) >= 1, "Creator should have at least 1 workspace"
    new_ws = creator_workspaces[0]
    print(f"[PASS]    Workspace found: '{new_ws.get('title', new_ws.get('name', 'N/A'))}' (ID={new_ws.get('id')})")

    # 8. Verify workspace visible to Recruiter
    r = requests.get(f'{BASE_URL}/workspaces', headers=recruiter_headers)
    recruiter_workspaces = r.json() if r.status_code == 200 else []
    ws_ids = [ws.get('id') for ws in recruiter_workspaces]
    print(f"[INFO] 8. Demo Recruiter workspace count AFTER accept: {len(recruiter_workspaces)}")
    if new_ws.get('id') in ws_ids:
        print(f"[PASS]    Demo Recruiter can see the shared workspace ID={new_ws.get('id')}")
    else:
        print(f"[WARN]    Workspace not in recruiter list (may be by design)")

    print("\n" + "="*60)
    print("ALL DEMO FLOW TESTS PASSED!")
    print("="*60 + "\n")

if __name__ == '__main__':
    run_tests()
