"""Workspaces and encrypted messaging tests."""

import pytest
from app.models.workspaces import WorkspaceMessage
from app.services.encryption import encrypt_message, decrypt_message


def test_encryption_service():
    secret = "Confidential Prompt Seed: cinematic 35mm film grain vintage 1970s"
    encrypted = encrypt_message(secret)
    assert encrypted != secret
    decrypted = decrypt_message(encrypted)
    assert decrypted == secret


def test_create_workspace_and_send_encrypted_message(client, brand_token, creator_user, db_session):
    # Brand creates a workspace
    ws_res = client.post(
        "/api/workspaces",
        headers={"Authorization": f"Bearer {brand_token}"},
        json={
            "creator_user_id": creator_user.id,
            "title": "Maison Lumina 2026 Collaboration",
        },
    )
    assert ws_res.status_code == 201
    ws_data = ws_res.json()
    ws_id = ws_data["id"]

    # Brand sends a message
    msg_res = client.post(
        f"/api/workspaces/{ws_id}/messages",
        headers={"Authorization": f"Bearer {brand_token}"},
        json={"content": "Here is the master color palette reference."},
    )
    assert msg_res.status_code == 201
    assert msg_res.json()["content"] == "Here is the master color palette reference."

    # Verify DB has encrypted content at rest
    raw_db_msg = db_session.query(WorkspaceMessage).filter(WorkspaceMessage.workspace_id == ws_id).order_by(WorkspaceMessage.id.desc()).first()
    assert raw_db_msg.encrypted_content != "Here is the master color palette reference."
    assert decrypt_message(raw_db_msg.encrypted_content) == "Here is the master color palette reference."

    # Retrieve workspace detail and check decrypted messages
    get_ws = client.get(
        f"/api/workspaces/{ws_id}",
        headers={"Authorization": f"Bearer {brand_token}"},
    )
    assert get_ws.status_code == 200
    messages = get_ws.json()["messages"]
    assert any(m["content"] == "Here is the master color palette reference." for m in messages)
