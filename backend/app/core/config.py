from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central app configuration, loaded from environment variables / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "CredenceScan API"
    environment: str = "development"

    # Comma-separated list of allowed origins for CORS, e.g. "http://localhost:5173"
    allowed_origins: str = "http://localhost:5173"

    # Rate limiting (per client IP)
    rate_limit_default: str = "60/minute"

    # Auth
    jwt_secret_key: str = "change-me-in-.env"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    # Upload constraints for later document-upload endpoints
    max_upload_size_bytes: int = 10 * 1024 * 1024  # 10 MB

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


settings = Settings()
