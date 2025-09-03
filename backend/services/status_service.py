import psutil
import GPUtil
import subprocess

def get_resource_status():
    """Fetch CPU, memory, and GPU stats."""
    # CPU usage %
    cpu_percent = psutil.cpu_percent(interval=None)

    # Memory usage %
    memory_percent = psutil.virtual_memory().percent

    # GPU info (supports multiple GPUs)
    gpus = GPUtil.getGPUs()
    gpu_data = []
    for gpu in gpus:
        gpu_data.append({
            "id": gpu.id,
            "name": gpu.name,
            "load": gpu.load * 100,  # %
            "vram_used": gpu.memoryUsed,  # MB
            "vram_total": gpu.memoryTotal,  # MB
        })

    return {
        "cpu": cpu_percent,
        "memory": memory_percent,
        "gpu": gpu_data
    }


def get_gpu_vram():
    """
    Returns available VRAM (in MB) for the first GPU.
    Uses nvidia-smi to query free memory.
    """
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.free",
                "--format=csv,noheader,nounits"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        free_mem = int(result.stdout.strip().split("\n")[0])
        return free_mem
    except Exception as e:
        return None
