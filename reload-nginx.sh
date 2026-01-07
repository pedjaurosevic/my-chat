#!/bin/bash
# Reload nginx sa novom konfiguracijom

echo "=== Nginx Reload ==="
echo ""

# Test konfiguracije
echo "1. Testiranje nginx konfiguracije..."
sudo nginx -t
if [ $? -eq 0 ]; then
    echo "   ✅ Konfiguracija je ispravna"
else
    echo "   ❌ Konfiguracija ima greške"
    exit 1
fi

# Kopiranje nove konfiguracije
echo "2. Kopiranje nove konfiguracije..."
sudo cp /home/peterofovik/my-chat/nginx-clean.conf /etc/nginx/sites-enabled/moj.perasper.com
if [ $? -eq 0 ]; then
    echo "   ✅ Konfiguracija kopirana"
else
    echo "   ❌ Greška pri kopiranju"
    exit 1
fi

# Reload nginx
echo "3. Reload nginx..."
sudo systemctl reload nginx
if [ $? -eq 0 ]; then
    echo "   ✅ Nginx reloadovan"
else
    echo "   ❌ Greška pri reload-u"
    exit 1
fi

# Test
echo ""
echo "4. Test nginx..."
systemctl is-active nginx
curl -s -I https://moj.perasper.com | head -1

echo ""
echo "=== Gotovo! ==="
echo "✅ Nginx uklonio /pwa/ location block"
echo "✅ moj.perasper.com sada je standardni web app"
