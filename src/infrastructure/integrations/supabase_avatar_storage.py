from urllib.parse import quote

import httpx

from src.entities.exceptions.profile_avatar import AvatarStorageError


class SupabaseAvatarStorage:
    def __init__(self, url: str, secret: str, bucket: str) -> None:
        self._url, self._secret, self._bucket = url.rstrip("/"), secret, bucket

    @property
    def _headers(self) -> dict[str, str]:
        return {"apikey": self._secret, "Authorization": f"Bearer {self._secret}"}

    async def create_signed_upload(self, path: str) -> tuple[str, str]:
        endpoint = f"{self._url}/storage/v1/object/upload/sign/{self._bucket}/{quote(path, safe='/')}"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(endpoint, headers=self._headers, json={"allowUpsert": False})
        if response.is_error:
            raise AvatarStorageError
        data = response.json()
        token = str(data.get("token", ""))
        raw_url = str(data.get("url") or data.get("signedURL") or "")
        if not token or not raw_url:
            raise AvatarStorageError
        upload_url = raw_url if raw_url.startswith("http") else f"{self._url}/storage/v1{raw_url}"
        if "token=" not in upload_url:
            upload_url = f"{upload_url}{'&' if '?' in upload_url else '?'}token={quote(token)}"
        return upload_url, token

    def public_url(self, path: str) -> str:
        return f"{self._url}/storage/v1/object/public/{self._bucket}/{quote(path, safe='/')}"

    async def object_is_valid(self, path: str, allowed_types: set[str], max_bytes: int) -> bool:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.head(self.public_url(path))
        if response.status_code != 200:
            return False
        content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        try:
            content_length = int(response.headers.get("content-length", "0"))
        except ValueError:
            return False
        return content_type in allowed_types and 0 < content_length <= max_bytes

    async def delete(self, path: str) -> None:
        endpoint = f"{self._url}/storage/v1/object/{self._bucket}"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.request("DELETE", endpoint, headers=self._headers, json={"prefixes": [path]})
        if response.is_error and response.status_code != 404:
            raise AvatarStorageError
