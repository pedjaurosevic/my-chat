"""
Dialogue/debate endpoints for AI conversations
"""

import sys
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from fastapi_app.core.dependencies import get_current_user
from fastapi_app.core.ollama_client import chat_with_model
from fastapi_app.core.config import MBTI_PERSONAS

# Import existing dialogue module from parent directory
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])  # Add my-chat to path

try:
    from dialogue import save_dialogue_to_file
except ImportError as e:
    print(f"Warning: Could not import dialogue module: {e}")

    def save_dialogue_to_file(history, topic):
        return "/tmp/dialogue.txt"


router = APIRouter()

# In-memory dialogue storage
dialogues = {}


class DialogueParticipant(BaseModel):
    model: str
    persona: Optional[str] = None
    source: str = "Ollama (11434)"


class StartDialogueRequest(BaseModel):
    participant1: DialogueParticipant
    participant2: DialogueParticipant
    initial_prompt: str
    max_rounds: int = 5
    topic: Optional[str] = None


class DialogueMessage(BaseModel):
    role: str  # "participant1", "participant2", "moderator"
    content: str
    model: Optional[str] = None
    persona: Optional[str] = None
    timestamp: float


class DialogueResponse(BaseModel):
    dialogue_id: str
    messages: List[DialogueMessage]
    current_turn: str  # "participant1" or "participant2"
    completed: bool
    topic: Optional[str] = None


def get_persona_prompt(persona: Optional[str]) -> str:
    """Get system prompt for MBTI persona"""
    if not persona:
        return "You are having a conversation. Respond naturally."

    # Extract MBTI type (e.g., "INTJ - Arhitekta" -> "INTJ")
    mbti_type = persona.split(" - ")[0] if " - " in persona else persona

    base_prompt = MBTI_PERSONAS.get(persona, "")
    if not base_prompt:
        # Try to find by MBTI type
        for key, value in MBTI_PERSONAS.items():
            if key.startswith(mbti_type):
                base_prompt = value
                break

    if base_prompt:
        return f"{base_prompt}\n\nYour conversational partner has a different personality. Stay in character."

    return f"You are having a conversation as {persona}. Stay in character."


@router.post("/dialogue/start")
async def start_dialogue(
    request: StartDialogueRequest, current_user: Dict = Depends(get_current_user)
):
    """Start a new dialogue between two AI models"""
    dialogue_id = f"dialogue_{int(time.time())}_{current_user['user_id']}"

    # Create initial messages
    messages = []

    # Add moderator message with initial prompt
    messages.append(
        DialogueMessage(
            role="moderator", content=request.initial_prompt, timestamp=time.time()
        )
    )

    # Store dialogue state
    dialogues[dialogue_id] = {
        "participant1": request.participant1.dict(),
        "participant2": request.participant2.dict(),
        "messages": messages,
        "current_turn": "participant1",
        "max_rounds": request.max_rounds,
        "rounds_completed": 0,
        "topic": request.topic or request.initial_prompt[:100],
        "user_id": current_user["user_id"],
    }

    # Get first response
    return await next_dialogue_round(dialogue_id, current_user)


@router.post("/dialogue/{dialogue_id}/next")
async def next_dialogue_round(
    dialogue_id: str, current_user: Dict = Depends(get_current_user)
):
    """Get next response in the dialogue"""
    if dialogue_id not in dialogues:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dialogue not found"
        )

    dialogue = dialogues[dialogue_id]

    # Check if dialogue is completed
    if dialogue["rounds_completed"] >= dialogue["max_rounds"]:
        dialogue["completed"] = True
        return DialogueResponse(
            dialogue_id=dialogue_id,
            messages=dialogue["messages"],
            current_turn="completed",
            completed=True,
            topic=dialogue["topic"],
        )

    current_turn = dialogue["current_turn"]
    participant = dialogue[current_turn]

    # Prepare conversation history for the model
    history_messages = []

    # Add persona system prompt
    persona_prompt = get_persona_prompt(participant["persona"])
    history_messages.append({"role": "system", "content": persona_prompt})

    # Add conversation history (last 10 messages)
    for msg in dialogue["messages"][-10:]:
        if msg.role == "moderator":
            history_messages.append({"role": "user", "content": msg.content})
        elif msg.role in ["participant1", "participant2"]:
            # Convert participant messages to assistant role for context
            history_messages.append({"role": "assistant", "content": msg.content})

    # Get the last message as prompt
    last_message = (
        dialogue["messages"][-1].content if dialogue["messages"] else "Hello!"
    )

    # Get response from model
    try:
        response_chunks = []
        for chunk in chat_with_model(
            participant["model"], history_messages, participant["source"], stream=True
        ):
            response_chunks.append(chunk)

        response = "".join(response_chunks)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model error: {str(e)}",
        )

    # Add response to messages
    new_message = DialogueMessage(
        role=current_turn,
        content=response,
        model=participant["model"],
        persona=participant["persona"],
        timestamp=time.time(),
    )

    dialogue["messages"].append(new_message)

    # Update turn
    next_turn = "participant2" if current_turn == "participant1" else "participant1"
    dialogue["current_turn"] = next_turn
    dialogue["rounds_completed"] += 1

    # Check if completed
    completed = dialogue["rounds_completed"] >= dialogue["max_rounds"]

    return DialogueResponse(
        dialogue_id=dialogue_id,
        messages=dialogue["messages"],
        current_turn=next_turn,
        completed=completed,
        topic=dialogue["topic"],
    )


@router.post("/dialogue/{dialogue_id}/moderator")
async def add_moderator_message(
    dialogue_id: str, message: str, current_user: Dict = Depends(get_current_user)
):
    """Add moderator message to dialogue"""
    if dialogue_id not in dialogues:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dialogue not found"
        )

    dialogue = dialogues[dialogue_id]

    moderator_message = DialogueMessage(
        role="moderator", content=message, timestamp=time.time()
    )

    dialogue["messages"].append(moderator_message)

    return {"success": True, "message": "Moderator message added"}


@router.post("/dialogue/{dialogue_id}/save")
async def save_dialogue(
    dialogue_id: str, current_user: Dict = Depends(get_current_user)
):
    """Save dialogue to file"""
    if dialogue_id not in dialogues:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dialogue not found"
        )

    dialogue = dialogues[dialogue_id]

    # Convert to format expected by save_dialogue_to_file
    history = []
    for msg in dialogue["messages"]:
        if msg.role in ["participant1", "participant2"]:
            history.append({"model": msg.model or "unknown", "response": msg.content})

    topic = dialogue["topic"]

    try:
        filepath = save_dialogue_to_file(history, topic)
        return {
            "success": True,
            "filepath": filepath,
            "message": f"Dialogue saved to {filepath}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save dialogue: {str(e)}",
        )


@router.get("/dialogue/{dialogue_id}")
async def get_dialogue(
    dialogue_id: str, current_user: Dict = Depends(get_current_user)
):
    """Get dialogue by ID"""
    if dialogue_id not in dialogues:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dialogue not found"
        )

    dialogue = dialogues[dialogue_id]

    return DialogueResponse(
        dialogue_id=dialogue_id,
        messages=dialogue["messages"],
        current_turn=dialogue["current_turn"],
        completed=dialogue.get("completed", False),
        topic=dialogue["topic"],
    )


@router.get("/dialogues")
async def list_dialogues(current_user: Dict = Depends(get_current_user)):
    """List user's dialogues"""
    user_dialogues = []

    for dialogue_id, dialogue in dialogues.items():
        if dialogue.get("user_id") == current_user["user_id"]:
            user_dialogues.append(
                {
                    "dialogue_id": dialogue_id,
                    "topic": dialogue.get("topic", "Untitled"),
                    "messages_count": len(dialogue.get("messages", [])),
                    "rounds_completed": dialogue.get("rounds_completed", 0),
                    "max_rounds": dialogue.get("max_rounds", 5),
                    "created_at": dialogue_id.split("_")[1]
                    if "_" in dialogue_id
                    else "unknown",
                }
            )

    return {"dialogues": user_dialogues}


@router.delete("/dialogue/{dialogue_id}")
async def delete_dialogue(
    dialogue_id: str, current_user: Dict = Depends(get_current_user)
):
    """Delete dialogue"""
    if dialogue_id not in dialogues:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dialogue not found"
        )

    # Check ownership
    if dialogues[dialogue_id].get("user_id") != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this dialogue",
        )

    del dialogues[dialogue_id]

    return {"success": True, "message": "Dialogue deleted"}


@router.get("/personas")
async def list_personas(current_user: Dict = Depends(get_current_user)):
    """Get list of available MBTI personas"""
    personas = []

    for key, description in MBTI_PERSONAS.items():
        # Extract MBTI type and name
        if " - " in key:
            mbti_type, name = key.split(" - ", 1)
        else:
            mbti_type, name = key, key

        personas.append(
            {
                "id": key,
                "mbti_type": mbti_type,
                "name": name,
                "description": description[:100] + "..."
                if len(description) > 100
                else description,
            }
        )

    return {"personas": personas}
