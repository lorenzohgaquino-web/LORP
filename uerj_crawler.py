import urllib.request
import ssl
import re
import json
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        res = urllib.request.urlopen(req, context=ctx, timeout=12)
        content = res.read()
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            return content.decode('iso-8859-1', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

raw_records = []

# 1. FEN - Faculdade de Engenharia (Maracanã)
print("Crawling FEN (Faculdade de Engenharia)...")
fen_main_html = fetch_url('https://www.eng.uerj.br/prof/')
if fen_main_html:
    soup = BeautifulSoup(fen_main_html, 'html.parser')
    prof_ids = set()
    for a in soup.find_all('a', href=True):
        m = re.search(r'/prof/(\d+)', a['href'])
        if m:
            prof_ids.add(m.group(1))

    print(f"Found {len(prof_ids)} FEN prof IDs. Crawling details...")
    for pid in sorted(prof_ids, key=int):
        prof_url = f'https://www.eng.uerj.br/prof/{pid}'
        p_html = fetch_url(prof_url)
        if not p_html:
            continue
        p_soup = BeautifulSoup(p_html, 'html.parser')

        title_tag = p_soup.find('h1') or p_soup.find('title')
        title_text = title_tag.get_text(strip=True) if title_tag else ""

        name_match = re.search(r'PROFESSOR:\s*([^,\(]+)', title_text, re.IGNORECASE)
        if not name_match:
            name_match = re.search(r'Docente - (.*)', title_text)
        name = name_match.group(1).strip() if name_match else ""
        if not name or 'abertura da fen' in name.lower():
            continue

        body_text = p_soup.get_text(separator=' ', strip=True)

        dept_match = re.search(r'Depto\.:\s*([A-Z0-9_-]+)', body_text)
        dept_code = dept_match.group(1).strip() if dept_match else "FEN"

        dept_map = {
            "MECAN": "FEN/MECAN - Departamento de Engenharia Mecânica",
            "DEEL": "FEN/DEEL - Departamento de Engenharia Eletrônica e Telecomunicações",
            "DEPRO": "FEN/DEPRO - Departamento de Engenharia de Produção",
            "DEQ": "FEN/DEQ - Departamento de Engenharia Química",
            "CIVIL": "FEN/DECIV - Departamento de Engenharia Civil",
            "SANITA": "FEN/DESMA - Departamento de Engenharia Sanitária e Meio Ambiente",
            "ESTRUT": "FEN/DECIV - Departamento de Engenharia de Estruturas"
        }
        dept_full = dept_map.get(dept_code, f"FEN/{dept_code}")

        lattes_url = ""
        for a in p_soup.find_all('a', href=True):
            if 'buscatextual.cnpq.br' in a['href'] or 'lattes.cnpq.br' in a['href']:
                lattes_url = a['href']
                break

        lab_match = re.search(r'Chefia ou Coordenação de:\s*(.*?)(?=Informações|Retorna|$)', body_text, re.IGNORECASE)
        lab_info = lab_match.group(1).strip() if lab_match else ""

        raw_records.append({
            "nome": name,
            "departamento": dept_full,
            "campus": "Campus Maracanã / Rio de Janeiro",
            "laboratorio": lab_info,
            "bio_text": body_text[:1000],
            "lattes_url": lattes_url,
            "fonte_url": prof_url,
            "source": "FEN_PROF"
        })

# Save raw crawled data
with open('uerj_raw_crawl.json', 'w', encoding='utf-8') as f:
    json.dump(raw_records, f, ensure_ascii=False, indent=2)

print(f"Raw crawl completed! Extracted {len(raw_records)} records saved to uerj_raw_crawl.json.")
