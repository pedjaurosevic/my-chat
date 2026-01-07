# Command AI - Ollama Web Interface

## Opis projekta

Command AI je privatni web wrapper za Ollama AI modele. Omogućava pristup lokalnim i cloud AI modelima kroz elegantni web interfejs sa autentifikacijom.

**URL:** https://moj.perasper.com
**PIN:** 2020

---

## Tehnologije

- **Backend:** Python + Streamlit
- **AI:** Ollama (lokalni i cloud modeli)
- **Server:** Nginx reverse proxy + Let's Encrypt SSL
- **PWA:** Installable Progressive Web App

---

## Struktura projekta

```
/home/peterofovik/my-chat/
├── app.py              # Glavna aplikacija
├── start.sh            # Start skripta
├── streamlit.log       # Log fajl
├── .settings.json      # Perzistentne postavke
├── static/             # PWA assets
│   ├── manifest.json   # PWA manifest
│   ├── sw.js           # Service Worker
│   ├── icon-192.png    # App ikona 192x192
│   └── icon-512.png    # App ikona 512x512
├── venv/               # Python virtual environment
└── CLAUDE.md           # Ovaj fajl
```

---

## Funkcionalnosti

### Osnovne
- Chat sa Ollama modelima (lokalni + cloud)
- Streaming odgovora u realnom vremenu
- Upload dokumenata (PDF, TXT, MD) kao kontekst
- System prompt podrška
- Selekcija modela

### Bezbednost
- PIN autentifikacija
- Anti-indexing (robots.txt, X-Robots-Tag, meta tagovi)
- HTTPS sa Let's Encrypt certifikatom

### PWA
- Instalacija kao desktop/mobile aplikacija
- Offline-ready service worker
- Custom ikone i theme color

### Perzistencija
- System prompt se čuva između sesija
- Poslednji korišćeni model se pamti
- Učitani dokumenti ostaju sačuvani

### UX
- Upozorenje pre napuštanja stranice (beforeunload)
- Narandžasti focus state na input poljima
- Animirani pulsirajuči okvir chat inputa
- Dark tema sa narandžastim akcentima

---

## Konfiguracija

### Nginx
Fajl: `/etc/nginx/sites-available/moj.perasper.com`

- Reverse proxy na port 8501
- SSL termination
- Static file serving za PWA (/static/)
- Anti-indexing headers

### SSL Certifikat
- Izdavač: Let's Encrypt
- Važi do: 4. april 2026.
- Auto-renewal: certbot timer

---

## Pokretanje

### Manuelno
```bash
cd /home/peterofovik/my-chat
source venv/bin/activate
python3 -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
```

### Background
```bash
cd /home/peterofovik/my-chat
source venv/bin/activate
nohup python3 -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true > streamlit.log 2>&1 &
```

### Restart
```bash
lsof -t -i:8501 | xargs kill 2>/dev/null
# zatim pokreni ponovo
```

---

## Istorija promena

### 4. januar 2026. (Claude Opus 4.5)

1. **SSL Fix**
   - Problem: Nginx vraćao pogrešan SSL certifikat (ai.crossroad.chat)
   - Rešenje: Kreiran novi certifikat za moj.perasper.com

2. **Anti-indexing**
   - Dodat robots.txt sa Disallow: /
   - Dodat X-Robots-Tag header
   - Dodati meta tagovi u HTML

3. **PWA podrška**
   - Kreiran manifest.json
   - Kreiran service worker (sw.js)
   - Generisane app ikone (192x192, 512x512)
   - Nginx konfigurisan za /static/ folder

4. **Focus boja**
   - Promenjena sa crvene na narandžastu (#e8a45c)
   - Dodati CSS stilovi za sve input elemente

5. **Perzistencija**
   - Implementirano čuvanje u .settings.json
   - Čuva: system_prompt, last_model, file_content

6. **Beforeunload upozorenje**
   - JavaScript upozorenje pre napuštanja stranice
   - Aktivira se kada korisnik unese tekst

---

## Poznati problemi

- Streamlit ponekad ne primenjuje custom CSS na neke elemente (browser cache)
- Service Worker možda neće raditi na prvom učitavanju (potreban refresh)

---

## Budući razvoj

Predlozi za unapređenje:
- Systemd service za auto-start
- Jači PIN ili pravi login sistem
- SQLite za istoriju razgovora
- Export razgovora u PDF/Markdown
- Višekorisnički režim
