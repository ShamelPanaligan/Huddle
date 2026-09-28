import pytest
from fastapi.testclient import TestClient

import db
import main

client = TestClient(main.app)

@pytest.fixture(autouse=True)
def use_temp_database(tmp_path, monkeypatch):
    test_db_path = tmp_path / "test_event_matcher.db"
    monkeypatch.setattr(db, "DB_PATH", test_db_path)

def test_register_success_excludes_password_hash():
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "password": "test123",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "newuser@example.com"
    assert "password_hash" not in body

def test_register_duplicate_email_returns_400():
    first_response = client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "test123",
    })

    second_response = client.post("/auth/register", json={
        "email":"duplicate@example.com",
        "password": "DifferingPassword",
    })

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Email already registered"

def test_login_success_returns_token():
    client.post("/auth/register", json={
        "email": "example@fakemaiil.com",
        "password": "passPass"
    }) 
    response = client.post("/auth/login", json={
        "email": "example@fakemaiil.com",
        "password": "passPass"
    })

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

def test_login_wrong_password_returns_401():
    # register a user, then try logging in with a different password
    client.post("/auth/register", json={
        "email": "fake@mail.com",
        "password": "fakePass"
    })
    response = client.post("/auth/login", json={
        "email": "fake@mail.com",
        "password": "MyPass"
    })

    assert response.status_code == 401

def test_me_with_valid_token_returns_user():
    client.post("/auth/register", json={
    "email": "me@example.com",
    "password": "test123"})
    login_response = client.post("/auth/login", json={
    "email": "me@example.com",
    "password": "test123"})

    token = login_response.json()["access_token"]
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"

def test_me_with_no_token_returns_401():    
    response = client.get("/me")
    assert response.status_code == 401

def test_me_with_invalid_token_returns_401():
    response = client.get("/me", headers={"Authorization": "Bearer not-real-token"})
    assert response.status_code ==401

def get_auth_headers(email= "user@example.com", password= "FakePass"):
    client.post("/auth/register", json={
    "email": email,
    "password": password})
    
    login = client.post("auth/login", json={
    "email": email,
    "password": password
    })

    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_event_idea_requires_auth():
    response = client.post("/event-ideas", json={
    "title": "Board Game Night",
    "min_headcount": 4,
    "max_headcount": 12,
    "duration_min": 240,
    })
    assert response.status_code == 401

def test_create_event_idea_creator_id_comes_from_token_not_body():
    headers = get_auth_headers()
    response = client.post("/event-ideas", json={
    "title": "Board Game Night",
    "min_headcount": 4,
    "max_headcount": 12,
    "duration_min": 240,
    "creator_id":999,
    }, headers= headers)

    assert response.status_code == 200
    me = client.get("/me", headers= headers)
    real_user_id = me.json()["id"]

    assert response.json()["creator_id"] == real_user_id
    assert response.json()["creator_id"] != 999    