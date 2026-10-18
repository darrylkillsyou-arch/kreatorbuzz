import urllib.request
import json
import uuid

BASE = "http://127.0.0.1:8000/api"

# 1. Test live Xero chat call
msg = "I need a luxury perfume Instagram video around Rs 60,000 with a cinematic premium style."
session_id = f"test_ollama_{uuid.uuid4().hex[:6]}"
payload = json.dumps({"message": msg, "session_id": session_id}).encode("utf-8")

req = urllib.request.Request(
    f"{BASE}/xero/chat",
    data=payload,
    headers={"Content-Type": "application/json"}
)

resp = urllib.request.urlopen(req)
res = json.loads(resp.read().decode("utf-8"))

print("=== LIVE XERO AI 2.0 CHAT RESULT ===")
print("HTTP Status:", resp.getcode())
print("Session ID:", res.get("session_id"))
print("AI Provider Used:", res.get("ai_provider_used"))
print("Reply Message:", res.get("message"))

plan = res.get("plan")
if plan:
    print("\n--- ProjectPlan Details ---")
    print("Project Title:", plan.get("project_title"))
    print("Core Category:", plan.get("core_category"))
    print("Specializations:", plan.get("specializations"))
    print("Budget:", plan.get("budget"))
    print("Timeline Days:", plan.get("timeline_days"))
    print("Deliverables Count:", len(plan.get("deliverables", [])))
    for d in plan.get("deliverables", []):
        print(f"  - {d.get('name')} ({d.get('type')}) x{d.get('quantity')}")
    print("Milestones Count:", len(plan.get("milestones", [])))
    print("Budget Breakdown Count:", len(plan.get("budget_breakdown", [])))

recs = res.get("recommended_creators", [])
print(f"\nRecommended Creators from Matching Engine ({len(recs)} returned):")
for r in recs:
    c = r["creator"]
    print(f" - {c['display_name']} ({c['specialization']}) | Rate: Rs {c['starting_rate']} | Match: {r['match_score']}%")
    print(f"   Reason: {r['recommendation_reason']}")
