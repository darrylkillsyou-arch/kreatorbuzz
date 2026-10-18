"""Creator Matching & Recommendation Engine for CODE XERO AI Creator Marketplace.

Priority Matching Order:
1. Creator Category & Specialization (40 pts)
2. Tools & Tags Match (25 pts)
3. Style & Creative Direction Match (15 pts)
4. Starting Price vs Project Budget (10 pts)
5. Availability (5 pts)
6. Rating & SLA Score (5 pts)
"""

from typing import List, Dict, Any, Tuple, Optional
from app.models.creators import CreatorProfile
from app.models.briefs import Brief


CATEGORY_KEYWORDS = {
    "ai video": ["video", "cinematic", "film", "motion", "reel", "vfx", "short", "director", "commercial film"],
    "ai videos": ["video", "cinematic", "film", "motion", "reel", "vfx", "short", "director", "commercial film"],
    "ai images": ["image", "photo", "photography", "portrait", "still", "generative image", "pixel", "illustration", "stills"],
    "ai image": ["image", "photo", "photography", "portrait", "still", "generative image", "pixel", "illustration", "stills"],
    "3d & cgi": ["3d", "cgi", "render", "spatial", "blender", "unreal", "cinema 4d", "v-ray", "houdini", "redshift", "sneaker"],
    "3d/cgi": ["3d", "cgi", "render", "spatial", "blender", "unreal", "cinema 4d", "v-ray", "houdini", "redshift", "sneaker"],
    "product advertising": ["product", "ad", "campaign", "commercial", "ecommerce", "brand", "packaging", "advertising"],
    "product ads": ["product", "ad", "campaign", "commercial", "ecommerce", "brand", "packaging", "advertising"],
    "fashion": ["fashion", "couture", "apparel", "lookbook", "textile", "runway", "model", "silk", "wear", "bridal"],
    "social media": ["social", "reels", "tiktok", "instagram", "viral", "short", "content creator", "youtube", "thumbnail"],
    "animation & motion": ["animation", "motion", "animated", "kinetic", "motion graphics", "2d", "anime"],
    "animation": ["animation", "motion", "animated", "kinetic", "motion graphics", "2d", "anime"],
    "branding & design": ["graphic", "design", "typography", "branding", "print", "visual", "poster", "identity", "packaging"],
    "graphic design": ["graphic", "design", "typography", "branding", "print", "visual", "poster", "identity", "packaging"],
    "audio & voice": ["audio", "sound", "voice", "music", "sonic", "podcast", "suno", "elevenlabs", "voiceover", "soundtrack"],
}


def recommend_top_creators(
    category: str,
    content_type: str = "",
    style: str = "",
    tools_suggested: Optional[List[str]] = None,
    budget: float = 0.0,
    budget_min: float = 0.0,
    budget_max: float = 0.0,
    timeline_days: int = 7,
    description: str = "",
    creators: Optional[List[CreatorProfile]] = None,
    limit: int = 3,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """Calculates deterministic matching scores and builds human-readable explanations.
    
    Priority matching:
    1. Category (40 pts)
    2. Tools / Tags (25 pts)
    3. Style (15 pts)
    4. Budget fit (10 pts)
    5. Availability (5 pts)
    6. Rating & SLA (5 pts)
    """
    if not creators:
        return []

    tools_suggested = [t.strip() for t in (tools_suggested or []) if t.strip()]
    target_budget = budget_max if budget_max > 0 else (budget if budget > 0 else budget_min)

    scored_list = []
    for creator in creators:
        score_breakdown, recommendation_reason, match_reasons, total_score = score_creator_for_recommendation(
            creator=creator,
            target_category=category or "AI Videos",
            content_type=content_type or "",
            style=style or "",
            tools_suggested=tools_suggested,
            budget=target_budget,
            timeline_days=timeline_days,
            description=description,
        )

        scored_list.append({
            "creator": creator,
            "match_score": int(round(total_score)),
            "raw_score": total_score,
            "recommendation_reason": recommendation_reason,
            "match_reasons": match_reasons,
            "score_breakdown": score_breakdown,
        })

    # Sort descending by match score, raw score, rating, SLA
    scored_list.sort(
        key=lambda x: (x["match_score"], x["raw_score"], x["creator"].rating or 0, x["creator"].sla_score or 0),
        reverse=True
    )
    return scored_list[offset:offset+limit]



def score_creator_for_recommendation(
    creator: CreatorProfile,
    target_category: str,
    content_type: str,
    style: str,
    tools_suggested: List[str],
    budget: float,
    timeline_days: int,
    description: str,
) -> Tuple[Dict[str, float], str, List[str], float]:
    match_reasons = []

    # 1. Category & Specialization Match (40 pts max)
    target_norm = (target_category or "").lower().strip()
    cat_keywords = CATEGORY_KEYWORDS.get(target_norm, [target_norm])
    creator_core = (getattr(creator, 'core_category', None) or "").lower().strip()
    spec_lower = (creator.specialization or "").lower()
    tagline_lower = (creator.tagline or "").lower()
    sub_specs = [s.lower() for s in (getattr(creator, 'sub_specializations', None) or [])]
    desc_lower = (description or "").lower()
    content_lower = (content_type or "").lower()

    category_score = 0.0
    direct_category_match = False

    # Exact core category match gives base 34.0
    if creator_core and (creator_core in target_norm or target_norm in creator_core):
        category_score = 34.0
        direct_category_match = True
        match_reasons.append(f"Specializes in {creator.core_category or target_category} ({creator.specialization})")
    else:
        for kw in cat_keywords:
            if kw in spec_lower or kw in tagline_lower:
                category_score = 30.0
                direct_category_match = True
                match_reasons.append(f"Specializes in {target_category} ({creator.specialization})")
                break

    # Check for sub-specialization alignment in brief description or content type (+6.0 pts)
    matched_subspecs = []
    if direct_category_match and sub_specs:
        for s in sub_specs:
            # check if sub-spec name or words appear in desc or content_type or style
            s_tokens = [w for w in s.replace("&", " ").replace("/", " ").split() if len(w) > 2]
            if any(tok in desc_lower or tok in content_lower for tok in s_tokens):
                matched_subspecs.append(s)
        if matched_subspecs:
            bonus = min(6.0, len(matched_subspecs) * 3.0)
            category_score += bonus
            match_reasons.append(f"Sub-specialty fit: {', '.join(matched_subspecs[:2])}")
        else:
            category_score += 2.0  # partial sub-spec baseline
    elif direct_category_match:
        category_score += 2.0

    if not direct_category_match:
        # Check portfolio items
        if creator.portfolio_items:
            for p in creator.portfolio_items:
                if any(kw in (p.category or "").lower() or kw in (p.title or "").lower() for kw in cat_keywords):
                    category_score = 24.0
                    match_reasons.append(f"Portfolio includes {target_category} works")
                    break

    if category_score == 0.0:
        category_score = 5.0  # base fallback
    category_score = min(40.0, category_score)

    # 2. Tools Overlap (25 pts max) — rewards tool breadth and exact hits
    creator_tools = [t.lower() for t in (creator.ai_tools or [])]
    matched_tools = []
    tools_score = 0.0

    if tools_suggested:
        for st in tools_suggested:
            st_clean = st.lower().replace("flux.1", "flux").replace("v6", "").strip()
            for ct in (creator.ai_tools or []):
                ct_clean = ct.lower().replace("flux.1", "flux").replace("v6", "").strip()
                if st_clean in ct_clean or ct_clean in st_clean:
                    if ct not in matched_tools:
                        matched_tools.append(ct)

        if matched_tools:
            # Multi-tool scaling: 1 tool = 14 pts, 2 tools = 20 pts, 3+ tools = 25 pts
            if len(matched_tools) == 1:
                tools_score = 14.0
            elif len(matched_tools) == 2:
                tools_score = 20.0
            else:
                tools_score = 25.0
            match_reasons.append(f"Proficient in {', '.join(matched_tools[:3])}")
        else:
            tools_score = 6.0
    else:
        tools_score = 15.0

    # 3. Style Match (15 pts max) — checks creator style_tags and descriptive text
    style_score = 0.0
    creator_styles = [s.lower() for s in (getattr(creator, 'style_tags', None) or [])]
    if style:
        style_tokens = [w.lower().strip() for w in style.replace(",", " ").replace("-", " ").split() if len(w) > 2]
        matched_style_words = []
        for w in style_tokens:
            if any(w in cs for cs in creator_styles):
                matched_style_words.append(w)
            elif w in spec_lower or w in tagline_lower:
                matched_style_words.append(w)

        if matched_style_words:
            # 8 base + 2.5 per matched style keyword, up to 15
            style_score = min(15.0, 7.5 + len(matched_style_words) * 2.5)
            match_reasons.append(f"Aesthetic match for {style}")
        else:
            style_score = 5.0
    else:
        style_score = 10.0

    # 4. Starting Price vs Budget (10 pts max) — granular headroom scaling
    price_score = 0.0
    creator_rate = creator.starting_rate or 25000.0
    if budget > 0:
        if creator_rate <= budget:
            # Differentiate creators within budget:
            # e.g. creator_rate == budget -> 7.0 pts
            # creator_rate == 0.5 * budget -> 9.5 pts
            # creator_rate == 0.25 * budget -> 10.0 pts
            headroom_ratio = (budget - creator_rate) / budget
            price_score = round(7.0 + headroom_ratio * 3.0, 2)
            price_score = min(10.0, max(7.0, price_score))
            if creator_rate <= budget * 0.7:
                match_reasons.append(f"Strong budget headroom (₹{int(creator_rate):,} vs ₹{int(budget):,})")
            else:
                match_reasons.append(f"Fits within budget (Starting at ₹{int(creator_rate):,})")
        elif creator_rate <= budget * 1.25:
            overage_ratio = (creator_rate - budget) / (budget * 0.25)
            price_score = round(max(2.0, 6.0 - overage_ratio * 4.0), 2)
        else:
            price_score = 1.0
    else:
        price_score = 7.0

    # 5. Availability (5 pts max)
    avail = (creator.availability_status or "available").lower()
    if avail == "available":
        avail_score = 5.0
    elif avail == "busy":
        avail_score = 2.5
    else:
        avail_score = 1.0

    # 6. Rating & SLA (5 pts max) — precise float contribution
    rating_val = creator.rating or 4.5
    sla_val = creator.sla_score or 90.0
    # Map rating 3.0–5.0 to 0–3.0 pts, SLA 70–100% to 0–2.0 pts
    rating_score = round(
        max(0.0, (rating_val - 3.0) / 2.0) * 3.0 + max(0.0, (sla_val - 70.0) / 30.0) * 2.0,
        2
    )
    rating_score = min(5.0, max(0.0, rating_score))

    total_score = min(100.0, category_score + tools_score + style_score + price_score + avail_score + rating_score)

    score_breakdown = {
        "style_match": round(style_score, 1),
        "tools_match": round(tools_score, 1),
        "skills_match": round(category_score, 1),
        "availability_match": round(avail_score, 1),
        "delivery_match": round(price_score, 1),
        "rights_match": round(rating_score, 1),
        "portfolio_match": 5.0,
    }

    # Construct the clear human-readable explanation
    # E.g.: "Recommended because this creator specializes in AI Images, uses Flux and Midjourney, and fits your ₹60,000 project budget."
    tools_phrase = ""
    highlight_tools = matched_tools if matched_tools else (creator.ai_tools[:2] if creator.ai_tools else ["AI Creative Suites"])
    clean_tool_names = [t.replace(".1", "").replace(" v6", "") for t in highlight_tools[:2]]
    if len(clean_tool_names) == 1:
        tools_phrase = clean_tool_names[0]
    elif len(clean_tool_names) >= 2:
        tools_phrase = f"{clean_tool_names[0]} and {clean_tool_names[1]}"

    budget_phrase = ""
    if budget > 0 and creator_rate <= budget:
        budget_phrase = f"fits your ₹{int(budget):,} project budget"
    elif budget > 0:
        budget_phrase = f"offers starting rate at ₹{int(creator_rate):,}"
    else:
        budget_phrase = f"maintains a {creator.rating}★ rating"

    spec_label = target_category if direct_category_match else (creator.specialization.split("&")[0].strip())
    if tools_phrase:
        recommendation_reason = f"Recommended because this creator specializes in {spec_label}, uses {tools_phrase}, and {budget_phrase}."
    else:
        recommendation_reason = f"Recommended because this creator specializes in {spec_label} and {budget_phrase}."

    return score_breakdown, recommendation_reason, match_reasons, total_score


def match_creators_for_brief(brief: Brief, creators: List[CreatorProfile]) -> List[Dict[str, Any]]:
    """Legacy helper for Brief model matching."""
    return recommend_top_creators(
        category=brief.content_type or "AI Videos",
        content_type=brief.content_type or "",
        style=brief.style or "",
        tools_suggested=brief.tools_suggested or [],
        budget_max=brief.budget_max or 0.0,
        budget_min=brief.budget_min or 0.0,
        description=brief.description or "",
        creators=creators,
        limit=10,
    )
