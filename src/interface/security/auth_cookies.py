from fastapi import Response

from src.entities.dto.authentication import SessionResponse, TokenResponse
from src.infrastructure.config.settings import Settings


def set_auth_cookies(
    response: Response, tokens: TokenResponse, settings: Settings
) -> None:
    response.set_cookie(
        key=settings.access_cookie_name,
        value=tokens.access_token,
        max_age=tokens.expires_in,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        domain=settings.cookie_domain,
        path="/",
    )
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=tokens.refresh_token,
        max_age=settings.refresh_token_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        path=settings.api_prefix + "/auth",
    )


def clear_auth_cookies(response: Response, settings: Settings) -> None:
    response.delete_cookie(
        settings.access_cookie_name, domain=settings.cookie_domain, path="/"
    )
    response.delete_cookie(
        settings.refresh_cookie_name, path=settings.api_prefix + "/auth"
    )


def session_response(tokens: TokenResponse) -> SessionResponse:
    return SessionResponse(
        expires_in=tokens.expires_in,
        user_id=tokens.user_id,
        email=tokens.email,
        full_name=tokens.full_name,
        role=tokens.role,
        permissions=tokens.permissions,
    )
