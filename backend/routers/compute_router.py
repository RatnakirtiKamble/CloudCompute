# routers/compute_router.py
from fastapi import APIRouter, Request, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import asyncio
import os
import docker
from pydantic import BaseModel

from db.db_connection import get_db
from crud import create_task, update_task_status, get_task, get_tasks_for_user, get_user_by_id
from schemas.task_schema import TaskCreate, TaskResponse

router = APIRouter(
    prefix="/compute",
    tags=["Compute"]
)

# Initialize Docker client
docker_client = docker.from_env()

# --------------------
# Request schema
# --------------------
class ComputeTaskRequest(BaseModel):
    image: str
    command: str = ""
    cpu_cores: int = 2
    gpu: bool = False


# --------------------
# Helper: run container
# --------------------
async def run_user_container(user_id: int, task_id: int, db: AsyncSession, image: str, command: str, cpu_cores=2, gpu=False):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")

    user_username = user.username
    print("Username is:", user_username)

    host_workspace = os.path.abspath(f"./workspaces/{user_username}/task_{task_id}")
    container_workspace = "/workspace"
    os.makedirs(host_workspace, exist_ok=True)

    try:
        docker_client.images.get(image)
    except docker.errors.ImageNotFound:
        docker_client.images.pull(image)

    cpu_quota = cpu_cores * 100000
    device_requests = [docker.types.DeviceRequest(count=1, capabilities=[["gpu"]])] if gpu else None

    container_command = f"/bin/sh -c 'cd {container_workspace} && {command}'" if command else None

    container = docker_client.containers.run(
        image=image,
        command=container_command,
        volumes={host_workspace: {"bind": container_workspace, "mode": "rw"}},
        detach=True,
        stdin_open=True,
        tty=True,
        cpu_quota=cpu_quota,
        device_requests=device_requests,
        name=f"user{user_id}_task{task_id}"
    )

    # Stream logs to file
    loop = asyncio.get_event_loop()

    def store_log():
        log_path = os.path.join(host_workspace, "container.log")
        with open(log_path, "a") as log_file:
            for line in container.logs(stream=True):
                log_file.write(line.decode())
                log_file.flush()

    loop.run_in_executor(None, store_log)

    return container


# --------------------
# Background task runner
# --------------------
async def run_container_task(task_id: int, user_id: int, task_request: ComputeTaskRequest):
    async for db in get_db():
        try:
            container = await run_user_container(
                user_id=user_id,
                task_id=task_id,
                db=db,
                image=task_request.image,
                command=task_request.command,
                cpu_cores=task_request.cpu_cores,
                gpu=task_request.gpu
            )

            # Print logs to console
            loop = asyncio.get_event_loop()

            def stream_logs():
                for line in container.logs(stream=True):
                    print(f"[Task {task_id}] {line.decode().strip()}")

            await loop.run_in_executor(None, stream_logs)

            container.wait()
            await update_task_status(db, task_id, status="completed", logs="Job finished successfully")
        except Exception as e:
            await update_task_status(db, task_id, status="failed", logs=str(e))


# --------------------
# CRUD Routes
# --------------------
@router.post("/start", response_model=TaskResponse)
async def start_compute(task_request: ComputeTaskRequest, request: Request, db: AsyncSession = Depends(get_db)):
    user = request.state.user
    task_data = TaskCreate(task_type="compute", user_id=user.id, status="running")
    task = await create_task(db, task_data)
    asyncio.create_task(run_container_task(task.id, user.id, task_request))
    return task


@router.post("/stop/{task_id}", response_model=TaskResponse)
async def stop_compute(task_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = request.state.user
    task = await get_task(db, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    for c in docker_client.containers.list(all=True):
        if f"user{user.id}_task{task.id}" in c.name:
            c.kill()
            break

    return await update_task_status(db, task_id, status="stopped", logs="User stopped the task")


@router.get("/status/{task_id}", response_model=TaskResponse)
async def task_status(task_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    user = request.state.user
    task = await get_task(db, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/list", response_model=List[TaskResponse])
async def list_user_tasks(request: Request, db: AsyncSession = Depends(get_db)):
    user = request.state.user
    return await get_tasks_for_user(db, user.id)


# --------------------
# Download artifacts
# --------------------
@router.get("/artifacts/{task_id}/{file_path:path}")
async def get_artifact(task_id: int, file_path: str, request: Request):
    user = request.state.user
    task_workspace = f"./workspaces/{user.username}/task_{task_id}"
    full_path = os.path.abspath(os.path.join(task_workspace, file_path))
    if not full_path.startswith(os.path.abspath(task_workspace)) or not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(full_path)


# --------------------
# WebSocket for live logs
# --------------------
@router.websocket("/logs/{task_id}")
async def websocket_logs(websocket: WebSocket, task_id: int):
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
                    asyncio.run_coroutine_threadsafe(websocket.send_text(line.decode().strip()), loop)

            await loop.run_in_executor(None, stream_logs)
            await websocket.close()
    except WebSocketDisconnect:
        print(f"User disconnected from logs for task {task_id}")
