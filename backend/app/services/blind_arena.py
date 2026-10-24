"""KreatorBuzz Blind Arena hiring engine.

Anonymizes creator reputation and popularity indicators so recruiters evaluate
candidates purely on work quality, portfolio evidence, and brief fit.
"""

import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.creators import CreatorProfile
from app.models.briefs import Brief
from app.schemas.blind_arena import (
    BlindArenaResponse,
    BlindCreatorCard,
    BlindPortfolioSample,
    BlindRevealResponse,
    WhatOthersDidBetter,
)
from app.services.comparison import build_compare_card, compare_creators

# In-memory mapping of session tokens to creator IDs (supports stateless token parsing too)
_BLIND_TOKEN_MAP: Dict[str, Dict[str, Any]] = {}

LETTERS = ["A", "B", "C", "D", "E", "F"]


def create_blind_arena(
    creator_ids: List[int],
    db: Session,
    brief_id: Optional[int] = None,
    target_category: Optional[str] = None,
    budget: float = 0.0,
    timeline_days: int = 7,
) -> BlindArenaResponse:
    """Generates an anonymized Blind Arena evaluation session."""
    arena_id = f"arena_{uuid.uuid4().hex[:10]}"
    brief = db.query(Brief).filter(Brief.id == brief_id).first() if brief_id else None
    creators = db.query(CreatorProfile).filter(CreatorProfile.id.in_(creator_ids)).all()

    # Preserve input ordering
    id_map = {c.id: c for c in creators}
    ordered = [id_map[cid] for cid in creator_ids if cid in id_map]

    cards: List[BlindCreatorCard] = []

    for idx, c in enumerate(ordered):
        letter = LETTERS[idx] if idx < len(LETTERS) else f"Candidate {idx+1}"
        anon_name = f"Creator {letter}"
        token = f"blind_{arena_id}_{c.id}_{uuid.uuid4().hex[:6]}"

        compare_card = build_compare_card(
            creator=c,
            db=db,
            brief=brief,
            target_category=target_category,
            budget=budget,
            timeline_days=timeline_days,
        )

        # Store for reveal
        _BLIND_TOKEN_MAP[token] = {
            "creator_id": c.id,
            "anonymous_id": anon_name,
            "arena_id": arena_id,
            "brief_id": brief_id,
            "target_category": target_category,
            "budget": budget,
            "timeline_days": timeline_days,
            "compare_card": compare_card,
        }

        # Anonymize portfolio samples: hide creator identity
        anon_portfolio = [
            BlindPortfolioSample(
                title=p["title"],
                category=p["category"],
                image_url=p["image_url"],
                tools_used=p.get("tools_used", []),
            )
            for p in compare_card.portfolio_samples
        ]

        # Anonymize strengths: strip real names if mentioned
        anon_strengths = [s.replace(c.display_name, anon_name) for s in compare_card.strengths]
        anon_concerns = [tc.replace(c.display_name, anon_name) for tc in compare_card.things_to_consider]

        cards.append(
            BlindCreatorCard(
                anonymous_id=anon_name,
                blind_token=token,
                specialization=compare_card.specialization,
                core_category=compare_card.core_category,
                match_score=compare_card.match_score,
                starting_rate=compare_card.starting_rate,
                delivery_days=compare_card.delivery_days,
                ai_tools=compare_card.ai_tools,
                portfolio_samples=anon_portfolio,
                licensing_status=compare_card.licensing_status,
                licensing_summary=compare_card.licensing_summary,
                is_rising_creator=compare_card.is_rising_creator,
                strengths=anon_strengths,
                things_to_consider=anon_concerns,
            )
        )

    return BlindArenaResponse(
        blind_arena_id=arena_id,
        tagline="Choose the work. Then meet the creator.",
        candidates=cards,
    )


def reveal_blind_creator(
    chosen_token: str,
    all_tokens: List[str],
    db: Session,
) -> BlindRevealResponse:
    """Reveals real creator identity and provides transparent decision explanation."""
    entry = _BLIND_TOKEN_MAP.get(chosen_token)
    if not entry:
        # Fallback decode if restarted or memory missed
        parts = chosen_token.split("_")
        if len(parts) >= 3 and parts[2].isdigit():
            c_id = int(parts[2])
            c = db.query(CreatorProfile).filter(CreatorProfile.id == c_id).first()
            if c:
                compare_card = build_compare_card(creator=c, db=db)
                entry = {
                    "creator_id": c_id,
                    "anonymous_id": "Chosen Creator",
                    "compare_card": compare_card,
                }

    if not entry:
        raise ValueError("Invalid or expired blind session token.")

    winner_card = entry["compare_card"]

    # Gather peer candidates
    peer_cards = []
    for tok in all_tokens:
        if tok != chosen_token and tok in _BLIND_TOKEN_MAP:
            peer_cards.append(_BLIND_TOKEN_MAP[tok])

    # Construct "Why this creator won"
    why_won_points = []
    if winner_card.portfolio_count > 0:
        why_won_points.append(f"portfolio visual evidence across {winner_card.portfolio_count} works")
    if "worldwide" in winner_card.licensing_territory.lower():
        why_won_points.append("worldwide commercial usage compatibility")
    if winner_card.delivery_days <= 5:
        why_won_points.append(f"rapid {winner_card.delivery_days}-day turnaround")
    if winner_card.match_score >= 85:
        why_won_points.append(f"highest brief fit score of {winner_card.match_score}%")

    reasons_str = ", ".join(why_won_points) if why_won_points else "superior portfolio and style alignment"
    why_won = f"{winner_card.display_name} won the Blind Arena evaluation due to {reasons_str}."

    # Construct "What the other candidates did better"
    what_others_did_better: List[WhatOthersDidBetter] = []
    for peer in peer_cards:
        p_card = peer["compare_card"]
        p_anon = peer.get("anonymous_id", "Alternative Candidate")
        strengths = []
        if p_card.starting_rate < winner_card.starting_rate:
            diff = int(winner_card.starting_rate - p_card.starting_rate)
            strengths.append(f"Offered ₹{diff:,}/day lower starting rate")
        if p_card.delivery_days < winner_card.delivery_days:
            diff_d = winner_card.delivery_days - p_card.delivery_days
            strengths.append(f"Offered faster turnaround by {diff_d} day(s)")
        if p_card.portfolio_count > winner_card.portfolio_count:
            strengths.append(f"Larger portfolio volume ({p_card.portfolio_count} works)")
        if not strengths:
            strengths.append(f"Strong alternative styling with {p_card.specialization}")

        what_others_did_better.append(
            WhatOthersDidBetter(
                anonymous_id=p_anon,
                strengths=strengths,
            )
        )

    return BlindRevealResponse(
        revealed_creator=winner_card,
        why_this_creator_won=why_won,
        what_others_did_better=what_others_did_better,
    )
