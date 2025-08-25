# upload_router.py
import os
import shutil
import uuid
import subprocess
from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from starlette.responses import JSONResponse
import docker
from utils import _get_free_port

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
    file: UploadFile = File(...)
):
    try:
        user = request.state.user  
        username = user.username

        # Create user-specific upload directory
        user_dir = os.path.join(BASE_DIR, username, "uploads")
        os.makedirs(user_dir, exist_ok=True)

        # Create project-specific folder
        project_id = str(uuid.uuid4())
        project_path = os.path.join(user_dir, project_id)
        os.makedirs(project_path, exist_ok=True)

        # Absolute path (Docker requires this)
        project_path = os.path.abspath(project_path)

        # Save uploaded ZIP/TAR
        file_path = os.path.join(project_path, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Unpack if archive
        if file.filename.endswith(".zip"):
            subprocess.run(["unzip", "-q", file_path, "-d", project_path], check=True)
        elif file.filename.endswith(".tar.gz"):
            subprocess.run(["tar", "-xzf", file_path, "-C", project_path], check=True)

        # Try to detect the real static root (must contain index.html)
        extracted_path = project_path
        contents = os.listdir(project_path)

        # If there's exactly one folder inside, and no index.html in root, dive into it
        if len(contents) == 1 and os.path.isdir(os.path.join(project_path, contents[0])):
            inner = os.path.join(project_path, contents[0])
            if os.path.exists(os.path.join(inner, "index.html")):
                extracted_path = inner

        # If still no index.html, search recursively
        if not os.path.exists(os.path.join(extracted_path, "index.html")):
            for root, dirs, files in os.walk(project_path):
                if "index.html" in files:
                    extracted_path = root
                    break

        if not os.path.exists(os.path.join(extracted_path, "index.html")):
            raise HTTPException(status_code=400, detail="No index.html found in uploaded archive")

        # Serve with NGINX container
        port = _get_free_port()
        container_name = f"{username}-static-{project_id[:8]}"

        docker_client.containers.run(
            "nginx:alpine",
            detach=True,
            name=container_name,
            ports={"80/tcp": port},
            volumes={extracted_path: {"bind": "/usr/share/nginx/html", "mode": "ro"}},
        )

        return JSONResponse({"url": f"http://localhost:{port}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- CONTAINER HOSTING ----------
@router.post("/container")
async def upload_container(
    request: Request,
    file: UploadFile = File(...)
):
    try:
        user = request.state.user
        username = user.username

        # User-specific dir
        user_dir = os.path.join(BASE_DIR, username, "uploads")
        os.makedirs(user_dir, exist_ok=True)

        project_id = str(uuid.uuid4())
        image_path = os.path.join(user_dir, f"{project_id}.tar")
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Load docker image
        with open(image_path, "rb") as f:
            image = docker_client.images.load(f.read())[0]

        # Run container
        port = _get_free_port()
        container_name = f"{username}-container-{project_id[:8]}"

        docker_client.containers.run(
            image.id,
            detach=True,
            name=container_name,
            ports={"80/tcp": port},
        )

        return JSONResponse({"url": f"http://localhost:{port}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
