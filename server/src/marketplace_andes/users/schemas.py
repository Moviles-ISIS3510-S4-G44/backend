from pydantic import BaseModel


class DeleteAllUsersResponse(BaseModel):
    deleted_count: int
