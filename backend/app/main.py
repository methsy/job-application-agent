from fastapi import FastAPI

app = FastAPI(
    title="Job Application Agent API",
    description="Backend API for searching, scoring, and tracking job applications.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}