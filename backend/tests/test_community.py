"""Community feed and engagement tests."""

import pytest


def test_create_and_list_posts(client, creator_token):
    post_res = client.post(
        "/api/community/posts",
        headers={"Authorization": f"Bearer {creator_token}"},
        json={
            "post_type": "showcase",
            "title": "Aethelgard Cinematic Breakdown",
            "content": "Exploring kinetic camera workflows in Runway Gen-3.",
            "image_url": "https://images.unsplash.com/photo-1503376780353-7e6692767b70",
            "tools_tags": ["Runway Gen-3", "Midjourney"],
        },
    )
    assert post_res.status_code == 201
    post_id = post_res.json()["id"]

    list_res = client.get("/api/community/posts")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_like_and_comment_post(client, creator_token, brand_token):
    post_res = client.post(
        "/api/community/posts",
        headers={"Authorization": f"Bearer {creator_token}"},
        json={
            "post_type": "showcase",
            "title": "Kinetic Silk Simulation",
            "content": "Cloth simulation testing.",
            "tools_tags": ["ComfyUI"],
        },
    )
    post_id = post_res.json()["id"]

    # Brand likes the post
    like_res = client.post(
        f"/api/community/posts/{post_id}/like",
        headers={"Authorization": f"Bearer {brand_token}"},
    )
    assert like_res.status_code == 200
    assert like_res.json()["liked"] is True
    assert like_res.json()["likes_count"] == 1

    # Brand comments on the post
    comment_res = client.post(
        f"/api/community/posts/{post_id}/comment",
        headers={"Authorization": f"Bearer {brand_token}"},
        json={"content": "Incredible lighting and fluid movement!"},
    )
    assert comment_res.status_code == 201
    assert comment_res.json()["content"] == "Incredible lighting and fluid movement!"
