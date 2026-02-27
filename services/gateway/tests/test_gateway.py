from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _make_httpx_response(status_code: int, json_data: dict) -> MagicMock:
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = status_code
    mock_resp.content = str(json_data).encode()
    mock_resp.headers = {"content-type": "application/json"}
    mock_resp.json.return_value = json_data
    return mock_resp


def _make_async_client(response: MagicMock) -> MagicMock:
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.request = AsyncMock(return_value=response)
    return mock_client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_public_register_no_auth_required(client):
    resp_data = {"id": 1, "username": "nikita"}
    mock_resp = _make_httpx_response(201, resp_data)
    mock_async = _make_async_client(mock_resp)

    with patch("httpx.AsyncClient", return_value=mock_async):
        resp = client.post(
            "/register",
            json={"username": "nikita", "password": "pass"},
        )
    assert resp.status_code == 201


def test_public_login_no_auth_required(client):
    resp_data = {"access_token": "tok", "token_type": "bearer"}
    mock_resp = _make_httpx_response(200, resp_data)
    mock_async = _make_async_client(mock_resp)

    with patch("httpx.AsyncClient", return_value=mock_async):
        resp = client.post(
            "/login",
            json={"username": "nikita", "password": "pass"},
        )
    assert resp.status_code == 200


def test_protected_endpoint_no_token(client):
    resp = client.get("/profile")
    assert resp.status_code == 401


def test_protected_endpoint_invalid_token(client):
    resp = client.get(
        "/profile",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert resp.status_code == 401


def test_unknown_route(client):
    with patch("app.main.decode_jwt", return_value={"sub": 1}):
        resp = client.get(
            "/unknown/path",
            headers={"Authorization": "Bearer dummy"},
        )
    assert resp.status_code == 404


def test_cards_route_forwarded(client):
    resp_data = [
        {
            "id": 1,
            "name": "Geralt",
            "strength": 15,
            "faction": "Neutral",
            "type": "Hero",
            "description": "",
        }
    ]
    mock_resp = _make_httpx_response(200, resp_data)
    mock_async = _make_async_client(mock_resp)

    with (
        patch("app.main.decode_jwt", return_value={"sub": 1}),
        patch("httpx.AsyncClient", return_value=mock_async),
    ):
        resp = client.get(
            "/cards",
            headers={"Authorization": "Bearer valid_token"},
        )
    assert resp.status_code == 200


def test_games_route_forwarded(client):
    resp_data = {
        "id": 1,
        "player1_id": 1,
        "player2_id": 2,
        "player1_deck_id": 1,
        "player2_deck_id": 2,
        "state": "in_progress",
        "current_turn": 1,
        "score1": 0,
        "score2": 0,
    }
    mock_resp = _make_httpx_response(201, resp_data)
    mock_async = _make_async_client(mock_resp)

    with (
        patch("app.main.decode_jwt", return_value={"sub": 1}),
        patch("httpx.AsyncClient", return_value=mock_async),
    ):
        resp = client.post(
            "/games",
            json={
                "player1_id": 1,
                "player2_id": 2,
                "player1_deck_id": 1,
                "player2_deck_id": 2,
            },
            headers={"Authorization": "Bearer valid_token"},
        )
    assert resp.status_code == 201
