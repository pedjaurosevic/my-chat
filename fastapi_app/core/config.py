"""
Configuration for FastAPI application
Import existing config values and add new ones
"""

import os
import sys
from pathlib import Path
from datetime import timedelta

# Add parent directory to sys.path to import existing config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from config import (
        MBTI_PERSONAS,
        MODEL_SOURCES,
        DEFAULT_MODEL_SOURCE,
        SETTINGS_FILE,
        SESSIONS_DIR,
    )
except ImportError:
    # Fallback values if original config.py is not available
    MBTI_PERSONAS = {}
    MODEL_SOURCES = ["Ollama (11434)", "Kiklop (11435)"]
    DEFAULT_MODEL_SOURCE = "Ollama (11434)"
    SETTINGS_FILE = Path(__file__).parent.parent.parent / ".settings.json"
    SESSIONS_DIR = Path(__file__).parent.parent.parent / "sessions"

# FastAPI settings
API_V1_PREFIX = "/api/v1"
PROJECT_NAME = "OLLAMA.CORE"
VERSION = "1.0.0"
DESCRIPTION = "AI Chat application with local Ollama models"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# PIN authentication
PIN_CODE = "2020"  # Hardcoded PIN for automatic login
PIN_LENGTH = 4

# Ollama settings
OLLAMA_HOSTS = {
    "Ollama (11434)": "http://localhost:11434",
    "Kiklop (11435)": "http://localhost:11435",
}

# Cache settings
RESPONSE_CACHE_TTL = 300  # 5 minutes in seconds
MODEL_LIST_CACHE_TTL = 300  # 5 minutes

# Upload settings
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_DOCUMENT_TYPES = [
    "application/pdf",
    "text/plain",
    "text/markdown",
    "application/epub+zip",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]

# PWA settings
PWA_MANIFEST_URL = "/manifest.json"
PWA_SERVICE_WORKER_URL = "/service-worker.js"

# Frontend settings
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"
STATIC_DIR = Path(__file__).parent.parent / "static"

# Theme colors (dark mode default)
THEME_COLORS = {
    "dark": {
        "primary": "#000000",
        "secondary": "#1a1a1a",
        "tertiary": "#2a2a2a",
        "accent": "#ff6b35",
        "ai": "#4a90a4",
        "user": "#e0e0e0",
        "text_primary": "#e0e0e0",
        "text_secondary": "#a0a0a0",
    },
    "light": {
        "primary": "#ffffff",
        "secondary": "#f5f5f5",
        "tertiary": "#e0e0e0",
        "accent": "#ff6b35",
        "ai": "#4a90a4",
        "user": "#333333",
        "text_primary": "#333333",
        "text_secondary": "#666666",
    },
}

# Create necessary directories
STATIC_DIR.mkdir(exist_ok=True)
SESSIONS_DIR.mkdir(exist_ok=True)
