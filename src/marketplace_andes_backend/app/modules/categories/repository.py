from sqlmodel import Session, select

from .models import Category


class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_category(self, category: Category) -> Category:
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def list_categories(self) -> list[Category]:
        statement = select(Category).order_by(Category.name.asc())
        return list(self.session.exec(statement))
