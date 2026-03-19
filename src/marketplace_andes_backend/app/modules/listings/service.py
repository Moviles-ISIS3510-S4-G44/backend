from datetime import datetime, timezone
from uuid import uuid4

from marketplace_andes_backend.app.modules.listings.models import Listing

from ..categories.schemas import CategoryResponse
from ..locations.schemas import LocationResponse
from .repository import ListingRepository
from .schemas import ListingCreate, ListingCreateResponse, ListingListItemResponse, ListingListResponse


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
                    created_at=listing.created_at,
                    category=CategoryResponse.model_validate(listing.category),
                    location=LocationResponse.model_validate(listing.location),
                )
            )

        return ListingListResponse(items=items, total=len(items))
    
    def create_listing(self, data: ListingCreate) -> ListingCreateResponse:
        listing = Listing(
            id=uuid4(),
            product_id=data.product_id,
            seller_id=data.seller_id,
            category_id=data.category_id,
            location_id=data.location_id,
            price=data.price,
            condition=data.condition,
            status="active",
            created_at=datetime.now(timezone.utc),
        )

        listing = self.repository.create_listing(listing)

        return ListingCreateResponse(
            id=listing.id,
            price=listing.price,
            condition=listing.condition,
            status=listing.status,
            created_at=listing.created_at,
        )
