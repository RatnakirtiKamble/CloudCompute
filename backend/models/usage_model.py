# models/usage.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from db.db_connection import Base

class Usage(Base):
    __tablename__ = "usage"

    id = Column(Integer, primary_key=True, index=True)
    cpu_seconds = Column(Integer, default=0)
    gpu_seconds = Column(Integer, default=0)
    memory_mb = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
