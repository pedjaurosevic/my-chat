"""
Dialogue/debate endpoints for AI conversations
"""

import sys
import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from fastapi_app.core.dependencies import get_current_user, optional_auth
from fastapi_app.core.ollama_client import chat_with_model
from fastapi_app.core.config import MBTI_PERSONAS

# Import existing dialogue module from parent directory
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])  # Add my-chat to path

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
    dialogue_type: Optional[str] = "debate"


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


def get_persona_prompt(
    persona: Optional[str],
    dialogue_type: str = "debate",
    dialogue_context: Optional[Dict] = None,
) -> str:
    """Get system prompt for MBTI persona with dialogue context"""
    if not persona:
        persona_msg = "You are having a conversation. Respond naturally."
    else:
        # Extract MBTI type (e.g., "INTJ - Arhitekta" -> "INTJ")
        mbti_type = persona.split(" - ")[0] if " - " in persona else persona

        base_prompt = MBTI_PERSONAS.get(persona, "")
        if not base_prompt:
            # Try to find by MBTI type
            for key, value in MBTI_PERSONAS.items():
                if key.startswith(mbti_type):
                    base_prompt = value
                    break

        # Add dialogue-specific context
        context_msg = ""
        if dialogue_type == "debate":
            context_msg = "\n\nYou are in a DEBATE. Your goal is to argue your position effectively, but also listen to your opponent's arguments and respond accordingly."
        elif dialogue_type == "discussion":
            context_msg = "\n\nYou are in a DISCUSSION. Focus on collaborative problem-solving and exchanging ideas constructively."
        elif dialogue_type == "brainstorming":
            context_msg = "\n\nYou are in a BRAINSTORMING session. Generate creative ideas without criticism. Encourage wild and unconventional thinking."

        if base_prompt:
            persona_msg = f"{base_prompt}{context_msg}\n\nYour conversational partner has a different personality. Stay in character."
        else:
            persona_msg = f"You are having a conversation as {persona}. Stay in character.{context_msg}"

    # Add dialogue context info
    if dialogue_context:
        context_info = f"\n\n**Dialogue Context:**\n"
        context_info += f"- Type: {dialogue_context.get('dialogue_type', 'debate')}\n"
        context_info += f"- Current Round: {dialogue_context.get('current_round', 1)}/{dialogue_context.get('total_rounds', 5)}\n"
        if dialogue_context.get("participant_info"):
            context_info += "- Participants: " + ", ".join(
                [
                    f"{p.get('model', 'Unknown')} ({p.get('persona', 'Unknown')})"
                    for p in dialogue_context["participant_info"]
                ]
            )
        if dialogue_context.get("moderation_context"):
            context_info += f"- Current State: {dialogue_context['moderation_context']}"

        persona_msg += context_info

    return persona_msg


def get_dialogue_context(dialogue_id: str) -> Optional[Dict]:
    """Get dialogue context from stored dialogue"""
    if dialogue_id not in dialogues:
        return None
    return dialogues.get(dialogue_id, {}).get("context")


@router.post("/dialogue/start")
async def start_dialogue(
    request: StartDialogueRequest, current_user: Dict = Depends(optional_auth)
):
    """Start a new dialogue between two AI models"""
    user_id = current_user.get("user_id", "guest") if current_user else "guest"
    dialogue_id = f"dialogue_{int(time.time())}_{user_id}"

    # Create dialogue context
    dialogue_context = {
        "dialogue_type": request.dialogue_type or "debate",
        "current_round": 1,
        "total_rounds": request.max_rounds,
        "participant_info": [
            {
                "model": request.participant1.model,
                "persona": request.participant1.persona,
            },
            {
                "model": request.participant2.model,
                "persona": request.participant2.persona,
            },
        ],
        "moderation_context": "Initial prompt: " + request.initial_prompt,
    }

    # Create initial messages
    messages = []

    # Add moderator message with initial prompt
    messages.append(
        DialogueMessage(
            role="moderator", content=request.initial_prompt, timestamp=time.time()
        )
    )

    # Store dialogue state with context
    dialogues[dialogue_id] = {
        "participant1": request.participant1.dict(),
        "participant2": request.participant2.dict(),
        "messages": messages,
        "current_turn": "participant1",
        "max_rounds": request.max_rounds,
        "rounds_completed": 0,
        "topic": request.topic or request.initial_prompt[:100],
        "user_id": user_id,
        "dialogue_type": request.dialogue_type or "debate",
        "context": dialogue_context,
    }

    # Get first response
    return await next_dialogue_round(dialogue_id, current_user)


@router.post("/dialogue/{dialogue_id}/next")
async def next_dialogue_round(
    dialogue_id: str, current_user: Dict = Depends(optional_auth)
):
    """Get next response in dialogue"""
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

    # Prepare conversation history for model
    history_messages = []

    # Add persona system prompt with dialogue context
    dialogue_context = get_dialogue_context(dialogue_id)
    persona_prompt = get_persona_prompt(
        participant["persona"],
        dialogue.get("dialogue_type", "debate"),
        dialogue_context,
    )
    history_messages.append({"role": "system", "content": persona_prompt})

    # Add conversation history (last 10 messages)
    for msg in dialogue["messages"][-10:]:
        if msg.role == "moderator":
            history_messages.append({"role": "user", "content": msg.content})
        elif msg.role in ["participant1", "participant2"]:
            # Convert participant messages to assistant role for context
            history_messages.append({"role": "assistant", "content": msg.content})

    # Get last message as prompt
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
    dialogue_id: str, message: str, current_user: Dict = Depends(optional_auth)
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

    # Update moderation context
    if "context" in dialogue:
        dialogue["context"]["moderation_context"] = message

    return {"success": True, "message": "Moderator message added"}


@router.post("/dialogue/{dialogue_id}/save")
async def save_dialogue(
    dialogue_id: str, format: str = "txt", current_user: Dict = Depends(optional_auth)
):
    """Save dialogue to different formats"""
    if dialogue_id not in dialogues:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dialogue not found"
        )

    dialogue = dialogues[dialogue_id]
    topic = dialogue["topic"]
    messages = dialogue["messages"]

    if format == "txt":
        # Generate TXT
        content = "OLLAMA.CORE - AI Dialogue Export\n"
        content += f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"Topic: {topic}\n"
        content += f"Type: {dialogue.get('dialogue_type', 'debate').title()}\n"
        content += f"Total messages: {len(messages)}\n"
        content += "\n" + "=" * 60 + "\n\n"

        for msg in messages:
            if msg.role in ["participant1", "participant2"]:
                role_name = "ASSISTANT"
                participant_info = (
                    f"{msg.model} ({msg.persona})" if msg.persona else msg.model
                )
            else:
                role_name = "MODERATOR"
                participant_info = ""

            content += f"[{role_name} {participant_info}]\n"
            content += f"{msg.content}\n"
            content += "-" * 40 + "\n\n"

        return {
            "success": True,
            "content": content,
            "filename": f"dialogue_{int(time.time())}.txt",
            "content_type": "text/plain",
        }

    elif format == "html":
        # Generate HTML (for PDF conversion)
        content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Dialogue - {topic}</title>
    <style>
        body {{
            font-family: 'Georgia', serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
            background-color: #f5f5f5;
        }}
        .participant1 {{
            background-color: #FFF9C6;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #FFD700;
        }}
        .participant2 {{
            background-color: #DDA0DD;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #9370DB;
        }}
        .moderator {{
            background-color: #F5F5F5;
            padding: 10px;
            margin: 10px 0;
            border-left: 4px solid #333333;
        }}
        .message {{
            margin: 0;
            padding: 10px;
        }}
        .meta {{
            font-size: 11px;
            color: #666;
            margin-bottom: 5px;
        }}
        .content {{
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <h1 style="text-align: center;">OLLAMA.CORE - AI Dialogue</h1>
    <p style="text-align: center;">Topic: {topic}</p>
    <p style="text-align: center;">Date: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
    <hr style="margin: 20px 0;">
"""

        for msg in messages:
            if msg.role == "participant1":
                css_class = "participant1"
                role = f"{msg.model} ({msg.persona})" if msg.persona else msg.model
            elif msg.role == "participant2":
                css_class = "participant2"
                role = f"{msg.model} ({msg.persona})" if msg.persona else msg.model
            else:
                css_class = "moderator"
                role = "Moderator"

            content += f"""
    <div class="{css_class}">
        <div class="meta">Role: {role}</div>
        <div class="message">{msg.content.replace("\n", "<br>").replace("\n\n", "<br><br>")}</div>
    </div>
"""

        content += """
</body>
</html>
        """

        return {
            "success": True,
            "content": content,
            "filename": f"dialogue_{int(time.time())}.html",
            "content_type": "text/html",
        }

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}. Supported formats: txt, html, pdf, epub",
        )


@router.get("/dialogue/{dialogue_id}")
async def get_dialogue(dialogue_id: str, current_user: Dict = Depends(optional_auth)):
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
async def list_dialogues(current_user: Dict = Depends(optional_auth)):
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
    dialogue_id: str, current_user: Dict = Depends(optional_auth)
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
async def list_personas(current_user: Dict = Depends(optional_auth)):
    """Get list of available MBTI personas"""
    personas = []

    for key, description in MBTI_PERSONAS.items():
        # Extract MBTI type and name
        if " - " in key:
            mbti_type, name = key.split(" - ", 1)
        else:
            mbti_type = key
            name = key

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
