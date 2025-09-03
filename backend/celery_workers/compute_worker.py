import os
import docker
from typing import Dict, List, Optional
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from schemas import TaskStatusEnum
from crud import update_task_status_sync
from config import settings

from utils import release_gpu

# --------------------
# Celery setup
# --------------------
celery = Celery(
    "compute_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
)

# --------------------
# Synchronous DB session for Celery
# --------------------
engine = create_engine(settings.SYNC_DATABASE_URL)  # use sync DB URL
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def _set_status(task_id: int, status: str, logs: Optional[str] = None):
    try:
        with SessionLocal() as session:
            update_task_status_sync(session, task_id, status, logs)
            session.commit()
            print(task_id, status)
    except Exception as e:
        print(f"[DB ERROR] Failed to update status for task {task_id}: {e}")

# --------------------
# Worker Task
## --------------------
# Worker Task
# --------------------
@celery.task(name="run_container_task")
def run_container_task(
    task_id: int,
    image: str,
    command: Optional[List[str]],
    args: Optional[List[str]],
    workspace: str,
    cpu_cores: int = 2,
    gpu: bool = False,
    env: Optional[Dict[str, str]] = None,
):
    client = docker.from_env()
    container_id = None
    env = env or {}
    logs_accumulated = []

    try:
        os.makedirs(workspace, exist_ok=True)

        container_env = {k: str(v) for k, v in env.items()}
        binds = {os.path.abspath(workspace): {"bind": "/workspaces", "mode": "rw"}}
        container_workdir = "/workspaces"
        container_env["TASK_OUTPUT_DIR"] = "/workspaces"
        runtime_command = command + (args or []) if command else None

        host_config = client.api.create_host_config(
            binds=binds,
            nano_cpus=cpu_cores * 1_000_000_000,
            device_requests=[
                docker.types.DeviceRequest(count=1, capabilities=[["gpu"]])
            ] if gpu else None,
        )

        container = client.api.create_container(
            image=image,
            command=runtime_command,
            working_dir=container_workdir,
            host_config=host_config,
            environment=container_env,
            detach=True,
        )
        container_id = container["Id"]
        client.api.start(container_id)

        # Capture logs
        for log in client.api.logs(container_id, stream=True, follow=True):
            decoded = log.decode(errors="ignore").rstrip()
            logs_accumulated.append(decoded)
            print(decoded)  # still print for realtime debugging

        # Wait for exit
        exit_code = client.api.wait(container_id)["StatusCode"]
        final_logs = "\n".join(logs_accumulated)
        _set_status(
            task_id,
            TaskStatusEnum.completed if exit_code == 0 else TaskStatusEnum.failed,
            logs=final_logs
        )

    except Exception as e:
        print(f"[ERROR] Task {task_id} failed: {e}")
        _set_status(task_id, TaskStatusEnum.failed, logs=f"Worker error: {e}")
    finally:
        if gpu:
            release_gpu(task_id)
        if container_id:
            try:
                client.api.remove_container(container_id, force=True)
            except Exception:
                pass
