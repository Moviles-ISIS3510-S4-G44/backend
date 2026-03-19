from passlib.context import CryptContext

__PWD_CTX = CryptContext(schemes=["argon2"])


class AuthService:
    pass
