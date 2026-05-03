# =============================================================================
# VTT-Node | vtt-ui/core/auth.py
# API key authentication — Bearer token checked against API_SECRET env var
# =============================================================================

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from core.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


async def require_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """
    FastAPI dependency — validates Bearer token on protected endpoints.
    Usage: @router.get("/endpoint", dependencies=[Depends(require_api_key)])
    """
    if not credentials or not secrets.compare_digest(credentials.credentials, settings.api_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Set Authorization: Bearer <API_SECRET>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials
