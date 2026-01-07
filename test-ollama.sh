#!/bin/bash
# Test performansi Ollama

echo "=== Ollama Performance Test ==="
echo ""

echo "1. System status..."
systemctl is-active ollama
echo ""

echo "2. Available memory:"
free -h | grep "Mem:"
echo ""

echo "3. CPU cores:"
nproc
echo ""

echo "4. Ollama environment:"
systemctl show ollama | grep Environment | grep -oP 'OLLAMA_\w+=\S+' | sed 's/=/ = /g'
echo ""

echo "5. Testing FAST model (qwen3:1.7b)..."
echo "Expected: < 10s"
start=$(date +%s)
timeout 30 ollama run qwen3:1.7b "Say hello" 2>&1 | grep -v "^[[:cntrl:]]" | tail -1
end=$(date +%s)
duration=$((end - start))
echo "Time: ${duration}s"
echo ""

echo "6. Checking loaded models..."
ollama ps 2>/dev/null
echo ""

echo "7. Checking recent Ollama logs..."
journalctl -u ollama --since "1 hour ago" | tail -5
echo ""

echo "=== Recommendations ==="
echo "For fastest responses:"
echo "  1. Use: qwen3:1.7b, tinyllama, deepseek-coder:latest"
echo "  2. Keep models loaded (ollama run <model> once)"
echo "  3. Use cloud models via direct API, not through Ollama"
echo ""
echo "Expected speeds (CPU-only, 12 cores):"
echo "  Tiny models (<1GB): 15-25 tokens/sec"
echo "  Small models (1-4GB): 10-20 tokens/sec"
echo "  Medium models (4-10GB): 5-15 tokens/sec"
echo "  Large models (>10GB): 1-8 tokens/sec"
