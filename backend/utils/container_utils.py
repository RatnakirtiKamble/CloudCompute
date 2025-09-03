import os 
import pathlib
from typing import Dict, List, Optional
from fastapi import HTTPException
from schemas import FileNode
import redis
import json
import subprocess


def task_workspace_for(user_name: str, task_id: int) -> str:
    return os.path.abspath(f"./workspaces/{user_name}/task_{task_id}")

def ensure_is_subpath(base: str, user_path: str) -> str:
    """
    Prevent path traversal; returns absolute path if inside base, else raises.
    """
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

r = redis.Redis(host="localhost", port=6379, db=0)

GPU_TOTAL = 8192   # total VRAM MB
GPU_SLICE = 2048   # 2 GB slices
GPU_KEY = "gpu:used"
GPU_ALLOC_KEY = "gpu:allocations"
GPU_QUEUE_KEY = "gpu:queue"


def try_acquire_gpu(task_id: int) -> bool:
    """Try allocating GPU slice immediately."""
    used = int(r.get(GPU_KEY) or 0)
    if used + GPU_SLICE <= GPU_TOTAL:
        r.incrby(GPU_KEY, GPU_SLICE)
        r.hset(GPU_ALLOC_KEY, task_id, GPU_SLICE)
        return True
    return False


def enqueue_gpu_task(task_id: int, payload: dict):
    """Put task into queue if GPU busy."""
    r.rpush(GPU_QUEUE_KEY, json.dumps({"task_id": task_id, "payload": payload}))


def release_gpu(task_id: int):
    """Release GPU slice, wake up next queued task if any."""
    slice_size = int(r.hget(GPU_ALLOC_KEY, task_id) or 0)
    if slice_size:
        r.decrby(GPU_KEY, slice_size)
        r.hdel(GPU_ALLOC_KEY, task_id)

    # Wake up next task in queue
    next_task_json = r.lpop(GPU_QUEUE_KEY)
    if next_task_json:
        next_task = json.loads(next_task_json)
        tid = next_task["task_id"]
        payload = next_task["payload"]

        if try_acquire_gpu(tid):
            # Trigger worker
            from celery_workers.compute_worker import run_container_task
            run_container_task.delay(**payload)
