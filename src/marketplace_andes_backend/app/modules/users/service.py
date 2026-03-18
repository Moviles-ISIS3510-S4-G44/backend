from uuid import uuid4

from .models import User
from .repository import UserRepository
from .schemas import UserCreate, UserResponse


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, user_create: UserCreate) -> UserResponse:
        user = User(id=uuid4(), name=user_create.name)
        created_user = self.repository.create_user(user)
        return UserResponse.model_validate(created_user)
