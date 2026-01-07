import streamlit as st
import ollama
import os
import json
import time
from pypdf import PdfReader
from streamlit.components.v1 import html
from functools import lru_cache
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Postavke
st.set_page_config(page_title="COMMAND AI", layout="wide", initial_sidebar_state="collapsed")

# Model Source Selection
if "model_source" not in st.session_state:
    st.session_state.model_source = "Ollama (11434)"

model_sources = ["Ollama (11434)", "Kiklop (11435)"]
selected_source = st.sidebar.selectbox(
    "🤖 Model Source:",
    model_sources,
    index=model_sources.index(st.session_state.model_source),
    help="Choose Ollama (11434) for standard models or Kiklop (11435) for your fine-tuned model"
)

# Reset model when source changes
if selected_source != st.session_state.model_source:
    st.session_state.model_source = selected_source
    st.session_state.last_model = None
    st.rerun()

# Get Ollama host
if selected_source == "Ollama (11434)":
    os.environ["OLLAMA_HOST"] = "127.0.0.1:11434"
    KIKLOP_MODE = False
else:
    KIKLOP_MODE = True
    KIKLOP_HOST = "127.0.0.1:11435"

# Model listing functions
@lru_cache(maxsize=None)
def get_ollama_models():
    try:
        response = ollama.list()
        if hasattr(response, 'models'):
            return [m.model if hasattr(m, 'model') else m.name for m in response.models]
        elif isinstance(response, dict) and 'models' in response:
            return [m['name'] for m in response['models']]
        return []
    except: return []

@lru_cache(maxsize=None)
def get_kiklop_models():
    try:
        response = requests.get(f"http://{KIKLOP_HOST}/api/tags", timeout=5)
        data = response.json()
        return [m['name'] for m in data['models']]
    except: return []

def get_models():
    if KIKLOP_MODE:
        return get_kiklop_models()
    return get_ollama_models()

# Chat functions
def chat_with_kiklop(model, messages, placeholder=None):
    if placeholder: placeholder.empty()
    
    full_text = ""
    try:
        response = requests.post(
            f"http://{KIKLOP_HOST}/api/generate",
            json={"model": model, "messages": messages, "stream": False},
            timeout=120
        )
        
        result = response.json()
        full_text = result.get('response', result.get('message', {}).get('content', ''))
        
        if placeholder:
            placeholder.markdown(full_text)
        
        return full_text
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        if placeholder: placeholder.error(error_msg)
        return error_msg

# Test the integration
st.title(f"🚀 Model Source: {selected_source}")
st.write(f"Mode: {'Kiklop (11435)' if KIKLOP_MODE else 'Ollama (11434)'}")

model_names = get_models()
st.write(f"Available models: {model_names}")

if model_names:
    selected_model = st.selectbox("Select Model:", model_names)
    
    if st.button("Test Chat"):
        messages = [{"role": "user", "content": "Hello, who are you?"}]
        
        if KIKLOP_MODE:
            response = chat_with_kiklop(selected_model, messages)
            st.write(f"Kiklop Response: {response}")
        else:
            response = ollama.chat(model=selected_model, messages=messages)
            st.write(f"Ollama Response: {response.message.content}")
else:
    st.error("No models found!")
