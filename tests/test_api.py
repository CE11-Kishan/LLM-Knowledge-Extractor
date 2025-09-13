import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.database import get_db, Base
from app.models import Analysis

SQLITE_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLITE_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@patch('app.routes.extract_text_insights')
def test_analyze_success(mock_llm, client, test_db):
    """Test successful text analysis"""
    mock_llm.return_value = ("Summary text", ["topic1", "topic2"], "Test Title", "positive")
    
    response = client.post("/analyze", json={"text": "This is a test text"})
    assert response.status_code == 200
    
    data = response.json()
    assert data["summary"] == "Summary text"
    assert data["topics"] == ["topic1", "topic2"]
    assert data["title"] == "Test Title"
    assert data["sentiment"] == "positive"

def test_analyze_empty_text(client, test_db):
    response = client.post("/analyze", json={"text": ""})
    assert response.status_code == 400
    assert "Input text cannot be empty" in response.json()["detail"]

def test_search_endpoint(client, test_db):
    db = TestingSessionLocal()
    analysis = Analysis(
        original_text="Test text",
        summary="Test summary", 
        topics="python,fastapi",
        sentiment="neutral",
        keywords="test,api",
        confidence=0.8
    )
    db.add(analysis)
    db.commit()
    db.close()
    
    response = client.get("/search?topic=python")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["results"]) == 1
    assert "python" in data["results"][0]["topics"]

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
