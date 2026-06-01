from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_txt_cv_profile():
    file_content = (
        b"Nandun Thellamurege\n"
        b"Senior Software Engineer\n"
        b"Skills: Java, Python, SQL, FastAPI, React, AWS"
    )

    response = client.post(
        "/cv-profiles/upload",
        files={
            "file": (
                "test_cv.txt",
                file_content,
                "text/plain",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert data["filename"] == "test_cv.txt"
    assert "Senior Software Engineer" in data["raw_text"]
    assert "Java" in data["raw_text"]


def test_upload_unsupported_file_type_returns_400():
    response = client.post(
        "/cv-profiles/upload",
        files={
            "file": (
                "test_cv.exe",
                b"fake executable content",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_empty_txt_returns_400():
    response = client.post(
        "/cv-profiles/upload",
        files={
            "file": (
                "empty_cv.txt",
                b"",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "No text could be extracted from the file."
