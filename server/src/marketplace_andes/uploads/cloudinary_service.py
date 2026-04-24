import logging
from functools import lru_cache
from typing import BinaryIO

from cloudinary import config as cloudinary_config
from cloudinary import uploader
from cloudinary.exceptions import Error as CloudinaryError

from marketplace_andes.config import get_global_config

logger = logging.getLogger(__name__)


class CloudinaryService:
    def __init__(self) -> None:
        config = get_global_config()
        missing = [
            key
            for key, value in (
                ("CLOUDINARY_CLOUD_NAME", config.cloudinary_cloud_name),
                ("CLOUDINARY_API_KEY", config.cloudinary_api_key),
                ("CLOUDINARY_API_SECRET", config.cloudinary_api_secret),
            )
            if not value
        ]
        if missing:
            missing_keys = ", ".join(missing)
            raise CloudinaryUploadError(
                f"Cloudinary configuration is missing: {missing_keys}"
            )

        cloudinary_config(
            cloud_name=config.cloudinary_cloud_name,
            api_key=config.cloudinary_api_key,
            api_secret=config.cloudinary_api_secret,
            secure=True,
        )

    def upload_file(self, file_obj: BinaryIO, folder: str) -> dict[str, str]:
        try:
            result = uploader.upload(file_obj, folder=folder)
        except CloudinaryError as exc:
            raise CloudinaryUploadError("Cloudinary upload failed") from exc

        secure_url = result.get("secure_url")
        public_id = result.get("public_id")
        if not secure_url:
            raise CloudinaryUploadError("Cloudinary did not return a secure_url")
        if not public_id:
            raise CloudinaryUploadError("Cloudinary did not return a public_id")
        return {"secure_url": str(secure_url), "public_id": str(public_id)}

    def delete_file(self, public_id: str) -> None:
        try:
            uploader.destroy(public_id)
        except CloudinaryError as exc:
            logger.warning(
                "Failed to rollback uploaded Cloudinary asset with public_id '%s': %s",
                public_id,
                exc,
            )


@lru_cache
def get_cloudinary_service() -> CloudinaryService:
    return CloudinaryService()


class CloudinaryUploadError(Exception):
    pass
