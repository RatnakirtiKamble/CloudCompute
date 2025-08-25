from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from models.usage_model import Usage
from schemas.usage_schema import UsageCreate


async def log_usage(db: AsyncSession, usage: UsageCreate):
    db_usage = Usage(
        user_id=usage.user_id,
        task_id=usage.task_id,
        cpu_seconds=usage.cpu_seconds,
        gpu_seconds=usage.gpu_seconds,
        memory_mb=usage.memory_mb,
    )
    db.add(db_usage)
    await db.commit()
    await db.refresh(db_usage)
    return db_usage


async def get_usage_for_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(Usage).filter(Usage.user_id == user_id))
    return result.scalars().all()


async def get_total_usage(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(
            func.sum(Usage.cpu_seconds).label("total_cpu_seconds"),
            func.sum(Usage.gpu_seconds).label("total_gpu_seconds"),
            func.sum(Usage.memory_mb).label("total_memory_mb"),
        ).filter(Usage.user_id == user_id)
    )
    return result.first()  
