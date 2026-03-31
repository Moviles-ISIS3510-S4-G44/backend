from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine
from sqlalchemy import Engine

from marketplace_andes.config import get_global_config

from .config import EngineConfig


def get_db_config() -> EngineConfig:
    global_config = get_global_config()

    return EngineConfig(db_url=global_config.get_db_url(), echo=global_config.db_echo)


DBConfigDep = Annotated[EngineConfig, Depends(get_db_config)]


def get_engine(config: DBConfigDep) -> Engine:
    return create_engine(config.db_url, echo=config.echo)


EngineDep = Annotated[Engine, Depends(get_engine)]


def get_session(engine: EngineDep) -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
