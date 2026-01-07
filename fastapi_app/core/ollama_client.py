"""
Ollama client wrapper with caching and streaming support
"""

import json
import time
import subprocess
import ollama
from functools import lru_cache
from typing import List, Dict, Any, Generator, Optional

from .config import OLLAMA_HOSTS, RESPONSE_CACHE_TTL, MODEL_LIST_CACHE_TTL

# Response cache
response_cache = {}
cache_timestamps = {}


def get_ollama_host(source: str) -> str:
    """Get Ollama host URL for given source"""
    return OLLAMA_HOSTS.get(source, OLLAMA_HOSTS["Ollama (11434)"])


@lru_cache(maxsize=1)
def get_models_cached(source: str) -> List[str]:
    """Get list of available models from Ollama (cached)"""
    import os

    # Set OLLAMA_HOST environment variable
    original_host = os.environ.get("OLLAMA_HOST")
    os.environ["OLLAMA_HOST"] = get_ollama_host(source)

    try:
        response = ollama.list()
        if hasattr(response, "models"):
            return [m.model for m in response.models]
        elif isinstance(response, dict) and "models" in response:
            return [m["name"] for m in response["models"]]
        return []
    finally:
        # Restore original OLLAMA_HOST
        if original_host is not None:
            os.environ["OLLAMA_HOST"] = original_host
        else:
            os.environ.pop("OLLAMA_HOST", None)


def get_models(source: str = "Ollama (11434)") -> List[str]:
    """Get list of models with cache TTL"""
    cache_key = f"models_{source}"
    current_time = time.time()

    if cache_key in cache_timestamps:
        if current_time - cache_timestamps[cache_key] < MODEL_LIST_CACHE_TTL:
            return get_models_cached(source)

    # Refresh cache
    get_models_cached.cache_clear()
    models = get_models_cached(source)
    cache_timestamps[cache_key] = current_time

    return models


def chat_with_model(
    model: str,
    messages: List[Dict[str, str]],
    source: str = "Ollama (11434)",
    stream: bool = True,
) -> Generator[str, None, None]:
    """
    Chat with Ollama model with streaming support

    Returns generator yielding response chunks
    """
    import os

    # Set OLLAMA_HOST
    original_host = os.environ.get("OLLAMA_HOST")
    os.environ["OLLAMA_HOST"] = get_ollama_host(source)

    try:
        if stream:
            response = ollama.chat(
                model=model,
                messages=messages,
                stream=True,
                options={"num_ctx": 1024, "temperature": 0.7, "num_threads": 4},
            )

            for chunk in response:
                if "message" in chunk and "content" in chunk["message"]:
                    yield chunk["message"]["content"]
        else:
            response = ollama.chat(
                model=model,
                messages=messages,
                stream=False,
                options={"num_ctx": 1024, "temperature": 0.7, "num_threads": 4},
            )
            yield response["message"]["content"]

    finally:
        # Restore original OLLAMA_HOST
        if original_host is not None:
            os.environ["OLLAMA_HOST"] = original_host
        else:
            os.environ.pop("OLLAMA_HOST", None)


def get_cached_response(model: str, messages: List[Dict[str, str]]) -> Optional[str]:
    """Get cached response if available"""
    cache_key = json.dumps([model, messages], sort_keys=True)
    current_time = time.time()

    if cache_key in response_cache:
        cached_time, response = response_cache[cache_key]
        if current_time - cached_time < RESPONSE_CACHE_TTL:
            return response

    return None


def cache_response(model: str, messages: List[Dict[str, str]], response: str):
    """Cache response with timestamp"""
    cache_key = json.dumps([model, messages], sort_keys=True)
    response_cache[cache_key] = (time.time(), response)


def clear_response_cache():
    """Clear response cache"""
    global response_cache, cache_timestamps
    response_cache = {}
    cache_timestamps = {}


# Uncertainty detection phrases (Serbian)
UNCERTAINTY_INDICATORS = [
    "nemam dovoljno informacija",
    "nije mi poznato",
    "ne mogu da potvrdim",
    "ne znam tačno",
    "nije mi poznat",
    "ne mogu da pronađem",
    "nemam informaciju",
    "nije dostupno",
    "nije poznato",
    "nemam podatak",
]


def contains_uncertainty(response: str) -> bool:
    """Check if response contains uncertainty indicators"""
    response_lower = response.lower()
    return any(indicator in response_lower for indicator in UNCERTAINTY_INDICATORS)
