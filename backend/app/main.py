from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.routes import auth, documents, health
from app.core.config import settings
from app.core.logging import logger
from app.core.security import limiter
from app.services.classifier import ClassifierNotTrainedError, get_model
from app.services.ocr import OcrExtractionError, get_reader

INSECURE_DEFAULTS = {"jwt_secret_key": "change-me-in-.env", "demo_password": "change-me-in-.env"}


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("%s starting up in '%s' mode", settings.app_name, settings.environment)

    if settings.environment == "production":
        for field, default_value in INSECURE_DEFAULTS.items():
            if getattr(settings, field) == default_value:
                logger.error(
                    "%s is left at its insecure default in production. "
                    "Set it via the environment before real traffic hits this service.",
                    field,
                )

    try:
        get_reader()
        logger.info("OCR model loaded and ready")
    except OcrExtractionError as exc:
        logger.error("OCR unavailable, uploads will fall back to PDF text only: %s", exc)

    try:
        get_model()
        logger.info("Document classifier loaded and ready")
    except ClassifierNotTrainedError as exc:
        logger.warning("Document classifier not available: %s", exc)

    yield

    logger.info("%s shutting down", settings.app_name)


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid request data."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error."},
    )


app.include_router(health.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
