from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class TaskEnum(str, Enum):
    staticpage = "staticpage"
    compute = "compute"

class TaskStatusEnum(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"

class TaskBase(BaseModel):
    task_type: TaskEnum
    status: Optional[TaskStatusEnum] = TaskStatusEnum.pending
    logs: Optional[str] = None
    path: Optional[str] = None


class TaskCreate(TaskBase):
    user_id: int


class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True