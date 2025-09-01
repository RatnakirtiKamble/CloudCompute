# middleware/static_logger.py
import os
from datetime import datetime
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class StaticAccessLogger(BaseHTTPMiddleware):
    """
    Middleware to log all accesses to /static.
    Stores logs in the workspace folder for each deployment.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.url.path.startswith("status/tasks/static/"):
            parts = request.url.path.split("/")
            try:
                print("yes")
                task_segment = [seg for seg in parts if seg.startswith("task_")]
                if task_segment:
                    task_id = task_segment[0].replace("task_", "")
                    workspace_path = os.path.abspath(f"./workspaces/task_{task_id}")
                    os.makedirs(workspace_path, exist_ok=True)
                    log_file = os.path.join(workspace_path, "access.log")
                    with open(log_file, "a") as f:
                        ip = request.client.host
                        timestamp = datetime.utcnow().isoformat()
                        f.write(f"{timestamp} {ip}\n")
            except Exception as e:
                print("Failed to log static access:", e)

        return response
