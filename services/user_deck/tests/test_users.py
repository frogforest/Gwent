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


def test_register_success(client):
    response = client.post(
        "/register", json={"username": "alice", "password": "pass123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert "id" in data


def test_register_duplicate(client):
    client.post("/register", json={"username": "alice", "password": "pass123"})
    response = client.post("/register", json={"username": "alice", "password": "other"})
    assert response.status_code == 409


def test_login_success(client):
    client.post("/register", json={"username": "bob", "password": "secret"})
    response = client.post("/login", json={"username": "bob", "password": "secret"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/register", json={"username": "bob", "password": "secret"})
    response = client.post("/login", json={"username": "bob", "password": "wrong"})
    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post("/login", json={"username": "nobody", "password": "x"})
    assert response.status_code == 401


def test_profile_authenticated(client):
    client.post("/register", json={"username": "carol", "password": "pw"})
    login = client.post("/login", json={"username": "carol", "password": "pw"})
    token = login.json()["access_token"]

    response = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "carol"


def test_profile_unauthenticated(client):
    response = client.get("/profile")
    assert response.status_code == 401
