"""
Chat endpoints for AI conversations
"""

import json
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from fastapi_app.core.dependencies import get_current_user, optional_auth
from fastapi_app.core.ollama_client import (
    chat_with_model,
    get_cached_response,
    cache_response,
    contains_uncertainty,
    get_models,
)
from fastapi_app.core.config import MODEL_SOURCES, DEFAULT_MODEL_SOURCE

router = APIRouter()

# In-memory chat storage (in production would use database)
chat_sessions = {}


class Message(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str
    model_name: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    model: str
    source: str = DEFAULT_MODEL_SOURCE
    use_cache: bool = True
    document_context: Optional[str] = None
    chat_document: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    model: str
    source: str
    cached: bool = False
    enhanced: bool = False
    processing_time: float


def get_session_key(user_id: str, session_id: str = "default") -> str:
    """Generate session key for chat storage"""
    return f"{user_id}:{session_id}"


@router.get("/models")
async def list_models(
    source: str = DEFAULT_MODEL_SOURCE, current_user: Dict = Depends(optional_auth)
):
    """Get list of available models"""
    if source not in MODEL_SOURCES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source. Available sources: {MODEL_SOURCES}",
        )

    models = get_models(source)
    return {"models": models, "source": source, "total": len(models)}


@router.post("/send")
async def send_message(
    request: ChatRequest, current_user: Dict = Depends(optional_auth)
):
    """Send message and get immediate response (non-streaming)"""
    start_time = time.time()

    # Check if model is available
    available_models = get_models(request.source)
    if request.model not in available_models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model '{request.model}' not available in source '{request.source}'. Available: {available_models}",
        )

    # Prepare messages with context
    messages = []

    # Add document context if provided
    if request.document_context:
        messages.append(
            {
                "role": "system",
                "content": f"Context from document:\n{request.document_context}\n\nUser question: {request.message}",
            }
        )
    elif request.chat_document:
        messages.append(
            {
                "role": "system",
                "content": f"Context from chat document:\n{request.chat_document}\n\nUser question: {request.message}",
            }
        )
    else:
        messages.append({"role": "user", "content": request.message})

    # Check cache
    cached_response = None
    if request.use_cache:
        cached_response = get_cached_response(request.model, messages)

    if cached_response:
        processing_time = time.time() - start_time
        return ChatResponse(
            response=cached_response,
            model=request.model,
            source=request.source,
            cached=True,
            processing_time=processing_time,
        )

    # Get response from model
    response_chunks = []
    for chunk in chat_with_model(request.model, messages, request.source, stream=True):
        response_chunks.append(chunk)

    full_response = "".join(response_chunks)

    # Cache response
    if request.use_cache:
        cache_response(request.model, messages, full_response)

    processing_time = time.time() - start_time

    # Check for uncertainty and potentially enhance with web search
    enhanced = False
    if contains_uncertainty(full_response):
        # TODO: Trigger web search and enhance response
        enhanced = True

    return ChatResponse(
        response=full_response,
        model=request.model,
        source=request.source,
        cached=False,
        enhanced=enhanced,
        processing_time=processing_time,
    )


@router.post("/stream")
async def stream_message(
    request: ChatRequest, current_user: Dict = Depends(optional_auth)
):
    """Stream response via Server-Sent Events (SSE)"""

    async def event_generator():
        start_time = time.time()

        # Prepare messages
        messages = []
        if request.document_context:
            messages.append(
                {
                    "role": "system",
                    "content": f"Context from document:\n{request.document_context}\n\nUser question: {request.message}",
                }
            )
        elif request.chat_document:
            messages.append(
                {
                    "role": "system",
                    "content": f"Context from chat document:\n{request.chat_document}\n\nUser question: {request.message}",
                }
            )
        else:
            messages.append({"role": "user", "content": request.message})

        # Check cache for non-streaming cache hit
        cached_response = None
        if request.use_cache:
            cached_response = get_cached_response(request.model, messages)

        if cached_response:
            # Send cached response as single event
            processing_time = time.time() - start_time
            yield f"data: {
                json.dumps(
                    {
                        'chunk': cached_response,
                        'done': True,
                        'cached': True,
                        'processing_time': processing_time,
                    }
                )
            }\n\n"
            return

        # Stream response from model
        full_response = ""
        for chunk in chat_with_model(
            request.model, messages, request.source, stream=True
        ):
            full_response += chunk
            yield f"data: {
                json.dumps({'chunk': chunk, 'done': False, 'cached': False})
            }\n\n"

        # Send completion event
        processing_time = time.time() - start_time
        yield f"data: {
            json.dumps(
                {
                    'chunk': '',
                    'done': True,
                    'cached': False,
                    'processing_time': processing_time,
                    'full_response': full_response,
                }
            )
        }\n\n"

        # Cache the response
        if request.use_cache:
            cache_response(request.model, messages, full_response)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/history")
async def get_chat_history(
    session_id: str = "default", current_user: Dict = Depends(get_current_user)
):
    """Get chat history for session"""
    session_key = get_session_key(current_user["user_id"], session_id)
    history = chat_sessions.get(session_key, [])
    return {"messages": history}


@router.post("/history")
async def save_message(
    message: Message,
    session_id: str = "default",
    current_user: Dict = Depends(get_current_user),
):
    """Save message to chat history"""
    session_key = get_session_key(current_user["user_id"], session_id)

    if session_key not in chat_sessions:
        chat_sessions[session_key] = []

    chat_sessions[session_key].append(message.dict())
    return {"success": True, "message_count": len(chat_sessions[session_key])}


@router.delete("/history")
async def clear_history(
    session_id: str = "default", current_user: Dict = Depends(get_current_user)
):
    """Clear chat history for session"""
    session_key = get_session_key(current_user["user_id"], session_id)

    if session_key in chat_sessions:
        del chat_sessions[session_key]

    return {"success": True, "message": "Chat history cleared"}


@router.get("/sources")
async def list_sources(current_user: Dict = Depends(get_current_user)):
    """Get available model sources"""
    return {"sources": MODEL_SOURCES, "default": DEFAULT_MODEL_SOURCE}
