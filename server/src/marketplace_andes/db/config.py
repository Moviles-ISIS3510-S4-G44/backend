from pydantic import BaseModel, ConfigDict


class EngineConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    db_url: str
    echo: bool
