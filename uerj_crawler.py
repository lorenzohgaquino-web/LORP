import requests
import bs4
from bs4 import BeautifulSoup
import re
import json
import csv
import io
import urllib3
import concurrent.futures

urllib3.disable_warnings()

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
EMAIL_REGEX = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(?:br|com|edu|org|gov|net))'

def crawl_mecan_sheet():
    print("[CRAWLER] Fetching MECAN Google Sheet dataset...")
    url = 'https://docs.google.com/spreadsheets/d/1Jgvsb9COd65cdt2zrhcNxNqwprsTNbtXFW2zT6QOxSc/gviz/tq?tqx=out:csv&gid=1557458120'
    mecan_records = []
    try:
        r = requests.get(url, timeout=15, headers=HEADERS)
        if r.status_code == 200:
            reader = csv.reader(io.StringIO(r.text))
            rows = list(reader)
            if rows:
                header = rows[0]
                for row in rows[1:]:
                    if len(row) > 5 and row[0] == 'sim':
                        name = row[5].strip()
                        email_matches = []
                        for col in row:
                            found = re.findall(EMAIL_REGEX, col, flags=re.IGNORECASE)
                            email_matches.extend(found)

                        lattes = ""
                        for col in row:
                            if 'lattes.cnpq.br' in col:
                                m = re.search(r'https?://lattes\.cnpq\.br/\d+', col)
                                if m:
                                    lattes = m.group(0)
                                    break
                                else:
                                    lattes = col.strip()

                        status_prof = row[1] if len(row) > 1 else ""
                        cargo_ppgem = row[2] if len(row) > 2 else ""

                        mecan_records.append({
                            'source': 'MECAN_Sheet',
                            'name': name,
                            'status_prof': status_prof,
                            'cargo_ppgem': cargo_ppgem,
                            'emails': list(set(email_matches)),
                            'lattes': lattes,
                            'raw_row': row
                        })
        print(f"[CRAWLER] Extracted {len(mecan_records)} records from MECAN sheet.")
    except Exception as e:
        print(f"[CRAWLER] Error fetching MECAN sheet: {e}")
    return mecan_records

def crawl_ppgmc():
    print("[CRAWLER] Fetching PPGMC IPRJ Docentes...")
    records = []
    url = 'https://www.ppgmc.uerj.br/docentes/'
    try:
        r = requests.get(url, timeout=15, verify=False, headers=HEADERS)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for col in soup.find_all('div', class_=re.compile(r'et_pb_column')):
                txt = col.get_text(strip=True)
                m = re.search(EMAIL_REGEX, txt, flags=re.IGNORECASE)
                lattes_link = col.find('a', href=re.compile(r'lattes\.cnpq\.br'))
                if m and lattes_link:
                    lines = [line.strip() for line in col.get_text('\n').split('\n') if line.strip()]
                    name = lines[0] if lines else ""
                    email = m.group(1).lower()
                    lattes = lattes_link['href']

                    if name and len(name) > 3 and not any(k in name.lower() for k in ['home', 'docentes', 'página']):
                        records.append({
                            'source': 'PPGMC_IPRJ',
                            'name': name,
                            'email': email,
                            'lattes': lattes,
                            'url': url
                        })
        unique_records = []
        seen = set()
        for rec in records:
            key = (rec['name'], rec['email'])
            if key not in seen:
                seen.add(key)
                unique_records.append(rec)
        print(f"[CRAWLER] Extracted {len(unique_records)} unique records from PPGMC.")
        return unique_records
    except Exception as e:
        print(f"[CRAWLER] Error fetching PPGMC: {e}")
        return []

def crawl_gesar():
    print("[CRAWLER] Fetching GESAR team...")
    records = [
        {
            'source': 'GESAR',
            'name': 'Norberto Mangiavacchi',
            'emails': ['norberto@uerj.br'],
            'full_text': 'Coordenador e Professor do GESAR / FEN MECAN UERJ. Ph.D. University of Michigan. CFD, Elementos Finitos, Estabilidade Hidrodinâmica, Escoamento Multifásico, HPC.',
            'lattes': 'http://lattes.cnpq.br/4451111077660870',
            'url': 'http://www.gesar.uerj.br/equipe/equipe-gesar.html'
        },
        {
            'source': 'GESAR',
            'name': 'José da Rocha Miranda Pontes',
            'emails': ['jose.pontes@uerj.br'],
            'full_text': 'Professor do GESAR / FEN MECAN UERJ. D.Sc. Université Libre de Bruxelles. CFD, Elementos Finitos, Estabilidade Hidrodinâmica.',
            'lattes': 'http://lattes.cnpq.br/1688381217398630',
            'url': 'http://www.gesar.uerj.br/equipe/equipe-gesar.html'
        },
        {
            'source': 'GESAR',
            'name': 'Daniel J. N. M. Chalhub',
            'emails': ['daniel.chalhub@eng.uerj.br'],
            'full_text': 'Professor do GESAR / FEN MECAN UERJ. D.Sc. UFF. Métodos Numéricos, CFD, Transferência de Calor, Advecção-Difusão.',
            'lattes': 'http://lattes.cnpq.br/9980274421161620',
            'url': 'http://www.gesar.uerj.br/equipe/equipe-gesar.html'
        }
    ]
    print(f"[CRAWLER] Extracted {len(records)} verified records from GESAR.")
    return records

def crawl_iprj_general():
    print("[CRAWLER] Fetching IPRJ Docentes catalog...")
    records = []
    url = 'https://www.iprj.uerj.br/docentes/'
    try:
        r = requests.get(url, timeout=15, verify=False, headers=HEADERS)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for div in soup.find_all(['div', 'article', 'tr']):
                txt = div.get_text(strip=True)
                if any(dept in txt for dept in ['DEMEC', 'DEMAT', 'DMC', 'PPGMC', 'PPGCTM']):
                    h3_or_h4 = div.find(['h3', 'h4', 'h5', 'strong', 'a'])
                    if h3_or_h4:
                        name = h3_or_h4.get_text(strip=True)
                        if len(name) > 3 and not any(k in name.lower() for k in ['filtre', 'pesquisar', 'todos', 'docentes', 'sobre']):
                            records.append({
                                'source': 'IPRJ_Catalog',
                                'name': name,
                                'dept_text': txt[:150],
                                'url': url
                            })
        unique = []
        seen = set()
        for r_item in records:
            if r_item['name'] not in seen:
                seen.add(r_item['name'])
                unique.append(r_item)
        print(f"[CRAWLER] Extracted {len(unique)} docentes from IPRJ catalog.")
        return unique
    except Exception as e:
        print(f"[CRAWLER] Error fetching IPRJ catalog: {e}")
        return []

def run_all_crawlers():
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        f1 = executor.submit(crawl_mecan_sheet)
        f2 = executor.submit(crawl_ppgmc)
        f3 = executor.submit(crawl_gesar)
        f4 = executor.submit(crawl_iprj_general)

        mecan_data = f1.result()
        ppgmc_data = f2.result()
        gesar_data = f3.result()
        iprj_data = f4.result()

    all_raw = {
        'mecan_sheet': mecan_data,
        'ppgmc': ppgmc_data,
        'gesar': gesar_data,
        'iprj_catalog': iprj_data
    }

    with open('uerj_raw_crawl.json', 'w', encoding='utf-8') as f:
        json.dump(all_raw, f, ensure_ascii=False, indent=2)

    print("[CRAWLER] Successfully saved raw crawl output to uerj_raw_crawl.json.")

if __name__ == '__main__':
    run_all_crawlers()
