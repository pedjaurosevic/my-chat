#!/bin/bash
cd /home/peterofovik/my-chat
source venv/bin/activate
exec python3 -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
