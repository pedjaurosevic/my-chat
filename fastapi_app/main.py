"""
FastAPI main application
"""

import os
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from fastapi_app.core.config import (
    PROJECT_NAME,
    VERSION,
    DESCRIPTION,
    FRONTEND_DIR,
    STATIC_DIR,
)
from fastapi_app.api import auth, chat, agents, sessions, export, dialogue


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    print(f"Starting {PROJECT_NAME} v{VERSION}")

    # Ensure directories exist
    FRONTEND_DIR.mkdir(exist_ok=True)
    STATIC_DIR.mkdir(exist_ok=True)

    yield

    # Shutdown
    print(f"Shutting down {PROJECT_NAME}")


# Create FastAPI app
app = FastAPI(title=PROJECT_NAME, version=VERSION, description=DESCRIPTION)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# API routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(dialogue.router, prefix="/api", tags=["dialogue"])


@app.get("/")
async def serve_frontend():
    """Serve frontend HTML"""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)

    # Fallback to a simple message
    return HTMLResponse(f"""
    <html>
        <head><title>{PROJECT_NAME}</title></head>
        <body>
            <h1>{PROJECT_NAME} v{VERSION}</h1>
            <p>Frontend files not found. Please build frontend.</p>
            <p>API is running. Check <a href="/docs">/docs"> for API documentation.</p>
        </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": PROJECT_NAME, "version": VERSION}


@app.get("/api")
async def api_info():
    """API information"""
    return {
        "name": PROJECT_NAME,
        "version": VERSION,
        "description": DESCRIPTION,
        "endpoints": {
            "authentication": "/api/auth",
            "chat": "/api/chat",
            "agents": "/api/agents",
            "sessions": "/api/sessions",
            "export": "/api/export",
            "dialogue": "/api/dialogue",
            "documentation": "/docs",
            "health": "/health",
        },
    }


@app.get("/manifest.json")
async def serve_manifest():
    """Serve PWA manifest"""
    manifest_path = FRONTEND_DIR / "manifest.json"
    if manifest_path.exists():
        return FileResponse(manifest_path)

    # Default manifest
    return {
        "name": PROJECT_NAME,
        "short_name": "OllamaChat",
        "description": DESCRIPTION,
        "start_url": "/",
        "display": "standalone",
        "theme_color": "#000000",
        "background_color": "#1a1a1a",
        "icons": [],
    }


@app.get("/service-worker.js")
async def serve_service_worker():
    """Serve service worker"""
    sw_path = FRONTEND_DIR / "service-worker.js"
    if sw_path.exists():
        return FileResponse(sw_path, media_type="application/javascript")

    # Empty service worker
    return "// Service worker not configured"


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": PROJECT_NAME, "version": VERSION}


@app.get("/")
async def serve_frontend():
    """Serve frontend HTML"""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)

    # Fallback to a simple message
    return HTMLResponse(f"""
    <html>
        <head><title>{PROJECT_NAME}</title></head>
        <body>
            <h1>{PROJECT_NAME} v{VERSION}</h1>
            <p>Frontend files not found. Please build the frontend.</p>
            <p>API is running. Check <a href="/docs">/docs</a> for API documentation.</p>
        </body>
    </html>
    """)


@app.get("/manifest.json")
async def serve_manifest():
    """Serve PWA manifest"""
    manifest_path = FRONTEND_DIR / "manifest.json"
    if manifest_path.exists():
        return FileResponse(manifest_path)

    # Default manifest
    return {
        "name": PROJECT_NAME,
        "short_name": "OllamaChat",
        "description": DESCRIPTION,
        "start_url": "/",
        "display": "standalone",
        "theme_color": "#000000",
        "background_color": "#1a1a1a",
        "icons": [],
    }


@app.get("/service-worker.js")
async def serve_service_worker():
    """Serve service worker"""
    sw_path = FRONTEND_DIR / "service-worker.js"
    if sw_path.exists():
        return FileResponse(sw_path, media_type="application/javascript")

    # Empty service worker
    return "// Service worker not configured"


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": PROJECT_NAME, "version": VERSION}


@app.get("/api")
async def api_info():
    """API information"""
    return {
        "name": PROJECT_NAME,
        "version": VERSION,
        "description": DESCRIPTION,
        "endpoints": {
            "authentication": "/api/auth",
            "chat": "/api/chat",
            "agents": "/api/agents",
            "sessions": "/api/sessions",
            "export": "/api/export",
            "dialogue": "/api/dialogue",
            "documentation": "/docs",
            "health": "/health",
        },
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 handler"""
    return HTMLResponse(
        f"""
    <html>
        <head><title>404 - Not Found</title></head>
        <body>
            <h1>404 - Page Not Found</h1>
            <p>The requested URL {request.url.path} was not found.</p>
            <p><a href="/">Go to homepage</a></p>
        </body>
    </html>
    """,
        status_code=404,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8501, reload=True, log_level="info")
