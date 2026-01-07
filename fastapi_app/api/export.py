"""
Export endpoints (TXT, EPUB, PDF, HTML)
"""

import sys
import tempfile
import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel

from fastapi_app.core.dependencies import get_current_user

# Import existing export module from parent directory
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])  # Add my-chat to path

try:
    from export import export_chat_to_text, export_chat_to_epub, export_chat_to_pdf
except ImportError as e:
    print(f"Warning: Could not import export module: {e}")

    # Create dummy functions for testing
    def export_chat_to_text(messages):
        return "Export module not available"

    def export_chat_to_epub(messages, filename):
        return False

    def export_chat_to_pdf(messages, filename):
        return False


router = APIRouter()


class ExportRequest(BaseModel):
    messages: List[Dict[str, Any]]
    format: str  # "txt", "epub", "pdf", "html"
    filename: Optional[str] = None


def create_html_export(messages: List[Dict[str, Any]]) -> str:
    """Create HTML export (similar to app.py's HTML export)"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OLLAMA.CORE - Chat Export</title>
    <style>
        body {
            font-family: Georgia, serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        .message {
            margin: 20px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid;
        }
        .user {
            background-color: #f5f5f5;
            border-color: #4a90a4;
        }
        .assistant {
            background-color: #f0f8ff;
            border-color: #ff6b35;
        }
        .role {
            font-weight: bold;
            margin-bottom: 5px;
            color: #666;
        }
        .model {
            font-style: italic;
            color: #888;
            font-size: 0.9em;
        }
        .content {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .separator {
            border: none;
            border-top: 1px solid #ddd;
            margin: 30px 0;
        }
        @media print {
            body { padding: 0; }
            .message { break-inside: avoid; }
        }
    </style>
</head>
<body>
    <h1>OLLAMA.CORE - Chat Export</h1>
    <hr class="separator">
"""

    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        model_name = msg.get("model_name", "")

        if role == "system":
            continue  # Skip system messages in export

        css_class = "user" if role == "user" else "assistant"

        html += f"""
    <div class="message {css_class}">
        <div class="role">{role.upper()}{f" - {model_name}" if model_name else ""}</div>
        <div class="content">{content}</div>
    </div>
"""

    html += """
    <hr class="separator">
    <footer style="text-align: center; color: #888; margin-top: 40px;">
        Exported from OLLAMA.CORE
    </footer>
</body>
</html>"""

    return html


@router.post("/export")
async def export_chat(
    request: ExportRequest, current_user: Dict = Depends(get_current_user)
):
    """Export chat to various formats"""
    try:
        if not request.messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No messages to export"
            )

        # Filter out system messages
        filtered_messages = [m for m in request.messages if m.get("role") != "system"]

        if not filtered_messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No exportable messages (only system messages found)",
            )

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=f".{request.format}"
        ) as tmp:
            filename = tmp.name

            if request.format == "txt":
                content = export_chat_to_text(filtered_messages)
                tmp.write(content)
                media_type = "text/plain"

            elif request.format == "epub":
                # EPUB returns boolean, writes file directly
                success = export_chat_to_epub(filtered_messages, filename)
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to generate EPUB",
                    )
                media_type = "application/epub+zip"

            elif request.format == "pdf":
                # PDF returns boolean, writes file directly
                success = export_chat_to_pdf(filtered_messages, filename)
                if not success:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to generate PDF",
                    )
                media_type = "application/pdf"

            elif request.format == "html":
                content = create_html_export(filtered_messages)
                tmp.write(content)
                media_type = "text/html"

            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported format: {request.format}. Supported: txt, epub, pdf, html",
                )

        # Generate download filename
        download_name = request.filename or f"chat_export.{request.format}"

        # Return file response
        return FileResponse(
            path=filename,
            media_type=media_type,
            filename=download_name,
            background=lambda: os.unlink(filename),  # Clean up temp file after sending
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )


@router.get("/formats")
async def list_export_formats(current_user: Dict = Depends(get_current_user)):
    """Get list of available export formats"""
    formats = [
        {
            "format": "txt",
            "name": "Plain Text",
            "description": "Simple text format with separators",
            "icon": "📄",
        },
        {
            "format": "epub",
            "name": "EPUB",
            "description": "E-reader format with chapters",
            "icon": "📚",
        },
        {
            "format": "pdf",
            "name": "PDF",
            "description": "Printable PDF document",
            "icon": "📕",
        },
        {
            "format": "html",
            "name": "HTML",
            "description": "Web page format for printing",
            "icon": "🖨️",
        },
    ]
    return {"formats": formats}
