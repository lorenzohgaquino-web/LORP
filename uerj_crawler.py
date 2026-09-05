import requests
from bs4 import BeautifulSoup
import json
import re
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

records = []

# 1. Crawl FEN (Maracanã)
print("--- Crawling FEN (Maracanã) with iso-8859-1 decoding ---")
try:
    r_fen = requests.get('https://www.eng.uerj.br/prof/', headers=HEADERS, verify=False, timeout=15)
    content_fen = r_fen.content.decode('iso-8859-1', errors='replace')
    soup_fen = BeautifulSoup(content_fen, 'html.parser')
    prof_links = []
    for a in soup_fen.find_all('a', href=True):
        href = a['href']
        if '/prof/' in href:
            if not href.startswith('http'):
                href = 'https://www.eng.uerj.br' + href if href.startswith('/') else 'https://www.eng.uerj.br/' + href
            prof_links.append(href)
    prof_links = sorted(list(set(prof_links)))
    print(f"Found {len(prof_links)} professor profile links in FEN.")

    def fetch_fen_prof(url):
        try:
            r = requests.get(url, headers=HEADERS, verify=False, timeout=12)
            content = r.content.decode('iso-8859-1', errors='replace')
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()

            # Extract name
            name = ""
            m_name = re.search(r'PROFESSOR:\s*([^,\n]+)', text)
            if m_name:
                name = m_name.group(1).strip()
            elif soup.title:
                t = soup.title.text
                if 'Docente -' in t:
                    name = t.split('Docente -')[-1].strip()

            if not name:
                return None

            # Extract department
            depto = ""
            m_dep = re.search(r'Depto\.:\s*([A-Z0-9_\-]+)', text)
            if m_dep:
                depto = m_dep.group(1).strip()

            # Extract email
            email = ""
            m_mail = re.search(r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', content)
            if m_mail:
                email = m_mail.group(1)
            else:
                m_mail2 = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
                if m_mail2:
                    email = m_mail2.group(1)

            # Extract lattes
            lattes = ""
            for a in soup.find_all('a', href=True):
                if 'lattes.cnpq.br' in a['href']:
                    lattes = a['href']
                    break

            # Extract bio / research area
            area = ""
            if 'Possui Graduação' in text or 'possui graduação' in text or 'Possui' in text:
                m_bio = re.search(r'Possui\s+(.*)', text, re.IGNORECASE)
                if m_bio:
                    bio = m_bio.group(1).split('Disciplinas')[0]
                    area = bio[:350].strip()
            if not area:
                area = "Engenharia / Exatas"

            depto_full = f"FEN/{depto} - Maracanã" if depto else "FEN - Maracanã"

            return {
                "name": name,
                "email": email,
                "department": depto_full,
                "laboratory": "",
                "area": area,
                "source_url": lattes if lattes else url,
                "raw_depto": depto
            }
        except Exception as e:
            return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_fen_prof, u) for u in prof_links]
        for f in as_completed(futures):
            res = f.result()
            if res and res["name"]:
                records.append(res)

    print(f"Captured {len(records)} records from FEN.")
except Exception as e:
    print(f"Error crawling FEN: {e}")

# Save raw records
with open('raw_uerj_records.json', 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"Total raw records collected: {len(records)}")
