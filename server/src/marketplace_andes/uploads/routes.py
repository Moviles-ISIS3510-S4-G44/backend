from fastapi import APIRouter, File, HTTPException, UploadFile, status

from .cloudinary_service import (
    CloudinaryUploadError,
    get_cloudinary_service,
)
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

    cloudinary_service = get_cloudinary_service()
    urls: list[str] = []
    uploaded_public_ids: list[str] = []

    try:
        for uploaded_file in files:
            upload_result = cloudinary_service.upload_file(
                uploaded_file.file,
                folder=LISTING_IMAGES_FOLDER,
            )
            urls.append(upload_result["secure_url"])
            uploaded_public_ids.append(upload_result["public_id"])
    except CloudinaryUploadError as exc:
        cleanup_failed = False
        for public_id in uploaded_public_ids:
            cleanup_failed = (
                cleanup_failed or not cloudinary_service.delete_file(public_id)
            )

        detail = f"Cloudinary error: {exc}"
        if cleanup_failed:
            detail += ". Cleanup of uploaded assets may be incomplete."

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        ) from exc

    return ListingImageUploadResponse(urls=urls)
