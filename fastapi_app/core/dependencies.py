"""
Dependencies for FastAPI routes
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .security import verify_token, get_token_from_header

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Dependency to get current user from JWT token"""
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In this simple app, we only have one user (PIN authenticated)
    # We could add user_id or other claims in the future
    return {"user_id": "default", "authenticated": True}


async def optional_auth(authorization: str = None):
    """Optional authentication - returns user info if token valid, else None"""
    if not authorization:
        return None

    token = get_token_from_header(authorization)
    if not token:
        return None

    payload = verify_token(token)
    if payload is None:
        return None

    return {"user_id": "default", "authenticated": True}
