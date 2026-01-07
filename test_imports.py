import sys

print("Python path:", sys.path)
try:
    import streamlit

    print("Streamlit imported")
    import ollama

    print("Ollama imported")
    from config import MODEL_SOURCES

    print("Config imported")
except Exception as e:
    print(f"Import error: {e}")
    import traceback

    traceback.print_exc()
