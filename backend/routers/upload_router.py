# upload_router.py
import os
import shutil
import uuid
import subprocess
from fastapi import APIRouter, HTTPException, UploadFile, File, Request, Depends, Form, Body
from starlette.responses import JSONResponse
import docker

from utils import _get_free_port
from db.db_connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from crud import task_crud
from schemas.task_schema import TaskCreate, TaskEnum, TaskResponse, TaskStatusEnum
import asyncio 
import glob
from services import upload_service, delete_static_task, auto_shutdown_ngrok

router = APIRouter(
    prefix="/static_pages",
    tags=["Static Pages"]
)

BASE_DIR = "workspaces"

docker_client = docker.from_env()

# ---------- STATIC HOSTING ----------
@router.post("/static")
async def upload_static(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    user = request.state.user
    user_id = user.id
    try:
        new_task = TaskCreate(
            task_type=TaskEnum.staticpage,
            status=TaskStatusEnum.pending,
            logs="Upload received, preparing workspace...",
            user_id=user_id,
            path=""
        )
        task_db = await task_crud.create_task(db, new_task)
        task_id = task_db.id 
        extracted_path = await upload_service.save_and_extract_upload(
            file, user.id, task_id
        )
        public_url = upload_service.serve_static_docker(
            extracted_path, user.id, task_id
        )

        await task_crud.update_task_status(
            db, task_id,
            TaskStatusEnum.running,
            logs=f"Serving static site at {public_url}"
        )

        auto_shutdown_ngrok(public_url, task_id, user_id, db, delay_seconds=6000)

        return {"url": public_url, "task_id": task_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Deploy from GitHub
@router.post("/github", response_model=TaskResponse)
async def deploy_from_github(
    repo_url: str = Body(...),
    build_command: str = Body(...),
    subdir: str | None = Body(None),
    env_vars: dict | None = Body(None),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    user = request.state.user
    task_data = TaskCreate(
        task_type=TaskEnum.staticpage,
        user_id=user.id,
        status=TaskStatusEnum.pending,
        logs="Cloning repo..."
    )
    task = await task_crud.create_task(db, task_data)

    task_workspace = os.path.abspath(f"./workspaces/{user.username}/task_{task.id}")
    os.makedirs(task_workspace, exist_ok=True)

    asyncio.create_task(
        upload_service.deploy_github_task(
            task.id, user.id, repo_url, build_command, task_workspace, db, subdir, env_vars
        )
    )
    return task

@router.delete("/tasks/{task_id}")
async def delete_task_route(task_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Delete a task (static or GitHub based).
    Stops Docker container, removes workspace, and deletes DB entry.
    """
    user = request.state.user  # Assuming you set this in middleware

    # Verify task exists & belongs to user
    task = await task_crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")

    await delete_static_task(task_id, user.username, db)
    return {"message": f"Task {task_id} deleted successfully"}