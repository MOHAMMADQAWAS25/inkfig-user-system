from uuid import UUID

import httpx

from src.entities.exceptions.registration import (
    EmailAlreadyRegisteredError,
    RegistrationProviderError,
)


class SupabaseAuthGateway:
    def __init__(self, supabase_url: str, secret_key: str) -> None:
        if not supabase_url or not secret_key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SECRET_KEY are required.")
        self._base_url = supabase_url.rstrip("/")
        self._headers = {
            "apikey": secret_key,
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json",
        }

    async def create_user(self, email: str, password: str) -> UUID:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self._base_url}/auth/v1/admin/users",
                    headers=self._headers,
                    json={"email": email, "password": password, "email_confirm": True},
                )
        except httpx.RequestError as error:
            raise RegistrationProviderError("Supabase user creation was unreachable.") from error
        if response.status_code in {400, 409, 422} and "already" in response.text.lower():
            raise EmailAlreadyRegisteredError
        if response.status_code not in {200, 201}:
            raise RegistrationProviderError(
                f"Supabase user creation failed with status {response.status_code}."
            )
        try:
            return UUID(response.json()["id"])
        except (KeyError, TypeError, ValueError) as error:
            raise RegistrationProviderError("Supabase returned an invalid user response.") from error

    async def delete_user(self, user_id: UUID) -> None:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.delete(
                    f"{self._base_url}/auth/v1/admin/users/{user_id}",
                    headers=self._headers,
                )
        except httpx.RequestError as error:
            raise RegistrationProviderError("Supabase compensation was unreachable.") from error
        if response.status_code not in {200, 204, 404}:
            raise RegistrationProviderError(
                f"Supabase compensation failed with status {response.status_code}."
            )
