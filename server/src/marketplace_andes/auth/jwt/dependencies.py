from typing import Annotated

from fastapi import Depends

from marketplace_andes.config import get_global_config

from .schemas import TokenConfig
from .service import JWTService


def get_jwt_service() -> JWTService:
    config = get_global_config()
    return JWTService(
        config=TokenConfig(
            jwt_public_key=config.jwt_public_key,
            jwt_secret_key=config.jwt_secret_key,
            jwt_algorithm=config.jwt_algorithm,
            jwt_access_token_expire_minutes=config.jwt_access_token_expire_minutes,
            jwt_refresh_token_expire_minutes=config.jwt_refresh_token_expire_minutes,
        )
    )


JWTServiceDep = Annotated[JWTService, Depends(get_jwt_service)]
