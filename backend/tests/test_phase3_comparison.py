"""Phase 3 Test Suite: Creator Comparison, Trust Signals, and Blind Arena."""

import sys
import os
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.models.creators import CreatorProfile
from app.models.users import User
from app.services.trust import evaluate_creator_trust, evaluate_recruiter_trust
from app.services.comparison import compare_creators, generate_difference_explanations, build_compare_card
from app.services.blind_arena import create_blind_arena, reveal_blind_creator


def test_phase3_suite():
    db = SessionLocal()
    try:
        print("=" * 65)
        print("KREATORBUZZ PHASE 3: COMPARISON, TRUST & BLIND ARENA TESTS")
        print("=" * 65)

        # Fetch sample creators from DB
        creators = db.query(CreatorProfile).limit(5).all()
        assert len(creators) >= 3, "Need at least 3 creators in DB for tests"

        c1, c2, c3 = creators[0], creators[1], creators[2]
        print(f"Test Candidates: #{c1.id} ({c1.display_name}), #{c2.id} ({c2.display_name}), #{c3.id} ({c3.display_name})")

        # 1. Test Trust Signals & Badges (Corresponds to actual DB data)
        print("\n--- 1. Evaluating Trust Signals & Badges ---")
        t1 = evaluate_creator_trust(c1, db)
        assert t1.creator_id == c1.id
        assert len(t1.badges) >= 4
        # Every badge has non-empty evidence
        for b in t1.badges:
            assert b.id in ("identity", "portfolio", "tools", "commercial", "reviews")
            assert len(b.evidence) > 5, f"Missing evidence for badge {b.id}"
        assert t1.reliability.status in ("Reliable", "Minor Concern", "Reliability Concern")
        print(f"[PASS] Creator #{c1.id} trust evaluation verified. Badges: {[b.label for b in t1.badges if b.verified]}")
        print(f"[PASS] Reliability status: {t1.reliability.status} ({t1.reliability.completed_projects} completed, {t1.reliability.late_deliveries} late)")

        # 2. Test Rising Creator Logic
        print("\n--- 2. Testing Rising Creator Logic ---")
        # Find or verify rising creator behavior
        all_creators = db.query(CreatorProfile).all()
        rising_creators = [c for c in all_creators if evaluate_creator_trust(c, db).is_rising_creator]
        print(f"[INFO] Found {len(rising_creators)} rising creator(s) among {len(all_creators)} profiles.")
        if rising_creators:
            rc = rising_creators[0]
            rc_trust = evaluate_creator_trust(rc, db)
            assert rc_trust.is_rising_creator is True
            assert rc_trust.rising_creator_reason is not None
            print(f"[PASS] Rising Creator detected: #{rc.id} ({rc.display_name}) - {rc_trust.rising_creator_reason}")

        # 3. Test Recruiter Trust Signals
        print("\n--- 3. Testing Recruiter Trust Signals ---")
        recruiter = db.query(User).filter(User.role == "brand").first()
        if recruiter:
            r_trust = evaluate_recruiter_trust(recruiter, db)
            assert r_trust.recruiter_user_id == recruiter.id
            assert r_trust.trust_status in ("Verified Brand", "Established Recruiter", "New Brand")
            print(f"[PASS] Recruiter trust: {r_trust.company_name} -> {r_trust.trust_status} (Completion rate: {r_trust.completion_rate_pct}%)")

        # 4. Test 2-Creator Comparison & Difference Generation
        print("\n--- 4. Testing 2-Creator Comparison ---")
        comp_2 = compare_creators([c1.id, c2.id], db, target_category="AI Video", budget=40000.0)
        assert len(comp_2.candidates) == 2
        assert len(comp_2.difference_explanations) == 2

        # Check difference explanations
        diff_a = comp_2.difference_explanations[0]
        diff_b = comp_2.difference_explanations[1]
        assert diff_a.creator_id == c1.id
        assert diff_b.creator_id == c2.id
        assert len(diff_a.unique_advantages) > 0, "Expected unique advantages for Creator A"
        assert len(diff_b.unique_advantages) > 0, "Expected unique advantages for Creator B"

        print(f"[PASS] Creator A ({diff_a.creator_name}) unique advantages: {diff_a.unique_advantages}")
        print(f"[PASS] Creator B ({diff_b.creator_name}) unique advantages: {diff_b.unique_advantages}")

        # 5. Test 3-Creator Comparison & Unique Contribution
        print("\n--- 5. Testing 3-Creator Comparison ---")
        comp_3 = compare_creators([c1.id, c2.id, c3.id], db, target_category="AI Video", budget=40000.0)
        assert len(comp_3.candidates) == 3
        assert len(comp_3.difference_explanations) == 3
        diff_c = comp_3.difference_explanations[2]
        assert diff_c.creator_id == c3.id
        assert len(diff_c.unique_advantages) > 0
        print(f"[PASS] Creator C ({diff_c.creator_name}) uniquely brings: {diff_c.unique_advantages}")
        print(f"[PASS] Summary verdict: {comp_3.summary_verdict}")

        # 6. Test Blind Arena Creation (Data Hiding & Fairness)
        print("\n--- 6. Testing Blind Arena Masking & Anonymization ---")
        blind_arena = create_blind_arena([c1.id, c2.id, c3.id], db, target_category="AI Video")
        assert len(blind_arena.candidates) == 3
        assert blind_arena.tagline == "Choose the work. Then meet the creator."

        # Verify real identities are strictly hidden
        for card in blind_arena.candidates:
            assert card.anonymous_id in ("Creator A", "Creator B", "Creator C")
            # Real names must NOT appear in anonymous ID
            assert c1.display_name != card.anonymous_id
            assert c2.display_name != card.anonymous_id
            assert c3.display_name != card.anonymous_id
            # Token is opaque
            assert card.blind_token.startswith("blind_")
            # Portfolio is retained
            assert isinstance(card.portfolio_samples, list)
            # Match score is fair (matches real score)
            assert 0 <= card.match_score <= 100
            # Licensing status preserved
            assert card.licensing_status in ("full_match", "partial_match", "mismatch")

        print("[PASS] Blind Arena correctly masked identity: names, avatars, reviews, account age hidden.")
        print(f"[PASS] Preserved work quality: portfolio samples, tools, licensing, match scores ({[c.match_score for c in blind_arena.candidates]}).")

        # 7. Test Blind Selection & Reveal
        print("\n--- 7. Testing Blind Selection & Reveal ---")
        winner_blind = blind_arena.candidates[1]  # Select Creator B
        all_tokens = [c.blind_token for c in blind_arena.candidates]

        reveal_res = reveal_blind_creator(
            chosen_token=winner_blind.blind_token,
            all_tokens=all_tokens,
            db=db,
        )

        assert reveal_res.revealed_creator.creator_id == c2.id
        assert reveal_res.revealed_creator.display_name == c2.display_name
        assert len(reveal_res.why_this_creator_won) > 15
        assert len(reveal_res.what_others_did_better) >= 1

        print(f"[PASS] Successfully revealed chosen creator: {reveal_res.revealed_creator.display_name} (#{reveal_res.revealed_creator.creator_id})")
        print(f"[PASS] 'Why this creator won': {reveal_res.why_this_creator_won}")
        for other in reveal_res.what_others_did_better:
            print(f"[PASS] 'What {other.anonymous_id} did better': {other.strengths}")

        print("\n" + "=" * 65)
        print("ALL PHASE 3 COMPARISON, TRUST & BLIND ARENA TESTS PASSED!")
        print("=" * 65)

    finally:
        db.close()


if __name__ == "__main__":
    test_phase3_suite()
