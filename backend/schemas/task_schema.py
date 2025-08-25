from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskBase(BaseModel):
    task_type: str
    status: Optional[str] = "pending"
    logs: Optional[str] = None


class TaskCreate(TaskBase):
    user_id: int


class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    user_id: int

    class Config:
        orm_mode = True
