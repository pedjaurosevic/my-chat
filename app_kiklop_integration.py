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

# Model source selection
if "model_source" not in st.session_state:
    st.session_state.model_source = "Ollama (11434)"

model_sources = ["Ollama (11434)", "Kiklop (11435)"]
selected_source = st.sidebar.selectbox("Model Source:", model_sources, index=model_sources.index(st.session_state.model_source))

if selected_source != st.session_state.model_source:
    st.session_state.model_source = selected_source
    st.session_state.last_model = None

# Set Ollama host based on source
if selected_source == "Ollama (11434)":
    os.environ["OLLAMA_HOST"] = "127.0.0.1:11434"
else:
    os.environ["OLLAMA_HOST"] = "127.0.0.1:11435"

# Rest of app.py continues here...
st.markdown(f"# {selected_source}")
st.write("Model source: ", selected_source)
