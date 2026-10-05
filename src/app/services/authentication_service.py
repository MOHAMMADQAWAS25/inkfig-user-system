import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from src.entities.dto.authentication import AuthenticatedUser, TokenResponse
from src.entities.exceptions.authentication import (
    AccountInactiveError,
    AccountAdminSuspendedError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from src.entities.repositories.authentication import AuthenticationRepository
from src.entities.repositories.registration import PasswordHasher
from src.entities.enums.account_status import AccountStatus


class AuthenticationService:
    def __init__(
        self,
        repository: AuthenticationRepository,
        password_hasher: PasswordHasher,
        jwt_secret: str,
        jwt_issuer: str,
        access_token_minutes: int = 15,
        refresh_token_days: int = 30,
    ) -> None:
        if len(jwt_secret.encode()) < 32:
            raise RuntimeError("JWT_SECRET must contain at least 32 bytes.")
        self._repository = repository
        self._password_hasher = password_hasher
        self._jwt_secret = jwt_secret
        self._jwt_issuer = jwt_issuer
        self._access_token_minutes = access_token_minutes
        self._refresh_token_days = refresh_token_days

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self._repository.find_user_by_email(email)
        if user is None or not self._password_hasher.verify(password, user.password_hash):
            raise InvalidCredentialsError
        if user.account_status == AccountStatus.ADMIN_SUSPENDED:
            raise AccountAdminSuspendedError
        if user.account_status == AccountStatus.SELF_DEACTIVATED:
            user = await self._repository.reactivate_self_deactivated(user.user_id)
        self._ensure_active(user)
        return await self._issue_session(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        now = datetime.now(timezone.utc)
        user = await self._repository.consume_refresh_token(
            self._hash_refresh_token(refresh_token), now
        )
        if user is None:
            raise InvalidRefreshTokenError
        self._ensure_active(user)
        return await self._issue_session(user)

    async def logout(self, refresh_token: str) -> None:
        await self._repository.revoke_refresh_token(
            self._hash_refresh_token(refresh_token), datetime.now(timezone.utc)
        )

    async def _issue_session(self, user: AuthenticatedUser) -> TokenResponse:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=self._access_token_minutes)
        access_token = jwt.encode(
            {
                "sub": str(user.user_id),
                "email": user.email,
                "ver": user.token_version,
                "role": user.role,
                "permissions": user.permissions,
                "type": "access",
                "iss": self._jwt_issuer,
                "iat": now,
                "exp": expires_at,
            },
            self._jwt_secret,
            algorithm="HS256",
        )
        refresh_token = secrets.token_urlsafe(48)
        await self._repository.store_refresh_token(
            uuid4(),
            user.user_id,
            self._hash_refresh_token(refresh_token),
            now + timedelta(days=self._refresh_token_days),
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self._access_token_minutes * 60,
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            permissions=user.permissions,
        )

    def _hash_refresh_token(self, token: str) -> str:
        return hashlib.sha256(f"{self._jwt_secret}:{token}".encode()).hexdigest()

    @staticmethod
    def _ensure_active(user: AuthenticatedUser) -> None:
        if not user.is_active or user.email_verified_at is None:
            raise AccountInactiveError
