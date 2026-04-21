import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock

import app.storage as storage
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        storage.reset()
        yield c
        storage.reset()


def _add_test_cards(client: TestClient, count: int = 5) -> None:
    for i in range(count):
        client.post(
            "/cards",
            json={
                "name": f"Test Card {i}",
                "strength": i + 1,
                "faction": "Neutral" if i % 2 == 0 else "Monster",
                "type": "Unit" if i % 3 == 0 else "Hero",
            },
        )


class TestDeckServiceIntegration:

    def test_deck_service_gets_card_by_id(self, client):
        resp = client.post(
            "/cards",
            json={
                "name": "Geralt of Rivia",
                "strength": 15,
                "faction": "Neutral",
                "type": "Hero",
                "description": "A witcher.",
            },
        )
        assert resp.status_code == 201
        card_id = resp.json()["id"]

        get_resp = client.get(f"/cards/{card_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == "Geralt of Rivia"
        assert get_resp.json()["id"] == card_id

    def test_deck_service_handles_missing_card(self, client):
        resp = client.get("/cards/99999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Card not found"

    def test_deck_service_gets_random_cards_for_quick_deck(self, client):
        _add_test_cards(client, 10)
        resp = client.get("/cards/random?count=7")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 7

        for card in data:
            assert "id" in card
            assert "name" in card
            assert "strength" in card

    def test_deck_service_filters_cards_by_faction_for_ui(self, client):
        client.post("/cards", json={"name": "A", "strength": 1, "faction": "Neutral", "type": "Unit"})
        client.post("/cards", json={"name": "B", "strength": 2, "faction": "Monster", "type": "Unit"})
        client.post("/cards", json={"name": "C", "strength": 3, "faction": "Neutral", "type": "Hero"})
        client.post("/cards", json={"name": "D", "strength": 4, "faction": "Northern Realms", "type": "Unit"})

        resp = client.get("/cards?faction=Neutral")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert all(c["faction"] == "Neutral" for c in data)

    def test_deck_service_filters_by_type_and_faction_combined(self, client):

        client.post("/cards", json={"name": "A", "strength": 1, "faction": "Monster", "type": "Hero"})
        client.post("/cards", json={"name": "B", "strength": 2, "faction": "Monster", "type": "Unit"})
        client.post("/cards", json={"name": "C", "strength": 3, "faction": "Neutral", "type": "Hero"})

        resp = client.get("/cards?faction=Monster&type=Hero")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "A"
