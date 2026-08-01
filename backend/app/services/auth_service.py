from ..core.security import hash_password


class AuthService:
    def __init__(self):
        self._users = {}

    def register(self, email: str, password: str, full_name: str) -> dict:
        self._users[email] = {
            "email": email,
            "full_name": full_name,
            "password_hash": hash_password(password),
        }
        return self._users[email]
