from pydantic import BaseModel


class PermissionBase(BaseModel):
    code: str
    description: str | None


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: int

    class Config:
        from_attributes = True
