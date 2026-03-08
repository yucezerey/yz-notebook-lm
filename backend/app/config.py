import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent

SKILL_DIR = Path(os.getenv(
    "SKILL_DIR",
    Path.home() / ".claude" / "skills" / "notebooklm"
))

SKILL_SCRIPTS_DIR = SKILL_DIR / "scripts"
SKILL_DATA_DIR = SKILL_DIR / "data"

FIREBASE_SERVICE_ACCOUNT = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT",
    str(BASE_DIR / "firebase-service-account.json")
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

GENERATION_TIMEOUTS = {
    "audio": 300,
    "video": 420,
    "slides": 180,
    "mindmap": 120,
    "infographic": 180,
    "datatable": 120,
    "reports": 120,
    "deep_research": 900,
    "ask_question": 120,
}
