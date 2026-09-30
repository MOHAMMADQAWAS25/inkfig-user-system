import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from src.entities.dto.registration import (
    EmailVerificationCreate,
    PendingEmailVerification,
    RegisterUserRequest,
    RegisterUserResponse,
    ResendVerificationResponse,
    UserProfileCreate,
    VerifyEmailResponse,
)
from src.entities.exceptions.registration import (
    VerificationAttemptsExceededError,
    VerificationCodeExpiredError,
    VerificationCodeInvalidError,
    VerificationNotFoundError,
    VerificationResendTooSoonError,
)
from src.entities.repositories.registration import (
    PasswordHasher,
    UserProfileRepository,
    VerificationEmailGateway,
)


class RegistrationService:
    def __init__(
        self,
        profile_repository: UserProfileRepository,
        email_gateway: VerificationEmailGateway,
        password_hasher: PasswordHasher,
        hash_secret: str,
        code_ttl_minutes: int = 10,
        max_attempts: int = 5,
        resend_cooldown_seconds: int = 60,
    ) -> None:
        if not hash_secret:
            raise RuntimeError("A verification hash secret is required.")
        self._profile_repository = profile_repository
        self._email_gateway = email_gateway
        self._password_hasher = password_hasher
        self._hash_secret = hash_secret.encode()
        self._code_ttl_minutes = code_ttl_minutes
        self._max_attempts = max_attempts
        self._resend_cooldown_seconds = resend_cooldown_seconds

    async def register(self, request: RegisterUserRequest) -> RegisterUserResponse:
        pending = await self._profile_repository.get_pending_verification(request.email)
        if pending is not None:
            return await self._resume_pending_registration(pending)
        legacy_user_id = await self._profile_repository.get_recoverable_legacy_user_id(
            request.email
        )
        user_id = legacy_user_id or UUID(bytes=secrets.token_bytes(16), version=4)
        code = self._generate_code()
        verification = self._new_verification(user_id, code)
        profile = UserProfileCreate(
            user_id=user_id,
            password_hash=self._password_hasher.hash(request.password),
            email=request.email,
            full_name=request.full_name,
            phone_number=request.phone_number,
            gender=request.gender,
            date_of_birth=request.date_of_birth,
        )
        if legacy_user_id is not None:
            await self._profile_repository.restart_legacy_account(profile, verification)
        else:
            await self._profile_repository.create_pending(
                profile,
                verification,
            )
        await self._email_gateway.send_verification_code(
            request.email, request.full_name, code, self._code_ttl_minutes
        )
        return RegisterUserResponse(
            email=request.email,
            expires_in_seconds=self._code_ttl_minutes * 60,
            resend_after_seconds=self._resend_cooldown_seconds,
        )

    async def _resume_pending_registration(
        self, challenge: PendingEmailVerification
    ) -> RegisterUserResponse:
        now = datetime.now(timezone.utc)
        resend_available_at = challenge.sent_at + timedelta(
            seconds=self._resend_cooldown_seconds
        )
        if resend_available_at <= now:
            code = self._generate_code()
            verification = self._new_verification(challenge.user_id, code)
            await self._email_gateway.send_verification_code(
                challenge.email, challenge.full_name, code, self._code_ttl_minutes
            )
            await self._profile_repository.replace_verification(
                challenge.verification_id, verification
            )
            expires_in_seconds = self._code_ttl_minutes * 60
            resend_after_seconds = self._resend_cooldown_seconds
        else:
            expires_in_seconds = max(0, int((challenge.expires_at - now).total_seconds()))
            resend_after_seconds = max(
                0, int((resend_available_at - now).total_seconds())
            )
        return RegisterUserResponse(
            email=challenge.email,
            expires_in_seconds=expires_in_seconds,
            resend_after_seconds=resend_after_seconds,
        )

    async def verify_email(self, email: str, code: str) -> VerifyEmailResponse:
        challenge = await self._profile_repository.get_pending_verification(email)
        if challenge is None:
            raise VerificationNotFoundError
        now = datetime.now(timezone.utc)
        if challenge.expires_at <= now:
            raise VerificationCodeExpiredError
        if challenge.attempts >= challenge.max_attempts:
            raise VerificationAttemptsExceededError
        if not hmac.compare_digest(challenge.code_hash, self._hash_code(challenge.user_id, code)):
            await self._profile_repository.record_failed_attempt(challenge.verification_id)
            if challenge.attempts + 1 >= challenge.max_attempts:
                raise VerificationAttemptsExceededError
            raise VerificationCodeInvalidError
        await self._profile_repository.activate_verified_user(
            challenge.verification_id, challenge.user_id, now
        )
        return VerifyEmailResponse(email=email)

    async def resend_verification(self, email: str) -> ResendVerificationResponse:
        challenge = await self._profile_repository.get_pending_verification(email)
        if challenge is None:
            raise VerificationNotFoundError
        now = datetime.now(timezone.utc)
        if challenge.sent_at + timedelta(seconds=self._resend_cooldown_seconds) > now:
            raise VerificationResendTooSoonError
        code = self._generate_code()
        verification = self._new_verification(challenge.user_id, code)
        await self._email_gateway.send_verification_code(
            challenge.email, challenge.full_name, code, self._code_ttl_minutes
        )
        await self._profile_repository.replace_verification(
            challenge.verification_id, verification
        )
        return ResendVerificationResponse(
            email=email,
            expires_in_seconds=self._code_ttl_minutes * 60,
            resend_after_seconds=self._resend_cooldown_seconds,
        )

    def _new_verification(self, user_id: UUID, code: str) -> EmailVerificationCreate:
        return EmailVerificationCreate(
            user_id=user_id,
            code_hash=self._hash_code(user_id, code),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=self._code_ttl_minutes),
            max_attempts=self._max_attempts,
        )

    @staticmethod
    def _generate_code() -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    def _hash_code(self, user_id: UUID, code: str) -> str:
        message = f"inkfig-email-verification:{user_id}:{code}".encode()
        return hmac.new(self._hash_secret, message, hashlib.sha256).hexdigest()
