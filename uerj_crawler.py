import requests
import json
import re
import urllib3
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def fetch(url):
    try:
        res = requests.get(url, headers=HEADERS, verify=False, timeout=12)
        if res.status_code == 200:
            return res.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return ""

def crawl_ppgmc():
    print("Crawling PPGMC / IPRJ...")
    html = fetch("https://www.ppgmc.uerj.br/docentes/")
    soup = BeautifulSoup(html, 'html.parser')

    # Extract Lattes links and associated names/emails
    records = []
    # Find all a elements with lattes
    lattes_links = soup.find_all('a', href=re.compile(r'lattes\.cnpq\.br/\d+'))

    for a in lattes_links:
        lattes_url = a['href']
        # Navigate up to parent container
        parent = a.parent
        while parent and not ('@' in parent.get_text()):
            parent = parent.parent
            if parent.name in ['body', 'html']:
                break

        text = parent.get_text(separator=' ') if parent else ""
        # Match email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        email = email_match.group(0) if email_match else ""

        # Name is usually capitalized before email or lattes
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        # Clean text lines
        name = ""
        for line in lines:
            clean = re.sub(r'Prof\.|Colaborador|Visitante|LATTES|@.*', '', line).strip()
            if len(clean) > 5 and clean.isupper():
                name = clean
                break

        if not name:
            # Fallback name search
            words = [w for w in text.split() if w.isupper() and len(w) > 2 and not '@' in w and not 'LATTES' in w]
            if words:
                name = " ".join(words[:4])

        records.append({
            "nome": name,
            "email": email,
            "lattes": lattes_url,
            "source": "https://www.ppgmc.uerj.br/docentes/"
        })
    print(f"Found {len(records)} PPGMC records")
    return records

if __name__ == "__main__":
    ppgmc_recs = crawl_ppgmc()
    print("Sample:", json.dumps(ppgmc_recs[:3], indent=2, ensure_ascii=False))
