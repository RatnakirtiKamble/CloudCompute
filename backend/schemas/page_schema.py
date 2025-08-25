from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PageBase(BaseModel):
    name: str
    path: str
    status: Optional[str] = "uploaded"


class PageCreate(PageBase):
    owner_id: int


class PageResponse(PageBase):
    id: int
    created_at: datetime
    owner_id: int

    class Config:
        orm_mode = True
