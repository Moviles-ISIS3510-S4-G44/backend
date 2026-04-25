from pydantic import BaseModel


class ListingImageUploadResponse(BaseModel):
    urls: list[str]
