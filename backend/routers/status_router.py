# routers/status_router.py
import os
import asyncio
from typing import List
from fastapi import APIRouter, Request, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import docker

from db.db_connection import get_db
from crud import get_task, get_tasks_for_user
from schemas.task_schema import TaskResponse

router = APIRouter(
    prefix="/status",
    tags=["Status & Logs"]
)

docker_client = docker.from_env()


# --------------------
# Task Status
# --------------------
@router.get("/task/{task_id}", response_model=TaskResponse)
async def task_status(task_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    """Check the status of a compute task."""
    user = request.state.user
    task = await get_task(db, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/tasks", response_model=List[TaskResponse])
async def list_user_tasks(request: Request, db: AsyncSession = Depends(get_db)):
    """List all tasks for the authenticated user."""
    user = request.state.user
    return await get_tasks_for_user(db, user.id)


# --------------------
# Logs (Stored in Workspace)
# --------------------
@router.get("/logs/{task_id}")
async def get_task_log(task_id: int, request: Request):
    """Return stored logs from the user's workspace."""
    user = request.state.user
    log_path = os.path.abspath(f"./workspaces/{user.username}/task_{task_id}/container.log")

    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Log file not found")

    return FileResponse(log_path, filename=f"task_{task_id}_logs.txt")


# --------------------
# Artifacts
# --------------------
@router.get("/artifacts/{task_id}/{file_path:path}")
async def get_artifact(task_id: int, file_path: str, request: Request):
    """Fetch an artifact file from user's task workspace."""
    user = request.state.user
    task_workspace = f"./workspaces/{user.username}/task_{task_id}"
    full_path = os.path.abspath(os.path.join(task_workspace, file_path))

    if not full_path.startswith(os.path.abspath(task_workspace)) or not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(full_path)


# --------------------
# WebSocket Live Logs
# --------------------
@router.websocket("/ws/logs/{task_id}")
async def websocket_logs(websocket: WebSocket, task_id: int):
    """Stream live logs from a running container."""
    await websocket.accept()
    try:
        async for db in get_db():
            task = await get_task(db, task_id)
            if not task:
                await websocket.send_text("Task not found")
                await websocket.close()
                return

            container = None
            for c in docker_client.containers.list(all=True):
                if f"user{task.user_id}_task{task_id}" in c.name:
                    container = c
                    break

            if not container:
                await websocket.send_text("Container not running")
                await websocket.close()
                return

            loop = asyncio.get_event_loop()

            def stream_logs():
                for line in container.logs(stream=True):
                    asyncio.run_coroutine_threadsafe(
                        websocket.send_text(line.decode().strip()), loop
                    )

            await loop.run_in_executor(None, stream_logs)
            await websocket.close()
    except WebSocketDisconnect:
        print(f"User disconnected from logs for task {task_id}")
