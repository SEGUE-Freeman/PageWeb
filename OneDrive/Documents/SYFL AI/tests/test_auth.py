"""
Tests pour les routes d'authentification
"""
import pytest


def test_register_success(client, test_user_data):
    """Test d'inscription réussie"""
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client, test_user_data):
    """Test d'inscription avec email déjà utilisé"""
    client.post("/api/auth/register", json=test_user_data)
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


def test_register_invalid_email(client, test_user_data):
    """Test d'inscription avec email invalide"""
    test_user_data["email"] = "invalid-email"
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 422


def test_register_weak_password(client, test_user_data):
    """Test d'inscription avec mot de passe faible"""
    test_user_data["password"] = "weak"
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 422


def test_register_short_username(client, test_user_data):
    """Test d'inscription avec username trop court"""
    test_user_data["username"] = "ab"
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 422


def test_login_success(client, test_user_data):
    """Test de connexion réussie"""
    client.post("/api/auth/register", json=test_user_data)
    response = client.post("/api/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_wrong_password(client, test_user_data):
    """Test de connexion avec mauvais mot de passe"""
    client.post("/api/auth/register", json=test_user_data)
    response = client.post("/api/auth/login", json={
        "email": test_user_data["email"],
        "password": "WrongPassword123"
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Test de connexion avec utilisateur inexistant"""
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "Password123"
    })
    assert response.status_code == 401


def test_get_me_success(client, auth_headers):
    """Test de récupération du profil"""
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "username" in data
    assert data["email"] == "test@example.com"


def test_get_me_unauthorized(client):
    """Test de récupération du profil sans authentification"""
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_get_me_invalid_token(client):
    """Test de récupération du profil avec token invalide"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401
