import os 
import pathlib
from typing import Dict, List, Optional
from fastapi import HTTPException
from schemas import FileNode

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