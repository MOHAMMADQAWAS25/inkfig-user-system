from uuid import uuid4

from fastapi import Response

from src.entities.dto.authentication import TokenResponse
from src.infrastructure.config.settings import Settings
from src.interface.security.auth_cookies import (
    clear_auth_cookies,
    session_response,
    set_auth_cookies,
)


def tokens() -> TokenResponse:
    return TokenResponse(
        access_token="access-secret",
        refresh_token="refresh-secret",
        expires_in=900,
        user_id=uuid4(),
        email="12345678@students.hebron.edu",
        full_name="Student",
    )


def test_auth_tokens_are_only_exposed_as_secure_http_only_cookies() -> None:
    response = Response()
    issued = tokens()
    settings = Settings(cookie_domain="inkfig-hu.com", cookie_secure=True)

    set_auth_cookies(response, issued, settings)
    public = session_response(issued).model_dump()
    cookies = response.headers.getlist("set-cookie")

    assert "access_token" not in public
    assert "refresh_token" not in public
    assert any(
        "inkfig_access=access-secret" in cookie
        and "HttpOnly" in cookie
        and "Secure" in cookie
        and "SameSite=lax" in cookie
        for cookie in cookies
    )
    assert any(
        "inkfig_refresh=refresh-secret" in cookie
        and "HttpOnly" in cookie
        and "Secure" in cookie
        and "SameSite=strict" in cookie
        for cookie in cookies
    )
    assert any(
        "Domain=inkfig-hu.com" in cookie
        for cookie in cookies
        if "inkfig_access=" in cookie
    )
    assert all(
        "Domain=" not in cookie for cookie in cookies if "inkfig_refresh=" in cookie
    )


def test_logout_expires_both_authentication_cookies() -> None:
    response = Response()
    clear_auth_cookies(response, Settings(cookie_domain="inkfig-hu.com"))
    cookies = response.headers.getlist("set-cookie")
    assert len(cookies) == 2
    assert all("Max-Age=0" in cookie for cookie in cookies)
