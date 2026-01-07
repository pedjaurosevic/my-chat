#!/bin/bash
echo "Optimizing Ollama and Streamlit setup..."

# Update Ollama config
echo "Updating Ollama config..."
sudo cp /home/peterofovik/my-chat/ollama-override.conf /etc/systemd/system/ollama.service.d/override.conf
sudo systemctl daemon-reload
sudo systemctl restart ollama

# Update Streamlit config
echo "Updating Streamlit config..."
cat > /home/peterofovik/my-chat/.streamlit/config.toml << 'EOF'
[server]
headless = true
port = 8501
address = "127.0.0.1"
enableCORS = false
enableXsrfProtection = false

[client]
showErrorDetails = false
maxUploadSize = 200

[runner]
magicEnabled = true

[logger]
level = "info"

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 8501
EOF

# Restart Streamlit
echo "Restarting Streamlit..."
pkill -f "streamlit run app.py"
sleep 2
cd /home/peterofovik/my-chat
nohup /home/peterofovik/my-chat/venv/bin/python3 -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true > streamlit.log 2>&1 &

echo "Done! Optimizations applied:"
echo "  - Ollama: 4 parallel requests, 2 models loaded, 30min keep-alive"
echo "  - Streamlit: Better timeout handling"
echo "  - App: Improved streaming and error handling"
