# OLLAMA.CORE PWA - Deployment Guide

## ✅ What's Deployed

Your modern ChatGPT-style PWA is now ready for deployment to moj.perasper.com!

### 🚀 **Current Status**
- ✅ PWA built and optimized
- ✅ Frontend deployed to `/home/peterofovik/my-chat/frontend/`
- ✅ FastAPI backend running on port 8001
- ✅ Nginx config updated for PWA + API proxy

## 📋 **Deployment Steps**

### 1. Update Nginx Configuration
```bash
# Backup current config
sudo cp /etc/nginx/sites-available/moj.perasper.com /etc/nginx/sites-available/moj.perasper.com.backup

# Copy new PWA config
sudo cp /home/peterofovik/my-chat/nginx-pwa.conf /etc/nginx/sites-available/moj.perasper.com

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 2. Test the Deployment
```bash
# Test website
curl -I https://moj.perasper.com

# Test API
curl https://moj.perasper.com/api/health
```

### 3. Alternative: Use Deployment Script
```bash
cd /home/peterofovik/my-chat
./deploy-pwa.sh
```

## 🎯 **What You'll Get**

### **Modern ChatGPT-Style Interface**
- Beautiful glassmorphism login screen
- PIN authentication (2020)
- Message bubbles with avatars
- Pill-style action buttons
- Responsive design for all devices

### **PWA Features**
- Installable on home screen
- Works offline with service worker
- Fast loading (~230KB gzipped)
- Native app-like experience

### **Mobile Optimized**
- Touch-friendly interface
- Optimized for iPad Mini, TCL tablets, and TCL 40 SE phone
- Full-screen experience
- Swipe gestures

## 🔧 **Architecture**

```
moj.perasper.com (Nginx)
├── / → Static PWA files (React)
├── /api/* → FastAPI backend (port 8001)
└── /sw.js → Service Worker
```

## 🧪 **Testing**

1. **Visit**: https://moj.perasper.com
2. **Login**: Enter PIN `2020`
3. **Chat**: Test the AI conversation
4. **Install**: Try adding to home screen
5. **Mobile**: Test on your devices

## 🚨 **Troubleshooting**

### If website shows old content:
```bash
# Clear browser cache or hard refresh (Ctrl+F5)
# Clear Nginx cache if needed
sudo systemctl reload nginx
```

### If API calls fail:
```bash
# Check FastAPI backend
curl http://127.0.0.1:8001/health

# Restart backend if needed
cd /home/peterofovik/my-chat
source venv/bin/activate
pkill -f uvicorn
python -m uvicorn fastapi_app.main:app --host 127.0.0.1 --port 8001
```

### If Nginx fails:
```bash
# Check config syntax
sudo nginx -t

# View error logs
sudo tail -f /var/log/nginx/error.log
```

## 🎉 **Success!**

Your private AI chat app is now live with a modern, mobile-first PWA interface! Users can:
- Access via any browser
- Install as a native app
- Chat with AI in a ChatGPT-like interface
- Use on mobile/tablet with full-screen experience

The app remains private with PIN protection and anti-indexing headers.