from pydantic import BaseModel, ConfigDict


from uuid import UUID


class LoggedUser(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: UUID
    username: str
    name: str
    email: str
    rating: int



class RegisterUserRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    name: str
    email: str
    password: str


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
