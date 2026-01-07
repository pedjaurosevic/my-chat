"""
Upravljanje sesijama (Chat History)
"""

import json
import os
import time
from config import SETTINGS_FILE, SESSIONS_DIR


def load_settings():
    """Učitaj postavke iz fajla"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"system_prompt": "", "last_model": "", "file_content": "", "messages": [], "chat_document": ""}


def save_settings(settings):
    """Sačuvaj postavke u fajl"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except:
        pass


def save_session(messages, filename=None):
    """Sačuvaj sesiju u fajl"""
    if not messages:
        return None

    if not filename:
        # Generiši ime na osnovu prve poruke ili datuma
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        first_msg = next((m['content'] for m in messages if m['role'] == 'user'), "New Chat")
        safe_title = "".join([c if c.isalnum() else "_" for c in first_msg[:30]]).strip("_")
        filename = f"{timestamp}__{safe_title}.json"

    filepath = SESSIONS_DIR / filename

    # Osiguraj da folder postoji
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with open(filepath, 'w') as f:
            json.dump(messages, f, indent=2)
        return filename
    except Exception as e:
        return None


def load_session(filename):
    """Učitaj sesiju iz fajla"""
    filepath = SESSIONS_DIR / filename
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return []


def get_session_list():
    """Vrati listu sačuvanih sesija"""
    sessions = []
    if SESSIONS_DIR.exists():
        files = sorted(os.listdir(SESSIONS_DIR), reverse=True)
        for f in files:
            if f.endswith(".json"):
                sessions.append(f)
    return sessions


def delete_session(filename):
    """Obriši sesiju"""
    filepath = SESSIONS_DIR / filename
    if filepath.exists():
        os.remove(filepath)
