from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ResourceSpec(BaseModel):
    cpu: int = Field(2, ge=1)
    gpu: int = Field(0, ge=0)
    memory: Optional[str] = Field(None, description="Optional: e.g. '8Gi' (not enforced by docker-py, kept for future K8s)")

class ComputeTaskRequest(BaseModel):
    image: str
    command: Optional[List[str]] = Field(None, description="If omitted, uses image CMD/ENTRYPOINT")
    args: Optional[List[str]] = Field(None, description="Extra args to append to command")
    env: Dict[str, str] = Field(default_factory=dict)
    resources: ResourceSpec = Field(default_factory=ResourceSpec)

class FileNode(BaseModel):
    path: str
    name: str
    is_dir: bool
    size: Optional[int] = None
