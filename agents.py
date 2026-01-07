"""
AI Agenti - Web pretraga, scraping, analiza dokumenata, vesti, API
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse


def web_search(query, num_results=3):
    """Osnovna funkcija za web pretragu koristeći Brave Search API ako je dostupan"""
    try:
        import os
        # Proveri da li postoji Brave API ključ u okruženju
        brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")

        if brave_api_key:
            # Koristi Brave Search API
            headers = {
                "X-Subscription-Token": brave_api_key,
                "Accept": "application/json"
            }

            params = {
                "q": query,
                "count": num_results,
                "freshness": "pd"  # za pretragu samo od juče i danas
            }

            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                for item in data.get("web", {}).get("results", [])[:num_results]:
                    results.append({
                        "title": item.get("title", "Bez naslova"),
                        "link": item.get("url", ""),
                        "snippet": item.get("description", "Bez opisa")
                    })

                return results
            else:
                # Ako Brave API ne uspe, koristi fallback metodu
                return web_search_fallback(query, num_results)
        else:
            # Ako nema Brave API ključa, koristi fallback metodu
            return web_search_fallback(query, num_results)

    except Exception as e:
        # Ako sve ostalo ne uspe, koristi fallback metodu
        return web_search_fallback(query, num_results)


def web_search_fallback(query, num_results=3):
    """Fallback metoda za web pretragu koristeći web scraping"""
    try:
        # Koristi Google Custom Search API ako je dostupan, ili koristi drugi pristup
        # Ovde implementiramo osnovnu verziju sa requests i BeautifulSoup
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        results = []
        for g in soup.find_all('div', class_='g')[:num_results]:
            anchor = g.find('a')
            if anchor:
                link = anchor.get('href')
                title_elem = g.find('h3')
                title = title_elem.text if title_elem else "Bez naslova"
                snippet_elem = g.find('span', class_='st')
                snippet = snippet_elem.text if snippet_elem else "Bez opisa"

                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })

        return results
    except Exception as e:
        return [{"error": str(e)}]


def web_scrape(url):
    """Osnovna funkcija za web skrejp"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ukloni skripte i stilove
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()
        # Očisti tekst
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text
    except Exception as e:
        return f"Greška prilikom skrejpa: {str(e)}"


def analyze_document(uploaded_file):
    """Osnovna funkcija za analizu dokumenata"""
    try:
        content = ""
        if uploaded_file.type == "application/pdf":
            from pypdf import PdfReader
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                content += page.extract_text() + "\n"
        elif uploaded_file.name.endswith(".epub"):
            import ebooklib
            from ebooklib import epub
            # Sačuvaj privremeno jer ebooklib radi sa putanjama
            with open("temp.epub", "wb") as f:
                f.write(uploaded_file.getbuffer())

            book = epub.read_epub("temp.epub")
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    # Očisti HTML tagove
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    content += soup.get_text() + "\n"

            os.remove("temp.epub")
        elif uploaded_file.type == "text/plain":
            content = uploaded_file.read().decode("utf-8")
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            import docx
            # Potrebno je instalirati python-docx: pip install python-docx
            # Za sada vraćamo poruku o podršci za Word fajlove
            return "Podrška za Word dokumente zahteva dodatnu biblioteku: python-docx"
        else:
            content = uploaded_file.read().decode("utf-8")

        # Vraćamo samo početak dokumenta za prikaz (limit na reči)
        words = content.split()
        if len(words) > 60000:
            content = " ".join(words[:60000]) + "\n\n[...DOKUMENT JE SKRAĆEN (limit 60.000 reči)...]"

        return content
    except Exception as e:
        return f"Greška prilikom analize dokumenta: {str(e)}"


def code_helper(code, task="analyze"):
    """Osnovna funkcija za pomoć sa kodom"""
    try:
        if task == "analyze":
            # Analizira kod i daje preporuke
            lines = code.split('\n')
            info = {
                "total_lines": len(lines),
                "non_empty_lines": len([l for l in lines if l.strip()]),
                "comments": len([l for l in lines if l.strip().startswith('#') or l.strip().startswith('//') or '/*' in l or '*/' in l or l.strip().startswith('*')]),
                "functions": len([l for l in lines if 'def ' in l or 'function ' in l or 'func ' in l])
            }
            return f"Analiza koda:\n- Ukupno linija: {info['total_lines']}\n- Linija sa sadržajem: {info['non_empty_lines']}\n- Komentara: {info['comments']}\n- Funkcija: {info['functions']}"
        elif task == "debug":
            # Osnovna analiza za greške u kodu
            lines = code.split('\n')
            errors = []
            for i, line in enumerate(lines, 1):
                if line.count('(') != line.count(')'):
                    errors.append(f"Red {i}: Neuparena zagrada")
                if line.count('[') != line.count(']'):
                    errors.append(f"Red {i}: Neuparena uglasta zagrada")
                if line.count('{') != line.count('}'):
                    errors.append(f"Red {i}: Neuparena vitičasta zagrada")
            if errors:
                return "Pronađene greške:\n" + "\n".join(errors)
            else:
                return "Nema očiglednih sintaksnih grešaka"
        elif task == "explain":
            # Ovde bi se koristio model za objašnjenje koda
            return "Kod objašnjenje: Ova funkcija bi koristila AI model da objasni funkcionalnost koda."
        else:
            return "Nepoznat tip zadatka. Dostupni: analyze, debug, explain"
    except Exception as e:
        return f"Greška prilikom obrade koda: {str(e)}"


def get_news_from_rss(rss_url, num_articles=5):
    """Osnovna funkcija za dohvatanje vesti iz RSS feeda"""
    try:
        import feedparser
        feed = feedparser.parse(rss_url)

        articles = []
        for entry in feed.entries[:num_articles]:
            article = {
                "title": entry.title,
                "summary": entry.summary if hasattr(entry, 'summary') else "Nema sažetka",
                "link": entry.link,
                "published": entry.published if hasattr(entry, 'published') else "Datum nije dostupan"
            }
            articles.append(article)

        return articles
    except ImportError:
        return [{"error": "Biblioteka 'feedparser' nije instalirana. Pokrenite: pip install feedparser"}]
    except Exception as e:
        return [{"error": f"Greška prilikom dohvatanja vesti: {str(e)}"}]


def get_top_news():
    """Funkcija za dohvatanje najnovijih vesti sa popularnih izvora"""
    # Definišemo nekoliko popularnih RSS feedova
    rss_feeds = {
        "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
        "TechCrunch": "https://techcrunch.com/feed/",
        "Reuters": "http://feeds.reuters.com/reuters/topNews",
        "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index"
    }

    all_articles = {}
    for source, url in rss_feeds.items():
        try:
            import feedparser
            feed = feedparser.parse(url)
            articles = []
            for entry in feed.entries[:3]:  # Uzimamo po 3 najnovije vesti sa svakog izvora
                article = {
                    "title": entry.title,
                    "summary": entry.summary if hasattr(entry, 'summary') else "Nema sažetka",
                    "link": entry.link,
                    "published": entry.published if hasattr(entry, 'published') else "Datum nije dostupan"
                }
                articles.append(article)
            all_articles[source] = articles
        except:
            all_articles[source] = [{"error": f"Greška prilikom dohvatanja vesti iz {source}"}]

    return all_articles


def api_caller(url, method="GET", headers=None, data=None, params=None):
    """Osnovna funkcija za API pozive"""
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, params=params)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, params=params)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, params=params)
        else:
            return f"Nepodržan metod: {method}"

        # Proveravamo status kod
        if response.status_code in [200, 201, 202]:
            try:
                # Pokušavamo da vratimo JSON ako je odgovor u tom formatu
                return response.json()
            except:
                # Ako nije JSON, vratimo tekstualni odgovor
                return response.text
        else:
            return f"Greška u API pozivu: {response.status_code} - {response.text}"

    except requests.exceptions.ConnectionError:
        return "Greška: Nije moguće povezivanje sa API-jem"
    except requests.exceptions.Timeout:
        return "Greška: Vreme za odgovor API-ja je isteklo"
    except requests.exceptions.RequestException as e:
        return f"Greška u API pozivu: {str(e)}"
    except Exception as e:
        return f"Greška: {str(e)}"
