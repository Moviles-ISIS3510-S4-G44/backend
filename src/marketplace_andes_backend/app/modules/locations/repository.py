from sqlmodel import Session

from .models import Location


class LocationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_location(self, location: Location) -> Location:
        self.session.add(location)
        self.session.commit()
        self.session.refresh(location)
        return location
