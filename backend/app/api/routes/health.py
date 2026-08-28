from fastapi import APIRouter, Request

from app.core.security import limiter

router = APIRouter(tags=["health"])


@router.get("/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    return {"status": "ok", "service": "credencescan-api"}
