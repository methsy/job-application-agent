from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_job_listing():
    response = client.post(
        "/job-listings",
        json={
            "title": "Senior Software Engineer",
            "company": "Example Company",
            "location": "Melbourne VIC",
            "source": "manual",
            "url": "https://example.com/jobs/senior-software-engineer",
            "raw_description": (
                "We are looking for a Senior Software Engineer with Java, "
                "Python, SQL, REST APIs and production support experience."
            ),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert data["title"] == "Senior Software Engineer"
    assert data["company"] == "Example Company"
    assert data["location"] == "Melbourne VIC"
    assert data["source"] == "manual"
    assert "Java" in data["raw_description"]
    assert data["created_at"]
    assert data["updated_at"]


def test_list_job_listings():
    response = client.get("/job-listings")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_job_listing_by_id():
    create_response = client.post(
        "/job-listings",
        json={
            "title": "Backend Developer",
            "company": "Another Company",
            "location": "Remote Australia",
            "source": "manual",
            "url": "https://example.com/jobs/backend-developer",
            "raw_description": "Backend developer role requiring FastAPI and PostgreSQL.",
        },
    )

    job_listing_id = create_response.json()["id"]

    get_response = client.get(f"/job-listings/{job_listing_id}")

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["id"] == job_listing_id
    assert data["title"] == "Backend Developer"
    assert data["company"] == "Another Company"


def test_get_job_listing_returns_404_for_missing_id():
    response = client.get("/job-listings/non-existent-id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Job listing not found"}


def test_create_job_listing_rejects_empty_description():
    response = client.post(
        "/job-listings",
        json={
            "title": "Invalid Job",
            "company": "Invalid Company",
            "location": "Melbourne VIC",
            "source": "manual",
            "url": "",
            "raw_description": "",
        },
    )

    assert response.status_code == 422
