from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "inkfig-user-system"
    environment: str = "local"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173"]
    database_url: str = ""
    jwt_secret: str = ""
    jwt_issuer: str = "inkfig-user-system"
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    access_cookie_name: str = "inkfig_access"
    refresh_cookie_name: str = "inkfig_refresh"
    cookie_domain: str | None = None
    cookie_secure: bool = False
    brevo_api_key: str = ""
    brevo_sender_email: str = ""
    brevo_sender_name: str = "InkFig"
    brevo_verify_email_template_id: int = 0
    verification_code_ttl_minutes: int = 10
    verification_max_attempts: int = 5
    verification_resend_cooldown_seconds: int = 60
    email_code_max_sends_per_hour: int = 5
    email_code_hourly_block_seconds: int = 3600
    password_reset_code_ttl_minutes: int = 10
    password_reset_max_attempts: int = 5
    password_reset_token_ttl_minutes: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
