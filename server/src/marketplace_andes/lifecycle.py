import logging
import sys
from contextlib import asynccontextmanager


from fastapi import FastAPI


def configure_logging() -> None:
    log_level = "INFO"
    logging.basicConfig(
        level=log_level,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        force=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    yield
