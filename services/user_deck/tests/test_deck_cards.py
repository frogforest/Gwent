from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import app.storage as storage
from app.main import app


@pytest.fixture(autouse=True)
def reset_storage():
    storage.reset()
    yield
    storage.reset()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _register_and_login(
    client: TestClient, username: str = "user1", password: str = "pass"
) -> str:
    client.post("/register", json={"username": username, "password": password})
    resp = client.post("/login", json={"username": username, "password": password})
    return resp.json()["access_token"]


def _create_deck(client: TestClient, token: str, name: str = "Deck") -> int:
    resp = client.post(
        "/decks",
        json={"name": name},
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.json()["id"]


@patch("app.routers.decks.card_exists", return_value=True)
def test_add_card_to_deck(mock_exists, client):
    token = _register_and_login(client)
    deck_id = _create_deck(client, token)

    resp = client.post(
        f"/decks/{deck_id}/cards/42",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert 42 in data["card_ids"]


@patch("app.routers.decks.card_exists", return_value=False)
def test_add_nonexistent_card_to_deck(mock_exists, client):
    token = _register_and_login(client)
    deck_id = _create_deck(client, token)

    resp = client.post(
        f"/decks/{deck_id}/cards/999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


@patch("app.routers.decks.card_exists", return_value=True)
def test_add_duplicate_card_to_deck(mock_exists, client):
    token = _register_and_login(client)
    deck_id = _create_deck(client, token)

    client.post(
        f"/decks/{deck_id}/cards/7",
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = client.post(
        f"/decks/{deck_id}/cards/7",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 409


@patch("app.routers.decks.card_exists", return_value=True)
def test_remove_card_from_deck(mock_exists, client):
    token = _register_and_login(client)
    deck_id = _create_deck(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    client.post(f"/decks/{deck_id}/cards/5", headers=headers)
    resp = client.delete(f"/decks/{deck_id}/cards/5", headers=headers)
    assert resp.status_code == 200
    assert 5 not in resp.json()["card_ids"]


def test_remove_card_not_in_deck(client):
    token = _register_and_login(client)
    deck_id = _create_deck(client, token)

    resp = client.delete(
        f"/decks/{deck_id}/cards/999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


@patch("app.routers.decks.card_exists", return_value=True)
def test_deck_contains_card_ids_in_response(mock_exists, client):
    token = _register_and_login(client)
    deck_id = _create_deck(client, token)
    headers = {"Authorization": f"Bearer {token}"}

    client.post(f"/decks/{deck_id}/cards/1", headers=headers)
    client.post(f"/decks/{deck_id}/cards/2", headers=headers)
    client.post(f"/decks/{deck_id}/cards/3", headers=headers)

    resp = client.get(f"/decks/{deck_id}", headers=headers)
    assert resp.status_code == 200
    assert sorted(resp.json()["card_ids"]) == [1, 2, 3]


@patch("app.routers.decks.card_exists", return_value=True)
def test_other_user_cannot_add_card(mock_exists, client):
    token1 = _register_and_login(client, "alice")
    token2 = _register_and_login(client, "bob", "pw2")
    deck_id = _create_deck(client, token1)

    resp = client.post(
        f"/decks/{deck_id}/cards/10",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert resp.status_code == 403
