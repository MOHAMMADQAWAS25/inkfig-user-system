import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from src.entities.dto.authentication import (
    PasswordResetRequestResponse,
    PasswordResetVerifyResponse,
)
from src.entities.exceptions.authentication import (
    PasswordResetAttemptsExceededError,
    PasswordResetCodeExpiredError,
    PasswordResetCodeInvalidError,
    PasswordResetTokenInvalidError,
)
from src.entities.repositories.authentication import AuthenticationRepository
from src.entities.repositories.password_reset import (
    PasswordResetEmailGateway,
    PasswordResetRepository,
)
from src.entities.repositories.registration import PasswordHasher


class PasswordResetService:
    def __init__(
        self,
        authentication_repository: AuthenticationRepository,
        reset_repository: PasswordResetRepository,
        email_gateway: PasswordResetEmailGateway,
        password_hasher: PasswordHasher,
        secret: str,
        code_ttl_minutes: int = 10,
        max_attempts: int = 5,
        reset_token_minutes: int = 10,
    ) -> None:
        if not secret:
            raise RuntimeError("JWT secret is required for password-reset tokens.")
        self._authentication_repository = authentication_repository
        self._reset_repository = reset_repository
        self._email_gateway = email_gateway
        self._password_hasher = password_hasher
        self._secret = secret.encode()
        self._code_ttl_minutes = code_ttl_minutes
        self._max_attempts = max_attempts
        self._reset_token_minutes = reset_token_minutes

    async def request(self, email: str) -> PasswordResetRequestResponse:
        user = await self._authentication_repository.find_user_by_email(email)
        if user is None or not user.is_active or user.email_verified_at is None:
            return PasswordResetRequestResponse(expires_in_seconds=self._code_ttl_minutes * 60)
        code = f"{secrets.randbelow(1_000_000):06d}"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=self._code_ttl_minutes)
        await self._reset_repository.create_challenge(
            user.user_id, self._hash(f"code:{user.user_id}:{code}"), expires_at,
            self._max_attempts,
        )
        await self._email_gateway.send_password_reset_code(
            user.email, user.full_name, code, self._code_ttl_minutes
        )
        return PasswordResetRequestResponse(expires_in_seconds=self._code_ttl_minutes * 60)

    async def verify(self, email: str, code: str) -> PasswordResetVerifyResponse:
        challenge = await self._reset_repository.get_pending(email)
        if challenge is None:
            raise PasswordResetCodeInvalidError
        now = datetime.now(timezone.utc)
        if challenge.expires_at <= now:
            raise PasswordResetCodeExpiredError
        if challenge.attempts >= challenge.max_attempts:
            raise PasswordResetAttemptsExceededError
        expected = self._hash(f"code:{challenge.user_id}:{code}")
        if not hmac.compare_digest(challenge.code_hash, expected):
            await self._reset_repository.record_failed_attempt(challenge.challenge_id)
            if challenge.attempts + 1 >= challenge.max_attempts:
                raise PasswordResetAttemptsExceededError
            raise PasswordResetCodeInvalidError
        token = secrets.token_urlsafe(48)
        token_expires = now + timedelta(minutes=self._reset_token_minutes)
        await self._reset_repository.verify_challenge(
            challenge.challenge_id, self._hash(f"token:{token}"), token_expires, now
        )
        return PasswordResetVerifyResponse(
            reset_token=token, expires_in_seconds=self._reset_token_minutes * 60
        )

    async def confirm(self, email: str, reset_token: str, password: str) -> None:
        changed = await self._reset_repository.reset_password(
            email, self._hash(f"token:{reset_token}"),
            self._password_hasher.hash(password), datetime.now(timezone.utc)
        )
        if not changed:
            raise PasswordResetTokenInvalidError

    def _hash(self, value: str) -> str:
        return hmac.new(self._secret, value.encode(), hashlib.sha256).hexdigest()
