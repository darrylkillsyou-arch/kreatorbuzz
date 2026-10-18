"""Brief builder and AI generation tests."""

import pytest


def test_brief_ai_builder_fallback(client):
    """Tests the fallback NLP brief generation when no Gemini API key is configured."""
    response = client.post(
        "/api/briefs/generate",
        json={
            "prompt": "We need a 30-second luxury cyber runway video for our Paris fashion week drop using Runway Gen-3 and Midjourney. Budget around $5,000.",
            "additional_notes": "Targeting high-end fashion enthusiasts.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "video" in data["content_type"].lower() or "fashion" in data["content_type"].lower()
    assert "9:16" in data["aspect_ratio"] or "16:9" in data["aspect_ratio"]
    assert len(data["tools_suggested"]) > 0
    assert data["budget_max"] >= 3000


def test_create_and_get_brief(client, brand_token):
    create_res = client.post(
        "/api/briefs",
        headers={"Authorization": f"Bearer {brand_token}"},
        json={
            "title": "Aethelgard 2026 Hypercar Reveal",
            "description": "High-concept luxury automotive commercial.",
            "content_type": "video",
            "style": "Warm Editorial Luxury",
            "platform": ["Instagram Reels", "YouTube"],
            "aspect_ratio": "16:9",
            "deliverables": ["4K Master ProRes"],
            "tools_suggested": ["Midjourney v6", "Runway Gen-3"],
            "budget_min": 3000.0,
            "budget_max": 6000.0,
            "commercial_rights_required": True,
            "status": "published",
        },
    )
    assert create_res.status_code == 201
    brief_data = create_res.json()
    brief_id = brief_data["id"]

    get_res = client.get(f"/api/briefs/{brief_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Aethelgard 2026 Hypercar Reveal"
