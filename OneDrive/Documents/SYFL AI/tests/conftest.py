"""
Configuration pour les tests pytest
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Créer une base de données de test pour chaque test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Client de test FastAPI"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    # Désactiver le rate limiting pour les tests
    app.state.limiter.enabled = False
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.state.limiter.enabled = True
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Données utilisateur pour les tests"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test123456",
        "full_name": "Test User"
    }


@pytest.fixture
def auth_headers(client, test_user_data):
    """Headers d'authentification pour les tests"""
    # Enregistrer l'utilisateur
    response = client.post("/api/auth/register", json=test_user_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
