from sqlmodel import Session, select

from .models import Category


class CategoryService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, payload: Category) -> Category:
        self.session.add(payload)
        self.session.commit()
        self.session.refresh(payload)
        return payload

    def list_all(self) -> list[Category]:
        statement = select(Category)
        return list(self.session.exec(statement).all())

    def get_by_id(self, category_id: int) -> Category | None:
        statement = select(Category).where(Category.id == category_id)
        return self.session.exec(statement).first()
