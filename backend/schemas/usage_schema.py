from pydantic import BaseModel
from datetime import datetime

class UsageBase(BaseModel):
    cpu_seconds: int = 0
    gpu_seconds: int = 0
    memory_mb: int = 0

class UsageCreate(UsageBase):
    user_id: int
    task_id: int

class UsageResponse(UsageBase):
    id: int
    created_at: datetime
    user_id: int
    task_id: int

    class Config:
        orm_mode = True
