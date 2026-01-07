# Ollama Optimizacija - Status i Preporuke

## Trenutna Analiza (Jan 4, 2026)

### Hardware
- **RAM**: 47GB (43GB free) ✅ Izuzetno dobro
- **CPU**: 12 cores ✅ Dobro za paralelno izvršavanje
- **GPU**: Nije prisutan ❌ Glavni bottleneck
- **Network**: VPS (Contabo) ❌ Dodatni latency za cloud modele

### Trenutna Konfiguracija

#### Ollama Service
```bash
OLLAMA_HOST=0.0.0.0:11434  ✅
OLLAMA_NUM_PARALLEL=4      ⚠️ (treba dodati)
OLLAMA_MAX_LOADED_MODELS=2 ⚠️ (treba dodati)
OLLAMA_KEEP_ALIVE=30m      ⚠️ (treba dodati)
MemoryLimit=40G            ⚠️ (treba dodati)
```

#### System/Kernel
```bash
vm.swappiness=60           ⚠️ Može biti 10
vm.vfs_cache_pressure=100  ⚠️ Može biti 50
vm.dirty_ratio=20          ✅
vm.dirty_background_ratio=10 ✅
```

#### Resource Limits
```bash
ulimit -n: 1048576         ✅
ulimit -u: 192543          ✅
```

### Identifikovani Problemi

1. **Nema model caching** - Modeli se učitavaju svaki put
2. **Vrlo dugački timeout** - 30min nije dovoljno za velike cloud modele
3. **VM settings nisu optimalni** za CPU-only workload
4. **Cloud modeli kroz proxy** - Dodatni latency

### Optimizacije koje treba primeniti

#### 1. Ollama Service Optimizacije
```bash
Environment="OLLAMA_NUM_PARALLEL=4"
Environment="OLLAMA_MAX_LOADED_MODELS=2"
Environment="OLLAMA_LOAD_TIMEOUT=5m"
Environment="OLLAMA_REQUEST_TIMEOUT=30m"
Environment="OLLAMA_KEEP_ALIVE=30m"
MemoryLimit=40G
LimitNOFILE=1048576
```

#### 2. Kernel Optimizacije
```bash
vm.swappiness=10
vm.vfs_cache_pressure=50
vm.dirty_ratio=15
vm.dirty_background_ratio=5
```

### Očekivane Brzine (Nakon optimizacija)

#### Lokalni Modeli (CPU-only)
| Model | Veličina | Tokens/sec | Kraki odgovor (100 tok.) |
|-------|----------|-------------|---------------------------|
| tinyllama | 637MB | 20-25 | 4-5s |
| qwen3:1.7b | 1.4GB | 18-22 | 4-6s |
| deepseek-coder:latest | 776MB | 20-23 | 4-5s |
| llama3.2:latest | 2.0GB | 12-18 | 5-8s |
| phi3:latest | 2.2GB | 12-16 | 6-8s |
| gemma3:4b | 3.3GB | 8-12 | 8-12s |
| qwen3:14b | 9.3GB | 3-6 | 15-30s |

#### Cloud Modeli (Kroz Ollama)
| Model | Latency | Tokens/sec |
|-------|---------|-------------|
| gemini-3-flash-preview:cloud | 500-2000ms | Varira (network dependent) |
| gpt-oss:20b-cloud | 800-3000ms | Varira (network dependent) |

### Preporuke za Najbolje Performanse

#### Za Brze Odgovore
1. **Koristi lokalne mali modeli**:
   - `qwen3:1.7b`
   - `tinyllama`
   - `deepseek-coder:latest`

2. **Preload modeli**:
   ```bash
   ollama run qwen3:1.7b "Hi"
   # Model ostane u memoriji 30 min
   ```

3. **Koristi iste modele** - Ostaju u kešu

#### Za Visok Kvalitet
1. **Koristi srednje velike lokalne modele**:
   - `llama3.2:latest`
   - `phi3:latest`
   - `gemma3:4b`

2. **Izbegavaj cloud modele** za web aplikaciju (latency)

#### Cloud Modeli - Bolja Alternativa
Umesto Ollama cloud, koristi direkt API:
```python
# Umesto: ollama.chat(model="gemini-3-flash-preview:cloud", ...)

# Koristi: Google Cloud AI, OpenAI, Anthropic API direkt
```

### Primena Optimizacija

```bash
# 1. Primeni Ollama optimizacije
bash /home/peterofovik/my-chat/optimize-ollama.sh

# 2. Restart aplikacije
bash /home/peterofovik/my-chat/optimize.sh

# 3. Testiraj performanse
bash /home/peterofovik/my-chat/test-ollama.sh
```

### Monitoring

Proveravaj status:
```bash
# System status
systemctl status ollama

# Učitani modeli
ollama ps

# Memory usage
free -h

# Logs
journalctl -u ollama -f
```

### Zaključak

**Trenutno**: Konfiguracija je osnovna, nije optimalna

**Nakon optimizacija**:
- Lokalni mali modeli: 4-6s za kraki odgovor ✅
- Lokalni srednji modeli: 6-12s za kraki odgovor ✅
- Cloud modeli: I dalje spori (network) ⚠️

**Ultimativno**: Dodaj GPU (T4 ili RTX 4000) za 10-20x bržu inferenciju
