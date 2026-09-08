import requests
from bs4 import BeautifulSoup
import re

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def clean_name(name):
    name = re.sub(r'^(Prof|Profª|Professora?|Dr|Dra|Ph\.D\.|D\.Sc\.|M\.Sc\.|Eng|Engª)\.?\s+', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def scrape_dem_full():
    url = "https://mec.puc-rio.br/pessoal/"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Parse blocks
        for card in soup.find_all(['tr', 'div']):
            text = card.get_text(' ', strip=True)
            emails = re.findall(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            if emails:
                for email in emails:
                    if any(x in email for x in ['pgmec@', 'fsoares@', 'simonesc@', 'mcm@', 'leni@', 'igordepaula@']):
                        continue
                    # Extract name
                    m = re.search(r'([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zA-Záéíóúâêôãõç]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-zA-Záéíóúâêôãõç]+)+)', text)
                    if m:
                        name = clean_name(m.group(1))
                        if len(name.split()) >= 2 and len(name) <= 50 and name not in ['Pessoal DEM', 'Departamento de', 'O Ciclo', 'Quadro Permanente', 'Pesquisadores Fernando']:
                            results.append({
                                'nome': name,
                                'email': email,
                                'unidade': 'CTC / DEM (Departamento de Engenharia Mecânica)',
                                'lab_grupo': 'POSMEC / DEM',
                                'url': url,
                                'raw_text': text[:200]
                            })
    except Exception as e:
        print("Error DEM:", e)
    return results

def scrape_deqm_full():
    url = "https://www.deqm.puc-rio.br/corpo-docente/"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for card in soup.find_all(['tr', 'div', 'article']):
            text = card.get_text(' ', strip=True)
            emails = re.findall(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            if emails:
                for email in emails:
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
        print("Error DEQM:", e)
    return results

def scrape_dee_full():
    url = "https://www.ele.puc-rio.br/pessoal/corpodocente/"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for card in soup.find_all(['tr', 'div']):
            text = card.get_text(' ', strip=True)
            emails = re.findall(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            if emails:
                for email in emails:
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
        print("Error DEE:", e)
    return results

def scrape_dei_full():
    url = "https://www.ind.puc-rio.br/tipo-de-equipe/docentes/quadro-principal/"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for card in soup.find_all(['tr', 'div', 'article']):
            text = card.get_text(' ', strip=True)
            emails = re.findall(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            if emails:
                for email in emails:
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
        print("Error DEI:", e)
    return results

def scrape_dec_full():
    url = "https://www.civ.puc-rio.br/corpo-docente-quadro-principal/"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for card in soup.find_all(['tr', 'div', 'article']):
            text = card.get_text(' ', strip=True)
            emails = re.findall(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            if emails:
                for email in emails:
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
        print("Error DEC:", e)
    return results

if __name__ == '__main__':
    dem = scrape_dem_full()
    deqm = scrape_deqm_full()
    dee = scrape_dee_full()
    dei = scrape_dei_full()
    dec = scrape_dec_full()
    print(f"Scraped raw items: DEM={len(dem)}, DEQM={len(deqm)}, DEE={len(dee)}, DEI={len(dei)}, DEC={len(dec)}")
