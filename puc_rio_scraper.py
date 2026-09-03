import requests
from bs4 import BeautifulSoup
import re
import json

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def clean_name(name):
    name = re.sub(r'^(Prof|Profª|Professora?|Dr|Dra|Ph\.D\.|D\.Sc\.|M\.Sc\.|Eng|Engª)\.?\s+', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def scrape_dem():
    url = "https://mec.puc-rio.br/pessoal/"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Each row or card
        for row in soup.find_all(['tr', 'div']):
            text = row.get_text(' ', strip=True)
            emails = re.findall(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            if emails:
                email = emails[0]
                if any(x in email for x in ['pgmec@', 'fsoares@', 'simonesc@', 'mcm@', 'leni@']):
                    continue
                # Extract name before degree/email
                # Typical pattern: "Ivan Fabio Mota de Menezes Ph.D., ..."
                m = re.search(r'([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zA-Záéíóúâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zA-Záéíóúâêôãõç]+)+)', text)
                if m:
                    name = clean_name(m.group(1))
                    if len(name.split()) >= 2 and len(name) <= 50 and name not in ['Pessoal DEM', 'Departamento de', 'O Ciclo']:
                        results.append({
                            'nome': name,
                            'email': email,
                            'unidade': 'CTC / DEM (Departamento de Engenharia Mecânica)',
                            'lab_grupo': 'POSMEC / DEM',
                            'url': url,
                            'raw_text': text[:200]
                        })
    except Exception as e:
        print("DEM error:", e)
    return results

def scrape_deqm():
    url = "https://www.deqm.puc-rio.br/corpo-docente/"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for div in soup.find_all(['div', 'tr', 'article']):
            text = div.get_text(' ', strip=True)
            emails = re.findall(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            if emails:
                email = emails[0]
                m = re.search(r'([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zA-Záéíóúâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zA-Záéíóúâêôãõç]+)+)', text)
                if m:
                    name = clean_name(m.group(1))
                    if len(name.split()) >= 2 and len(name) <= 50:
                        results.append({
                            'nome': name,
                            'email': email,
                            'unidade': 'CTC / DEQM (Departamento de Engenharia Química e de Materiais)',
                            'lab_grupo': 'PPGEQ / PPGEM / DEQM',
                            'url': url,
                            'raw_text': text[:200]
                        })
    except Exception as e:
        print("DEQM error:", e)
    return results

def scrape_dee():
    url = "https://www.ele.puc-rio.br/pessoal/corpodocente/"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for div in soup.find_all(['tr', 'div']):
            text = div.get_text(' ', strip=True)
            emails = re.findall(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            if emails:
                email = emails[0]
                m = re.search(r'([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zA-Záéíóúâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zA-Záéíóúâêôãõç]+)+)', text)
                if m:
                    name = clean_name(m.group(1))
                    if len(name.split()) >= 2 and len(name) <= 50:
                        results.append({
                            'nome': name,
                            'email': email,
                            'unidade': 'CTC / DEE (Departamento de Engenharia Elétrica)',
                            'lab_grupo': 'PPGEE / DEE',
                            'url': url,
                            'raw_text': text[:200]
                        })
    except Exception as e:
        print("DEE error:", e)
    return results

def scrape_dei():
    url = "https://www.ind.puc-rio.br/tipo-de-equipe/docentes/quadro-principal/"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for div in soup.find_all(['tr', 'div', 'article']):
            text = div.get_text(' ', strip=True)
            emails = re.findall(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            if emails:
                email = emails[0]
                m = re.search(r'([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zA-Záéíóúâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zA-Záéíóúâêôãõç]+)+)', text)
                if m:
                    name = clean_name(m.group(1))
                    if len(name.split()) >= 2 and len(name) <= 50:
                        results.append({
                            'nome': name,
                            'email': email,
                            'unidade': 'CTC / DEI (Departamento de Engenharia Industrial)',
                            'lab_grupo': 'PPGEP / DEI',
                            'url': url,
                            'raw_text': text[:200]
                        })
    except Exception as e:
        print("DEI error:", e)
    return results

def scrape_dec():
    url = "https://www.civ.puc-rio.br/corpo-docente-quadro-principal/"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for div in soup.find_all(['tr', 'div', 'article']):
            text = div.get_text(' ', strip=True)
            emails = re.findall(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            if emails:
                email = emails[0]
                m = re.search(r'([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zA-Záéíóúâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zA-Záéíóúâêôãõç]+)+)', text)
                if m:
                    name = clean_name(m.group(1))
                    if len(name.split()) >= 2 and len(name) <= 50:
                        results.append({
                            'nome': name,
                            'email': email,
                            'unidade': 'CTC / DEC (Departamento de Engenharia Civil e Ambiental)',
                            'lab_grupo': 'PPGEC / DEC',
                            'url': url,
                            'raw_text': text[:200]
                        })
    except Exception as e:
        print("DEC error:", e)
    return results

if __name__ == '__main__':
    dem = scrape_dem()
    deqm = scrape_deqm()
    dee = scrape_dee()
    dei = scrape_dei()
    dec = scrape_dec()
    print(f"Scraped: DEM={len(dem)}, DEQM={len(deqm)}, DEE={len(dee)}, DEI={len(dei)}, DEC={len(dec)}")
