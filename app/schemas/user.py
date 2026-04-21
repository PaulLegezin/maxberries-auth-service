import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

MIN_EMAIL_LENGTH = 1
MIN_NAME_LENGTH = 1
MIN_PASSWORD_LENGTH = 1


class UserBase(BaseModel):
    email: EmailStr = Field(min_length=MIN_EMAIL_LENGTH)
    name: str = Field(min_length=MIN_NAME_LENGTH)


class UserCreate(UserBase):
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, repr=False)


class UserResponse(UserBase):
    id: uuid.UUID
    role_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(UserBase):
    role_id: int


class UserCreateAdmin(UserCreate):
    role_id: int
