"""
Phase 2A Licensing Compatibility Tests.

Tests the deterministic licensing compatibility engine.
No server required - tests the pure Python logic directly.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.licensing import check_licensing_compatibility, build_licensing_explanation


class MockBriefLicensing:
    def __init__(self, commercial_use_required=True, usage_types=None, territory="india",
                 usage_duration_months=12, platforms=None):
        self.commercial_use_required = commercial_use_required
        self.usage_types = usage_types or []
        self.territory = territory
        self.usage_duration_months = usage_duration_months
        self.platforms = platforms or []


class MockCreatorLicensing:
    def __init__(self, commercial_use=True, usage_types=None, territories=None,
                 max_duration_months=12, platforms=None):
        self.commercial_use = commercial_use
        self.usage_types = usage_types or []
        self.territories = territories or ["india"]
        self.max_duration_months = max_duration_months
        self.platforms = platforms or []


def test_case_1_full_match():
    """CASE 1: Perfect full match - worldwide, 12 months, paid_ads, Instagram + YouTube."""
    brand = MockBriefLicensing(
        commercial_use_required=True,
        usage_types=["paid_ads"],
        territory="worldwide",
        usage_duration_months=12,
        platforms=["instagram", "youtube"],
    )
    creator = MockCreatorLicensing(
        commercial_use=True,
        usage_types=["paid_ads", "organic_social"],
        territories=["worldwide"],
        max_duration_months=12,
        platforms=["instagram", "youtube", "website"],
    )
    result = check_licensing_compatibility(brand, creator)
    assert result["licensing_status"] == "full_match", (
        f"Expected full_match, got {result['licensing_status']}: {result}"
    )
    assert result["licensing_score"] >= 23.0, f"Expected score >= 23, got {result['licensing_score']}"
    assert not result["licensing_conflicts"], f"Unexpected conflicts: {result['licensing_conflicts']}"
    print(f"[PASS] Case 1 - Full Match: score={result['licensing_score']}, status={result['licensing_status']}")


def test_case_2_territory_mismatch():
    """CASE 2: Brand requires worldwide, creator only offers India."""
    brand = MockBriefLicensing(territory="worldwide", usage_duration_months=12)
    creator = MockCreatorLicensing(territories=["india"], max_duration_months=12)
    result = check_licensing_compatibility(brand, creator)
    assert result["licensing_status"] == "mismatch", (
        f"Expected mismatch, got {result['licensing_status']}: {result}"
    )
    assert any(
        "worldwide" in c.lower() or "india" in c.lower() for c in result["licensing_conflicts"]
    ), f"Expected territory conflict message, got: {result['licensing_conflicts']}"
    print(
        f"[PASS] Case 2 - Territory Mismatch: score={result['licensing_score']}, "
        f"conflicts={result['licensing_conflicts']}"
    )


def test_case_3_duration_mismatch():
    """CASE 3: Brand needs 12 months, creator offers only 6 months."""
    brand = MockBriefLicensing(territory="india", usage_duration_months=12)
    creator = MockCreatorLicensing(territories=["india"], max_duration_months=6)
    result = check_licensing_compatibility(brand, creator)
    assert result["licensing_status"] in ("partial_match", "mismatch"), (
        f"Expected partial or mismatch, got {result['licensing_status']}"
    )
    assert any("month" in c.lower() for c in result["licensing_conflicts"]), (
        f"Expected duration conflict, got: {result['licensing_conflicts']}"
    )
    print(
        f"[PASS] Case 3 - Duration Mismatch: score={result['licensing_score']}, "
        f"conflicts={result['licensing_conflicts']}"
    )


def test_case_4_platform_mismatch():
    """CASE 4: Brand needs TikTok + Instagram, creator only offers Instagram."""
    brand = MockBriefLicensing(territory="india", platforms=["instagram", "tiktok"])
    creator = MockCreatorLicensing(territories=["india"], platforms=["instagram", "youtube"])
    result = check_licensing_compatibility(brand, creator)
    assert any("tiktok" in c.lower() for c in result["licensing_conflicts"]), (
        f"Expected tiktok conflict, got: {result['licensing_conflicts']}"
    )
    print(
        f"[PASS] Case 4 - Platform Mismatch: score={result['licensing_score']}, "
        f"conflicts={result['licensing_conflicts']}"
    )


def test_case_5_commercial_use_mismatch():
    """CASE 5: Brand requires commercial use, creator does not offer it."""
    brand = MockBriefLicensing(commercial_use_required=True, territory="india")
    creator = MockCreatorLicensing(commercial_use=False, territories=["india"])
    result = check_licensing_compatibility(brand, creator)
    assert result["licensing_status"] == "mismatch", (
        f"Expected mismatch, got {result['licensing_status']}"
    )
    assert any("commercial" in c.lower() for c in result["licensing_conflicts"]), (
        f"Expected commercial conflict, got: {result['licensing_conflicts']}"
    )
    print(
        f"[PASS] Case 5 - Commercial Use Mismatch: score={result['licensing_score']}, "
        f"conflicts={result['licensing_conflicts']}"
    )


def test_case_6_partial_match():
    """CASE 6: Good territory match but platform gap - partial match."""
    brand = MockBriefLicensing(
        territory="india",
        usage_duration_months=6,
        platforms=["instagram", "youtube", "tiktok"],
    )
    creator = MockCreatorLicensing(
        territories=["india"],
        max_duration_months=12,
        platforms=["instagram", "youtube"],
    )
    result = check_licensing_compatibility(brand, creator)
    assert result["licensing_status"] in ("partial_match", "mismatch"), (
        f"Expected partial_match or mismatch, got {result['licensing_status']}"
    )
    print(
        f"[PASS] Case 6 - Partial Match: score={result['licensing_score']}, "
        f"status={result['licensing_status']}"
    )


def test_case_7_worldwide_vs_india():
    """CASE 7: Brand requires worldwide rights, creator offers India only."""
    brand = MockBriefLicensing(territory="worldwide", usage_duration_months=12)
    creator = MockCreatorLicensing(territories=["india"], max_duration_months=24)
    result = check_licensing_compatibility(brand, creator)
    assert result["licensing_status"] == "mismatch"
    print(
        f"[PASS] Case 7 - Worldwide vs India-only: score={result['licensing_score']}, "
        f"status={result['licensing_status']}"
    )


def test_case_8_missing_creator_data():
    """CASE 8: Creator has no licensing data yet - should return partial_match, not mismatch."""
    brand = MockBriefLicensing(territory="india")
    result = check_licensing_compatibility(brand, None)
    assert result["licensing_status"] == "partial_match", (
        f"Expected partial_match for missing creator data, got {result['licensing_status']}"
    )
    print(
        f"[PASS] Case 8 - Missing Creator Data: score={result['licensing_score']}, "
        f"status={result['licensing_status']}"
    )


def test_explanation_generation():
    """Test that explanations are human-readable."""
    brand = MockBriefLicensing(territory="worldwide")
    creator = MockCreatorLicensing(territories=["india"])
    result = check_licensing_compatibility(brand, creator)
    explanation = build_licensing_explanation(result)
    assert len(explanation) > 10, "Explanation too short"
    assert any(
        word in explanation.lower() for word in ["worldwide", "india", "rights", "usage"]
    ), f"Explanation not meaningful: {explanation}"
    print(f"[PASS] Explanation: {explanation}")


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 2A LICENSING COMPATIBILITY TESTS")
    print("=" * 60)

    test_case_1_full_match()
    test_case_2_territory_mismatch()
    test_case_3_duration_mismatch()
    test_case_4_platform_mismatch()
    test_case_5_commercial_use_mismatch()
    test_case_6_partial_match()
    test_case_7_worldwide_vs_india()
    test_case_8_missing_creator_data()
    test_explanation_generation()

    print()
    print("=" * 60)
    print("ALL LICENSING TESTS PASSED!")
    print("=" * 60)
