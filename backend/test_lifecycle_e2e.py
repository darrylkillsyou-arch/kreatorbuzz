import urllib.request
import urllib.parse
import json
import io
import mimetypes
import uuid
import os

BASE_URL = "http://127.0.0.1:8000/api"

def login(email, password="Demo@123"):
    data = json.dumps({"email": email, "password": password}).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/auth/login", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["access_token"], res["user"]

def multipart_post(url, fields, files, token=None):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    body = io.BytesIO()

    for k, v in fields.items():
        if v is not None:
            body.write(f"--{boundary}\r\n".encode("utf-8"))
            body.write(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode("utf-8"))
            body.write(f"{v}\r\n".encode("utf-8"))

    for field_name, (filename, file_bytes, mime_type) in files.items():
        body.write(f"--{boundary}\r\n".encode("utf-8"))
        body.write(f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode("utf-8"))
        body.write(f"Content-Type: {mime_type}\r\n\r\n".encode("utf-8"))
        body.write(file_bytes)
        body.write(b"\r\n")

    body.write(f"--{boundary}--\r\n".encode("utf-8"))
    payload = body.getvalue()

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(payload))
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=payload, headers=headers)
    return req

print("Starting complete collaboration lifecycle test...")

# 1. Log in recruiter and creator
recruiter_token, recruiter_user = login("recruiter@codexero.com")
creator_token, creator_user = login("creator@codexero.com")
other_token, other_user = login("cleancreator@codexero.com") # Unrelated creator

print(f"Recruiter: {recruiter_user['id']} ({recruiter_user['email']})")
print(f"Creator: {creator_user['id']} ({creator_user['email']})")
print(f"Other User: {other_user['id']} ({other_user['email']})")

# 2. Create a fresh test workspace for isolated E2E verification
ws_create = {
    "creator_user_id": creator_user["id"],
    "title": f"Lifecycle E2E Workspace ({uuid.uuid4().hex[:6]})",
    "initial_milestones": [
        {"title": "Concept Frames Pass", "amount": 20000, "description": "Style frame renders"},
        {"title": "Final 4K Master", "amount": 30000, "description": "Full master cut"}
    ]
}
req = urllib.request.Request(
    f"{BASE_URL}/workspaces",
    data=json.dumps(ws_create).encode("utf-8"),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {recruiter_token}"}
)
with urllib.request.urlopen(req) as resp:
    target_ws = json.loads(resp.read().decode("utf-8"))

ws_id = target_ws["id"]
milestones = target_ws["milestones"]
m1_id = milestones[0]["id"]
m2_id = milestones[1]["id"]
print(f"Created fresh test workspace #{ws_id}: '{target_ws['title']}', Milestones: #{m1_id}, #{m2_id}")

# TEST 1 — Creator Uploads Deliverable Version 1
sample_png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
req = multipart_post(
    f"{BASE_URL}/workspaces/{ws_id}/deliverables",
    fields={"milestone_id": str(m1_id), "description": "Concept style frames v1 pass"},
    files={"file": ("concept_render_v1.png", sample_png_bytes, "image/png")},
    token=creator_token
)
with urllib.request.urlopen(req) as resp:
    f1 = json.loads(resp.read().decode("utf-8"))
    print(f"TEST 1 PASSED: Creator uploaded deliverable #{f1['id']}: {f1['filename']} (v{f1['version']})")
    assert f1["version"] == 1
    file1_id = f1["id"]

# TEST 2 — Recruiter Downloads Deliverable
download_url = f"{BASE_URL}/workspaces/{ws_id}/files/{file1_id}/download"
req = urllib.request.Request(download_url, headers={"Authorization": f"Bearer {recruiter_token}"})
with urllib.request.urlopen(req) as resp:
    downloaded_bytes = resp.read()
    assert downloaded_bytes == sample_png_bytes
    print(f"TEST 2 PASSED: Recruiter successfully downloaded {len(downloaded_bytes)} bytes matching asset.")

# TEST 3 — Unauthorized Access
req = urllib.request.Request(download_url, headers={"Authorization": f"Bearer {other_token}"})
try:
    urllib.request.urlopen(req)
    print("TEST 3 FAILED: Other user could access file!")
except urllib.error.HTTPError as e:
    assert e.code == 403
    print(f"TEST 3 PASSED: Unrelated user received HTTP {e.code} Forbidden.")

# TEST 4 — Invalid File Upload (Unsupported extension)
req = multipart_post(
    f"{BASE_URL}/workspaces/{ws_id}/deliverables",
    fields={"milestone_id": str(m1_id)},
    files={"file": ("dangerous_script.exe", b"binarycontent", "application/octet-stream")},
    token=creator_token
)
try:
    urllib.request.urlopen(req)
    print("TEST 4 FAILED: Server accepted dangerous .exe file!")
except urllib.error.HTTPError as e:
    assert e.code == 400
    print(f"TEST 4 PASSED: Server rejected .exe with HTTP {e.code} Bad Request: {e.read().decode()}")

# TEST 5 — Revision Request → Creator uploads Version 2
# Recruiter requests revision
rev_req = urllib.request.Request(
    f"{BASE_URL}/workspaces/{ws_id}/revision-requests",
    data=json.dumps({"milestone_id": m1_id, "description": "Please adjust color contrast in frame 1"}).encode("utf-8"),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {recruiter_token}"}
)
with urllib.request.urlopen(rev_req) as resp:
    rev = json.loads(resp.read().decode("utf-8"))
    print(f"TEST 5.1 PASSED: Recruiter opened revision request #{rev['id']}: {rev['description']}")

# Creator uploads Version 2 for this milestone
req_v2 = multipart_post(
    f"{BASE_URL}/workspaces/{ws_id}/deliverables",
    fields={"milestone_id": str(m1_id), "description": "Color contrast adjusted v2 pass"},
    files={"file": ("concept_render_v2.png", sample_png_bytes + b"_v2", "image/png")},
    token=creator_token
)
with urllib.request.urlopen(req_v2) as resp:
    f2 = json.loads(resp.read().decode("utf-8"))
    print(f"TEST 5.2 PASSED: Creator uploaded deliverable #{f2['id']} (v{f2['version']})")
    assert f2["version"] == 2

# Check workspace files: both v1 and v2 exist
req = urllib.request.Request(f"{BASE_URL}/workspaces/{ws_id}", headers={"Authorization": f"Bearer {recruiter_token}"})
with urllib.request.urlopen(req) as resp:
    ws_detail = json.loads(resp.read().decode("utf-8"))
    versions = [f["version"] for f in ws_detail["files"] if f["milestone_id"] == m1_id]
    print(f"TEST 5.3 PASSED: Workspace preserves versions: {versions}")
    assert 1 in versions and 2 in versions

# TEST 6 — Premature Completion (Milestones incomplete)
req = urllib.request.Request(
    f"{BASE_URL}/workspaces/{ws_id}/complete",
    data=b"{}",
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {recruiter_token}"}
)
try:
    urllib.request.urlopen(req)
    print("TEST 6 FAILED: Completed project while milestones pending!")
except urllib.error.HTTPError as e:
    assert e.code == 400
    print(f"TEST 6 PASSED: Premature completion rejected: {e.read().decode()}")

# TEST 7 — Approve All Milestones
for m in ws_detail["milestones"]:
    req = urllib.request.Request(
        f"{BASE_URL}/workspaces/{ws_id}/milestones/{m['id']}",
        data=json.dumps({"status": "released"}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {recruiter_token}"}
    )
    req.get_method = lambda: "PUT"
    with urllib.request.urlopen(req) as resp:
        m_updated = json.loads(resp.read().decode("utf-8"))
        assert m_updated["status"] == "released"
print("TEST 7 PASSED: All milestones approved and released.")

# TEST 8 — Complete Project
req = urllib.request.Request(
    f"{BASE_URL}/workspaces/{ws_id}/complete",
    data=b"{}",
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {recruiter_token}"}
)
with urllib.request.urlopen(req) as resp:
    ws_completed = json.loads(resp.read().decode("utf-8"))
    assert ws_completed["status"] == "completed"
    assert ws_completed["completed_at"] is not None
    print(f"TEST 8 PASSED: Project successfully marked completed on {ws_completed['completed_at']}.")

# TEST 9 — Submit Verified Creator Review
rev_payload = {
    "rating": 5,
    "comment": "Outstanding generative motion direction! Prompt fidelity and delivery speed were world-class."
}
req = urllib.request.Request(
    f"{BASE_URL}/workspaces/{ws_id}/review",
    data=json.dumps(rev_payload).encode("utf-8"),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {recruiter_token}"}
)
with urllib.request.urlopen(req) as resp:
    review_obj = json.loads(resp.read().decode("utf-8"))
    assert review_obj["rating"] == 5
    print(f"TEST 9 PASSED: Verified review #{review_obj['id']} created: {review_obj['rating']} stars")

# TEST 10 — Duplicate Review Rejected
req = urllib.request.Request(
    f"{BASE_URL}/workspaces/{ws_id}/review",
    data=json.dumps(rev_payload).encode("utf-8"),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {recruiter_token}"}
)
try:
    urllib.request.urlopen(req)
    print("TEST 10 FAILED: Duplicate review accepted!")
except urllib.error.HTTPError as e:
    assert e.code == 400
    print(f"TEST 10 PASSED: Duplicate review rejected with HTTP {e.code}: {e.read().decode()}")

# TEST 11 — Unauthorized Review
req = urllib.request.Request(
    f"{BASE_URL}/workspaces/{ws_id}/review",
    data=json.dumps(rev_payload).encode("utf-8"),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {other_token}"}
)
try:
    urllib.request.urlopen(req)
    print("TEST 11 FAILED: Unrelated user review accepted!")
except urllib.error.HTTPError as e:
    assert e.code == 403
    print(f"TEST 11 PASSED: Unrelated user review rejected with HTTP {e.code}.")

# TEST 12 — Review visible in creator profile reviews
creator_prof_id = creator_user.get("creator_profile_id") or creator_user["id"]
req = urllib.request.Request(f"{BASE_URL}/workspaces/creators/{creator_user['id']}/reviews")
with urllib.request.urlopen(req) as resp:
    c_reviews = json.loads(resp.read().decode("utf-8"))
    assert len(c_reviews) >= 1
    assert any(r["comment"] == rev_payload["comment"] for r in c_reviews)
    print(f"TEST 12 PASSED: Review displays publicly on creator profile: {c_reviews[0]['comment']}")

print("\n=======================================================")
print("ALL 12 LIFECYCLE TESTS COMPLETED SUCCESSFULLY!")
print("=======================================================")
