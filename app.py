"""
OLLAMA.CORE - Modularna AI Chat Aplikacija
"""
OLLAMA.CORE - Modularna AI Chat Aplikacija
"""

import streamlit as st
import ollama
import os
import json
import time
from functools import lru_cache

# Custom moduli
from config import (
    MODEL_SOURCES,
    DEFAULT_MODEL_SOURCE,
    MBTI_PERSONAS,
    CSS_STYLES,
    SETTINGS_FILE,
    SESSIONS_DIR,
)
from session import (
    load_settings,
    save_settings,
    save_session,
    load_session,
    get_session_list,
    delete_session,
)
from export import export_chat_to_text, export_chat_to_epub, export_chat_to_pdf
from agents import (
    web_search,
    web_scrape,
    analyze_document,
    code_helper,
    get_news_from_rss,
    get_top_news,
    api_caller,
)
from dialogue import run_dialogue, save_dialogue_to_file
from ui_helpers import get_model_avatar

# =============================================================================
# FUNKCIJE (ostaju u app.py)
# =============================================================================

st.error("DEBUG: Script started")


@st.cache_data(ttl=300)  # Kešira podatke 5 minuta
def get_models():
    """Dobavi listu dostupnih Ollama modela"""
    try:
        response = ollama.list()
        if hasattr(response, "models"):
            return [m.model for m in response.models]
        elif isinstance(response, dict) and "models" in response:
            return [m["name"] for m in response["models"]]
        return []
    except:
        return []


def get_cloud_models():
    """Dobavi listu cloud modela (sadrže 'cloud' u imenu)"""
    all_models = get_models()
    return [model for model in all_models if "cloud" in model.lower()]


def get_local_models():
    """Dobavi listu lokalnih modela (bez 'cloud' u imenu)"""
    all_models = get_models()
    return [model for model in all_models if "cloud" not in model.lower()]


def chat_with_model(model, messages, placeholder=None):
    """Optimizovano pozivanje modela sa timeoutom"""
    start_time = time.time()
    full_response = ""

    # Kreiraj jedinstveni ključ za keširanje na osnovu modela i poruka
    cache_key = json.dumps([model, messages], sort_keys=True, default=str)

    # Proveri da li već postoji keširani odgovor za ovaj upit
    if "response_cache" not in st.session_state:
        st.session_state.response_cache = {}

    if cache_key in st.session_state.response_cache:
        cached_response = st.session_state.response_cache[cache_key]
        duration = time.time() - start_time
        st.caption(f"Response from cache in {duration:.1f}s")
        if placeholder:
            placeholder.markdown(cached_response)
        return cached_response

    try:
        with st.spinner(f"Generating response using {model}..."):
            stream = ollama.chat(
                model=model,
                messages=messages,
                stream=True,
                options={"num_ctx": 4096, "temperature": 0.7},
            )

            for chunk in stream:
                content = chunk["message"]["content"]
                full_response += content

                # Ažuriraj placeholder uživo ako postoji
                if placeholder:
                    placeholder.markdown(full_response + "▌")

                # Dodaj malo delay da bi stream bio glatkiji
                if len(full_response) % 100 == 0:
                    time.sleep(0.01)

            # Ukloni kursor na kraju
            if placeholder:
                placeholder.markdown(full_response)

        duration = time.time() - start_time
        st.caption(f"Response generated in {duration:.1f}s")

        # Proveri da li je odgovor neizrazit ili da li model izgleda nesigurno
        uncertainty_indicators = [
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

        is_uncertain = any(
            indicator in full_response.lower() for indicator in uncertainty_indicators
        )

        if is_uncertain:
            # Ekstraktuj ključne reči iz korisničkog upita za pretragu
            user_query = messages[-1]["content"] if messages else ""
            if user_query:
                st.info(
                    "Model nije siguran u odgovor. Pokrećem web pretragu za dodatne informacije..."
                )
                search_results = web_search(user_query, num_results=3)

                if search_results and "error" not in search_results[0]:
                    # Dodaj rezultate pretrage u poruku i ponovo pozovi model
                    search_context = "Pronađene informacije iz web pretrage:\n"
                    for i, result in enumerate(search_results):
                        search_context += (
                            f"{i + 1}. {result['title']}: {result['snippet']}\n"
                        )

                    # Dodaj kontekst iz pretrage u poruku za model
                    enhanced_messages = messages + [
                        {
                            "role": "user",
                            "content": f"{user_query}\n\nKontekst iz web pretrage:\n{search_context}",
                        }
                    ]

                    with st.spinner(
                        "Ponovno generišem odgovor sa dodatnim informacijama..."
                    ):
                        enhanced_stream = ollama.chat(
                            model=model,
                            messages=enhanced_messages,
                            stream=True,
                            options={"num_ctx": 4096, "temperature": 0.7},
                        )

                        full_response = ""
                        for chunk in enhanced_stream:
                            content = chunk["message"]["content"]
                            full_response += content

                            # Dodaj malo delay da bi stream bio glatkiji
                            if len(full_response) % 100 == 0:
                                time.sleep(0.01)

                        duration = time.time() - start_time
                        st.caption(f"Enhanced response generated in {duration:.1f}s")

        # Sačuvaj odgovor u keš
        st.session_state.response_cache[cache_key] = full_response

        # AUTO-SAVE: Sačuvaj nakon svakog odgovora
        auto_save_settings()

        return full_response

    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            st.error(
                "Timeout: Model took too long to respond. Try a smaller model or check your connection."
            )
        else:
            st.error(f"Error: {error_msg}")
        return None


def auto_save_settings():
    """Automatski sačuvaj sve važne postavke (uključujući messages)"""
    try:
        settings = {
            "system_prompt": st.session_state.get("system_prompt", ""),
            "last_model": st.session_state.get("last_model", ""),
            "file_content": st.session_state.get("file_content", ""),
            "messages": st.session_state.get("messages", []),
            "chat_document": st.session_state.get("chat_document", ""),
        }
        save_settings(settings)
    except:
        pass


# =============================================================================
# MAIN APP
# =============================================================================

# Postavke

# Model Source Selection - only Ollama (11434)
st.session_state.model_source = DEFAULT_MODEL_SOURCE
os.environ["OLLAMA_HOST"] = "127.0.0.1:11434"

st.set_page_config(
    page_title="COMMAND AI", layout="wide", initial_sidebar_state="collapsed"
)

# Anti-indexing meta tags + Instapaper support
st.markdown(
    """
    <meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
    <meta name="googlebot" content="noindex, nofollow">
    <meta name="bingbot" content="noindex, nofollow">

    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    
    <!-- PWA Meta Tags -->
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Command AI">
    <meta name="theme-color" content="#e8a45c">
    <link rel="manifest" href="/pwa/manifest.json">
    <link rel="apple-touch-icon" href="/pwa/icon-192.png">
    <link rel="icon" type="image/png" sizes="192x192" href="/pwa/icon-192.png">

    <!-- Instapaper and readability support -->
    <meta name="description" content="OLLAMA.CORE - AI Chat Conversation">
    <meta property="og:title" content="OLLAMA.CORE - Chat Conversation">
    <meta property="og:description" content="AI-powered chat conversation saved for offline reading">

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Dynamically add PWA meta tags to head (Streamlit might strip them from body)
        function ensureMetaTag(name, content, attribute = 'name') {
            let meta = document.querySelector(`meta[${attribute}="${name}"]`);
            if (!meta) {
                meta = document.createElement('meta');
                meta.setAttribute(attribute, name);
                meta.setAttribute('content', content);
                document.head.appendChild(meta);
                console.log('Added meta tag:', name);
            }
            return meta;
        }
        
        function ensureLinkTag(rel, href, sizes = null) {
            let link = document.querySelector(`link[rel="${rel}"]`);
            if (!link) {
                link = document.createElement('link');
                link.setAttribute('rel', rel);
                link.setAttribute('href', href);
                if (sizes) link.setAttribute('sizes', sizes);
                document.head.appendChild(link);
                console.log('Added link tag:', rel, href);
            }
            return link;
        }
        
        // Add essential PWA meta tags
        ensureMetaTag('theme-color', '#e8a45c');
        ensureMetaTag('apple-mobile-web-app-capable', 'yes');
        ensureMetaTag('apple-mobile-web-app-status-bar-style', 'black-translucent');
        ensureMetaTag('apple-mobile-web-app-title', 'Command AI');
        ensureMetaTag('mobile-web-app-capable', 'yes');
        
        // Add manifest and icons
        ensureLinkTag('manifest', '/pwa/manifest.json');
        ensureLinkTag('apple-touch-icon', '/pwa/icon-192.png');
        ensureLinkTag('icon', '/pwa/icon-192.png', '192x192');
        
        // Force all chat messages to be left-aligned
        setInterval(function() {
            const messages = document.querySelectorAll('[data-testid="stChatMessage"]');
            messages.forEach(function(msg) {
                msg.style.textAlign = 'left !important';
                msg.style.marginLeft = '0 !important';
                msg.style.marginRight = 'auto !important';
            });
        }, 500);
        
        // Service Worker Registration
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/pwa/sw.js', { scope: '/' })
                .then(reg => console.log('Service Worker registered with scope /:', reg))
                .catch(err => console.log('Service Worker registration failed:', err));
        }
        
        // Beforeunload warning for unsaved changes
        let hasUnsavedChanges = false;
        const chatInput = document.querySelector('[data-testid="stChatInputTextArea"]');
        if (chatInput) {
            chatInput.addEventListener('input', () => {
                hasUnsavedChanges = chatInput.value.trim().length > 0;
            });
        }
        
        window.addEventListener('beforeunload', (e) => {
            if (hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    });
    </script>
""",
    unsafe_allow_html=True,
)

# Custom CSS
st.markdown(f"<style>{CSS_STYLES}</style>", unsafe_allow_html=True)

# Ucitaj sacuvane postavke
saved_settings = load_settings()

# Inicijalizacija sesije
for key in [
    "authenticated",
    "messages",
    "system_prompt",
    "file_content",
    "show_system",
    "show_files",
    "last_model",
    "response_cache",
    "show_agents",
    "show_dialogue",
    "show_history",
    "current_session_file",
    "chat_document",
    "show_multi_debate",
    "show_local_models",
]:
    if key not in st.session_state:
        if key == "authenticated":
            st.session_state[key] = True
        elif key in [
            "show_system",
            "show_files",
            "show_agents",
            "show_dialogue",
            "show_history",
            "show_local_models",
        ]:
            st.session_state[key] = False
        elif key == "messages":
            # Oporavi poslednji razgovor
            st.session_state[key] = saved_settings.get("messages", [])
        elif key == "system_prompt":
            st.session_state[key] = saved_settings.get("system_prompt", "")
        elif key == "file_content":
            st.session_state[key] = saved_settings.get("file_content", "")
        elif key == "last_model":
            st.session_state[key] = saved_settings.get("last_model", "")
        elif key == "chat_document":
            st.session_state[key] = saved_settings.get("chat_document", "")
        elif key == "response_cache":
            st.session_state[key] = {}
        elif key == "show_multi_debate":
            st.session_state[key] = False
        else:
            st.session_state[key] = ""

# --- LOGIN ---
if not st.session_state.authenticated:
    st.error("DEBUG: Login page loaded")
    st.markdown(
        "<div class='ollama-title' style='text-align: center; font-size: 1.8rem; margin: 30px 0;'>╔════════════════════════╗<br>║  O L L A M A . C O R E  ║<br>╚════════════════════════╝</div>",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<div class='pin-display'>", unsafe_allow_html=True)
        pin_input = st.text_input(
            "",
            value="",
            max_chars=6,
            key="pin_display",
            disabled=True,
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='numpad-container'>", unsafe_allow_html=True)
        num_row1 = st.columns([1, 1, 1])
        num_row2 = st.columns([1, 1, 1])
        num_row3 = st.columns([1, 1, 1])
        num_row4 = st.columns([1, 1, 1])

        with num_row1[0]:
            if st.button("1", key="n1"):
                st.session_state.pin_input = (
                    st.session_state.get("pin_input", "") + "1"
                )[:6]
                st.rerun()
        with num_row1[1]:
            if st.button("2", key="n2"):
                st.session_state.pin_input = (
                    st.session_state.get("pin_input", "") + "2"
                )[:6]
                st.rerun()
        with num_row1[2]:
            if st.button("3", key="n3"):
                st.session_state.pin_input = (
                    st.session_state.get("pin_input", "") + "3"
                )[:6]
                st.rerun()

        with num_row2[0]:
            if st.button("4", key="n4"):
                st.session_state.pin_input = (
                    st.session_state.get("pin_input", "") + "4"
                )[:6]
                st.rerun()
        with num_row2[1]:
            if st.button("5", key="n5"):
                st.session_state.pin_input = (
                    st.session_state.get("pin_input", "") + "5"
                )[:6]
                st.rerun()
        with num_row2[2]:
            if st.button("6", key="n6"):
                st.session_state.pin_input = (
                    st.session_state.get("pin_input", "") + "6"
                )[:6]
                st.rerun()

        with num_row3[0]:
            if st.button("7", key="n7"):
                st.session_state.pin_input = (
                    st.session_state.get("pin_input", "") + "7"
                )[:6]
                st.rerun()
        with num_row3[1]:
            if st.button("8", key="n8"):
                st.session_state.pin_input = (
                    st.session_state.get("pin_input", "") + "8"
                )[:6]
                st.rerun()
        with num_row3[2]:
            if st.button("9", key="n9"):
                st.session_state.pin_input = (
                    st.session_state.get("pin_input", "") + "9"
                )[:6]
                st.rerun()

        with num_row4[0]:
            if st.button("⌫", key="clear"):
                st.session_state.pin_input = st.session_state.get("pin_input", "")[:-1]
                st.rerun()
        with num_row4[1]:
            if st.button("0", key="n0"):
                st.session_state.pin_input = (
                    st.session_state.get("pin_input", "") + "0"
                )[:6]
                st.rerun()
        with num_row4[2]:
            if st.button("✓", key="enter", type="primary"):
                if st.session_state.get("pin_input", "") == "2020":
                    st.session_state.authenticated = True
                else:
                    st.error("Netačan PIN")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='command-container'>", unsafe_allow_html=True)
        if st.button("COMMAND", key="login_command", use_container_width=True):
            st.session_state.pin_input = ""
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='toolbar-tags'>", unsafe_allow_html=True)

        st.markdown("<div class='tag-buttons'>", unsafe_allow_html=True)

        col_tags = st.columns([1, 1, 1, 1, 1, 1])

        with col_tags[0]:
            if st.button("📁 DOCS", key="tag_docs", use_container_width=True):
                st.session_state.show_files = not st.session_state.get(
                    "show_files", False
                )
                st.rerun()

        with col_tags[1]:
            if st.button("⚙️ SYSTEM", key="tag_system", use_container_width=True):
                st.session_state.show_system = not st.session_state.get(
                    "show_system", False
                )
                st.rerun()

        with col_tags[2]:
            if st.button("💾 HISTORY", key="tag_history", use_container_width=True):
                st.session_state.show_history = not st.session_state.get(
                    "show_history", False
                )
                st.rerun()

        with col_tags[3]:
            if st.button("🤖 AGENTS", key="tag_agents", use_container_width=True):
                st.session_state.show_agents = not st.session_state.get(
                    "show_agents", False
                )
                st.rerun()

        with col_tags[4]:
            if st.button("💬 DEBATE", key="tag_debate", use_container_width=True):
                st.session_state.show_dialogue = not st.session_state.get(
                    "show_dialogue", False
                )
                st.rerun()

        with col_tags[5]:
            if st.button("🎯 MULTI", key="tag_multi", use_container_width=True):
                st.session_state.show_multi_debate = not st.session_state.get(
                    "show_multi_debate", False
                )
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.stop()

# --- HEADER TOOLBAR ---
t_col1, t_col2, t_col3, t_col4, t_col5, t_col6, t_col7, t_col8 = st.columns(
    [1.5, 0.8, 0.8, 0.8, 0.8, 0.8, 1.2, 0.8]
)

with t_col1:
    st.markdown(
        "<div class='ollama-title' style='margin: 0; font-size: 1.1rem;'>╔═════════════╗<br>║ OLLAMA.CORE ║<br>╚═════════════╝</div>",
        unsafe_allow_html=True,
    )

with t_col2:
    if st.button("➕ CLEAR"):
        st.session_state.messages = []
        st.session_state.file_content = ""
        st.session_state.response_cache = {}
        st.session_state.current_session_file = None
        auto_save_settings()
        st.rerun()

with t_col3:
    if st.button("⚙️ SYSTEM"):
        st.session_state.show_system = not st.session_state.show_system

with t_col4:
    if st.button("💾 HISTORY"):
        st.session_state.show_history = not st.session_state.get("show_history", False)

with t_col5:
    if st.button("🤖 AGENTS"):
        st.session_state.show_agents = not st.session_state.get("show_agents", False)

with t_col6:
    if st.button("💬 DIALOG"):
        st.session_state.show_dialogue = not st.session_state.get(
            "show_dialogue", False
        )

with t_col7:
    # Checkbox za prikaz lokalnih modela
    st.session_state.show_local_models = st.checkbox(
        "➕ Local",
        value=st.session_state.show_local_models,
        key="show_local_models_checkbox",
        help="Show local models in addition to cloud models",
    )

    # Dobavi odgovarajucu listu modela
    try:
        if st.session_state.show_local_models:
            model_names = get_models()  # Svi modeli
        else:
            model_names = get_cloud_models()  # Samo cloud modeli
            # Ako nema cloud modela, prikazi sve
            if not model_names:
                model_names = get_models()
    except Exception as e:
        st.error(f"Greška pri dobavljanju modela: {e}")
        model_names = []

    default_index = 0
    if st.session_state.last_model and st.session_state.last_model in model_names:
        default_index = model_names.index(st.session_state.last_model)

    selected_model = st.selectbox(
        "Model",
        model_names,
        index=default_index if model_names else None,
        label_visibility="collapsed",
    )

    if selected_model and selected_model != st.session_state.last_model:
        st.session_state.last_model = selected_model
        save_settings(
            {
                "system_prompt": st.session_state.system_prompt,
                "last_model": selected_model,
                "file_content": st.session_state.file_content,
            }
        )

with t_col8:
    if st.button("📋 EXPORT"):
        if st.session_state.messages:
            st.write("**Export Chat**")

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                chat_text = export_chat_to_text(st.session_state.messages)
                filename_txt = f"ollama_chat_{time.strftime('%Y%m%d_%H%M%S')}.txt"
                st.download_button(
                    label="📄 TXT",
                    data=chat_text,
                    file_name=filename_txt,
                    mime="text/plain",
                    key="download_txt",
                    use_container_width=True,
                )

            with c2:
                filename_epub = f"ollama_chat_{time.strftime('%Y%m%d_%H%M%S')}.epub"
                if export_chat_to_epub(st.session_state.messages, filename_epub):
                    with open(filename_epub, "rb") as f:
                        st.download_button(
                            label="📚 EPUB",
                            data=f.read(),
                            file_name=filename_epub,
                            mime="application/epub+zip",
                            key="download_epub",
                            use_container_width=True,
                        )
                else:
                    st.error("EPUB error")

            with c3:
                filename_pdf = f"ollama_chat_{time.strftime('%Y%m%d_%H%M%S')}.pdf"
                if export_chat_to_pdf(st.session_state.messages, filename_pdf):
                    with open(filename_pdf, "rb") as f:
                        st.download_button(
                            label="📕 PDF",
                            data=f.read(),
                            file_name=filename_pdf,
                            mime="application/pdf",
                            key="download_pdf",
                            use_container_width=True,
                        )
                else:
                    st.error("PDF error")

            with c4:
                clean_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>OLLAMA.CORE - Chat Export</title>
                    <style>
                        body {{
                            font-family: Georgia, serif;
                            line-height: 1.6;
                            color: #000;
                            background-color: #fff;
                            padding: 20px;
                            max-width: 800px;
                            margin: 0 auto;
                        }}
                        .header {{
                            text-align: center;
                            border-bottom: 2px solid #000;
                            padding-bottom: 20px;
                            margin-bottom: 30px;
                        }}
                        .message {{
                            margin: 20px 0;
                            padding: 15px;
                            border-left: 4px solid #333;
                            background-color: #f5f5f5;
                        }}
                        .user {{
                            border-left-color: #666;
                        }}
                        .assistant {{
                            border-left-color: #999;
                        }}
                        .role {{
                            font-weight: bold;
                            color: #333;
                            margin-bottom: 10px;
                        }}
                        .content {{
                            white-space: pre-wrap;
                        }}
                        .separator {{
                            border-top: 1px solid #ccc;
                            margin: 30px 0;
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>OLLAMA.CORE - Chat Export</h1>
                        <p>Date: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
                        <p>Total messages: {len([m for m in st.session_state.messages if m["role"] != "system"])}</p>
                    </div>
                """

                for msg in st.session_state.messages:
                    if msg["role"] == "system":
                        continue

                    role = msg["role"].upper()
                    model = msg.get("model_name", "")
                    content = msg["content"]

                    if msg["role"] == "user":
                        clean_html += f'<div class="message user"><div class="role">[{role}]</div><div class="content">{content}</div></div>'
                    else:
                        clean_html += f'<div class="message assistant"><div class="role">[{role} - {model}]</div><div class="content">{content}</div></div>'

                    clean_html += '<div class="separator"></div>'

                clean_html += """
                </body>
                </html>
                """

                st.download_button(
                    label="🖨️ PRINT",
                    data=clean_html,
                    file_name=f"ollama_chat_print_{time.strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    key="download_print",
                    help="Otvoriti u novom tab-u i Print → Save as PDF",
                )
        else:
            st.warning("No messages to export")

# --- MODALNE SEKCIJE ---
if st.session_state.show_system:
    with st.container():
        st.markdown(
            "<div style='background-color: #333333; padding: 25px; border-radius: 12px; border: 1px solid #b388b3;'>",
            unsafe_allow_html=True,
        )
        new_prompt = st.text_area(
            "SYSTEM INSTRUCTION:", value=st.session_state.system_prompt, height=150
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("SAVE & CLOSE"):
                st.session_state.system_prompt = new_prompt
                st.session_state.show_system = False
                auto_save_settings()
                st.success("Saved!")
                st.rerun()
        with col2:
            if st.button("CANCEL"):
                st.session_state.show_system = False
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- HISTORY PANEL ---
if st.session_state.get("show_history", False):
    with st.container():
        st.markdown(
            "<div style='background-color: #333333; padding: 25px; border-radius: 12px; border: 1px solid #b388b3;'>",
            unsafe_allow_html=True,
        )
        st.markdown("### 💾 SAČUVANE SESIJE")

        # Opcija za čuvanje trenutne sesije
        if st.session_state.messages:
            c1, c2 = st.columns([3, 1])
            with c1:
                new_session_name = st.text_input(
                    "Ime za novu sesiju (opciono):",
                    placeholder="Ostavite prazno za automatsko ime",
                )
            with c2:
                if st.button("SAČUVAJ TRENUTNU"):
                    filename = new_session_name + ".json" if new_session_name else None
                    saved_name = save_session(st.session_state.messages, filename)
                    if saved_name:
                        st.session_state.current_session_file = saved_name
                        auto_save_settings()
                        st.success(f"Sačuvano: {saved_name}")
                        time.sleep(1)
                        st.rerun()

        st.divider()

        # Lista sesija
        sessions = get_session_list()
        if not sessions:
            st.info("Nema sačuvanih sesija.")
        else:
            for sess in sessions:
                col_name, col_load, col_del = st.columns([4, 1, 1])
                with col_name:
                    st.write(f"📄 {sess}")
                with col_load:
                    if st.button("UČITAJ", key=f"load_{sess}"):
                        loaded_msgs = load_session(sess)
                        if loaded_msgs:
                            st.session_state.messages = loaded_msgs
                            st.session_state.current_session_file = sess
                            auto_save_settings()
                            st.session_state.show_history = False
                            st.rerun()
                with col_del:
                    if st.button("🗑️", key=f"del_{sess}"):
                        delete_session(sess)
                        auto_save_settings()
                        st.rerun()

        if st.button("ZATVORI ISTORIJU"):
            st.session_state.show_history = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

if st.button("📁 DOCS"):
    st.session_state.show_files = not st.session_state.show_files

if st.session_state.show_files:
    with st.container():
        st.markdown(
            "<div style='background-color: #333333; padding: 25px; border-radius: 12px; border: 1px solid #FDFD96;'>",
            unsafe_allow_html=True,
        )

        # Prikazi ako vec ima uucitan sadrzaj
        if st.session_state.file_content:
            word_count = len(st.session_state.file_content.split())
            st.info(
                f"Učitan dokument: {word_count} reči ({len(st.session_state.file_content)} karaktera)"
            )

            if st.button("CLEAR DOCUMENT"):
                st.session_state.file_content = ""
                st.session_state.response_cache = {}
                save_settings(
                    {
                        "system_prompt": st.session_state.system_prompt,
                        "last_model": st.session_state.get("last_model", ""),
                        "file_content": "",
                    }
                )
                st.rerun()

        uploaded_file = st.file_uploader(
            "UPLOAD (TXT, PDF, MD, EPUB):", type=["txt", "pdf", "md", "epub"]
        )
        if uploaded_file:
            content = analyze_document(uploaded_file)
            if not content.startswith("Greška"):
                st.session_state.file_content = content
                save_settings(
                    {
                        "system_prompt": st.session_state.system_prompt,
                        "last_model": st.session_state.get("last_model", ""),
                        "file_content": content,
                    }
                )
                st.success("DATA LOADED & SAVED.")
            else:
                st.error(content)

        if st.button("CLOSE UPLOAD"):
            st.session_state.show_files = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- AGENT PANEL ---
if st.session_state.get("show_agents", False):
    with st.container():
        st.markdown(
            "<div style='background-color: #333333; padding: 25px; border-radius: 12px; border: 1px solid #5c94e8;'>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<h3 style='color: #5c94e8;'>🤖 AGENTI</h3>", unsafe_allow_html=True
        )

        agent_option = st.selectbox(
            "Izaberi agenta:",
            [
                "",
                "🔍 Web Pretraga",
                "🕷️ Web Skrejp",
                "📄 Dokumenti",
                "💻 Kod pomoćnik",
                "📰 Vesti",
                "🔌 API poziv",
            ],
        )

        if agent_option == "🔍 Web Pretraga":
            query = st.text_input("Unesi upit za pretragu:")
            if st.button("Pokreni pretragu"):
                if query:
                    with st.spinner("Pretražujem web..."):
                        results = web_search(query)
                        if results and "error" not in results[0]:
                            st.success(f"Pronađeno {len(results)} rezultata:")
                            for i, result in enumerate(results):
                                with st.expander(
                                    f"Rezultat {i + 1}: {result['title']}"
                                ):
                                    st.write(f"**Link:** {result['link']}")
                                    st.write(f"**Opis:** {result['snippet']}")
                        else:
                            st.error(
                                f"Greška u pretrazi: {results[0]['error'] if results else 'Nema rezultata'}"
                            )

        elif agent_option == "🕷️ Web Skrejp":
            url = st.text_input("Unesi URL za skrejpovanje:")
            if st.button("Skrejpuj stranicu"):
                if url:
                    with st.spinner("Skrejpujem stranicu..."):
                        content = web_scrape(url)
                        if not content.startswith("Greška"):
                            st.success("Stranica uspešno skrejpovana:")
                            st.text_area(
                                "Sadržaj stranice:",
                                content,
                                height=200,
                                key="scraped_content",
                            )
                        else:
                            st.error(content)

        elif agent_option == "📄 Dokumenti":
            st.markdown("**Obrada dokumenata**")
            uploaded_doc = st.file_uploader(
                "Otpremi dokument (PDF, TXT, EPUB):",
                type=["pdf", "txt", "docx", "epub"],
            )
            if uploaded_doc:
                with st.spinner("Analiziram dokument..."):
                    content = analyze_document(uploaded_doc)
                    st.success("Dokument uspešno analiziran:")
                    with st.expander("Prikaži sadržaj dokumenta"):
                        st.text_area("Sadržaj dokumenta:", content, height=300)

        elif agent_option == "💻 Kod pomoćnik":
            st.markdown("**Pomoć sa kodom**")
            code_input = st.text_area("Unesi kod za analizu:", height=200)
            task_option = st.selectbox(
                "Izaberi zadatak:", ["analyze", "debug", "explain"]
            )
            if st.button("Procesuiraj kod"):
                if code_input:
                    with st.spinner("Analiziram kod..."):
                        result = code_helper(code_input, task_option)
                        st.text_area("Rezultat:", result, height=200)

        elif agent_option == "📰 Vesti":
            st.markdown("**Najnovije vesti**")
            if st.button("Dohvati vesti"):
                with st.spinner("Dohvatam vesti..."):
                    news = get_top_news()
                    for source, articles in news.items():
                        with st.expander(f"**{source}**"):
                            if not articles or (
                                "error" in articles[0]
                                if isinstance(articles[0], dict)
                                and "error" in articles[0]
                                else False
                            ):
                                error_msg = (
                                    articles[0]["error"]
                                    if articles
                                    and isinstance(articles[0], dict)
                                    and "error" in articles[0]
                                    else "Nema dostupnih vesti"
                                )
                                st.error(error_msg)
                            else:
                                for i, article in enumerate(articles):
                                    st.write(f"**{article['title']}**")
                                    st.write(f"*{article['published']}*")
                                    st.write(f"{article['summary'][:200]}...")
                                    st.write(f"[Link]({article['link']})")
                                    st.markdown("---")

        elif agent_option == "🔌 API poziv":
            st.markdown("**API poziv**")
            api_url = st.text_input("Unesi URL API-ja:")
            api_method = st.selectbox("Metod:", ["GET", "POST", "PUT", "DELETE"])
            api_headers = st.text_area(
                "Zaglavlja (JSON format):",
                placeholder='{"Content-Type": "application/json"}',
                height=100,
            )
            api_data = st.text_area(
                "Podaci (za POST/PUT):", placeholder='{"kljuc": "vrednost"}', height=150
            )

            if st.button("Pozovi API"):
                if api_url:
                    with st.spinner("Pozivam API..."):
                        try:
                            headers = (
                                json.loads(api_headers) if api_headers.strip() else None
                            )
                            data = json.loads(api_data) if api_data.strip() else None
                            result = api_caller(api_url, api_method, headers, data)
                            if isinstance(result, dict) or isinstance(result, list):
                                st.json(result)
                            else:
                                st.text_area("Odgovor:", result, height=300)
                        except json.JSONDecodeError as e:
                            st.error(f"Greška u parsiranju JSON-a: {str(e)}")

        if st.button("Zatvori agente"):
            st.session_state.show_agents = False
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# --- DIALOG PANEL (DEBATA) ---
if st.session_state.get("show_dialogue", False):
    with st.container():
        st.markdown(
            "<div style='background-color: #333333; padding: 25px; border-radius: 12px; border: 1px solid #FDFD96;'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h3 style='color: #FDFD96;'>💬 AI DEBATA (16 Personalities)</h3>",
            unsafe_allow_html=True,
        )

        model_names = get_models()

        # Inicijalizacija dijalog stanja
        if "dialogue_history" not in st.session_state:
            st.session_state.dialogue_history = []
        if "dialogue_active" not in st.session_state:
            st.session_state.dialogue_active = False

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### LEVI UGAO")
            model1 = st.selectbox("Model 1:", model_names, key="m1_sel")
            persona1 = st.selectbox(
                "Ličnost 1:", list(MBTI_PERSONAS.keys()), key="p1_sel", index=0
            )

        with c2:
            st.markdown("#### DESNI UGAO")
            model2 = st.selectbox(
                "Model 2:",
                model_names,
                key="m2_sel",
                index=1 if len(model_names) > 1 else 0,
            )
            persona2 = st.selectbox(
                "Ličnost 2:", list(MBTI_PERSONAS.keys()), key="p2_sel", index=3
            )

        initial_prompt = st.text_area("Tema debate / Početni scenario:", height=100)

        col_act1, col_act2, col_act3 = st.columns([1, 1, 1])

        with col_act1:
            if st.button("🚀 POČNI DEBATU"):
                st.session_state.dialogue_history = []
                st.session_state.dialogue_active = True

                # Dodaj sistemske poruke za persone u istoriju (ali ih ne prikazuj)
                sys_msg1 = {
                    "role": "system",
                    "content": MBTI_PERSONAS[persona1]
                    + " Tvoj sagovornik ima drugu ličnost. Ostani u svom karakteru.",
                }
                sys_msg2 = {
                    "role": "system",
                    "content": MBTI_PERSONAS[persona2]
                    + " Tvoj sagovornik ima drugu ličnost. Ostani u svom karakteru.",
                }

                # Prva poruka (Korisnikova tema)
                user_msg = {
                    "role": "user",
                    "content": f"Tema diskusije je: {initial_prompt}. Počnite razgovor.",
                }

                st.session_state.dialogue_history.append(user_msg)

                # Prikazujemo korisnikovu poruku odmah
                st.markdown(f"**MODERATOR:** {initial_prompt}")

                # Prvi odgovor Modela 1
                response_box = st.empty()
                with st.spinner(f"{persona1} razmišlja..."):
                    msgs = [sys_msg1, user_msg]
                    resp1 = chat_with_model(model1, msgs, placeholder=response_box)

                    st.session_state.dialogue_history.append(
                        {
                            "role": "assistant",
                            "content": resp1,
                            "model_name": f"{model1} ({persona1.split(' - ')[0]})",
                            "side": "left",
                        }
                    )
                st.rerun()

        with col_act2:
            if st.session_state.dialogue_active and st.button("▶️ SLEDEĆA RUNDA"):
                # Uzmi poslednjih par poruka za kontekst
                history_text = ""
                for msg in st.session_state.dialogue_history[-10:]:
                    if msg["role"] == "assistant":
                        history_text += f"{msg['model_name']}: {msg['content']}\n\n"
                    elif msg["role"] == "user":
                        history_text += f"MODERATOR: {msg['content']}\n\n"

                # Odredi ko je na redu (na osnovu "side" poslednje poruke)
                last_msg = st.session_state.dialogue_history[-1]
                if last_msg.get("side") == "left":
                    # Red je na desnog (Model 2)
                    current_model = model2
                    current_persona = persona2
                    current_side = "right"
                    sys_prompt = MBTI_PERSONAS[persona2]
                else:
                    # Red je na levog (Model 1)
                    current_model = model1
                    current_persona = persona1
                    current_side = "left"
                    sys_prompt = MBTI_PERSONAS[persona1]

                # Kreiraj prompt za modela
                prompt_messages = [
                    {"role": "system", "content": sys_prompt},
                    {
                        "role": "user",
                        "content": f"Ovo je transkript dosadašnjeg razgovora:\n{history_text}\n\nTi si na redu. Odgovori u skladu sa svojom ličnošću ({current_persona}). Budi kratak i konkretan.",
                    },
                ]

                response_box = st.empty()
                with st.spinner(f"{current_persona} odgovara..."):
                    response = chat_with_model(
                        current_model, prompt_messages, placeholder=response_box
                    )

                    st.session_state.dialogue_history.append(
                        {
                            "role": "assistant",
                            "content": response,
                            "model_name": f"{current_model} ({current_persona.split(' - ')[0]})",
                            "side": current_side,
                        }
                    )
                st.rerun()

        with col_act3:
            if st.session_state.dialogue_history and st.button(
                "💾 SAČUVAJ (BookCreator)"
            ):
                path = save_dialogue_to_file(
                    st.session_state.dialogue_history, initial_prompt
                )
                st.success(f"Sačuvano u: {path}")

        # Intervencija moderatora
        if st.session_state.dialogue_active:
            mod_input = st.text_input(
                "Intervencija moderatora (ti):", placeholder="Ubacite se u razgovor..."
            )
            if st.button("Ubaci komentar"):
                st.session_state.dialogue_history.append(
                    {
                        "role": "user",
                        "content": mod_input,
                        "model_name": "MODERATOR",
                        "side": "center",
                    }
                )
                st.rerun()

        st.markdown("---")

        # Prikaz istorije dijaloga
        for msg in st.session_state.dialogue_history:
            if msg["role"] == "user" and msg.get("side") != "center":
                continue

            side = msg.get("side", "left")
            align = (
                "left" if side == "left" else ("right" if side == "right" else "center")
            )
            color = (
                "#FDFD96"
                if side == "left"
                else ("#b388b3" if side == "right" else "#ffffff")
            )
            bg = (
                "rgba(253, 253, 150, 0.1)"
                if side == "left"
                else (
                    "rgba(179, 136, 179, 0.1)"
                    if side == "right"
                    else "rgba(255,255,255,0.1)"
                )
            )

            st.markdown(
                f"""
                <div style='text-align: {align}; margin: 10px 0;'>
                    <div style='display: inline-block; background-color: {bg}; padding: 10px; border-radius: 10px; border-left: 3px solid {color}; max-width: 80%; text-align: left;'>
                        <small style='color: {color}; font-weight: bold;'>{msg.get("model_name", "System")}</small><br>
                        {msg["content"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button("Zatvori dijalog"):
            st.session_state.show_dialogue = False
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# --- MULTI-MODEL DEBATE PANEL (5 participants: 4 LLMs + User) ---
if st.session_state.get("show_multi_debate", False):
    with st.container():
        st.markdown(
            "<div style='background-color: #333333; padding: 25px; border-radius: 12px; border: 1px solid #5c94e8;'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h3 style='color: #5c94e8;'>🎯 MULTI-MODEL DEBATE (5 Učesnika)</h3>",
            unsafe_allow_html=True,
        )

        model_names = get_models()

        if "multi_debate_history" not in st.session_state:
            st.session_state.multi_debate_history = []
        if "multi_debate_active" not in st.session_state:
            st.session_state.multi_debate_active = False
        if "multi_debate_participants" not in st.session_state:
            st.session_state.multi_debate_participants = {}

        st.markdown("#### Konfiguracija Učesnika")

        m1, m2 = st.columns(2)
        with m1:
            st.markdown("**Učesnik 1 (Model):**")
            model_1 = st.selectbox("Model 1:", model_names, key="mm_model1")
            persona_1 = st.selectbox(
                "Ličnost 1:", list(MBTI_PERSONAS.keys()), key="mm_persona1"
            )

        with m2:
            st.markdown("**Učesnik 2 (Model):**")
            model_2 = st.selectbox(
                "Model 2:",
                model_names,
                key="mm_model2",
                index=1 if len(model_names) > 1 else 0,
            )
            persona_2 = st.selectbox(
                "Ličnost 2:", list(MBTI_PERSONAS.keys()), key="mm_persona2", index=3
            )

        m3, m4 = st.columns(2)
        with m3:
            st.markdown("**Učesnik 3 (Model):**")
            model_3 = st.selectbox(
                "Model 3:",
                model_names,
                key="mm_model3",
                index=2 if len(model_names) > 2 else 0,
            )
            persona_3 = st.selectbox(
                "Ličnost 3:", list(MBTI_PERSONAS.keys()), key="mm_persona3", index=6
            )

        with m4:
            st.markdown("**Učesnik 4 (Model):**")
            model_4 = st.selectbox(
                "Model 4:",
                model_names,
                key="mm_model4",
                index=3 if len(model_names) > 3 else 0,
            )
            persona_4 = st.selectbox(
                "Ličnost 4:", list(MBTI_PERSONAS.keys()), key="mm_persona4", index=9
            )

        st.markdown("**Korisnik (Ti) - Učesnik 5**")

        initial_prompt = st.text_area("Tema debate / Početni scenario:", height=100)

        col_act1, col_act2, col_act3 = st.columns([1, 1, 1])

        with col_act1:
            if st.button("🚀 POČNI DEBATU"):
                st.session_state.multi_debate_history = []
                st.session_state.multi_debate_active = True
                st.session_state.multi_debate_participants = {
                    1: {"model": model_1, "persona": persona_1, "side": "1"},
                    2: {"model": model_2, "persona": persona_2, "side": "2"},
                    3: {"model": model_3, "persona": persona_3, "side": "3"},
                    4: {"model": model_4, "persona": persona_4, "side": "4"},
                    5: {"model": "USER", "persona": "Korisnik", "side": "5"},
                }

                user_msg = {
                    "role": "user",
                    "content": f"Tema diskusije je: {initial_prompt}. Počnite razgovor.",
                    "participant": 5,
                }
                st.session_state.multi_debate_history.append(user_msg)

                st.markdown(f"**MODERATOR:** {initial_prompt}")

                with st.spinner("Modeli razmišljaju..."):
                    for i in range(1, 5):
                        participant = st.session_state.multi_debate_participants[i]
                        model = participant["model"]
                        persona = participant["persona"]
                        sys_prompt = (
                            MBTI_PERSONAS[persona]
                            + " Ucestvujes u debati sa jos tri modela i jednim korisnikom. Daj svoje stajaliste."
                        )

                        prompt_messages = [
                            {"role": "system", "content": sys_prompt},
                            {
                                "role": "user",
                                "content": f"Ovo je tema debate: {initial_prompt}. Tvoj stav?",
                            },
                        ]

                        with st.spinner(f"{model} ({persona}) razmišlja..."):
                            resp = chat_with_model(
                                model, prompt_messages, placeholder=None
                            )
                            if resp:
                                st.session_state.multi_debate_history.append(
                                    {
                                        "role": "assistant",
                                        "content": resp,
                                        "model_name": f"{model} ({persona.split(' - ')[0]})",
                                        "participant": i,
                                    }
                                )

                                st.markdown(
                                    f"**{model} ({persona.split(' - ')[0]}):** {resp}"
                                )
                                st.divider()

                st.rerun()

        with col_act2:
            if st.session_state.multi_debate_active and st.button("▶️ SLEDEĆA RUNDA"):
                history_text = ""
                for msg in st.session_state.multi_debate_history[-15:]:
                    if msg.get("participant") == 5:
                        history_text += f"KORISNIK: {msg['content']}\n\n"
                    else:
                        history_text += f"{msg['model_name']}: {msg['content']}\n\n"

                last_participant = st.session_state.multi_debate_history[-1].get(
                    "participant", 5
                )
                next_participant = (last_participant % 5) + 1

                if next_participant == 5:
                    st.info("Red je na tebe! Upiši tvoj odgovor ispod.")
                    user_input = st.text_input("Tvoj odgovor:")
                    if user_input and st.button("Pošalji odgovor"):
                        st.session_state.multi_debate_history.append(
                            {"role": "user", "content": user_input, "participant": 5}
                        )
                        st.rerun()
                else:
                    participant = st.session_state.multi_debate_participants[
                        next_participant
                    ]
                    model = participant["model"]
                    persona = participant["persona"]
                    sys_prompt = MBTI_PERSONAS[persona]

                    prompt_messages = [
                        {"role": "system", "content": sys_prompt},
                        {
                            "role": "user",
                            "content": f"Ovo je dosadašnja debata:\n{history_text}\n\nTi si na redu. Odgovori u skladu sa svojim stavom.",
                        },
                    ]

                    with st.spinner(f"{model} ({persona}) odgovara..."):
                        resp = chat_with_model(model, prompt_messages, placeholder=None)
                        if resp:
                            st.session_state.multi_debate_history.append(
                                {
                                    "role": "assistant",
                                    "content": resp,
                                    "model_name": f"{model} ({persona.split(' - ')[0]})",
                                    "participant": next_participant,
                                }
                            )
                            st.markdown(
                                f"**{model} ({persona.split(' - ')[0]}):** {resp}"
                            )
                            st.rerun()

        with col_act3:
            if st.session_state.multi_debate_history and st.button("💾 SAČUVAJ"):
                path = save_dialogue_to_file(
                    st.session_state.multi_debate_history, initial_prompt
                )
                st.success(f"Sačuvano: {path}")

        moderator_input = st.text_input(
            "Intervencija moderatora:", placeholder="Dodaj komentar ili promeni temu..."
        )
        if st.button("Ubaci komentar"):
            st.session_state.multi_debate_history.append(
                {
                    "role": "user",
                    "content": moderator_input,
                    "participant": 5,
                    "is_moderator": True,
                }
            )
            st.rerun()

        st.markdown("---")

        for msg in st.session_state.multi_debate_history:
            if msg.get("participant") == 5 and not msg.get("is_moderator"):
                continue

            participant_id = msg.get("participant", 1)
            participant = st.session_state.multi_debate_participants.get(
                participant_id, {}
            )

            bg_colors = {
                1: "rgba(253, 253, 150, 0.1)",
                2: "rgba(179, 136, 179, 0.1)",
                3: "rgba(92, 148, 232, 0.1)",
                4: "rgba(150, 150, 150, 0.1)",
                5: "rgba(255, 255, 255, 0.1)",
            }

            border_colors = {
                1: "#FDFD96",
                2: "#b388b3",
                3: "#5c94e8",
                4: "#969696",
                5: "#ffffff",
            }

            bg = bg_colors.get(participant_id, "#ffffff")
            border = border_colors.get(participant_id, "#ffffff")
            align = "left"

            name = msg.get("model_name", "MODERATOR")

            st.markdown(
                f"""
                <div style='text-align: {align}; margin: 10px 0;'>
                    <div style='display: inline-block; background-color: {bg}; padding: 10px; border-radius: 10px; border-left: 3px solid {border}; max-width: 80%; text-align: left;'>
                        <small style='color: {border}; font-weight: bold;'>{name}</small><br>
                        {msg["content"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button("Zatvori multi-debatu"):
            st.session_state.show_multi_debate = False
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# --- CHAT DISPLAY WITH DOCUMENT UPLOAD ---
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            # Odredi avatar
            if msg["role"] == "user":
                avatar = "🧠"
            else:
                model_used = msg.get("model_name", "")
                avatar = get_model_avatar(model_used) if model_used else "🤖"

            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

# --- DOCUMENT UPLOAD IN CHAT ---
if st.session_state.messages:
    with st.container():
        col_doc1, col_doc2, col_doc3, col_doc4 = st.columns([2, 1, 1, 1])

        with col_doc1:
            uploaded_doc = st.file_uploader(
                "📄 Učitaj dokument za diskusiju:",
                type=["txt", "pdf", "md", "epub"],
                key="chat_doc_upload",
            )

        with col_doc2:
            if uploaded_doc:
                if st.button("Analiziraj"):
                    with st.spinner("Analiziram dokument..."):
                        doc_content = analyze_document(uploaded_doc)
                        if not doc_content.startswith("Greška"):
                            st.session_state.chat_document = doc_content
                            st.success("Dokument učitan!")
                        else:
                            st.error(doc_content)

        with col_doc3:
            if st.session_state.get("chat_document"):
                word_count = len(st.session_state.chat_document.split())
                st.info(f"📝 {word_count} reči")

        with col_doc4:
            if st.session_state.get("chat_document"):
                if st.button("Ukloni"):
                    st.session_state.chat_document = None
                    st.rerun()

# --- INPUT ---
if prompt := st.chat_input("Command..."):
    if len(st.session_state.messages) == 0:
        if st.session_state.system_prompt:
            st.session_state.messages.append(
                {"role": "system", "content": st.session_state.system_prompt}
            )

    if st.session_state.get("chat_document"):
        prompt = f"Context from document:\n{st.session_state.chat_document}\n\nUser Question: {prompt}"

    if st.session_state.file_content:
        prompt = f"Context:\n{st.session_state.file_content}\n\nUser Question: {prompt}"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧠"):
        st.markdown(prompt)

    if selected_model:
        current_avatar = get_model_avatar(selected_model)
        with st.chat_message("assistant", avatar=current_avatar):
            response_placeholder = st.empty()

            full_response = chat_with_model(selected_model, st.session_state.messages)

            if full_response:
                response_placeholder.markdown(full_response)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": full_response,
                        "model_name": selected_model,
                    }
                )

# --- INSTAPAPER READABLE CONTENT (Hidden from view, visible to save services) ---
if st.session_state.messages:
    chat_text = export_chat_to_text(st.session_state.messages)
    st.markdown(
        f"""
    <div id="instapaper-readable-content">
        <pre style="white-space: pre-wrap; font-family: monospace;">{chat_text}</pre>
    </div>
    """,
        unsafe_allow_html=True,
    )
