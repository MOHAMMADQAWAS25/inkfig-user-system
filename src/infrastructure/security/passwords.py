import base64
import hashlib
import hmac
import secrets


class Pbkdf2PasswordHasher:
    _iterations = 600_000

    def hash(self, password: str) -> str:
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, self._iterations)
        return "pbkdf2_sha256${}${}${}".format(
            self._iterations,
            base64.urlsafe_b64encode(salt).decode(),
            base64.urlsafe_b64encode(digest).decode(),
        )

    def verify(self, password: str, encoded: str) -> bool:
        try:
            algorithm, iterations, salt_value, digest_value = encoded.split("$", 3)
            if algorithm != "pbkdf2_sha256":
                return False
            salt = base64.urlsafe_b64decode(salt_value)
            expected = base64.urlsafe_b64decode(digest_value)
            actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iterations))
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False
