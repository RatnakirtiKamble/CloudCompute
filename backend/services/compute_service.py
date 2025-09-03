# services/run_container_task.py

# services/compute_service.py
import os
import pathlib
from typing import List
from fastapi import HTTPException
from fastapi.responses import FileResponse

from schemas import FileNode, TaskCreate, TaskEnum, ComputeTaskRequest, TaskStatusEnum
from crud import create_task, update_task_status, get_task, get_tasks_for_user
from sqlalchemy.ext.asyncio import AsyncSession

from celery_workers.compute_worker import run_container_task

from utils import try_acquire_gpu, enqueue_gpu_task
# --------------------
# Workspace helpers
# --------------------
def task_workspace_for(user_name: str, task_id: int) -> str:
    return os.path.abspath(f"./workspaces/{user_name}/task_{task_id}")

def ensure_is_subpath(base: str, user_path: str) -> str:
    base_path = pathlib.Path(base).resolve()
    target = (base_path / user_path).resolve()
    if not str(target).startswith(str(base_path)):
        raise HTTPException(status_code=400, detail="Invalid path")
    return str(target)

def list_dir(path: str) -> List[FileNode]:
    if not os.path.exists(path):
        return []
    items: List[FileNode] = []
    with os.scandir(path) as it:
        for entry in it:
            try:
                stat = entry.stat()
            except FileNotFoundError:
                continue
            items.append(
                FileNode(
                    path=os.path.relpath(entry.path, path),
                    name=entry.name,
                    is_dir=entry.is_dir(),
                    size=None if entry.is_dir() else stat.st_size,
                )
            )
    return items

# --------------------
# Task operations
# --------------------
async def start_compute_task(
    task_request: ComputeTaskRequest,
    user,
    db: AsyncSession
):
    # Cap CPU cores
    cpu_cores = min(task_request.resources.cpu, 4)

    # Create DB task row
    task_data = TaskCreate(
        task_type=TaskEnum.compute,
        user_id=user.id,
        status=TaskStatusEnum.running,
        path=None,
    )
    task = await create_task(db, task_data)

    # Workspace
    workspace = task_workspace_for(user.username, task.id)
    os.makedirs(workspace, exist_ok=True)
    task.path = workspace
    db.add(task)
    await db.commit()
    await db.refresh(task)

    # Env
    command = task_request.command or None
    args = task_request.args or []
    env = dict(task_request.env or {})
    env["TASK_OUTPUT_DIR"] = "/workspaces"
    if command is None:
        env.setdefault("OUTPUT_DIR", "/outputs")

    gpu_requested = task_request.resources.gpu
    payload = {
        "task_id": task.id,
        "image": task_request.image,
        "command": command,
        "args": args,
        "workspace": workspace,
        "cpu_cores": cpu_cores,
        "gpu": gpu_requested,  # always request, scheduler decides
        "env": env,
    }

   
    if gpu_requested:
        if try_acquire_gpu(task.id):
            run_container_task.delay(**payload)
        else:
            enqueue_gpu_task(task.id, {**payload})
    else:
        run_container_task.delay(**payload, gpu=False)

    return task


async def list_user_tasks(user, db: AsyncSession):
    tasks = await get_tasks_for_user(db, user.id)
    return tasks

async def list_task_files(user, task_id: int, db: AsyncSession, path: str = "") -> List[FileNode]:
    task = await get_task(db, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    base = task_workspace_for(user.username, task_id)
    target_dir = ensure_is_subpath(base, path)
    if not os.path.isdir(target_dir):
        raise HTTPException(status_code=400, detail="Not a directory")

    return list_dir(target_dir)

async def download_task_file(user, task_id: int, db: AsyncSession, path: str) -> FileResponse:
    task = await get_task(db, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    base = task_workspace_for(user.username, task_id)
    abs_path = ensure_is_subpath(base, path)
    if not os.path.isfile(abs_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(abs_path, filename=os.path.basename(abs_path))

async def get_tree_task_workspace(user, task_id: int, db: AsyncSession) -> List[FileNode]:
    task = await get_task(db, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    base = task_workspace_for(user.username, task_id)
    if not os.path.exists(base):
        return []

    result: List[FileNode] = []
    for root, dirs, files in os.walk(base):
        depth = pathlib.Path(root).relative_to(base).parts
        if len(depth) > 2:
            continue
        for d in dirs:
            full = os.path.join(root, d)
            result.append(
                FileNode(
                    path=os.path.relpath(full, base),
                    name=d,
                    is_dir=True,
                    size=None,
                )
            )
        for f in files:
            full = os.path.join(root, f)
            try:
                size = os.path.getsize(full)
            except FileNotFoundError:
                continue
            result.append(
                FileNode(
                    path=os.path.relpath(full, base),
                    name=f,
                    is_dir=False,
                    size=size,
                )
            )
    return result
