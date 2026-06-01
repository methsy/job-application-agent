from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_cv_profile():
    response = client.post(
        "/cv-profiles",
        json={
            "filename": "test_cv.txt",
            "raw_text": "Experienced software engineer with Java, Python, SQL and AWS.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert data["filename"] == "test_cv.txt"
    assert data["raw_text"] == "Experienced software engineer with Java, Python, SQL and AWS."
    assert data["created_at"]


def test_list_cv_profiles():
    response = client.get("/cv-profiles")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_cv_profile_by_id():
    create_response = client.post(
        "/cv-profiles",
        json={
            "filename": "get_test_cv.txt",
            "raw_text": "Backend developer with FastAPI and PostgreSQL experience.",
        },
    )

    cv_profile_id = create_response.json()["id"]

    get_response = client.get(f"/cv-profiles/{cv_profile_id}")

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["id"] == cv_profile_id
    assert data["filename"] == "get_test_cv.txt"


def test_get_cv_profile_returns_404_for_missing_id():
    response = client.get("/cv-profiles/non-existent-id")

    assert response.status_code == 404
    assert response.json() == {"detail": "CV profile not found"}
