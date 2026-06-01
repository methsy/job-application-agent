from fastapi import FastAPI

from app.api.cv_profiles import router as cv_profiles_router
from app.api.health import router as health_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="Backend API for searching, scoring, and tracking job applications.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(health_router)
app.include_router(cv_profiles_router)
