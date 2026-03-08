from pydantic import BaseModel
from typing import Optional


class NotebookCreate(BaseModel):
    url: str
    name: str
    description: str = ""
    topics: str = ""


class NotebookResponse(BaseModel):
    id: str
    url: str
    name: str
    description: str
    topics: list[str]
    created_at: str
    updated_at: str
    use_count: int
    last_used: Optional[str] = None


class NotebookStats(BaseModel):
    total: int
    active_id: Optional[str] = None
