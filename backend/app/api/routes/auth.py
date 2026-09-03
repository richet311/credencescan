import secrets

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app.core.auth import create_access_token
from app.core.config import settings
from app.core.security import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginRequest):
    username_ok = secrets.compare_digest(credentials.username, settings.demo_username)
    password_ok = secrets.compare_digest(credentials.password, settings.demo_password)

    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = create_access_token(subject=credentials.username)
    return {"access_token": token, "token_type": "bearer"}
