from sqlmodel import Session, select

from .models import Location


class LocationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_location(self, location: Location) -> Location:
        self.session.add(location)
        self.session.commit()
        self.session.refresh(location)
        return location

    def list_locations(self) -> list[Location]:
        statement = select(Location).order_by(Location.name.asc())
        return list(self.session.exec(statement))
