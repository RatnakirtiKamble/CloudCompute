from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.task_model import Task
from schemas.task_schema import TaskCreate, TaskStatusEnum


async def create_task(db: AsyncSession, task: TaskCreate):
    db_task = Task(
        task_type=task.task_type,
        status=task.status,
        logs=task.logs,
        user_id=task.user_id,
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def get_task(db: AsyncSession, task_id: int):
    result = await db.execute(select(Task).filter(Task.id == task_id))
    return result.scalars().first()


async def get_tasks_for_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(Task).filter(Task.user_id == user_id))
    return result.scalars().all()


async def update_task_status(db: AsyncSession, task_id: int, status: str, logs: str = None):
    result = await db.execute(select(Task).filter(Task.id == task_id))
    db_task = result.scalars().first()
    if db_task:
        db_task.status = status
        if logs is not None:
            db_task.logs = logs
        await db.commit()
        await db.refresh(db_task)
    return db_task


async def delete_task(db: AsyncSession, task_id: int):
    result = await db.execute(select(Task).filter(Task.id == task_id))
    db_task = result.scalars().first()
    if db_task:
        await update_task_status(db, task_id, TaskStatusEnum.failed, logs="Task deleted by user.")
    return db_task
