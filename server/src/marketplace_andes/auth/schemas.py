from pydantic import BaseModel, ConfigDict, model_validator


from uuid import UUID


class LoggedUser(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: UUID
    username: str


class RegisterUserRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    name: str | None = None
    email: str | None = None
    username: str | None = None
    password: str

    @model_validator(mode="after")
    def validate_identifier(self):
        if self.email is None and self.username is None:
            raise ValueError("Either email or username must be provided")
        return self

    @property
    def identifier(self) -> str:
        return self.email if self.email is not None else self.username or ""


class RegisterUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    user_id: UUID


class AuthUserRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    username: str
    password: str


class LoginResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    session_id: UUID
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str
    refresh_expires_in: int


class LogoutRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    session_id: UUID
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    refresh_token: str
