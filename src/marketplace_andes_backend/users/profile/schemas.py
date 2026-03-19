from pydantic import BaseModel, Field


class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    rating: int = Field(ge=0, le=5)
