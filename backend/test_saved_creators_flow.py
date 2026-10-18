import requests
import sys

BASE_URL = 'http://localhost:8000/api'

def run_tests():
    print("============================================================")
    print("SAVED CREATORS / SHORTLIST END-TO-END VERIFICATION")
    print("============================================================")

    # 1. Login as Demo Recruiter
    r = requests.post(f'{BASE_URL}/auth/login', json={'email': 'recruiter@codexero.com', 'password': 'Demo@123'})
    assert r.status_code == 200, f"Demo Recruiter login failed: {r.text}"
    recruiter_tok = r.json()['access_token']
    rec_headers = {'Authorization': f'Bearer {recruiter_tok}'}
    print("[PASS] 1. Demo Recruiter logged in successfully")

    # 2. Fetch creators list to pick a creator
    r = requests.get(f'{BASE_URL}/creators', headers=rec_headers)
    assert r.status_code == 200, f"Fetch creators failed: {r.text}"
    creators = r.json()
    assert len(creators) > 0, "No creators found"
    target_creator = creators[0]
    target_id = target_creator['id']
    target_name = target_creator.get('name') or target_creator.get('display_name')
    print(f"[INFO] 2. Selected target creator: '{target_name}' (ID={target_id})")

    # Clear any previous shortlist for this creator to test cleanly
    requests.delete(f'{BASE_URL}/shortlist/{target_id}', headers=rec_headers)

    # Verify initial saved count
    r_initial = requests.get(f'{BASE_URL}/shortlist', headers=rec_headers)
    assert r_initial.status_code == 200, "Get shortlist failed"
    initial_count = len(r_initial.json())
    print(f"[INFO]    Initial shortlist count for Demo Recruiter: {initial_count}")

    # 3. Save creator to shortlist
    r_add = requests.post(f'{BASE_URL}/shortlist', json={'creator_id': target_id}, headers=rec_headers)
    assert r_add.status_code in (200, 201), f"Add to shortlist failed: {r_add.text}"
    added_entry = r_add.json()
    print(f"[PASS] 3. Creator added to Saved Creators (Entry ID: {added_entry.get('id')})")

    # 4. Fetch Saved Creators - Confirm creator appears with profile
    r_saved = requests.get(f'{BASE_URL}/shortlist', headers=rec_headers)
    assert r_saved.status_code == 200, f"Get saved creators failed: {r_saved.text}"
    saved_list = r_saved.json()
    assert len(saved_list) == initial_count + 1, f"Expected {initial_count + 1} items, got {len(saved_list)}"
    matching = [item for item in saved_list if str(item.get('creator_user_id')) == str(target_creator.get('user_id', '')) or str(item.get('id')) == str(added_entry.get('id'))]
    assert len(matching) > 0, "Saved creator not found in returned shortlist"
    saved_item = matching[0]
    print(f"[PASS] 4. Creator verified in Saved Creators list:")
    print(f"       Creator Name: {saved_item.get('creator_user', {}).get('full_name')}")
    print(f"       Profile Starting Rate: INR {saved_item.get('creator_profile', {}).get('starting_rate', 1500)}")

    # 5. Simulate Refresh (re-fetch with same auth)
    r_refresh = requests.get(f'{BASE_URL}/shortlist', headers=rec_headers)
    assert len(r_refresh.json()) == len(saved_list), "Shortlist did not persist on refresh!"
    print(f"[PASS] 5. Shortlist persists across refresh ({len(r_refresh.json())} items)")

    # 6. Verify User Isolation: Clean Recruiter should NOT see Demo Recruiter's saved creators
    r_clean = requests.post(f'{BASE_URL}/auth/login', json={'email': 'cleanrecruiter@codexero.com', 'password': 'Demo@123'})
    assert r_clean.status_code == 200, "Clean Recruiter login failed"
    clean_tok = r_clean.json()['access_token']
    clean_headers = {'Authorization': f'Bearer {clean_tok}'}
    r_clean_saved = requests.get(f'{BASE_URL}/shortlist', headers=clean_headers)
    assert r_clean_saved.status_code == 200, "Clean Recruiter shortlist get failed"
    assert len(r_clean_saved.json()) == 0, f"Clean Recruiter saw {len(r_clean_saved.json())} items, expected 0 (Isolation failed)"
    print("[PASS] 6. Cross-user isolation verified (Clean Recruiter has 0 saved creators)")

    # 7. Remove creator from Saved Creators
    r_del = requests.delete(f'{BASE_URL}/shortlist/{target_id}', headers=rec_headers)
    assert r_del.status_code in (200, 204), f"Delete shortlist failed: {r_del.status_code}"
    print(f"[PASS] 7. Creator removed from Saved Creators")

    # 8. Confirm creator disappeared from saved list
    r_after_del = requests.get(f'{BASE_URL}/shortlist', headers=rec_headers)
    assert r_after_del.status_code == 200, "Get shortlist after delete failed"
    after_del_list = r_after_del.json()
    assert len(after_del_list) == initial_count, f"Expected {initial_count} items after delete, got {len(after_del_list)}"
    print(f"[PASS] 8. Confirmed creator no longer in Saved Creators ({len(after_del_list)} items)")

    # 9. Verify Re-Login session persistence
    r_relogin = requests.post(f'{BASE_URL}/auth/login', json={'email': 'recruiter@codexero.com', 'password': 'Demo@123'})
    relogin_tok = r_relogin.json()['access_token']
    r_relogin_check = requests.get(f'{BASE_URL}/shortlist', headers={'Authorization': f'Bearer {relogin_tok}'})
    assert len(r_relogin_check.json()) == initial_count, "State did not persist across re-login"
    print(f"[PASS] 9. Logout/re-login state persistence verified")

    print("\n============================================================")
    print("ALL SAVED CREATORS END-TO-END TESTS PASSED!")
    print("============================================================")

if __name__ == '__main__':
    run_tests()
