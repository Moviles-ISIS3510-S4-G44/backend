from typing import Annotated

from fastapi import APIRouter, Depends

from ...db.session import SessionDep
from .repository import CategoryRepository
from .schemas import CategoryCreate, CategoryResponse
from .service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


def get_category_service(session: SessionDep) -> CategoryService:
    repository = CategoryRepository(session)
    return CategoryService(repository)


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]


@router.post("", response_model=CategoryResponse)
def create_category(
    service: CategoryServiceDep,
    category_create: CategoryCreate,
) -> CategoryResponse:
    return service.create_category(category_create)
