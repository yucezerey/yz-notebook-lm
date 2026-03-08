import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.firebase_auth import verify_token
from app.models.question import (
    BatchQuestionRequest,
    QuestionRequest,
    TaskResponse,
    TaskResultResponse,
)
from app.services.skill_runner import SkillRunner, SkillRunnerError
from app.services.task_manager import task_manager

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


async def _run_question(task_id: str, question: str, notebook_id: str | None, notebook_url: str | None):
    task_manager.set_running(task_id)
    args = ["--question", question]
    if notebook_id:
        args.extend(["--notebook-id", notebook_id])
    elif notebook_url:
        args.extend(["--notebook-url", notebook_url])

    try:
        result = await SkillRunner.run("ask_question.py", *args)
        task_manager.set_completed(task_id, result["stdout"])
    except SkillRunnerError as e:
        task_manager.set_failed(task_id, str(e))


@router.post("/ask", response_model=TaskResponse)
async def ask_question(
    data: QuestionRequest,
    background_tasks: BackgroundTasks,
    _user: dict = Depends(verify_token),
):
    """Ask a question to a notebook. Returns a task_id for polling."""
    task_id = task_manager.create("ask_question", data.model_dump())
    background_tasks.add_task(
        _run_question,
        task_id,
        data.question,
        data.notebook_id,
        data.notebook_url,
    )
    return TaskResponse(task_id=task_id, status="queued")


@router.get("/tasks/{task_id}", response_model=TaskResultResponse)
async def get_task_result(
    task_id: str,
    _user: dict = Depends(verify_token),
):
    """Get the result of a question task."""
    task = task_manager.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResultResponse(
        task_id=task["id"],
        status=task["status"],
        result=task["result"],
        error=task["error"],
        progress_messages=task["progress_messages"],
    )


@router.post("/batch", response_model=list[TaskResponse])
async def batch_question(
    data: BatchQuestionRequest,
    background_tasks: BackgroundTasks,
    _user: dict = Depends(verify_token),
):
    """Ask the same question to multiple notebooks."""
    responses = []
    for nb_id in data.notebook_ids:
        task_id = task_manager.create("ask_question", {"question": data.question, "notebook_id": nb_id})
        background_tasks.add_task(_run_question, task_id, data.question, nb_id, None)
        responses.append(TaskResponse(task_id=task_id, status="queued"))
    return responses
