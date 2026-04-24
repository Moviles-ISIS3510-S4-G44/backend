from cloudinary import config as cloudinary_config
from cloudinary import uploader
from cloudinary.exceptions import Error as CloudinaryError

from marketplace_andes.config import get_global_config


class CloudinaryService:
    def __init__(self) -> None:
        config = get_global_config()
        cloudinary_config(
            cloud_name=config.cloudinary_cloud_name,
            api_key=config.cloudinary_api_key,
            api_secret=config.cloudinary_api_secret,
            secure=True,
        )

    def upload_file(self, file_obj: object, folder: str) -> str:
        try:
            result = uploader.upload(file_obj, folder=folder)
        except CloudinaryError as exc:
            raise CloudinaryUploadError("Cloudinary upload failed") from exc

        secure_url = result.get("secure_url")
        if not secure_url:
            raise CloudinaryUploadError("Cloudinary did not return a secure_url")
        return str(secure_url)


class CloudinaryUploadError(Exception):
    pass
