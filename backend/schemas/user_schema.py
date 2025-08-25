from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional, List
import re

from schemas.page_schema import PageResponse
from schemas.task_schema import TaskResponse
from enum import Enum

class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: RoleEnum = RoleEnum.user


class UserCreate(UserBase):
    password: str  

    @validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[@$!%*?&]", value):
            raise ValueError("Password must contain at least one special character (@$!%*?&)")
        return value



class UserResponse(UserBase):
    id: int
    created_at: datetime
    pages: List[PageResponse] = []
    tasks: List[TaskResponse] = []

    class Config:
        orm_mode = True
