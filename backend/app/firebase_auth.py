import os
from pathlib import Path

import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import FIREBASE_SERVICE_ACCOUNT

_app = None
security = HTTPBearer()


def init_firebase():
    global _app
    if _app is not None:
        return

    sa_path = Path(FIREBASE_SERVICE_ACCOUNT)
    if sa_path.exists():
        cred = credentials.Certificate(str(sa_path))
        _app = firebase_admin.initialize_app(cred)
    else:
        # Falls back to GOOGLE_APPLICATION_CREDENTIALS env var or default credentials
        _app = firebase_admin.initialize_app()


async def verify_token(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """FastAPI dependency that verifies Firebase ID token."""
    try:
        decoded = auth.verify_id_token(creds.credentials)
        return decoded
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase token",
        )
