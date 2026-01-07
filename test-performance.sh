#!/bin/bash
echo "=== Performance Test ==="
echo "Testing Ollama API and model performance..."
echo ""

# Test Ollama API
echo "1. Testing Ollama API..."
if curl -s http://127.0.0.1:11434/api/version > /dev/null; then
    echo "   ✓ Ollama API is responding"
else
    echo "   ✗ Ollama API not responding"
    exit 1
fi

echo ""
echo "2. Testing fast model (qwen3:1.7b)..."
start=$(date +%s)
output=$(ollama run qwen3:1.7b "Say hello" 2>&1)
end=$(date +%s)
duration=$((end - start))
echo "   Response: $output"
echo "   Time: ${duration}s"
echo ""

echo "3. Testing small model (tinyllama)..."
start=$(date +%s)
output=$(ollama run tinyllama "Say hello" 2>&1)
end=$(date +%s)
duration=$((end - start))
echo "   Response: $output"
echo "   Time: ${duration}s"
echo ""

echo "4. Testing cloud model (gemini-3-flash-preview:cloud)..."
echo "   Note: Cloud models depend on network latency"
start=$(date +%s)
timeout 30 ollama run gemini-3-flash-preview:cloud "Say hello" 2>&1 || echo "   Timeout or error (expected for cloud models)"
end=$(date +%s)
duration=$((end - start))
echo "   Time: ${duration}s"
echo ""

echo "=== Summary ==="
echo "Fast models (local): < 5s for simple queries"
echo "Medium models (local): 5-15s for simple queries"
echo "Cloud models: Varies, often slower due to network"
echo ""
echo "For best experience, use local models like qwen3:1.7b or tinyllama"
