"""
AI Agent endpoints (web search, scraping, documents, etc.)
"""

import sys
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from fastapi_app.core.dependencies import get_current_user

# Import existing agents from parent directory
sys.path.insert(0, str(__file__).rsplit("/", 3)[0])  # Add my-chat to path

try:
    from agents import (
        web_search,
        web_scrape,
        analyze_document,
        code_helper,
        get_top_news,
        api_caller,
    )
except ImportError as e:
    print(f"Warning: Could not import agents: {e}")

    # Create dummy functions for testing
    def web_search(*args, **kwargs):
        return [{"error": "Agents module not available"}]

    def web_scrape(*args, **kwargs):
        return "Agents module not available"

    def analyze_document(*args, **kwargs):
        return "Agents module not available"

    def code_helper(*args, **kwargs):
        return "Agents module not available"

    def get_top_news(*args, **kwargs):
        return {"error": "Agents module not available"}

    def api_caller(*args, **kwargs):
        return "Agents module not available"


router = APIRouter()


# Request/Response models
class WebSearchRequest(BaseModel):
    query: str
    num_results: int = 3


class WebScrapeRequest(BaseModel):
    url: str


class CodeHelperRequest(BaseModel):
    code: str
    task: str = "analyze"  # "analyze", "debug", "explain"


class ApiCallRequest(BaseModel):
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    data: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, str]] = None


@router.post("/web-search")
async def agent_web_search(
    request: WebSearchRequest, current_user: Dict = Depends(get_current_user)
):
    """Web search using Brave API or Google fallback"""
    try:
        results = web_search(request.query, request.num_results)
        return {"results": results, "query": request.query}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Web search failed: {str(e)}",
        )


@router.post("/web-scrape")
async def agent_web_scrape(
    request: WebScrapeRequest, current_user: Dict = Depends(get_current_user)
):
    """Scrape webpage content"""
    try:
        content = web_scrape(request.url)
        return {
            "url": request.url,
            "content": content,
            "truncated": len(content) > 10000,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Web scrape failed: {str(e)}",
        )


@router.post("/analyze-document")
async def agent_analyze_document(
    file: UploadFile = File(...), current_user: Dict = Depends(get_current_user)
):
    """Analyze uploaded document (PDF, EPUB, TXT, DOCX)"""
    try:
        # Read file content
        content = await file.read()

        # Create a file-like object for the existing analyze_document function
        # The existing function expects a Streamlit UploadedFile-like object
        # We'll create a simple object with the required attributes
        class SimpleUploadedFile:
            def __init__(self, content, filename, content_type):
                self.content = content
                self.name = filename
                self.type = content_type

            def getbuffer(self):
                return self.content

            def read(self):
                return self.content

        uploaded_file = SimpleUploadedFile(
            content=content, filename=file.filename, content_type=file.content_type
        )

        result = analyze_document(uploaded_file)
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "content": result,
            "size": len(content),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document analysis failed: {str(e)}",
        )


@router.post("/code-helper")
async def agent_code_helper(
    request: CodeHelperRequest, current_user: Dict = Depends(get_current_user)
):
    """Code analysis, debugging, or explanation"""
    try:
        result = code_helper(request.code, request.task)
        return {
            "task": request.task,
            "code_length": len(request.code),
            "result": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code helper failed: {str(e)}",
        )


@router.get("/news")
async def agent_news(current_user: Dict = Depends(get_current_user)):
    """Get top news from RSS feeds"""
    try:
        news = get_top_news()
        return {"news": news}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"News fetch failed: {str(e)}",
        )


@router.post("/api-call")
async def agent_api_call(
    request: ApiCallRequest, current_user: Dict = Depends(get_current_user)
):
    """Make API calls (GET, POST, PUT, DELETE)"""
    try:
        result = api_caller(
            url=request.url,
            method=request.method,
            headers=request.headers,
            data=request.data,
            params=request.params,
        )
        return {"url": request.url, "method": request.method, "result": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"API call failed: {str(e)}",
        )


@router.get("/available-agents")
async def list_agents(current_user: Dict = Depends(get_current_user)):
    """List available AI agents"""
    agents = [
        {
            "name": "web-search",
            "description": "Search the web using Brave API or Google fallback",
            "icon": "🔍",
        },
        {
            "name": "web-scrape",
            "description": "Scrape content from webpages",
            "icon": "🕷️",
        },
        {
            "name": "analyze-document",
            "description": "Analyze PDF, EPUB, TXT, DOCX documents",
            "icon": "📄",
        },
        {
            "name": "code-helper",
            "description": "Analyze, debug, or explain code",
            "icon": "💻",
        },
        {
            "name": "news",
            "description": "Get top news from RSS feeds (BBC, TechCrunch, etc.)",
            "icon": "📰",
        },
        {
            "name": "api-call",
            "description": "Make API calls (GET, POST, PUT, DELETE)",
            "icon": "🔌",
        },
    ]
    return {"agents": agents}
