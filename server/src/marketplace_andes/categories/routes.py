from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid7

from fastapi import APIRouter, HTTPException, Path

from marketplace_andes.db.dependencies import SessionDep

from .models import Category
from .schemas import (
    CategoryCreateRequest,
    CategoryResponse,
    DeleteAllCategoriesResponse,
)
from .service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", status_code=201)
async def create_category(
    payload: CategoryCreateRequest,
    session: SessionDep,
) -> CategoryResponse:
    now = datetime.now(UTC)
    service = CategoryService(session)
    category = service.create(
        Category(
            id=uuid7(),
            name=payload.name,
            created_at=now,
            updated_at=now,
        )
    )
    return CategoryResponse.model_validate(category)


@router.get("")
async def list_categories(session: SessionDep) -> list[CategoryResponse]:
    service = CategoryService(session)
    categories = service.list_all()
    return [CategoryResponse.model_validate(category) for category in categories]


@router.delete("")
async def delete_all_categories(session: SessionDep) -> DeleteAllCategoriesResponse:
    service = CategoryService(session)
    deleted_count = service.delete_all()
    return DeleteAllCategoriesResponse(deleted_count=deleted_count)


@router.get("/{category_id}")
async def get_category(
    category_id: Annotated[UUID, Path()],
    session: SessionDep,
) -> CategoryResponse:
    service = CategoryService(session)
    category = service.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse.model_validate(category)
