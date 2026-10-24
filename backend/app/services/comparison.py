"""Creator comparison and deterministic difference engine."""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.creators import CreatorProfile
from app.models.briefs import Brief
from app.schemas.comparison import CreatorCompareCard, DifferenceItem, CreatorComparisonResponse
from app.services.trust import evaluate_creator_trust
from app.services.licensing import check_licensing_compatibility
from app.services.matching import score_creator_for_recommendation


def build_compare_card(
    creator: CreatorProfile,
    db: Session,
    brief: Optional[Brief] = None,
    target_category: Optional[str] = None,
    budget: float = 0.0,
    timeline_days: int = 7,
) -> CreatorCompareCard:
    """Constructs a normalized comparison card with match scores and licensing fit."""
    trust_eval = evaluate_creator_trust(creator, db)

    # Calculate match score & strengths/concerns
    category = target_category or (brief.content_type if brief else creator.core_category or "AI Video")
    b_min = brief.budget_min if brief else 0.0
    b_max = brief.budget_max if brief else (budget or 0.0)
    tools_req = brief.tools_suggested if brief else []
    desc = brief.description if brief else ""
    style = brief.style if brief else ""

    score_bd, rec_reason, match_reasons, total_score = score_creator_for_recommendation(
        creator=creator,
        target_category=category,
        content_type=brief.content_type if brief else "",
        style=style,
        tools_suggested=tools_req,
        budget=b_max or budget,
        timeline_days=timeline_days,
        description=desc,
    )

    # Licensing checks
    brief_lic = getattr(brief, "licensing", None) if brief else None
    creator_lic = getattr(creator, "licensing", None)
    lic_res = check_licensing_compatibility(brief_lic, creator_lic)

    lic_territory = "Worldwide" if creator_lic and "worldwide" in (creator_lic.territories or []) else "India"
    lic_duration = f"{creator_lic.max_duration_months} Months" if creator_lic and creator_lic.max_duration_months else "12 Months"
    if creator_lic and creator_lic.max_duration_months == 0:
        lic_duration = "Perpetual"

    # Strengths & Things to consider
    strengths = list(match_reasons)
    if lic_res["licensing_strengths"]:
        strengths.append(lic_res["licensing_strengths"][0])
    if trust_eval.is_rising_creator:
        strengths.append("High agility rising creator with verified workflow")

    things_to_consider = []
    if lic_res["licensing_conflicts"]:
        things_to_consider.extend(lic_res["licensing_conflicts"])
    if (b_max > 0 or budget > 0) and creator.starting_rate > (b_max or budget):
        things_to_consider.append(f"Day rate (₹{int(creator.starting_rate):,}) exceeds target budget")
    if creator.delivery_days > timeline_days:
        things_to_consider.append(f"Turnaround is {creator.delivery_days} days vs requested {timeline_days} days")
    if trust_eval.reliability.status != "Reliable":
        things_to_consider.append(f"Marketplace notice: {trust_eval.reliability.status}")
    if not things_to_consider:
        things_to_consider.append("No critical conflicts identified for this brief")

    portfolio_samples = [
        {
            "id": p.id,
            "title": p.title,
            "category": p.category,
            "image_url": p.image_url,
            "tools_used": p.tools_used or [],
        }
        for p in (creator.portfolio_items or [])[:4]
    ]

    return CreatorCompareCard(
        creator_id=creator.id,
        user_id=creator.user_id,
        display_name=creator.display_name,
        avatar_url=creator.user.avatar_url if creator.user else None,
        specialization=creator.specialization,
        core_category=creator.core_category or "AI Video",
        starting_rate=creator.starting_rate or 25000.0,
        delivery_days=creator.delivery_days or 7,
        rating=creator.rating or 5.0,
        sla_score=creator.sla_score or 98.0,
        match_score=int(round(total_score)),
        ai_tools=creator.ai_tools or [],
        portfolio_count=len(creator.portfolio_items or []),
        portfolio_samples=portfolio_samples,
        licensing_status=lic_res["licensing_status"],
        licensing_summary="Worldwide Commercial Grant" if lic_territory == "Worldwide" else "India Commercial Rights",
        licensing_territory=lic_territory,
        licensing_duration=lic_duration,
        is_rising_creator=trust_eval.is_rising_creator,
        reliability=trust_eval.reliability,
        badges=trust_eval.badges,
        strengths=strengths[:4],
        things_to_consider=things_to_consider[:3],
    )


def generate_difference_explanations(candidates: List[CreatorCompareCard]) -> List[DifferenceItem]:
    """
    Computes pairwise or triplet differences from real platform data.
    Answers: 'What A has that B doesn't' and 'What B has that A doesn't'.
    """
    if len(candidates) < 2:
        return []

    diff_items: List[DifferenceItem] = []

    for i, c_current in enumerate(candidates):
        others = [c for j, c in enumerate(candidates) if j != i]
        unique_advantages: List[str] = []
        tradeoffs: List[str] = []

        # 1. Day rate comparison
        cheaper_than_all = all(c_current.starting_rate < o.starting_rate for o in others)
        more_expensive_than_all = all(c_current.starting_rate > o.starting_rate for o in others)
        if cheaper_than_all:
            diff_amount = int(min(o.starting_rate for o in others) - c_current.starting_rate)
            unique_advantages.append(f"Most cost-effective (saves ₹{diff_amount:,} per day vs others)")
        elif more_expensive_than_all:
            premium_amount = int(c_current.starting_rate - max(o.starting_rate for o in others))
            tradeoffs.append(f"Higher project investment (+₹{premium_amount:,} premium over alternatives)")

        # 2. Turnaround velocity
        faster_than_all = all(c_current.delivery_days < o.delivery_days for o in others)
        slower_than_all = all(c_current.delivery_days > o.delivery_days for o in others)
        if faster_than_all:
            diff_days = min(o.delivery_days for o in others) - c_current.delivery_days
            unique_advantages.append(f"Fastest delivery turnaround ({c_current.delivery_days} days, {diff_days} days faster)")
        elif slower_than_all:
            diff_days = c_current.delivery_days - max(o.delivery_days for o in others)
            tradeoffs.append(f"Longer lead time ({c_current.delivery_days} days, +{diff_days} days slower)")

        # 3. Licensing coverage
        has_worldwide = "worldwide" in c_current.licensing_territory.lower()
        others_lack_worldwide = any("worldwide" not in o.licensing_territory.lower() for o in others)
        if has_worldwide and others_lack_worldwide:
            unique_advantages.append("Broader licensing rights (Worldwide coverage included)")

        # 4. Tool distinctions
        current_tools = set(t.lower() for t in c_current.ai_tools)
        other_tools = set(t.lower() for o in others for t in o.ai_tools)
        unique_tool_names = [t for t in c_current.ai_tools if t.lower() not in other_tools]
        if unique_tool_names:
            unique_advantages.append(f"Unique tool mastery: {', '.join(unique_tool_names[:2])}")

        # 5. Portfolio volume & rating
        if c_current.portfolio_count > max(o.portfolio_count for o in others):
            unique_advantages.append(f"Deepest portfolio evidence ({c_current.portfolio_count} catalog pieces)")
        elif c_current.portfolio_count < min(o.portfolio_count for o in others):
            tradeoffs.append(f"More focused portfolio showcase ({c_current.portfolio_count} published works)")

        if c_current.rating > max(o.rating for o in others):
            unique_advantages.append(f"Highest verified rating ({c_current.rating} stars)")

        if c_current.is_rising_creator:
            unique_advantages.append("Rising Creator agility: dedicated attention and direct collaboration")

        if not unique_advantages:
            unique_advantages.append(f"Strong balanced candidate with {c_current.match_score}% brief alignment")
        if not tradeoffs:
            tradeoffs.append("Balanced profile with no standout operational disadvantages")

        diff_items.append(
            DifferenceItem(
                creator_id=c_current.creator_id,
                creator_name=c_current.display_name,
                unique_advantages=unique_advantages,
                tradeoffs_vs_others=tradeoffs,
            )
        )

    return diff_items


def compare_creators(
    creator_ids: List[int],
    db: Session,
    brief_id: Optional[int] = None,
    target_category: Optional[str] = None,
    budget: float = 0.0,
    timeline_days: int = 7,
) -> CreatorComparisonResponse:
    """Orchestrates side-by-side comparison for 2 or 3 creators."""
    brief = db.query(Brief).filter(Brief.id == brief_id).first() if brief_id else None
    creators = db.query(CreatorProfile).filter(CreatorProfile.id.in_(creator_ids)).all()

    # Preserve requested order
    id_map = {c.id: c for c in creators}
    ordered_creators = [id_map[cid] for cid in creator_ids if cid in id_map]

    cards = [
        build_compare_card(
            creator=c,
            db=db,
            brief=brief,
            target_category=target_category,
            budget=budget,
            timeline_days=timeline_days,
        )
        for c in ordered_creators
    ]

    differences = generate_difference_explanations(cards)

    top_candidate = max(cards, key=lambda c: c.match_score) if cards else None
    verdict = (
        f"{top_candidate.display_name} holds the highest overall brief compatibility ({top_candidate.match_score}%), "
        f"while alternatives provide distinct budget or turnaround advantages."
        if top_candidate
        else "Comparison complete."
    )

    return CreatorComparisonResponse(
        candidates=cards,
        difference_explanations=differences,
        summary_verdict=verdict,
    )
