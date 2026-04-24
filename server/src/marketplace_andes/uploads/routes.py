from fastapi import APIRouter, File, HTTPException, UploadFile, status

from .cloudinary_service import CloudinaryService, CloudinaryUploadError
from .schemas import ListingImageUploadResponse

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
LISTING_IMAGES_FOLDER = "marketplace/listings"


@router.post(
    "/listing-images",
    response_model=ListingImageUploadResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_listing_images(
    files: list[UploadFile] = File(...),
) -> ListingImageUploadResponse:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file is required",
        )

    invalid_types = sorted(
        {
            uploaded_file.content_type
            for uploaded_file in files
            if uploaded_file.content_type not in ALLOWED_IMAGE_TYPES
        }
    )
    if invalid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only image/jpeg, image/png, and image/webp are allowed. "
                f"Received: {', '.join(t or 'unknown' for t in invalid_types)}"
            ),
        )

    cloudinary_service = CloudinaryService()
    urls: list[str] = []

    try:
        for uploaded_file in files:
            urls.append(
                cloudinary_service.upload_file(
                    uploaded_file.file,
                    folder=LISTING_IMAGES_FOLDER,
                )
            )
    except CloudinaryUploadError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Cloudinary error: {exc}",
        ) from exc

    return ListingImageUploadResponse(urls=urls)
