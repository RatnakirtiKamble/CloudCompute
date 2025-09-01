from fastapi import APIRouter, Request, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db.db_connection import get_db
from schemas import TaskResponse, FileNode, ComputeTaskRequest
from services import start_compute_task, list_user_tasks, list_task_files, download_task_file, get_tree_task_workspace
router = APIRouter(prefix="/compute", tags=["Compute"])

@router.post("/start", response_model=TaskResponse)
async def start_compute(
    task_request: ComputeTaskRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    task = await start_compute_task(task_request, request.state.user, db)
    return TaskResponse.model_validate(task)

@router.get("/tasks", response_model=List[TaskResponse])
async def list_my_tasks(request: Request, db: AsyncSession = Depends(get_db)):
    tasks = await list_user_tasks(request.state.user, db)
    return [TaskResponse.model_validate(t) for t in tasks]

@router.get("/{task_id}/files", response_model=List[FileNode])
async def list_task_files(
    task_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    path: str = Query(default="", description="Optional relative path inside the task workspace"),
):
    return await list_task_files(request.state.user, task_id, db, path)

@router.get("/{task_id}/download")
async def download_task_file(
    task_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    path: str = Query(..., description="Relative path to file inside task workspace"),
):
    return await download_task_file(request.state.user, task_id, db, path)

@router.get("/{task_id}/tree", response_model=List[FileNode])
async def tree_task_workspace(task_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    return await get_tree_task_workspace(request.state.user, task_id, db)
