from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_match_score_from_cv_and_job_returns_400_when_extracted_data_missing():
    cv_response = client.post(
        "/cv-profiles",
        json={
            "filename": "test_cv.txt",
            "raw_text": "Experienced software engineer with Java and Python.",
        },
    )

    assert cv_response.status_code in [200, 201]
    cv_profile_id = cv_response.json()["id"]

    job_response = client.post(
        "/job-listings",
        json={
            "title": "Senior Software Engineer",
            "company": "Test Company",
            "location": "Melbourne VIC",
            "source": "manual",
            "url": "https://example.com/jobs/senior-software-engineer",
            "raw_description": "We need Java, Python, APIs, and backend engineering.",
        },
    )


    assert job_response.status_code in [200, 201]
    job_listing_id = job_response.json()["id"]

    response = client.post(
        "/match-scores/from-cv-and-job",
        json={
            "cv_profile_id": cv_profile_id,
            "job_listing_id": job_listing_id,
            "auto_extract_missing": False,
        },
    )

    assert response.status_code == 400

    body = response.json()
    assert "detail" in body
    assert "candidate_profile" in str(body["detail"])
    assert "job_requirement" in str(body["detail"])


def test_create_match_score_from_cv_and_job_returns_404_when_cv_profile_missing():
    job_response = client.post(
        "/job-listings",
        json={
            "title": "Senior Software Engineer",
            "company": "Test Company",
            "location": "Melbourne VIC",
            "source": "manual",
            "url": "https://example.com/jobs/senior-software-engineer-missing-cv-test",
            "raw_description": "We need Java and Python.",
        },
    )

    assert job_response.status_code in [200, 201]
    job_listing_id = job_response.json()["id"]

    response = client.post(
        "/match-scores/from-cv-and-job",
        json={
            "cv_profile_id": "missing-cv-profile-id",
            "job_listing_id": job_listing_id,
            "auto_extract_missing": False,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "CV profile not found"


def test_create_match_score_from_cv_and_job_returns_404_when_job_listing_missing():
    cv_response = client.post(
        "/cv-profiles",
        json={
            "filename": "test_cv.txt",
            "raw_text": "Experienced software engineer with Java and Python.",
        },
    )

    assert cv_response.status_code in [200, 201]
    cv_profile_id = cv_response.json()["id"]

    response = client.post(
        "/match-scores/from-cv-and-job",
        json={
            "cv_profile_id": cv_profile_id,
            "job_listing_id": "missing-job-listing-id",
            "auto_extract_missing": False,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job listing not found"
