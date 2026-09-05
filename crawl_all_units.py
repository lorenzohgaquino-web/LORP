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

all_records = []

# Load existing FEN records if present
try:
    with open('raw_uerj_records.json', 'r', encoding='utf-8') as f:
        all_records = json.load(f)
    print(f"Loaded {len(all_records)} FEN records from raw_uerj_records.json")
except Exception:
    pass

# 2. Crawl IPRJ Docentes
print("\n--- Crawling IPRJ (Nova Friburgo) ---")
try:
    r_iprj = requests.get('https://www.iprj.uerj.br/docentes/', headers=HEADERS, verify=False, timeout=15)
    soup_iprj = BeautifulSoup(r_iprj.text, 'html.parser')

    iprj_profile_urls = []
    for a in soup_iprj.find_all('a', href=True):
        href = a['href']
        if 'iprj.uerj.br/' in href and not any(k in href for k in ['/category/', '/tag/', 'page_id', 'wp-content', 'institucional', 'historico', 'departamentos', 'secretarias', 'mecanica', 'computacao', 'extensao', 'docentes', 'noticias', 'pesquisa']):
            iprj_profile_urls.append(href)

    iprj_profile_urls = sorted(list(set(iprj_profile_urls)))
    print(f"Found {len(iprj_profile_urls)} candidate teacher profile links in IPRJ.")

    def fetch_iprj_prof(url):
        try:
            r = requests.get(url, headers=HEADERS, verify=False, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.get_text()

            # Check if this is a prof profile
            if 'Currículo Lattes' not in text and '@iprj.uerj.br' not in text and 'DEMEC' not in text and 'DMC' not in text:
                return None

            # Extract name
            h1 = soup.find('h1')
            name = h1.text.strip() if h1 else ""
            if not name:
                title = soup.title.text if soup.title else ""
                name = title.split('|')[0].strip()

            if not name or len(name) < 3 or 'IPRJ' in name or 'Corpo Docente' in name:
                return None

            # Extract email
            email = ""
            m_mail = re.search(r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r.text)
            if m_mail:
                email = m_mail.group(1)
            else:
                m_mail2 = re.search(r'([a-zA-Z0-9._%+-]+@iprj\.uerj\.br)', text)
                if m_mail2:
                    email = m_mail2.group(1)

            # Extract dept & ppg
            depto = "IPRJ - Nova Friburgo"
            if "DEMEC" in text or "Mecânica" in text:
                depto = "IPRJ/DEMEC - Nova Friburgo"
            elif "DMC" in text or "Modelagem Computacional" in text:
                depto = "IPRJ/DMC - Nova Friburgo"

            ppg = ""
            if "Pós-graduação em Modelagem Computacional" in text or "PPGMC" in text:
                ppg = "PPGMC (Programa de Pós-Graduação em Modelagem Computacional)"
            elif "Pós-graduação em Ciência e Tecnologia dos Materiais" in text or "PPGCTM" in text:
                ppg = "PPGCTM"

            # Extract Lattes
            lattes = ""
            for a in soup.find_all('a', href=True):
                if 'lattes.cnpq.br' in a['href']:
                    lattes = a['href']
                    break

            # Extract bio
            bio = ""
            m_bio = re.search(r'Biografia\s*(.*)', text, re.DOTALL)
            if m_bio:
                bio = m_bio.group(1)[:350].strip()
            else:
                bio = "Modelagem Computacional / Engenharia Mecânica"

            dept_full = f"{depto} ({ppg})" if ppg else depto

            return {
                "name": name,
                "email": email,
                "department": dept_full,
                "laboratory": "",
                "area": bio,
                "source_url": lattes if lattes else url,
                "raw_depto": "IPRJ"
            }
        except Exception as e:
            return None

    iprj_count = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_iprj_prof, u) for u in iprj_profile_urls]
        for f in as_completed(futures):
            res = f.result()
            if res and res["name"]:
                all_records.append(res)
                iprj_count += 1

    print(f"Captured {iprj_count} records from IPRJ.")
except Exception as e:
    print(f"Error crawling IPRJ: {e}")

# Save updated raw records
with open('raw_uerj_records.json', 'w', encoding='utf-8') as f:
    json.dump(all_records, f, ensure_ascii=False, indent=2)

print(f"\nTotal raw records collected so far: {len(all_records)}")
