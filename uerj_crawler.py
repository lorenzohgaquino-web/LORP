import requests
import urllib3
import re
import json
import concurrent.futures
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def fetch_fen_prof(pid):
    url = f'https://www.eng.uerj.br/prof/{pid}'
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=5)
        if r.status_code != 200:
            return None
        # Use iso-8859-1 decoding for FEN pages
        html_text = r.content.decode('iso-8859-1', errors='replace')
        soup = BeautifulSoup(html_text, 'html.parser')
        text = soup.get_text()

        name_m = re.search(r'PROFESSOR:\s*([^,\n\r|]+)', text)
        if not name_m:
            return None
        name = name_m.group(1).strip()
        if not name or ('não leciona' in name.lower() and len(name.split()) < 2):
            return None

        # Dept
        dept_m = re.search(r'Depto\.:\s*\|?\s*([A-Z0-9_-]+)', text)
        dept = dept_m.group(1).strip() if dept_m else 'FEN'

        # Emails
        emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))

        # Lattes
        lattes = None
        for a in soup.find_all('a', href=True):
            if 'lattes.cnpq.br' in a['href']:
                lattes = a['href']
                break

        return {
            'id': pid,
            'nome': name,
            'depto': dept,
            'bio': text[:2000],
            'emails': emails,
            'lattes': lattes,
            'url': url
        }
    except Exception as e:
        return None

def crawl_fen():
    print("Crawling FEN profiles (IDs 1-500)...")
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(fetch_fen_prof, i): i for i in range(1, 501)}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                records.append(res)
    print(f"Fetched {len(records)} FEN raw profiles.")
    return records

def crawl_ppgmc():
    print("Crawling PPGMC IPRJ...")
    url = 'https://www.ppgmc.uerj.br/docentes/'
    records = []
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=10)
        html_text = r.content.decode('utf-8', errors='replace')
        soup = BeautifulSoup(html_text, 'html.parser')

        items = soup.find_all(['p', 'div', 'li'])
        for item in items:
            text = item.get_text(strip=True)
            if '@' in text and 'LATTES' in text:
                email_m = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
                if email_m:
                    email = email_m.group(1)
                    name_part = text.split('')[0] if '' in text else text.split(email)[0]
                    name_part = name_part.replace('Docentes', '').replace('Home', '').replace('5', '').strip()
                    lattes_url = None
                    for a in item.find_all('a', href=True):
                        if 'lattes' in a['href'].lower():
                            lattes_url = a['href']
                            break
                    records.append({
                        'nome': name_part,
                        'email': email,
                        'lattes': lattes_url or 'https://www.ppgmc.uerj.br/docentes/',
                        'url': url,
                        'source': 'PPGMC IPRJ'
                    })
    except Exception as e:
        print("PPGMC crawl error:", e)
    print(f"Fetched {len(records)} PPGMC records.")
    return records

def crawl_ccomp():
    print("Crawling PPG-COMPMAT IME...")
    url = 'https://ccomp.ime.uerj.br/corpo-docente/'
    records = []
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=10)
        html_text = r.content.decode('utf-8', errors='replace')
        soup = BeautifulSoup(html_text, 'html.parser')
        for tr in soup.find_all(['tr', 'p', 'div']):
            text = tr.get_text(strip=True)
            if '@' in text and ('Lattes' in text or 'Site Pessoal' in text or 'COMP' in text or 'ENG' in text or 'MAT' in text):
                email_m = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
                if email_m:
                    email = email_m.group(1)
                    lattes_url = None
                    for a in tr.find_all('a', href=True):
                        if 'lattes' in a['href'].lower():
                            lattes_url = a['href']
                            break
                    records.append({
                        'raw_text': text,
                        'email': email,
                        'lattes': lattes_url,
                        'url': url,
                        'source': 'PPG-COMPMAT IME'
                    })
    except Exception as e:
        print("CCOMP crawl error:", e)
    print(f"Fetched {len(records)} CCOMP records.")
    return records

if __name__ == '__main__':
    fen_data = crawl_fen()
    ppgmc_data = crawl_ppgmc()
    ccomp_data = crawl_ccomp()

    with open('raw_crawled_uerj.json', 'w', encoding='utf-8') as f:
        json.dump({'fen': fen_data, 'ppgmc': ppgmc_data, 'ccomp': ccomp_data}, f, ensure_ascii=False, indent=2)
    print("Saved raw_crawled_uerj.json successfully.")
