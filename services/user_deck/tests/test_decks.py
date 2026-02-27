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


def test_create_deck(client):
    token = _register_and_login(client)
    response = client.post(
        "/decks",
        json={"name": "My Deck"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Deck"


def test_list_decks(client):
    token = _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/decks", json={"name": "Deck A"}, headers=headers)
    client.post("/decks", json={"name": "Deck B"}, headers=headers)
    response = client.get("/decks", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_deck(client):
    token = _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    create = client.post("/decks", json={"name": "Solo"}, headers=headers)
    deck_id = create.json()["id"]
    response = client.get(f"/decks/{deck_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Solo"


def test_get_deck_not_found(client):
    token = _register_and_login(client)
    response = client.get("/decks/9999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_delete_deck(client):
    token = _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}
    create = client.post("/decks", json={"name": "ToDelete"}, headers=headers)
    deck_id = create.json()["id"]
    response = client.delete(f"/decks/{deck_id}", headers=headers)
    assert response.status_code == 204
    get = client.get(f"/decks/{deck_id}", headers=headers)
    assert get.status_code == 404


def test_deck_isolation_between_users(client):
    token1 = _register_and_login(client, "user1")
    token2 = _register_and_login(client, "user2", "pw2")
    create = client.post(
        "/decks",
        json={"name": "Private"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    deck_id = create.json()["id"]
    response = client.get(
        f"/decks/{deck_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert response.status_code == 403
