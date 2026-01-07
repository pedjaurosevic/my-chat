"""
Session management endpoints (save/load/delete chat sessions)
"""

import sys
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from fastapi_app.core.dependencies import get_current_user

# Import existing session module from parent directory
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])  # Add my-chat to path

try:
    from session import (
        save_session as save_session_original,
        load_session as load_session_original,
        get_session_list as get_session_list_original,
        delete_session as delete_session_original,
    )
except ImportError as e:
    print(f"Warning: Could not import session module: {e}")

    # Create dummy functions for testing
    def save_session_original(messages, filename=None):
        return filename or "dummy_session.json"

    def load_session_original(filename):
        return []

    def get_session_list_original():
        return []

    def delete_session_original(filename):
        return True


router = APIRouter()


class SaveSessionRequest(BaseModel):
    messages: List[Dict[str, Any]]
    name: Optional[str] = None


class SessionInfo(BaseModel):
    filename: str
    name: str
    created: str
    message_count: int


@router.get("/sessions")
async def list_sessions(current_user: Dict = Depends(get_current_user)):
    """Get list of saved chat sessions"""
    try:
        session_files = get_session_list_original()
        sessions = []

        for filename in session_files:
            # Extract session name from filename
            # Format: timestamp__session_name.json
            if "__" in filename:
                name = filename.split("__")[1].replace(".json", "")
            else:
                name = filename.replace(".json", "")

            # Load session to get message count
            try:
                messages = load_session_original(filename)
                message_count = len(messages)
            except:
                message_count = 0

            sessions.append(
                {"filename": filename, "name": name, "message_count": message_count}
            )

        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}",
        )


@router.post("/sessions")
async def save_session(
    request: SaveSessionRequest, current_user: Dict = Depends(get_current_user)
):
    """Save current chat session"""
    try:
        filename = save_session_original(request.messages, request.name)

        return {
            "success": True,
            "filename": filename,
            "message_count": len(request.messages),
            "message": "Session saved successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save session: {str(e)}",
        )


@router.get("/sessions/{filename}")
async def load_session(filename: str, current_user: Dict = Depends(get_current_user)):
    """Load saved chat session"""
    try:
        messages = load_session_original(filename)

        return {
            "success": True,
            "filename": filename,
            "messages": messages,
            "message_count": len(messages),
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{filename}' not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load session: {str(e)}",
        )


@router.delete("/sessions/{filename}")
async def delete_session(filename: str, current_user: Dict = Depends(get_current_user)):
    """Delete saved chat session"""
    try:
        delete_session_original(filename)

        return {
            "success": True,
            "filename": filename,
            "message": "Session deleted successfully",
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{filename}' not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}",
        )


@router.get("/sessions/{filename}/info")
async def get_session_info(
    filename: str, current_user: Dict = Depends(get_current_user)
):
    """Get information about a saved session"""
    try:
        messages = load_session_original(filename)

        # Extract session name from filename
        if "__" in filename:
            name = filename.split("__")[1].replace(".json", "")
        else:
            name = filename.replace(".json", "")

        # Count messages by role
        user_messages = sum(1 for m in messages if m.get("role") == "user")
        assistant_messages = sum(1 for m in messages if m.get("role") == "assistant")

        return {
            "filename": filename,
            "name": name,
            "total_messages": len(messages),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "system_messages": len(messages) - user_messages - assistant_messages,
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{filename}' not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session info: {str(e)}",
        )
