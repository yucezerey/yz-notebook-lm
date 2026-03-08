from pydantic import BaseModel
from typing import Optional


class QuestionRequest(BaseModel):
    question: str
    notebook_id: Optional[str] = None
    notebook_url: Optional[str] = None


class BatchQuestionRequest(BaseModel):
    question: str
    notebook_ids: list[str]


class TaskResponse(BaseModel):
    task_id: str
    status: str


class TaskResultResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None
    progress_messages: list[str] = []
