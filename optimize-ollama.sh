#!/bin/bash
# Ollama Optimizacija - Jan 2026

echo "=== Ollama Optimization Script ==="
echo ""

# 1. Update override config
echo "1. Optimizacija Ollama service..."
sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null <<'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_NUM_PARALLEL=4"
Environment="OLLAMA_MAX_LOADED_MODELS=2"
Environment="OLLAMA_LOAD_TIMEOUT=5m"
Environment="OLLAMA_REQUEST_TIMEOUT=30m"
Environment="OLLAMA_KEEP_ALIVE=30m"
Environment="OLLAMA_GPU_OVERHEAD=false"
Environment="OLLAMA_DEBUG=0"
MemoryLimit=40G
MemorySwapMax=2G
TasksMax=infinity
LimitNOFILE=1048576
EOF

# 2. Update VM settings for better performance
echo "2. Optimizacija kernel VM settings..."
sudo tee -a /etc/sysctl.conf > /dev/null <<'EOF'
# Ollama optimizacije
vm.swappiness=10
vm.vfs_cache_pressure=50
vm.dirty_ratio=15
vm.dirty_background_ratio=5
net.core.somaxconn=1024
net.core.netdev_max_backlog=1000
EOF

# 3. Apply VM settings
echo "3. Primena kernel settings..."
sudo sysctl -p > /dev/null 2>&1

# 4. Reload and restart Ollama
echo "4. Restart Ollama service..."
sudo systemctl daemon-reload
sudo systemctl restart ollama

# 5. Wait and check status
sleep 3
echo ""
echo "=== Status ==="
systemctl status ollama --no-pager | head -10

echo ""
echo "=== Učitani modeli ==="
ollama ps 2>/dev/null || echo "Nema učitanih modela"

echo ""
echo "=== Memory info ==="
free -h | grep "Mem:"

echo ""
echo "=== Optimizacije primenjene! ==="
echo "  - 4 paralelna zahteva"
echo "  - 2 modela u memoriji (30min keep-alive)"
echo "  - 40GB limit za Ollama"
echo "  - Bolje VM settings za CPU-only"
echo "  - 30min timeout za zahteve"
echo ""
echo "Testiraj sa: ollama run qwen3:1.7b 'Say hello'"
