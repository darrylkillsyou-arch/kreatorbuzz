import requests

BASE_URL = 'http://localhost:8000/api'

def run_tests():
    # 1. Login as Demo Recruiter
    r = requests.post(f'{BASE_URL}/auth/login', json={'email': 'brand@maccall.demo', 'password': 'demo1234'})
    assert r.status_code == 200, f'Recruiter login failed: {r.text}'
    recruiter_token = r.json()['access_token']
    recruiter_headers = {'Authorization': f'Bearer {recruiter_token}'}
    recruiter_user = r.json()['user']
    print('1. Recruiter logged in:', recruiter_user['full_name'], '(ID:', recruiter_user['id'], ')')

    # 2. Send proposal to Creator (Aarav Studio, creator ID 1 / user ID 2)
    payload = {
        'creator_id': '1',
        'project_title': 'Automated Luxury Campaign Test',
        'project_requirement': 'Create a photorealistic 30s 4K video advertisement with custom soundtrack.',
        'budget_in_rupees': 85000,
        'deadline': '4 Business Days'
    }
    r = requests.post(f'{BASE_URL}/proposals', json=payload, headers=recruiter_headers)
    assert r.status_code == 201, f'Proposal send failed: {r.text}'
    proposal = r.json()
    proposal_id = proposal['id']
    print(f"2. Proposal created: #{proposal_id} | Title: {proposal['project_title']} | Status: {proposal['status']} | Budget: INR {proposal['budget_in_rupees']}")
    assert proposal['status'] == 'pending', 'Status should be pending'
    assert proposal['budget_in_rupees'] == 85000

    # 3. Login as Demo Creator (creator@maccall.demo)
    r = requests.post(f'{BASE_URL}/auth/login', json={'email': 'creator@maccall.demo', 'password': 'demo1234'})
    assert r.status_code == 200, f'Creator login failed: {r.text}'
    creator_token = r.json()['access_token']
    creator_headers = {'Authorization': f'Bearer {creator_token}'}
    creator_user = r.json()['user']
    print('3. Creator logged in:', creator_user['full_name'], '(ID:', creator_user['id'], ')')

    # 4. Fetch Creator Project Requests
    r = requests.get(f'{BASE_URL}/proposals', headers=creator_headers)
    assert r.status_code == 200, f'List proposals failed: {r.text}'
    creator_proposals = r.json()
    matching = [p for p in creator_proposals if p['id'] == proposal_id]
    assert len(matching) == 1, 'Creator must see the incoming proposal'
    print(f"4. Creator sees incoming proposal: '{matching[0]['project_title']}' from {matching[0]['recruiter_name']}")

    # 5. Creator Accepts Proposal
    r = requests.post(f'{BASE_URL}/proposals/{proposal_id}/accept', headers=creator_headers)
    assert r.status_code == 200, f'Accept proposal failed: {r.text}'
    accepted_proposal = r.json()
    assert accepted_proposal['status'] == 'accepted'
    workspace_id = accepted_proposal['workspace_id']
    assert workspace_id is not None, 'Workspace ID must be set upon acceptance'
    print(f'5. Proposal accepted! Created Workspace ID: {workspace_id}')

    # 6. Test Idempotency (prevent duplicate workspace)
    r = requests.post(f'{BASE_URL}/proposals/{proposal_id}/accept', headers=creator_headers)
    assert r.status_code == 200
    assert r.json()['workspace_id'] == workspace_id, 'Must return the same workspace ID without duplicating'
    print('6. Idempotency verified: re-accepting returns existing workspace.')

    # 7. Creator checks their Workspaces
    r = requests.get(f'{BASE_URL}/workspaces', headers=creator_headers)
    assert r.status_code == 200
    creator_ws_ids = [w['id'] for w in r.json()]
    assert workspace_id in creator_ws_ids, 'Workspace must be in creator workspaces list'
    print('7. Creator sees workspace in their list.')

    # 8. Recruiter checks their Workspaces
    r = requests.get(f'{BASE_URL}/workspaces', headers=recruiter_headers)
    assert r.status_code == 200
    recruiter_ws_ids = [w['id'] for w in r.json()]
    assert workspace_id in recruiter_ws_ids, 'Workspace must be in recruiter workspaces list'
    print('8. Recruiter sees workspace in their list.')

    # 9. Test Unrelated User cannot see the workspace
    r = requests.post(f'{BASE_URL}/auth/login', json={'email': 'meera@atelier.demo', 'password': 'demo1234'})
    assert r.status_code == 200
    meera_token = r.json()['access_token']
    meera_headers = {'Authorization': f'Bearer {meera_token}'}
    r = requests.get(f'{BASE_URL}/workspaces', headers=meera_headers)
    assert r.status_code == 200
    meera_ws_ids = [w['id'] for w in r.json()]
    assert workspace_id not in meera_ws_ids, 'Unrelated user must NOT see this workspace'
    print('9. Workspace isolation confirmed: Meera Atelier does NOT see this workspace.')

    # 10. Test Decline Flow
    r = requests.post(f'{BASE_URL}/proposals', json={
        'creator_id': '1',
        'project_title': 'Decline Test Project',
        'project_requirement': 'Testing decline scenario',
        'budget_in_rupees': 20000,
        'deadline': '2 Days'
    }, headers=recruiter_headers)
    assert r.status_code == 201
    decline_prop_id = r.json()['id']
    r = requests.post(f'{BASE_URL}/proposals/{decline_prop_id}/decline', headers=creator_headers)
    assert r.status_code == 200
    assert r.json()['status'] == 'declined'
    assert r.json()['workspace_id'] is None, 'Declined proposal must have no workspace'
    print('10. Decline flow confirmed: status is declined and no workspace created.')
    
    print('\n=============================================')
    print('ALL 10 HIRING FLOW VERIFICATION CHECKS PASSED!')
    print('=============================================')

if __name__ == '__main__':
    run_tests()
