"""
Tests pour les routes de chat
"""
import pytest


def test_send_message_success(client, auth_headers):
    """Test d'envoi de message réussi"""
    response = client.post(
        "/api/chat/send",
        json={"message": "Bonjour, j'ai été licencié sans préavis"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "conversation_id" in data
    assert isinstance(data["conversation_id"], int)


def test_send_message_unauthorized(client):
    """Test d'envoi de message sans authentification"""
    response = client.post(
        "/api/chat/send",
        json={"message": "Test message"}
    )
    assert response.status_code == 401


def test_send_empty_message(client, auth_headers):
    """Test d'envoi de message vide"""
    response = client.post(
        "/api/chat/send",
        json={"message": ""},
        headers=auth_headers
    )
    assert response.status_code == 422


def test_send_message_too_long(client, auth_headers):
    """Test d'envoi de message trop long"""
    long_message = "a" * 6000
    response = client.post(
        "/api/chat/send",
        json={"message": long_message},
        headers=auth_headers
    )
    assert response.status_code == 422


def test_conversation_continuity(client, auth_headers):
    """Test de continuité d'une conversation"""
    # Premier message
    response1 = client.post(
        "/api/chat/send",
        json={"message": "Premier message"},
        headers=auth_headers
    )
    conversation_id = response1.json()["conversation_id"]
    
    # Deuxième message dans la même conversation
    response2 = client.post(
        "/api/chat/send",
        json={
            "message": "Deuxième message",
            "conversation_id": conversation_id
        },
        headers=auth_headers
    )
    assert response2.status_code == 200
    assert response2.json()["conversation_id"] == conversation_id


def test_get_conversations(client, auth_headers):
    """Test de récupération de la liste des conversations"""
    # Créer une conversation
    client.post(
        "/api/chat/send",
        json={"message": "Test message"},
        headers=auth_headers
    )
    
    response = client.get("/api/chat/conversations", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_conversations_unauthorized(client):
    """Test de récupération des conversations sans authentification"""
    response = client.get("/api/chat/conversations")
    assert response.status_code == 401


def test_delete_conversation(client, auth_headers):
    """Test de suppression d'une conversation"""
    # Créer une conversation
    response = client.post(
        "/api/chat/send",
        json={"message": "Test message"},
        headers=auth_headers
    )
    conversation_id = response.json()["conversation_id"]
    
    # Supprimer la conversation
    delete_response = client.delete(
        f"/api/chat/conversations/{conversation_id}",
        headers=auth_headers
    )
    assert delete_response.status_code == 200
    
    # Vérifier qu'elle n'existe plus
    conversations = client.get("/api/chat/conversations", headers=auth_headers)
    assert len(conversations.json()) == 0


def test_delete_nonexistent_conversation(client, auth_headers):
    """Test de suppression d'une conversation inexistante"""
    response = client.delete(
        "/api/chat/conversations/99999",
        headers=auth_headers
    )
    assert response.status_code == 404


def test_get_stats(client, auth_headers):
    """Test de récupération des statistiques"""
    # Créer des données
    client.post(
        "/api/chat/send",
        json={"message": "Test message"},
        headers=auth_headers
    )
    
    response = client.get("/api/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "conversations" in data
    assert "messages" in data
    assert data["conversations"]["total"] > 0


def test_get_cases(client):
    """Test de récupération de la liste des cas juridiques"""
    response = client.get("/api/chat/cases")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "cases" in data
    assert data["total"] == 10
    assert len(data["cases"]) == 10
    
    # Vérifier structure d'un cas
    first_case = data["cases"][0]
    assert "id" in first_case
    assert "titre" in first_case
    assert "description" in first_case
