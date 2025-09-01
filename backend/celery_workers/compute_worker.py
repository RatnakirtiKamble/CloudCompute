import os
import docker
from typing import Dict, List, Optional
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from schemas import TaskStatusEnum
from crud import update_task_status
from config import settings

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

def _set_status(task_id: int, status: str):
    try:
        with SessionLocal() as session:
            update_task_status(session, task_id, status)
            session.commit()
    except Exception as e:
        print(f"[DB ERROR] Failed to update status for task {task_id}: {e}")

# --------------------
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
    """
    Run a containerized compute task.
    Behavior:
      - If `command` is None: use image CMD/ENTRYPOINT. Mount workspace at /outputs and set TASK_OUTPUT_DIR.
      - If `command` is provided: override command and set working_dir=/workspace, mounting workspace at /workspace and TASK_OUTPUT_DIR.
    """
    client = docker.from_env()
    container_id = None
    env = env or {}

    try:
        # Ensure workspace exists
        os.makedirs(workspace, exist_ok=True)

        container_env = {k: str(v) for k, v in env.items()}
        binds = {os.path.abspath(workspace): {"bind": "/workspaces", "mode": "rw"}}
        container_workdir = "/workspaces"
        container_env["TASK_OUTPUT_DIR"] = "/workspaces"
        runtime_command = command + (args or []) if command else None

        # Host config for resources
        host_config = client.api.create_host_config(
            binds=binds,
            nano_cpus=cpu_cores * 1_000_000_000,
            device_requests=[
                docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])
            ] if gpu else None,
        )

        # Create and start container
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

        # Stream logs
        for log in client.api.logs(container_id, stream=True, follow=True):
            print(log.decode(errors="ignore").rstrip())

        # Wait for exit
        exit_code = client.api.wait(container_id)["StatusCode"]
        _set_status(task_id, TaskStatusEnum.completed if exit_code == 0 else TaskStatusEnum.failed)

    except Exception as e:
        print(f"[ERROR] Task {task_id} failed: {e}")
        _set_status(task_id, TaskStatusEnum.failed)
    finally:
        if container_id:
            try:
                client.api.remove_container(container_id, force=True)
            except Exception:
                pass
