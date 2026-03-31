from typing import Annotated

from fastapi import Depends

from .interface import IPasswordHasher

from argon2 import PasswordHasher


class Argon2PasswordHasher(IPasswordHasher):
    def __init__(self) -> None:
        self.__hasher = PasswordHasher()

    def hash(self, password: str) -> str:
        return self.__hasher.hash(password)

    def verify(self, hashed_password: str, password: str) -> bool:
        return self.__hasher.verify(hashed_password, password)


def get_password_hasher() -> IPasswordHasher:
    return Argon2PasswordHasher()


PasswordHasherDep = Annotated[IPasswordHasher, Depends(get_password_hasher)]
