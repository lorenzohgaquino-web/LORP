import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
import uuid

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()

def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_crawl_endpoint():
    response = client.post("/api/v1/crawl", json={
        "seed_urls": ["https://www.cos.ufrj.br"],
        "max_depth": 0
    })
    assert response.status_code == 200
    assert "message" in response.json()

def test_entities_endpoint():
    response = client.get("/api/v1/entities")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_export_endpoint():
    response = client.get("/api/v1/export")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
