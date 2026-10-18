"""Creator matching algorithm tests."""

import pytest
from app.models.briefs import Brief
from app.models.creators import CreatorProfile
from app.services.matching import match_creators_for_brief


def test_creator_matching_algorithm(db_session, brand_user, creator_user):
    brief = Brief(
        brand_user_id=brand_user.id,
        title="Luxury Automotive Runway Video",
        description="High-end video commercial requiring Runway Gen-3 and Midjourney.",
        content_type="video",
        style="Cinematic Video & Luxury",
        tools_suggested=["Runway Gen-3", "Midjourney v6"],
        commercial_rights_required=True,
    )
    db_session.add(brief)
    db_session.commit()
    db_session.refresh(brief)

    creator_profile = db_session.query(CreatorProfile).first()
    results = match_creators_for_brief(brief, [creator_profile])

    assert len(results) == 1
    top_match = results[0]
    assert top_match["match_score"] >= 75
    assert len(top_match["match_reasons"]) > 0
    assert "style_match" in top_match["score_breakdown"]
    assert "tools_match" in top_match["score_breakdown"]
    assert "availability_match" in top_match["score_breakdown"]
    assert top_match["score_breakdown"]["style_match"] > 0
