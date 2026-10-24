"""Licensing Compatibility Engine for KreatorBuzz Phase 2A.

Compares brand licensing requirements (from BriefLicensing) against
creator licensing offers (from CreatorLicensing) and returns a
deterministic compatibility result.
"""

from typing import Optional, List, Dict, Any

TERRITORY_HIERARCHY = {
    "worldwide": ["worldwide", "global"],
    "asia": ["asia", "india", "southeast_asia", "apac"],
    "india": ["india"],
}

DURATION_MONTHS = {
    "3_months": 3,
    "6_months": 6,
    "12_months": 12,
    "24_months": 24,
    "perpetual": 9999,
}


def territory_covers(creator_territory: str, brand_territory: str) -> bool:
    """
    Returns True if the creator's territory offer covers the brand's requirement.

    e.g. creator="worldwide" covers brand="india" -> True
         creator="india" covers brand="worldwide" -> False
    """
    ct = (creator_territory or "").lower().strip()
    bt = (brand_territory or "").lower().strip()
    if not ct or not bt:
        return True  # assume compatible when data is missing
    if ct == bt:
        return True
    if ct in ("worldwide", "global"):
        return True
    # Asia covers india/southeast_asia etc
    if ct == "asia" and bt in ("india", "southeast_asia", "apac", "asia"):
        return True
    return False


def check_licensing_compatibility(
    brief_licensing: Optional[Any],
    creator_licensing: Optional[Any],
) -> Dict[str, Any]:
    """
    Deterministically checks brand licensing requirements vs creator licensing offer.

    Returns:
        {
          "licensing_status": "full_match" | "partial_match" | "mismatch",
          "licensing_score": float (0-25),
          "licensing_strengths": list[str],
          "licensing_conflicts": list[str],
        }

    Rules:
    - If either is None/missing: return partial_match with appropriate score, noting missing data
    - Commercial use: if brand requires it and creator doesn't offer it -> MISMATCH (score 0)
    - Territory: if creator territory doesn't cover brand territory -> CONFLICT (heavy penalty)
    - Duration: if creator max_duration < brand required duration -> CONFLICT (medium penalty)
    - Platforms: if brand requires platforms that creator doesn't support -> CONFLICT (light penalty)
    - Usage types: if brand requires usage types not offered by creator -> CONFLICT (medium penalty)

    Scoring (out of 25):
    - Commercial use match: 8 pts
    - Territory match: 8 pts
    - Duration match: 5 pts
    - Platform match: 4 pts
    """
    strengths: List[str] = []
    conflicts: List[str] = []

    # Handle missing licensing data gracefully
    if brief_licensing is None and creator_licensing is None:
        return {
            "licensing_status": "partial_match",
            "licensing_score": 12.5,
            "licensing_strengths": ["No specific licensing requirements set"],
            "licensing_conflicts": [],
        }

    if creator_licensing is None:
        return {
            "licensing_status": "partial_match",
            "licensing_score": 10.0,
            "licensing_strengths": [],
            "licensing_conflicts": ["Creator has not specified their licensing terms yet"],
        }

    if brief_licensing is None:
        return {
            "licensing_status": "partial_match",
            "licensing_score": 15.0,
            "licensing_strengths": ["Creator has licensing terms available"],
            "licensing_conflicts": [],
        }

    score = 0.0

    # --- 1. Commercial Use (8 pts) ---
    brand_needs_commercial = getattr(brief_licensing, "commercial_use_required", True)
    creator_offers_commercial = getattr(creator_licensing, "commercial_use", True)

    if brand_needs_commercial:
        if creator_offers_commercial:
            score += 8.0
            strengths.append("Creator supports commercial usage rights")
        else:
            conflicts.append(
                "Brand requires commercial usage rights, but creator does not currently offer them"
            )
    else:
        score += 8.0  # brand doesn't need it - no conflict

    # --- 2. Territory (8 pts) ---
    brand_territory = getattr(brief_licensing, "territory", "india") or "india"
    creator_territories = getattr(creator_licensing, "territories", []) or []

    if not creator_territories:
        creator_territories = ["india"]  # conservative default

    territory_ok = any(territory_covers(ct, brand_territory) for ct in creator_territories)

    if territory_ok:
        score += 8.0
        if brand_territory == "worldwide":
            strengths.append("Creator supports worldwide commercial usage")
        elif brand_territory:
            strengths.append(f"Creator's usage territory covers {brand_territory}")
    else:
        creator_territory_str = (
            ", ".join(creator_territories) if creator_territories else "unspecified"
        )
        conflicts.append(
            f"Brand requires {brand_territory} usage rights, but creator currently offers "
            f"{creator_territory_str}-only rights"
        )

    # --- 3. Duration (5 pts) ---
    brand_duration = getattr(brief_licensing, "usage_duration_months", 12) or 12
    creator_max_duration = getattr(creator_licensing, "max_duration_months", 12) or 12
    # 0 = perpetual in creator model
    if creator_max_duration == 0:
        creator_max_duration = 9999

    if creator_max_duration >= brand_duration:
        score += 5.0
        if creator_max_duration == 9999:
            strengths.append("Creator offers perpetual usage rights")
        else:
            strengths.append(
                f"Creator supports the required {brand_duration}-month usage period"
            )
    else:
        conflicts.append(
            f"Brand requires {brand_duration}-month rights, but creator currently offers "
            f"up to {creator_max_duration} months"
        )

    # --- 4. Platforms (4 pts) ---
    brand_platforms = [
        p.lower().strip() for p in (getattr(brief_licensing, "platforms", []) or [])
    ]
    creator_platforms = [
        p.lower().strip() for p in (getattr(creator_licensing, "platforms", []) or [])
    ]

    if not brand_platforms:
        score += 4.0  # no specific platform requirement
    elif not creator_platforms:
        score += 2.0  # creator hasn't specified - partial credit
        conflicts.append("Creator has not specified supported platforms")
    else:
        missing_platforms = [p for p in brand_platforms if p not in creator_platforms]
        if not missing_platforms:
            score += 4.0
            strengths.append(
                f"Creator supports all required platforms ({', '.join(brand_platforms[:3])})"
            )
        elif len(missing_platforms) < len(brand_platforms):
            score += 2.0
            conflicts.append(
                f"Creator does not support these required platforms: {', '.join(missing_platforms)}"
            )
        else:
            conflicts.append(
                f"Creator's platform coverage does not match brand requirements "
                f"({', '.join(missing_platforms)})"
            )

    # --- 5. Usage Types (bonus check - influences final status but not score directly) ---
    brand_usage_types = [
        u.lower().strip() for u in (getattr(brief_licensing, "usage_types", []) or [])
    ]
    creator_usage_types = [
        u.lower().strip() for u in (getattr(creator_licensing, "usage_types", []) or [])
    ]

    if brand_usage_types and creator_usage_types:
        missing_types = [u for u in brand_usage_types if u not in creator_usage_types]
        if not missing_types:
            strengths.append(
                f"Creator supports all required usage types ({', '.join(brand_usage_types[:2])})"
            )
        else:
            conflicts.append(
                f"Creator does not currently offer: {', '.join(missing_types)} usage"
            )

    # --- Determine final status ---
    score = round(min(25.0, max(0.0, score)), 1)

    # Hard dealbreakers
    has_hard_mismatch = (
        (brand_needs_commercial and not creator_offers_commercial)
        or (not territory_ok)
    )

    if has_hard_mismatch or score < 14.0 or len(conflicts) >= 3:
        licensing_status = "mismatch"
    elif score >= 23.0 and not conflicts:
        licensing_status = "full_match"
    else:
        licensing_status = "partial_match"

    return {
        "licensing_status": licensing_status,
        "licensing_score": score,
        "licensing_strengths": strengths,
        "licensing_conflicts": conflicts,
    }


def build_licensing_explanation(result: Dict[str, Any]) -> str:
    """
    Builds a single human-readable explanation string from a compatibility result.
    Keeps language simple — no technical jargon.
    """
    status = result.get("licensing_status", "partial_match")
    strengths = result.get("licensing_strengths", [])
    conflicts = result.get("licensing_conflicts", [])

    if status == "full_match":
        return strengths[0] if strengths else "Creator fully meets the licensing requirements."
    elif status == "mismatch":
        return conflicts[0] if conflicts else "Licensing terms do not match the brand requirements."
    else:
        parts = []
        if strengths:
            parts.append(strengths[0])
        if conflicts:
            parts.append(conflicts[0])
        return " However, ".join(parts) if parts else "Partial licensing compatibility."
