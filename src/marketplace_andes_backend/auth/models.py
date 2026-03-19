from sqlmodel import SQLModel


class UserAuth(SQLModel, table=True):
    hashed_password: str
