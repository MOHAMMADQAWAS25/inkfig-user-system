from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "inkfig-user-system"
    environment: str = "local"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173"]
    supabase_url: str = ""
    supabase_secret_key: str = ""
    database_url: str = ""
    brevo_api_key: str = ""
    brevo_sender_email: str = ""
    brevo_sender_name: str = "InkFig"
    brevo_verify_email_template_id: int = 0
    verification_code_ttl_minutes: int = 10
    verification_max_attempts: int = 5
    verification_resend_cooldown_seconds: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
