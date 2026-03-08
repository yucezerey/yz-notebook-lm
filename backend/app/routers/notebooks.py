from fastapi import APIRouter, Depends, HTTPException

from app.firebase_auth import verify_token
from app.models.notebook import NotebookCreate
from app.services.skill_runner import SkillRunner, SkillRunnerError

router = APIRouter(prefix="/api/v1/notebooks", tags=["Notebooks"])


@router.get("")
async def list_notebooks(_user: dict = Depends(verify_token)):
    """List all notebooks in the library."""
    try:
        result = await SkillRunner.run("notebook_manager.py", "list")
        return {"notebooks": result["stdout"]}
    except SkillRunnerError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def add_notebook(
    data: NotebookCreate,
    _user: dict = Depends(verify_token),
):
    """Add a notebook to the library."""
    args = [
        "add",
        "--url", data.url,
        "--name", data.name,
    ]
    if data.description:
        args.extend(["--description", data.description])
    if data.topics:
        args.extend(["--topics", data.topics])

    try:
        result = await SkillRunner.run("notebook_manager.py", *args)
        return {"success": True, "details": result["stdout"]}
    except SkillRunnerError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notebook_id}")
async def remove_notebook(
    notebook_id: str,
    _user: dict = Depends(verify_token),
):
    """Remove a notebook from the library."""
    try:
        result = await SkillRunner.run("notebook_manager.py", "remove", "--id", notebook_id)
        return {"success": True, "details": result["stdout"]}
    except SkillRunnerError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{notebook_id}/activate")
async def activate_notebook(
    notebook_id: str,
    _user: dict = Depends(verify_token),
):
    """Set a notebook as active."""
    try:
        result = await SkillRunner.run("notebook_manager.py", "activate", "--id", notebook_id)
        return {"success": True, "details": result["stdout"]}
    except SkillRunnerError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_notebooks(
    q: str,
    _user: dict = Depends(verify_token),
):
    """Search notebooks by keyword."""
    try:
        result = await SkillRunner.run("notebook_manager.py", "search", "--query", q)
        return {"results": result["stdout"]}
    except SkillRunnerError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def notebook_stats(_user: dict = Depends(verify_token)):
    """Get notebook library statistics."""
    try:
        result = await SkillRunner.run("notebook_manager.py", "stats")
        return {"stats": result["stdout"]}
    except SkillRunnerError as e:
        raise HTTPException(status_code=500, detail=str(e))
