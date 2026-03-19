from fastapi import APIRouter, HTTPException

from src.marketplace_andes_backend.db import SessionDep

from .models import Category
from .schemas import CategoryCreateRequest, CategoryResponse
from .service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("")
async def create_category(
    payload: CategoryCreateRequest,
    session: SessionDep,
) -> CategoryResponse:
    service = CategoryService(session)
    category = service.create(Category(name=payload.name))
    return CategoryResponse.model_validate(category)


@router.get("")
async def list_categories(session: SessionDep) -> list[CategoryResponse]:
    service = CategoryService(session)
    categories = service.list_all()
    return [CategoryResponse.model_validate(category) for category in categories]


@router.get("/{category_id}")
async def get_category(
    category_id: int,
    session: SessionDep,
) -> CategoryResponse:
    service = CategoryService(session)
    category = service.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse.model_validate(category)
