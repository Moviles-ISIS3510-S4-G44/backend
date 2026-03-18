from ..categories.schemas import CategoryResponse
from ..locations.schemas import LocationResponse
from .repository import ListingRepository
from .schemas import ListingListItemResponse, ListingListResponse


class ListingService:
    def __init__(self, repository: ListingRepository):
        self.repository = repository

    def get_listings(self) -> ListingListResponse:
        listings = self.repository.list_listings()
        items: list[ListingListItemResponse] = []

        for listing in listings:
            sorted_images = sorted(listing.images, key=lambda image: image.order)
            items.append(
                ListingListItemResponse(
                    id=listing.id,
                    price=listing.price,
                    condition=listing.condition,
                    status=listing.status,
                    images=[image.url for image in sorted_images],
                    category=CategoryResponse.model_validate(listing.category),
                    location=LocationResponse.model_validate(listing.location),
                )
            )

        return ListingListResponse(items=items, total=len(items))
