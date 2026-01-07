#!/bin/bash
# Deployment script for OLLAMA.CORE PWA

echo "🚀 Deploying OLLAMA.CORE PWA to moj.perasper.com"

# Build PWA
echo "📦 Building PWA..."
cd /home/peterofovik/my-chat/frontend-pwa
npm run build

# Deploy frontend
echo "📤 Deploying frontend files..."
rm -rf /home/peterofovik/my-chat/frontend/*
cp -r dist/* /home/peterofovik/my-chat/frontend/

# Update Nginx config
echo "🔧 Updating Nginx configuration..."
sudo cp /etc/nginx/sites-available/moj.perasper.com /etc/nginx/sites-available/moj.perasper.com.backup.$(date +%Y%m%d_%H%M%S)
sudo cp /home/peterofovik/my-chat/nginx-pwa.conf /etc/nginx/sites-available/moj.perasper.com

# Test Nginx config
echo "✅ Testing Nginx configuration..."
sudo nginx -t

# Reload Nginx
echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx

# Start FastAPI backend
echo "⚙️ Starting FastAPI backend..."
cd /home/peterofovik/my-chat
source venv/bin/activate
pkill -f "uvicorn.*fastapi_app.main"
nohup python -m uvicorn fastapi_app.main:app --host 127.0.0.1 --port 8001 > fastapi.log 2>&1 &

# Wait for backend to start
sleep 3

# Test deployment
echo "🧪 Testing deployment..."
curl -s -I https://moj.perasper.com | head -1
curl -s http://127.0.0.1:8001/health

echo ""
echo "🎉 Deployment complete!"
echo "🌐 Visit: https://moj.perasper.com"
echo "🔒 Private access with PIN: 2020"