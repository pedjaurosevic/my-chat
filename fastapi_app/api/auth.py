"""
Authentication endpoints
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from fastapi_app.core.security import verify_pin, create_access_token
from fastapi_app.core.config import PIN_LENGTH

router = APIRouter()


class LoginRequest(BaseModel):
    pin: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # minutes


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate with PIN code"""
    if len(request.pin) != PIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PIN must be {PIN_LENGTH} digits",
        )

    if not verify_pin(request.pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid PIN"
        )

    # Create access token
    access_token = create_access_token(data={"sub": "user"})

    return LoginResponse(
        access_token=access_token,
        expires_in=60 * 24,  # 24 hours in minutes
    )


@router.post("/logout")
async def logout():
    """Logout endpoint (client should discard token)"""
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "Logged out successfully"}
    )


@router.get("/status")
async def auth_status():
    """Check authentication status (always returns true for this endpoint)"""
    return {"authenticated": True}
