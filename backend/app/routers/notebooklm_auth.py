from fastapi import APIRouter, Depends

from app.firebase_auth import verify_token
from app.services.skill_runner import SkillRunner

router = APIRouter(prefix="/api/v1/notebooklm-auth", tags=["NotebookLM Auth"])


@router.get("/status")
async def auth_status(_user: dict = Depends(verify_token)):
    """Check NotebookLM authentication status."""
    try:
        result = await SkillRunner.run("auth_manager.py", "status")
        stdout = result["stdout"]
        authenticated = "authenticated" in stdout.lower() or "valid" in stdout.lower()
        return {"authenticated": authenticated, "details": stdout}
    except Exception as e:
        return {"authenticated": False, "details": str(e)}


@router.post("/setup")
async def auth_setup(_user: dict = Depends(verify_token)):
    """Initiate NotebookLM authentication (opens browser for manual Google login)."""
    try:
        result = await SkillRunner.run("auth_manager.py", "setup", timeout=120)
        return {"success": True, "details": result["stdout"]}
    except Exception as e:
        return {"success": False, "details": str(e)}
