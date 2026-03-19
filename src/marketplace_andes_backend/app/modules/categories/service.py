from uuid import uuid4

from .models import Category
from .repository import CategoryRepository
from .schemas import CategoryCreate, CategoryResponse


class CategoryService:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def create_category(self, category_create: CategoryCreate) -> CategoryResponse:
        category = Category(id=uuid4(), name=category_create.name)
        created_category = self.repository.create_category(category)
        return CategoryResponse.model_validate(created_category)
