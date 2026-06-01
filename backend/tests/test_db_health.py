from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_database_health_endpoint():
    response = client.get("/db/health")

    assert response.status_code == 200
    assert response.json() == {"database": "ok"}
