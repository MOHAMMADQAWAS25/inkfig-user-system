from datetime import date
from uuid import uuid4

import pytest

from src.app.services.settings_service import SettingsService
from src.entities.dto.settings import ChangePasswordRequest, ProfileSettingsResponse, UpdateProfileSettingsRequest
from src.entities.exceptions.settings import CurrentPasswordInvalidError
from src.entities.enums.gender import Gender
from src.infrastructure.security.passwords import Pbkdf2PasswordHasher


class SettingsRepositoryStub:
    def __init__(self) -> None:
        self.user_id = uuid4()
        self.password_hash = Pbkdf2PasswordHasher().hash("old-password")
        self.updated_password_hash: str | None = None
        self.active = True

    async def get_profile(self, user_id):
        return ProfileSettingsResponse(email="12345678@students.hebron.edu", full_name="Ink Fig", phone_number="0599123456", gender=Gender.FEMALE, date_of_birth=date(2000, 1, 1), is_active=True)

    async def get_password_hash(self, user_id):
        return self.password_hash

    async def update_profile(self, user_id, request):
        return ProfileSettingsResponse(email="12345678@students.hebron.edu", is_active=True, **request.model_dump())

    async def update_password(self, user_id, password_hash):
        self.updated_password_hash = password_hash

    async def set_active(self, user_id, is_active):
        self.active = is_active


def test_profile_update_reuses_registration_validation() -> None:
    with pytest.raises(ValueError):
        UpdateProfileSettingsRequest(full_name="Ink Fig", phone_number="123", gender="female", date_of_birth="2000-01-01")


@pytest.mark.asyncio
async def test_password_change_requires_current_password_and_hashes_new_password() -> None:
    repository = SettingsRepositoryStub()
    service = SettingsService(repository, Pbkdf2PasswordHasher())
    with pytest.raises(CurrentPasswordInvalidError):
        await service.change_password(repository.user_id, ChangePasswordRequest(current_password="wrong-pass", password="new-password", password_confirmation="new-password"))
    await service.change_password(repository.user_id, ChangePasswordRequest(current_password="old-password", password="new-password", password_confirmation="new-password"))
    assert repository.updated_password_hash is not None
    assert Pbkdf2PasswordHasher().verify("new-password", repository.updated_password_hash)


@pytest.mark.asyncio
async def test_account_deactivation_is_scoped_to_authenticated_user() -> None:
    repository = SettingsRepositoryStub()
    service = SettingsService(repository, Pbkdf2PasswordHasher())
    await service.set_active(repository.user_id, False)
    assert repository.active is False
