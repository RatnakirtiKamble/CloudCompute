# middleware/ratelimit.py
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.task_model import Task, TaskStatusEnum, TaskEnum
from datetime import datetime, timedelta

class TaskRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db_session: AsyncSession):
        super().__init__(app)
        self.db_session = db_session

    async def dispatch(self, request: Request, call_next):
        user = request.state.user  # assuming user is set in auth middleware

        if not user:
            return await call_next(request)  # skip if no user (or handle auth separately)

        # Only apply limits on task creation routes
        if request.url.path.startswith("/compute/start") or request.url.path.startswith("/static/github") or request.url.path.startswith("/static"):
            # Count running or pending tasks today
            async with self.db_session() as session:
                now = datetime.now(datetime.UTC)
                start_of_day = datetime(now.year, now.month, now.day)

                result = await session.execute(
                    select(Task)
                    .filter(
                        Task.user_id == user.id,
                        Task.created_at >= start_of_day,
                        Task.status.in_([TaskStatusEnum.pending, TaskStatusEnum.running])
                    )
                )
                tasks_today = result.scalars().all()

            compute_count = sum(1 for t in tasks_today if t.task_type == TaskEnum.compute)
            static_count = sum(1 for t in tasks_today if t.task_type == TaskEnum.staticpage)

            # Enforce limits
            if request.url.path.startswith("/compute") and compute_count >= 2:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Daily limit of 2 compute tasks reached."}
                )
            if request.url.path.startswith("/static") and static_count >= 2:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Daily limit of 2 static tasks reached."}
                )

        response = await call_next(request)
        return response
