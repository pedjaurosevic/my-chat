#!/bin/bash
# Vracanje na osnovu - uklanjanje PVA elementa

echo "=== Vracanje na osnovu ==="
echo ""

# 1. Test app.py syntax
echo "1. Testiranje app.py..."
/home/peterofovik/my-chat/venv/bin/python3 -m py_compile /home/peterofovik/my-chat/app.py
if [ $? -eq 0 ]; then
    echo "   ✅ Syntax OK"
else
    echo "   ❌ Syntax Error"
    exit 1
fi

# 2. Restart Streamlit
echo "2. Restart Streamlit..."
pkill -f "streamlit run app.py"
sleep 2
cd /home/peterofovik/my-chat
nohup /home/peterofovik/my-chat/venv/bin/python3 -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true > streamlit.log 2>&1 &
sleep 3

# Check if running
if pgrep -f "streamlit run app.py" > /dev/null; then
    echo "   ✅ Streamlit restartovan"
else
    echo "   ❌ Streamlit nije pokrenut"
    exit 1
fi

# 3. Note: Nginx config update requires sudo
echo ""
echo "3. Nginx konfiguracija:"
echo "   Da bi uklonio /pwa/ location block, pokreni:"
echo "   sudo cp /home/peterofovik/my-chat/nginx-clean.conf /etc/nginx/sites-enabled/moj.perasper.com"
echo "   sudo nginx -t"
echo "   sudo systemctl reload nginx"

# 4. Test
echo ""
echo "4. Test sistema..."
echo "   Streamlit:"
curl -s http://127.0.0.1:8501/_stcore/health 2>&1 | grep -q "ok" && echo "   ✅ OK" || echo "   ❌ Error"
echo "   Ollama:"
curl -s http://127.0.0.1:11434/api/version 2>&1 | grep -q "version" && echo "   ✅ OK" || echo "   ❌ Error"

echo ""
echo "=== Rezultat ==="
echo "✅ App.py: Uklonjeni PWA meta tagovi i service worker"
echo "✅ CSS: Responsivan, bez PWA specifičnih elemenata"
echo "⚠️  Nginx: Treba primeniti nginx-clean.conf (zahteva sudo)"
echo ""
echo "Da primeniš nginx promene:"
echo "sudo bash /home/peterofovik/my-chat/reload-nginx.sh"
