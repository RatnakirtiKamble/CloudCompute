# upload_service.py
import os
import shutil
import subprocess
import asyncio
import glob
import docker
from sqlalchemy.ext.asyncio import AsyncSession
from crud import task_crud
from schemas.task_schema import TaskStatusEnum
from pyngrok import ngrok
from config import settings

docker_client = docker.from_env()
BASE_DIR = "workspaces"

ngrok.set_auth_token(settings.NGROK_AUTH_TOKEN)

# -----------------------------
# Save & extract uploaded archive
# -----------------------------
# -----------------------------
# Save & extract uploaded archive
# -----------------------------
async def save_and_extract_upload(file, user_id: int, task_id: int) -> str:
    """
    Save uploaded ZIP/TAR inside uploads/ and extract to extracted/.
    Returns absolute path to folder containing index.html.
    """
    task_dir = os.path.abspath(os.path.join(BASE_DIR, str(user_id), f"task_{task_id}"))
    uploads_dir = os.path.join(task_dir, "uploads")
    extracted_dir = os.path.join(task_dir, "extracted")

    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(extracted_dir, exist_ok=True)

    # Save uploaded file inside uploads
    file_path = os.path.join(uploads_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract archive in extracted_dir
    if file.filename.endswith(".zip"):
        subprocess.run(["unzip", "-q", file_path, "-d", extracted_dir], check=True)
    elif file.filename.endswith(".tar.gz"):
        subprocess.run(["tar", "-xzf", file_path, "-C", extracted_dir], check=True)
    else:
        raise ValueError("Unsupported file format (only .zip or .tar.gz)")

    # Locate folder containing index.html
    extracted_path = extracted_dir
    contents = os.listdir(extracted_dir)
    if len(contents) == 1 and os.path.isdir(os.path.join(extracted_dir, contents[0])):
        inner = os.path.join(extracted_dir, contents[0])
        if os.path.exists(os.path.join(inner, "index.html")):
            extracted_path = inner
            
    if not os.path.exists(os.path.join(extracted_path, "index.html")):
        for root, dirs, files in os.walk(extracted_dir):
            if "index.html" in files:
                extracted_path = root
                break

    if not os.path.exists(os.path.join(extracted_path, "index.html")):
        raise ValueError("No index.html found in uploaded archive")

    return os.path.abspath(extracted_path)  



# -----------------------------
# Serve static content in Docker + ngrok
# -----------------------------
def serve_static_docker(extracted_path: str, user_id: int, task_id: int) -> str:
    container_name = f"user{user_id}-task{task_id}"

    # Find free host port
    from utils import _get_free_port
    host_port = _get_free_port()

    # Run NGINX container
    docker_client.containers.run(
        "nginx:alpine",
        detach=True,
        name=container_name,
        ports={"80/tcp": host_port},
        volumes={extracted_path: {"bind": "/usr/share/nginx/html", "mode": "ro"}},
    )

    # Expose public URL with ngrok
    public_url = ngrok.connect(host_port, "http").public_url
    return public_url


# -----------------------------
# Deploy GitHub repo
# -----------------------------
async def deploy_github_task(
    task_id: int,
    user_id: int,
    repo_url: str,
    build_command: str,
    workspace: str,
    db: AsyncSession,
    subdir: str | None = None,
    env_vars: dict | None = None
):
    try:
        # Always use absolute workspace path
        workspace = os.path.abspath(workspace)

        # Clone repo into workspace
        proc = await asyncio.create_subprocess_exec(
            "git", "clone", repo_url, workspace,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        out, err = await proc.communicate()
        if proc.returncode != 0:
            await task_crud.update_task_status(db, task_id, TaskStatusEnum.failed, logs=err.decode())
            return

        # Where to run build
        run_dir = os.path.join(workspace, subdir) if subdir else workspace
        run_dir = os.path.abspath(run_dir)

        # Install dependencies
        install_proc = await asyncio.create_subprocess_exec(
            "npm", "install",
            cwd=run_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await install_proc.communicate()

        # Run build command
        build_parts = build_command.split()
        build_proc = await asyncio.create_subprocess_exec(
            *build_parts,
            cwd=run_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        out, err = await build_proc.communicate()
        if build_proc.returncode != 0:
            await task_crud.update_task_status(db, task_id, TaskStatusEnum.failed, logs=err.decode())
            return

        # Find build folder
        candidates = glob.glob(os.path.join(run_dir, "**/dist"), recursive=True)
        candidates += glob.glob(os.path.join(run_dir, "**/build"), recursive=True)
        if not candidates:
            await task_crud.update_task_status(db, task_id, TaskStatusEnum.failed, logs="No dist/build folder found")
            return
        static_folder = os.path.abspath(candidates[0])  # make absolute

        # Dockerfile (absolute paths)
        dockerfile_path = os.path.join(workspace, "Dockerfile")
        rel_static_folder = os.path.relpath(static_folder, workspace)  # relative inside image
        with open(dockerfile_path, "w") as f:
            f.write(f"""
                FROM nginx:alpine
                COPY {rel_static_folder} /usr/share/nginx/html
                EXPOSE 80
                CMD ["nginx", "-g", "daemon off;"]
            """)

        # Build Docker image
        image_tag = f"{user_id}_task_{task_id}"
        image, _ = docker_client.images.build(path=workspace, tag=image_tag)

        # Run container
        from utils import _get_free_port
        host_port = _get_free_port()
        container_name = f"user{user_id}-task{task_id}"
        safe_env = {k: str(v) for k, v in (env_vars or {}).items()}

        logs_dir = os.path.join(workspace, "nginx_logs")
        os.makedirs(logs_dir, exist_ok=True)

        docker_client.containers.run(
            image.id,
            detach=True,
            name=container_name,
            ports={"80/tcp": host_port},
            volumes={logs_dir: {"bind": "/var/log/nginx", "mode": "rw"}},
            environment=safe_env
        )

        public_url = ngrok.connect(host_port, "http").public_url
        await task_crud.update_task_status(db, task_id, TaskStatusEnum.running, logs=f"Deployed at {public_url}")

        auto_shutdown_ngrok(public_url, task_id, user_id, db, delay_seconds=600)


    except Exception as e:
        await task_crud.update_task_status(db, task_id, "failed", logs=str(e))



# -----------------------------
# Delete task: remove container + workspace + DB
# -----------------------------
async def delete_static_task(task_id: int, user_id: int, db: AsyncSession):
    container_name = f"user{user_id}-task{task_id}"

    # Stop & remove Docker container
    try:
        container = docker_client.containers.get(container_name)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        pass

    # Remove task workspace (uploads + extracted)
    task_dir = os.path.join(BASE_DIR, str(user_id), f"task_{task_id}")
    if os.path.exists(task_dir):
        shutil.rmtree(task_dir)

    # Delete DB record
    await task_crud.delete_task(db, task_id)


async def auto_shutdown_ngrok(url: str, task_id: int, user_id: int, db: AsyncSession, delay_seconds: int = 600, ) -> None:
    await asyncio.sleep(delay_seconds)
    try:
        tunnels = ngrok.get_tunnels()
        for tunnel in tunnels:
            if tunnel.public_url == url:
                ngrok.disconnect(url)
                await delete_static_task(task_id, user_id, db)
                break
    except Exception as e:
        print(f"Error during ngrok autoshutdown: {e}")