from sqlmodel import Session


class LocationRepository:
    def __init__(self, session: Session):
        self.session = session

