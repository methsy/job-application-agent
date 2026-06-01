from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.database import check_database_connection

router = APIRouter(tags=["health"])


@router.get("/db/health")
def database_health_check():
    is_connected = check_database_connection()

    if not is_connected:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"database": "unavailable"},
        )

    return {"database": "ok"}
