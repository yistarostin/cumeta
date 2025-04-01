import hashlib


class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.md5(password.encode()).hexdigest()

    @staticmethod
    def validate_password(password: str, hashed_password: str) -> bool:
        return PasswordHasher.hash_password(password) == hashed_password
