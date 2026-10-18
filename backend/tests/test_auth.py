"""Authentication tests."""

import pytest


def test_register_brand_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newbrand@example.com",
            "password": "securepassword123",
            "full_name": "New Maison Brand",
            "role": "brand",
            "location": "Paris",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newbrand@example.com"
    assert data["user"]["role"] == "brand"


def test_register_creator_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newcreator@example.com",
            "password": "securepassword123",
            "full_name": "Neo Cinema Lab",
            "role": "creator",
            "location": "Tokyo",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["role"] == "creator"


def test_login_success(client, brand_user):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test_brand@maccall.demo",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test_brand@maccall.demo"


def test_login_invalid_credentials(client, brand_user):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test_brand@maccall.demo",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


def test_get_current_user_me(client, brand_token):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {brand_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_brand@maccall.demo"
