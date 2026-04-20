from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.permission import PermissionResponse

MIN_NAME_LENGTH = 1


class RoleBase(BaseModel):
    name: str = Field(min_length=MIN_NAME_LENGTH)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleResponse(RoleBase):
    id: int
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True
