import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import app.storage as storage

from app.main import app

client = TestClient(app)

class TestDeckServiceIntegration:
    """Тесты, имитирующие взаимодействие Deck-сервиса с Card-сервисом."""
    
    def test_deck_service_gets_card_by_id(self):
        """Deck-сервис запрашивает карту по ID для отображения в колоде."""
        # Создаём карту
        resp = client.post("/cards", json={
            "name": "Test Card",
            "strength": 5,
            "faction": "Neutral",
            "type": "Unit"
        })
        card_id = resp.json()["id"]
        
        # Deck-сервис запрашивает её
        get_resp = client.get(f"/cards/{card_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == card_id
    
    def test_deck_service_handles_missing_card(self):
        """Deck-сервис пытается добавить в колоду несуществующую карту."""
        resp = client.get("/cards/99999")
        assert resp.status_code == 404
        # Deck-сервис на основе 404 покажет пользователю ошибку
    storage.reset()
    def test_deck_service_filters_cards_for_collection(self):
        """Deck-сервис запрашивает все карты определённой фракции для UI."""
        # Создаём карты разных фракций
        client.post("/cards", json={"name": "A", "strength": 1, "faction": "Neutral", "type": "Unit"})
        client.post("/cards", json={"name": "B", "strength": 1, "faction": "Monster", "type": "Unit"})
        client.post("/cards", json={"name": "C", "strength": 1, "faction": "Neutral", "type": "Hero"})
        
        # Deck-сервис хочет показать пользователю только Neutral карты
        resp = client.get("/cards?faction=Neutral")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert all(c["faction"] == "Neutral" for c in data)
