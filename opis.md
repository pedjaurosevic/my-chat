# OLLAMA.CORE - Detaljan Opis Aplikacije

## Pregled

OLLAMA.CORE je modularna AI chat aplikacija izgrađena sa Streamlit-om, koja koristi lokalne AI modele putem Ollama sistema. Aplikacija omogućava razgovore sa različitim AI modelima, upravljanje sesijama, analizu dokumenata, web pretragu, i debatne sisteme između više modela.

**Javno dostupna na:** moj.perasper.com

## Arhitektura Aplikacije

### Glavni Fajlovi

1. **app.py** (1334 linija) - Glavna aplikacija
   - Definiše korisničko sučelje i logiku toka
   - Upravlja sesijama i stanjem
   - Implementira autentifikaciju i chat funkcionalnost

2. **config.py** (382 linija) - Konfiguracija
   - Definiše MBTI ličnosti i sistemske promptove (16 osobina)
   - Sadrži CSS stilove za moderni glassmorphism dizajn
   - Konfiguriše izvore modela (Ollama 11434, Kiklop 11435)

3. **agents.py** (286 linija) - AI Agenti
   - Web pretraga (Brave Search API ili Google fallback)
   - Web scraping
   - Analiza dokumenata (PDF, EPUB, TXT, DOCX)
   - Code helper (analiza, debug, objašnjenje)
   - Vesti sa RSS feed-ova (BBC, TechCrunch, Reuters, Ars Technica)
   - API pozivi (GET, POST, PUT, DELETE)

4. **session.py** (82 linija) - Upravljanje Sesijama
   - Čuvanje i učitavanje postavki
   - Čuvanje i učitavanje istorije razgovora
   - Brisanje sesija

5. **export.py** (160 linija) - Export Funkcionalnost
   - Export u TXT format
   - Export u EPUB format (za e-readere)
   - Export u PDF format
   - Export u HTML za štampanje

6. **dialogue.py** (72 linija) - Dijalog Sistem
   - Dijalog između dva AI modela
   - Čuvanje dijaloga u fajl

7. **ui_helpers.py** (47 linija) - UI Helperi
   - Određivanje avatara na osnovu imena modela (30+ različitih emoji-ja)

## Funkcionalnosti

### 1. Autentifikacija i Login Ekran

- **PIN zaštitu:** Korisnik mora da unese 4-cifreni PIN (trenutno: 2020) da bi pristupio aplikaciji
- **Preview mode:** Pre autentifikacije se prikazuje blurovana verzija interfejsa sa demo razgovorom
- **Stilovi:** Taman dizajn sa transparentnim elementima i blur efektima

### 2. Glavni Chat Interfejs

**Header (Top Bar):**
- Model Source selector: Ollama (11434) ili Kiklop (11435)
- Dugmad za brz pristup opcijama (New, Docs, System, History, Agents, Dialog, Export)

**Chat Area:**
- Centralna zona za prikaz razgovora
- Poruke korisnika (avatar: 🧠)
- Poruke AI modela sa specifičnim avatarima
- Poruke su levo poravnate i imaju moderni stil

**Input Area (Fixed Bottom):**
- Floating input box sa glassmorphism efektom
- Placeholder: "Command..."
- Automatsko fokusiranje na unos

### 3. Toolbar (Dugmadi u Footer-u)

Dugmad su poredjena u red sa 8 sekcija:

1. **➕ Clear** - Briše sve poruke, resetuje sesiju
2. **⚙️ System** - Otvara sistemski prompt editor
3. **💾 History** - Otvara panel sačuvanih sesija
4. **🤖 Agents** - Otvara panel AI agenata
5. **💬 Dialog** - Otvara panel za AI debate
6. **📁 Docs** - Otvara panel za upload dokumenata
7. **Model Selector** - Dropdown meni za izbor AI modela
8. **📋 Export** - Otvara panel za export razgovora

### 4. Modalni Paneli

#### ⚙️ SYSTEM INSTRUCTION Panel

- Text area za unos sistemskog prompta (visina: 150px)
- Dugmad: "💾 Save & Close" i "✖️ Cancel"
- Automatsko čuvanje svake promene
- Ovaj prompt se koristi kao prva sistemska poruka za svaki novi razgovor

#### 💾 HISTORY Panel

- **Save Current:** Čuvanje trenutnog razgovora
  - Mogućnost imenovanja sesije (opciono)
  - Automatsko generisanje imena ako se ostavi prazno
- **Lista sačuvanih sesija:**
  - Sortirane kronološki (najnovije prvo)
  - Za svaku sesiju: "📂 Load" i "🗑️ Delete" dugmad
  - Pri učitavanju se restauruju sve poruke

#### 📁 DOCUMENT UPLOAD Panel

- **Upload dokumenta:** Support za TXT, PDF, MD, EPUB
- **Display info:** Prikazuje broj reči i karaktera učitanog dokumenta
- **Clear Document:** Brisanje učitanog dokumenta
- Dokument se automatski koristi kao kontekst u svim budućim porukama

#### 🤖 AI AGENTS Panel

Sadrži 6 tipova agenata:

1. **🔍 Web Search**
   - Unos search query-ja
   - Koristi Brave Search API (ako je dostupan) ili Google fallback
   - Prikazuje 3 rezultata (naslov, link, snippet)

2. **🕷️ Web Scrape**
   - Unos URL-a
   - Skrejp sadržaja stranice
   - Čišćenje HTML tagova
   - Text area za prikaz sadržaja

3. **📄 Documents**
   - Upload dokumenta (PDF, TXT, DOCX, EPUB)
   - Analiza dokumenta
   - Ekspaner za prikaz sadržaja

4. **💻 Code Helper**
   - Text area za unos koda (visina: 200px)
   - Select box za tip zadatka: "analyze", "debug", "explain"
   - Analiza: Broj linija, komentara, funkcija
   - Debug: Pretraga neuparenih zagrada

5. **📰 News**
   - Dohvatanje najnovijih vesti iz 4 izvora:
     - BBC News
     - TechCrunch
     - Reuters
     - Ars Technica
   - Po 3 najnovije vesti sa svakog izvora
   - Prikaz u ekspanerima (naslov, datum, sažetak, link)

6. **🔌 API Call**
   - API URL input
   - Method selector: GET, POST, PUT, DELETE
   - Headers input (JSON format)
   - Data input (za POST/PUT)
   - Prikaz odgovora kao JSON ili tekst

#### 💬 DIALOG PANEL (AI Debate - 16 Personalities)

Dvosmerna debata između dva AI modela:

**Konfiguracija:**
- Model 1: Dropdown meni sa dostupnim modelima + MBTI persona (16 opcija)
- Model 2: Dropdown meni sa dostupnim modelima + MBTI persona (16 opcija)
- Initial prompt: Text area za temu debatu (visina: 100px)

**Akcije:**
- **🚀 Start Debate:** Inicira debatu
  - Postavlja sistemski prompt sa MBTI ličnošću za svaki model
  - Šalje initial prompt moderatoru
  - Prvi model odgovara prema svojoj ličnosti
- **▶️ Next Round:** Nastavlja debatu
  - Sledeći model na redu (alterniraju)
  - Kontekst poslednjih 10 poruka se prenosi
- **💾 Save:** Čuva debatu u fajl
- **Moderator intervention:** Text input za dodavanje komentara u debatu

**Prikaz poruka:**
- Levo-poravnate poruke
- Žuta pozadina za Model 1 (#FDFD96)
- Ljubičasta pozadina za Model 2 (#b388b3)
- Ime modela i ličnosti prikazano iznad svake poruke
- Centralni alignment za moderatora

#### 🎯 MULTI-MODEL DEBATE PANEL (5 Participants)

Debata sa 5 učesnika: 4 AI modela + korisnik

**Konfiguracija učesnika:**
- Participant 1: Model + MBTI persona
- Participant 2: Model + MBTI persona
- Participant 3: Model + MBTI persona
- Participant 4: Model + MBTI persona
- Participant 5: User (korisnik) - učestvuje u debati

**Teme i akcije:**
- Initial prompt za debatu
- **🚀 Start Debate:** Svi 4 modela daju svoj stav na temu
- **▶️ Next Round:** Rotirajući redosled (1→2→3→4→5→1...)
  - Kad dođe na korisnika, informacija: "It's your turn! Type your response below."
  - User input za unos korisnikove poruke
- **💾 Save:** Čuvanje debatu
- **Moderator intervention:** Dodavanje komentara

**Prikaz:**
- 4 različite boje za 4 AI modela
- Bela pozadina za korisnika/moderatora
- Svaki učesnik ima svoj border boju
- Levo-poravnate poruke sa imenom učesnika

#### 📋 EXPORT PANEL

Sadrži 4 opcije za export:

1. **📄 TXT:** Plain tekst format
   - Header: Naziv, datum, broj poruka
   - Format: [ROL - Model]\nSadržaj\n----\n\n

2. **📚 EPUB:** E-reader format
   - Svaka poruka kao poseban chapter
   - CSS stilovi za čitljivost
   - Različite boje pozadine za USER/ASSISTANT

3. **📕 PDF:** PDF dokument
   - Header sa nazivom i brojem stranice
   - Formatiran tekst sa linijama razdvajanja
   - Ime modela u kurzivu

4. **🖨️ PRINT:** HTML za štampanje
   - Clean HTML bez Streamlit UI
   - Serif font (Georgia) za bolju čitljivost
   - CSS stilovi za štampu
   - Može se otvoriti u novom tab-u i Print → Save as PDF

## MBTI Ličnosti (16 opcija)

Svaka ličnost ima detaljan sistemski prompt:

1. **INTJ - Arhitekta:** Analitičan, strateški, rezervisan
2. **INTP - Logičar:** Apstraktan, radoznao, objektivan
3. **ENTJ - Komandant:** Odlučan, direktan, ambiciozan
4. **ENTP - Debatnik:** Provokativan, inovativan, energičan
5. **INFJ - Zastupnik:** Dubok, empatičan, idealistički
6. **INFP - Posrednik:** Poetičan, ljubazan, vođen vrednostima
7. **ENFJ - Protagonista:** Harizmatičan, inspirativan, fokusiran na ljude
8. **ENFP - Aktivista:** Entuzijastičan, kreativan, društven
9. **ISTJ - Logističar:** Praktičan, faktički, odgovoran
10. **ISFJ - Branilac:** Posvećen, topao, savestan
11. **ESTJ - Izvršilac:** Direktan, organizovan, poštuje pravila
12. **ESFJ - Konzul:** Brižan, društven, lojalan
13. **ISTP - Virtuoso:** Logičan, prilagodljiv, fokusiran na akciju
14. **ISFP - Avanturista:** Umetnički, osetljiv, spontan
15. **ESTP - Preduzetnik:** Energičan, pronicljiv, fokusiran na akciju
16. **ESFP - Zabavljač:** Spontan, energičan, zabavan

## Chat Funkcionalnost

### Poruke

**Korisnik:**
- Avatar: 🧠
- Desno-poravnate (u standardnom chat-u, ali ovde su levo zbog specifičnog styling-a)
- Siva pozadina (#3d3d3d)

**AI Model:**
- Avatar: Dinamički na osnovu imena modela (30+ opcija)
- Lijevo-poravnate
- Zelena pozadina (#2a3a2a)

### Streaming

- Real-time streaming odgovora
- Prikazuje kursor "▌" tokom generisanja
- Smooth delay za bolje vizuelno iskustvo (maleni delay svakih 100 karaktera)

### Caching

- Kešira odgovore za 5 minuta (TTL: 300s)
- Ključ za keširanje: JSON hash [model, messages]
- Prikazuje "Response from cache in X.Xs" za keširane odgovore
- Cache se čuva u session_state

### Web Search Enhancement

- Ako model nije siguran (detektuje fraze tipa "nemam dovoljno informacija")
- Automatski pokreće web pretragu za ključne reči iz korisničkog upita
- Dodaje kontekst iz pretrage u poruku
- Ponovo generiše odgovor sa dodatnim informacijama
- Prikazuje "Enhanced response generated in X.Xs"

### Document Context

- Dva nacina konteksta:
  1. **Globalni dokument:** Uploadovan kroz Docs panel → automatski se koristi u svim porukama
  2. **Chat dokument:** Uploadovan kroz chat area → koristi se samo za trenutnu diskusiju

- Format:
  ```
  Context from document:
  [document_content]

  User Question: [user_message]
  ```

### Auto-Save

- Automatski čuva sve postavke nakon svakog odgovora
- Čuva: system_prompt, last_model, file_content, messages, chat_document
- Čuva u fajl: .settings.json

## Model Avatars

Sistem određuje avatare na osnovu imena modela:

### Specifična mapiranja:

- Llama: 🦙
- Mistral: 🌪️
- Mixtral: 🌀
- Gemma: 💎
- Qwen: 🐉
- DeepSeek: 🐳
- Phi: 🔮
- Vicuna: 🐪
- Wizard: 🧙‍♂️
- Code Llama: 👾
- Dolphin: 🐬
- Orca: 🐋
- Zephyr: 🌬️
- Falcon: 🦅
- Starling: 🐦
- Solar: ☀️
- Command R: ⌘
- Hermes: ⚚
- Aya: 🌺
- Yi: 🏔️
- Claude: 🎭
- GPT: 🤖

### Fallback pool (30 emoji-ja):
`["👾", "👽", "👻", "👺", "👹", "💀", "🤡", "🦾", "👁️", "🧘", "🕵️", "🧞", "🧟", "🧛", "🦉", "🐙", "🍄", "🎲", "🧩", "🎹", "🎯", "🎰", "🎱", "💿", "💾", "📡", "🛸", "🦠", "🧬", "🧪"]`

- Deterministički izbor preko hash-a imena modela
- Isto ime uvek daje isti avatar

## CSS Styling

### Boje i Dizajn

**Pozadina:**
- Gradient: `#0f0f1a → #1a1a2e → #16213e` (tamno plava/violetna)
- Full screen bez scroll (overflow: hidden)

**Glassmorphism:**
- Container: `rgba(255, 255, 255, 0.05)` sa blur-om
- Border: `1px solid rgba(255, 255, 255, 0.08)`
- Border radius: 20px
- Shadow: `0 8px 32px rgba(0, 0, 0, 0.3)`

**Dugmadi:**
- Background: `rgba(255, 255, 255, 0.05)`
- Text: `#e2e8f0` (svetlo siva)
- Hover: `rgba(102, 126, 234, 0.15)` sa plavim border-om
- Border radius: 12px
- Transform: `translateY(-2px)` on hover
- Min height: 44px

**Input fields:**
- Background: `rgba(255, 255, 255, 0.05)`
- Border: `1px solid rgba(255, 255, 255, 0.1)`
- Text color: `#e2e8f0`
- Focus border: `rgba(102, 126, 234, 0.5)`
- Focus shadow: `0 0 0 3px rgba(102, 126, 234, 0.1)`

**Chat poruke:**
- Font size: 1.05rem
- Line height: 1.7
- Margin: 24px 0
- Transparent pozadina

**Chat Input Container:**
- Fixed position na dnu ekrana
- Bottom: 24px
- Width: `calc(100% - 48px)`, max-width: 900px
- Center: `left: 50%, transform: translateX(-50%)`
- Blur: 20px
- Border radius: 16px
- Padding: 16px 20px
- Z-index: 9999

**Responsivnost:**

**Tablet (≤1024px):**
- Input width: `calc(100% - 32px)`, max-width: 600px
- Input padding: 14px 18px

**Mobile (≤768px):**
- Input width: `calc(100% - 24px)`, max-width: 100%
- Input bottom: 16px
- Input padding: 12px 16px
- Button padding: 8px 16px, min-height: 40px
- Bottom padding: 100px

**Small mobile (≤480px):**
- Input width: `calc(100% - 16px)`, bottom: 12px
- Input padding: 10px 14px
- Button padding: 6px 12px, min-height: 36px

### Fontovi

- Import: Inter font sa Google Fonts
- Weights: 300, 400, 500, 600, 700, 800
- Font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif

### Hide Streamlit UI

Sledeći elementi su sakriveni:
- Header, footer, sidebar
- Main menu, toolbar, top level actions
- Collapsed control

## Tehnički Detalji

### Ollama Integracija

- **Model Source:** Dinamički putem environment varijable `OLLAMA_HOST`
- **Source options:**
  - "Ollama (11434)" → `localhost:11434`
  - "Kiklop (11435)" → `localhost:11435`
- **Stream chat:** `ollama.chat(model=model, messages=messages, stream=True)`
- **Options:**
  - `num_ctx`: 1024 (kontekstni prozor)
  - `temperature`: 0.7 (kreativnost)
  - `num_threads`: 4 (broj niti)

### Streamlit State Management

**Session state ključevi:**
- `authenticated`: Boolean (da li je korisnik ulogovan)
- `messages`: Lista poruka (chat istorija)
- `system_prompt`: String (sistemski prompt)
- `file_content`: String (sadržaj globalnog dokumenta)
- `show_system`: Boolean (da li je otvoren system panel)
- `show_files`: Boolean (da li je otvoren docs panel)
- `last_model`: String (zadnji korišćeni model)
- `response_cache`: Dict (keširani odgovori)
- `show_agents`: Boolean (da li je otvoren agents panel)
- `show_dialogue`: Boolean (da li je otvoren dialog panel)
- `show_history`: Boolean (da li je otvoren history panel)
- `current_session_file`: String (trenutno učitana sesija)
- `chat_document`: String (sadržaj chat dokumenta)
- `show_multi_debate`: Boolean (da li je otvoren multi-debate panel)
- `show_export`: Boolean (da li je otvoren export panel)

### Struktura Fajlova

```
my-chat/
├── app.py                    # Glavna aplikacija
├── config.py                 # Konfiguracija
├── agents.py                 # AI agenti
├── session.py                # Upravljanje sesijama
├── export.py                 # Export funkcionalnost
├── dialogue.py               # Dijalog sistem
├── ui_helpers.py             # UI helper funkcije
├── .settings.json            # Auto-saved postavke
├── sessions/                 # Folder sa sačuvanim sesijama
│   ├── 20260106_000000__Chat_Title.json
│   └── ...
├── venv/                     # Virtual environment
└── [backup files]            # Razne backup verzije
```

## Ollama Pozivi

### Dobavljanje Modela

```python
@st.cache_data(ttl=300)
def get_models():
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    # Parsiranje output-a: "model_name -> tag"
```

### Chat Poziv

```python
def chat_with_model(model, messages, placeholder=None):
    stream = ollama.chat(
        model=model,
        messages=messages,
        stream=True,
        options={
            'num_ctx': 1024,
            'temperature': 0.7,
            'num_threads': 4
        }
    )

    for chunk in stream:
        content = chunk['message']['content']
        full_response += content
        if placeholder:
            placeholder.markdown(full_response + "▌")
```

### Error Handling

- Timeout: Poruka greške "Timeout: Model took too long to respond"
- General error: Prikazuje error message
- Web search fallback: Ako Brave API ne uspe, koristi Google scraping

## Meta Tagovi i Anti-Indexing

Aplikacija sadrži meta tagove da bi se sprečila indeksacija:

```html
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
<meta name="googlebot" content="noindex, nofollow">
<meta name="bingbot" content="noindex, nofollow">
```

Takođe sadrži meta tagove za Instapaper i readability podršku:

```html
<meta name="description" content="OLLAMA.CORE - AI Chat Conversation">
<meta property="og:title" content="OLLAMA.CORE - Chat Conversation">
<meta property="og:description" content="AI-powered chat conversation saved for offline reading">
```

### Instapaper Readable Content

Aplikacija generuje skriveni `div` sa sadržajem za read-it-later servise:

```html
<div id="instapaper-readable-content">
    <pre style="white-space: pre-wrap; font-family: monospace;">
        [chat_text]
    </pre>
</div>
```

Ovaj div je pozicioniran van ekrana (`left: -9999px`) ali je vidljiv za read-it-later servise.

## JavaScript Funkcionalnost

Aplikacija sadrži JavaScript kod za forsiranje left-align poruka:

```javascript
setInterval(function() {
    const messages = document.querySelectorAll('[data-testid="stChatMessage"]');
    messages.forEach(function(msg) {
        msg.style.textAlign = 'left !important';
        msg.style.marginLeft = '0 !important';
        msg.style.marginRight = 'auto !important';
    });
}, 500);
```

## Export Formati

### TXT Format

```
============================================================
OLLAMA.CORE - Chat Export
Date: 2026-01-06 12:00:00
Total messages: 10
============================================================

[USER]
Hello, how are you?
----------------------------------------

[ASSISTANT - llama3.2:3b]
I'm doing great! How can I help you?
----------------------------------------
```

### EPUB Format

- Svaka poruka kao poseban chapter
- CSS stilovi za razlikovanje user/assistant
- Serif font za bolju čitljivost

### PDF Format

- Header na svakoj stranici: "OLLAMA.CORE Chat"
- Footer: Broj stranice
- Formatiran tekst sa horizontalnim linijama
- Ime modela u kurzivu

### Print Format (HTML)

- Clean HTML bez Streamlit UI elementa
- Serif font (Georgia)
- Boxed poruke sa border-ima
- Optimalno za Print → Save as PDF

## Session Management

### Čuvanje Sesije

```python
def save_session(messages, filename=None):
    if not filename:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        first_msg = next(m['content'] for m in messages if m['role'] == 'user')
        safe_title = "".join(c if c.isalnum() else "_" for c in first_msg[:30])
        filename = f"{timestamp}__{safe_title}.json"

    filepath = SESSIONS_DIR / filename
    with open(filepath, 'w') as f:
        json.dump(messages, f, indent=2)
```

### Učitavanje Sesije

```python
def load_session(filename):
    filepath = SESSIONS_DIR / filename
    with open(filepath, 'r') as f:
        return json.load(f)
```

### Brisanje Sesije

```python
def delete_session(filename):
    filepath = SESSIONS_DIR / filename
    if filepath.exists():
        os.remove(filepath)
```

## Security

### PIN Autentifikacija

- 4-cifreni PIN (trenutno: "2020")
- Čuvan u session_state kao `authenticated`
- Neautentifikovani korisnici vide samo blurovani preview

### Environment Varijable

- `OLLAMA_HOST`: Dinamički se menja na osnovu selected source
- `BRAVE_SEARCH_API_KEY`: Opciono za web search (ako nije definisano, koristi fallback)

## Performance Optimizacije

1. **Caching:**
   - Keširanje model liste (5 min TTL)
   - Keširanje odgovora u session_state

2. **Streaming:**
   - Real-time streaming za bolje UX
   - Mala delay za glatkiji prikaz

3. **Efficient DOM Updates:**
   - Streamlit-ova efikasna rerun mehanizma
   - Minimalan broj re-render-a

4. **Lazy Loading:**
   - Modalni paneli se prikazuju samo kad su otvoreni
   - Chat se ažurira samo kad je potrebno

## Deployment

**Trenutno dostupna na:** moj.perasper.com

**Tehnologije:**
- Python
- Streamlit
- Ollama (lokalni AI models)
- Requests (HTTP requests)
- BeautifulSoup (web scraping)
- EbookLib (EPUB export)
- FPDF (PDF export)
- PyPDF (PDF analiza)

## Mogućnosti Budućeg Razvoja

Na osnovu trenutne arhitekture, moguća dodatna poboljšanja:

1. **Više model sources:** Dodavanje dodatnih API endpoint-a
2. **Collaborative chat:** Više korisnika u istom chat-u
3. **Voice input:** Microphone integration za glasovni unos
4. **Image generation:** Integration sa DALL-E ili Midjourney
5. **Advanced analytics:** Statistika o korišćenju, token count, itd.
6. **Better caching:** Redis ili memcached za distribuirano keširanje
7. **Rate limiting:** Zaštita od zloupotrebe API-ja
8. **User profiles:** Više korisnika sa različitim PIN-ovima
9. **Themes:** Switch između multiple color schemes
10. **Better error recovery:** Retry mechanism za failed API pozive

## Zaključak

OLLAMA.CORE je kompletna AI chat aplikacija sa modernim UI-om, bogatim funkcionalnostima i modularnom arhitekturom. Glavne karakteristike su:

- **Autentifikacija:** PIN-based zaštita
- **Chat Interface:** Moderni glassmorphism dizajn
- **Multiple Models:** Podrška za više Ollama modela
- **MBTI Personalities:** 16 različitih ličnosti za debate
- **Document Analysis:** PDF, EPUB, TXT, DOCX podrška
- **Web Integration:** Search, scraping, vesti, API pozivi
- **Session Management:** Čuvanje i učitavanje razgovora
- **Export Options:** TXT, EPUB, PDF, HTML
- **AI Debates:** Dvosmerna i višesmerna debata
- **Caching:** Efikasno keširanje odgovora
- **Responsive Design:** Rad na desktop, tablet i mobile uređajima

Aplikacija je potpuno funkcionalna i spremna za korišćenje na moj.perasper.com.
