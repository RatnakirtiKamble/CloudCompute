from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ResourceSpec(BaseModel):
    cpu: int = Field(2, ge=1)
    gpu: bool = Field(False, description="Whether GPU is required")
    gpu_memory: Optional[int] = Field(None, ge=256, description="GPU memory requirement in MB")

class ComputeTaskRequest(BaseModel):
    image: str
    command: Optional[List[str]] = Field(None, description="Override image CMD/ENTRYPOINT")
    args: Optional[List[str]] = Field(None, description="Extra args to append to command")
    env: Dict[str, str] = Field(default_factory=dict)
    resources: ResourceSpec = Field(default_factory=ResourceSpec)

class FileNode(BaseModel):
    path: str
    name: str
    is_dir: bool
    size: Optional[int] = None
