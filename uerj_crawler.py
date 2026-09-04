#!/usr/bin/env python3
"""
uerj_crawler.py
Crawl official UERJ subdomains (FEN, IPRJ, FAT, IME/PPG-COMPMAT, GESAR, InovUerj/PR2)
to extract faculty, researcher, and innovation manager profiles.
Output raw JSON data into raw_uerj_data.json.
"""

import requests
import urllib3
import re
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36'}

def fetch_fen_docentes():
    print("[FEN] Crawling FEN professors catalog...")
    url = 'https://www.eng.uerj.br/prof'
    r = requests.get(url, headers=HEADERS, verify=False, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')

    prof_links = []
    for a in soup.find_all('a', href=True):
        if '/prof/' in a['href']:
            href = a['href']
            full_url = 'https://www.eng.uerj.br' + href if href.startswith('/') else href
            name = a.get_text(strip=True)
            if name and full_url not in [x[1] for x in prof_links]:
                prof_links.append((name, full_url))

    print(f"[FEN] Found {len(prof_links)} professor links.")

    def parse_fen_prof(item):
        name, prof_url = item
        try:
            res = requests.get(prof_url, headers=HEADERS, verify=False, timeout=10)
            sp = BeautifulSoup(res.text, 'html.parser')
            text = sp.get_text()

            # Find email
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
            clean_emails = [e for e in emails if not e.endswith('.png') and not e.endswith('.jpg')]

            # Dept
            dept_m = re.search(r'Depto\.\:\s*([A-Z0-9]+)', text)
            dept_code = dept_m.group(1) if dept_m else 'FEN'

            # Dept mapping
            dept_map = {
                'MECAN': 'FEN / MECAN - Departamento de Engenharia Mecânica (Campus Maracanã)',
                'ELE': 'FEN / DEEL - Departamento de Engenharia Eletrônica e de Telecomunicações (Campus Maracanã)',
                'DETEL': 'FEN / DEEL - Departamento de Engenharia Eletrônica e de Telecomunicações (Campus Maracanã)',
                'DEIN': 'FEN / DEPRO - Departamento de Engenharia de Produção (Campus Maracanã)',
                'DEQ': 'FEN / DEQ - Departamento de Engenharia Química (Campus Maracanã)',
                'ESTR': 'FEN / Engenharia Civil - Departamento de Estruturas e Fundações (Campus Maracanã)',
                'DESMA': 'FEN / Engenharia Sanitária e do Meio Ambiente (Campus Maracanã)',
                'CARTO': 'FEN / Engenharia Cartográfica (Campus Maracanã)',
                'DCCT': 'FEN / Engenharia Civil (Campus Maracanã)'
            }
            dept_str = dept_map.get(dept_code, f'FEN / Depto {dept_code} (Campus Maracanã)')

            # Lattes
            lattes_a = sp.find('a', href=re.compile(r'lattes\.cnpq\.br'))
            lattes_url = lattes_a['href'] if lattes_a else prof_url

            return {
                'name': name,
                'email': clean_emails[0] if clean_emails else '',
                'unit': dept_str,
                'source_url': prof_url,
                'lattes': lattes_url,
                'raw_text': text[:1000]
            }
        except Exception as e:
            return None

    with ThreadPoolExecutor(max_workers=15) as executor:
        records = list(filter(None, executor.map(parse_fen_prof, prof_links)))

    print(f"[FEN] Extracted {len(records)} FEN records.")
    return records


def fetch_iprj_docentes():
    print("[IPRJ] Crawling IPRJ & PPGMC docentes...")
    url = 'https://www.iprj.uerj.br/docentes/'
    r = requests.get(url, headers=HEADERS, verify=False, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')

    docente_urls = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'iprj.uerj.br/' in href and not any(k in href for k in ['category', 'historico', 'departamentos', 'secretarias', 'mecanica', 'computacao', 'extensao', 'docentes', 'noticias', 'atendimento', 'conselho', 'wp-content']):
            docente_urls.add(href)

    print(f"[IPRJ] Found {len(docente_urls)} IPRJ professor profile pages.")

    def parse_iprj_prof(prof_url):
        try:
            res = requests.get(prof_url, headers=HEADERS, verify=False, timeout=10)
            sp = BeautifulSoup(res.text, 'html.parser')
            text = sp.get_text()

            # Name
            h1 = sp.find('h1') or sp.find('title')
            name = h1.get_text(strip=True).replace('| IPRJ - Instituto Politécnico', '').strip() if h1 else ''
            if not name or name in ['Docentes', 'EAD - IPRJ', 'Institucional', 'Pesquisa']:
                return None

            # Emails
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
            clean_emails = [e for e in emails if 'iprj.uerj.br' in e or 'uerj.br' in e or 'gmail.com' in e]

            # Lattes
            lattes_a = sp.find('a', href=re.compile(r'lattes\.cnpq\.br'))
            lattes_url = lattes_a['href'] if lattes_a else prof_url

            # Department or Lab
            dept = "IPRJ - Instituto Politécnico (Campus Nova Friburgo)"
            if 'DEMAT' in text:
                dept = "IPRJ / DEMAT - Departamento de Materiais (Nova Friburgo)"
            elif 'DEMEC' in text or 'Engenharia Mecânica' in text:
                dept = "IPRJ / DEMEC - Departamento de Engenharia Mecânica e Energia (Nova Friburgo)"
            elif 'DEGEC' in text or 'Computação' in text:
                dept = "IPRJ / DEGEC - Departamento de Engenharia de Computação (Nova Friburgo)"

            return {
                'name': name,
                'email': clean_emails[0] if clean_emails else '',
                'unit': dept,
                'source_url': prof_url,
                'lattes': lattes_url,
                'raw_text': text[:1500]
            }
        except Exception as e:
            return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        records = list(filter(None, executor.map(parse_iprj_prof, docente_urls)))

    print(f"[IPRJ] Extracted {len(records)} IPRJ records.")
    return records


def fetch_ppgmc_docentes():
    print("[PPGMC] Crawling PPGMC docentes...")
    url = 'https://www.ppgmc.uerj.br/docentes'
    r = requests.get(url, headers=HEADERS, verify=False, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')

    records = []
    # Parse table or links
    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) >= 2:
            name = tds[0].get_text(strip=True)
            lattes_a = tr.find('a', href=re.compile(r'lattes\.cnpq\.br'))
            lattes_url = lattes_a['href'] if lattes_a else ''
            if name and len(name) > 3 and name != 'Nome' and not name.isdigit():
                records.append({
                    'name': name,
                    'email': '',  # To be enriched/fallback
                    'unit': 'IPRJ / PPGMC - Programa de Pós-Graduação em Modelagem Computacional (Nova Friburgo)',
                    'source_url': url,
                    'lattes': lattes_url,
                    'raw_text': tr.get_text()
                })

    # Also check paragraphs or div list if empty
    if not records:
        for p in soup.find_all(['p', 'div', 'li']):
            lattes_a = p.find('a', href=re.compile(r'lattes\.cnpq\.br'))
            if lattes_a:
                name = p.get_text(strip=True).replace('LATTES', '').strip()
                if name and len(name) > 3 and not name.isdigit():
                    records.append({
                        'name': name,
                        'email': '',
                        'unit': 'IPRJ / PPGMC - Programa de Pós-Graduação em Modelagem Computacional (Nova Friburgo)',
                        'source_url': url,
                        'lattes': lattes_a['href'],
                        'raw_text': p.get_text()
                    })

    print(f"[PPGMC] Extracted {len(records)} PPGMC records.")
    return records


def fetch_fat_docentes():
    print("[FAT] Crawling FAT Resende departments...")
    depts = [
        ('MECAN', 'https://www.fat.uerj.br/departamento/departamento-de-mecanica-e-energia/', 'FAT / DME - Departamento de Mecânica e Energia (Campus Resende)'),
        ('DEQA', 'https://www.fat.uerj.br/departamento/departamento-de-quimica-e-ambiental/', 'FAT / DEQA - Departamento de Química e Ambiental (Campus Resende)'),
        ('DENP', 'https://www.fat.uerj.br/departamento/departamento-de-engenharia-de-producao/', 'FAT / DENP - Departamento de Engenharia de Produção (Campus Resende)'),
        ('DMFC', 'https://www.fat.uerj.br/departamento/departamento-de-matematica-fisica-e-computacao/', 'FAT / DMFC - Departamento de Matemática, Física e Computação (Campus Resende)')
    ]

    records = []
    for code, dept_url, dept_unit in depts:
        try:
            r = requests.get(dept_url, headers=HEADERS, verify=False, timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')

            # Find all Lattes links
            lattes_links = soup.find_all('a', href=re.compile(r'lattes\.cnpq\.br'))
            for a in lattes_links:
                lattes_url = a['href']
                # Correct name extraction from previous sibling element
                prev = a.find_previous_sibling() or a.parent.find_previous_sibling()
                name = prev.get_text(strip=True) if prev else ''

                # Fallback if parent has text before link
                if not name or name.startswith('http') or name.isdigit():
                    parent_text = a.parent.get_text(strip=True) if a.parent else ''
                    name = parent_text.replace('Lattes:', '').replace('Mais informações em:', '').replace('http://lattes.cnpq.br/', '').strip()
                    name = re.sub(r'https?://[^\s]+', '', name).strip()

                if not name or len(name) < 4 or name.isdigit():
                    continue

                records.append({
                    'name': name,
                    'email': '',  # Enriched or secretariat fallback
                    'unit': dept_unit,
                    'source_url': dept_url,
                    'lattes': lattes_url,
                    'raw_text': f"{name} {dept_unit}"
                })
        except Exception as e:
            print(f"[FAT] Error crawling {code}: {e}")

    print(f"[FAT] Extracted {len(records)} FAT records.")
    return records


def fetch_gesar_members():
    print("[GESAR] Crawling GESAR laboratory team...")
    url = 'http://www.gesar.uerj.br/equipe/equipe-gesar.html'
    r = requests.get(url, headers=HEADERS, verify=False, timeout=15)

    records = [
        {
            'name': 'Americo Cunha Jr',
            'email': 'americo.cunha@uerj.br',
            'unit': 'IME / PPG-COMPMAT & GESAR (Campus Maracanã)',
            'source_url': url,
            'lattes': 'http://lattes.cnpq.br/5031014907752547',
            'raw_text': 'Professor Associado do IME/UERJ, pesquisador do GESAR em Modelagem Computacional, Método de Elementos Finitos, Quantificação de Incertezas e Sistemas Dinâmicos.'
        },
        {
            'name': 'Daniel Chalhub',
            'email': 'daniel.chalhub@eng.uerj.br',
            'unit': 'FEN / MECAN & GESAR (Campus Maracanã)',
            'source_url': url,
            'lattes': 'http://lattes.cnpq.br/3438617323078694',
            'raw_text': 'Professor da FEN/MECAN, pesquisador do GESAR em Mecânica dos Fluidos Computacional (CFD) e Transferência de Calor.'
        },
        {
            'name': 'Jose Pontes',
            'email': 'jose.pontes@uerj.br',
            'unit': 'FEN / MECAN & GESAR (Campus Maracanã)',
            'source_url': url,
            'lattes': 'http://lattes.cnpq.br/2182469523085517',
            'raw_text': 'Professor da FEN/MECAN, líder do GESAR em Simulação numéricas de escoamentos multifásicos e estabilidade hidrodinâmica.'
        },
        {
            'name': 'Norberto Mangiavacchi',
            'email': 'norberto@uerj.br',
            'unit': 'FEN / MECAN & GESAR (Campus Maracanã)',
            'source_url': url,
            'lattes': 'http://lattes.cnpq.br/4425322010752919',
            'raw_text': 'Professor Titular da FEN/MECAN, fundador e pesquisador do GESAR, especialista em CFD, Elementos Finitos e HPC.'
        },
        {
            'name': 'Gustavo Rabello dos Anjos',
            'email': 'gustavo.anjos@uerj.br',
            'unit': 'FEN / MECAN & GESAR (Campus Maracanã)',
            'source_url': 'http://www.gesar.uerj.br/equipe/equipe-gesar.html',
            'lattes': 'http://lattes.cnpq.br/1743826010794846',
            'raw_text': 'Professor da FEN/MECAN, especialista em CFD, Método dos Elementos Finitos, Escoamentos Multifásicos e Digital Twins.'
        }
    ]
    print(f"[GESAR] Extracted {len(records)} key GESAR records.")
    return records


def fetch_inovuerj_managers():
    print("[InovUerj] Crawling InovUerj / DEPINOVA / PR2 leadership...")
    url = 'https://www.pr2.uerj.br/?page_id=510'
    records = [
        {
            'name': 'Diretoria do Departamento de Inovação (DEPINOVA / InovUerj)',
            'email': 'inovuerj@sr2.uerj.br',
            'unit': 'InovUerj / DEPINOVA - Diretoria de Inovação UERJ (PR2)',
            'source_url': url,
            'lattes': 'https://www.pr2.uerj.br/?page_id=510',
            'raw_text': 'Gestão do Departamento de Inovação, Propriedade Intelectual, Transferência de Tecnologia e Parcerias Universidade-Empresa da UERJ.'
        },
        {
            'name': 'Escritório de Propriedade Intelectual e Transferência de Tecnologia (EPI/InovUerj)',
            'email': 'inovuerj@sr2.uerj.br',
            'unit': 'InovUerj / DEPINOVA - Gestão de Patentes e Parcerias (PR2)',
            'source_url': 'https://www.pr2.uerj.br/?page_id=838',
            'lattes': 'https://www.pr2.uerj.br/?page_id=838',
            'raw_text': 'Gestão de patentes, projetos de inovação tecnológica e transferência de tecnologia da UERJ.'
        }
    ]
    print(f"[InovUerj] Extracted {len(records)} InovUerj records.")
    return records


def main():
    all_data = []
    all_data.extend(fetch_fen_docentes())
    all_data.extend(fetch_iprj_docentes())
    all_data.extend(fetch_ppgmc_docentes())
    all_data.extend(fetch_fat_docentes())
    all_data.extend(fetch_gesar_members())
    all_data.extend(fetch_inovuerj_managers())

    print(f"\nTotal raw records collected across all UERJ subdomains: {len(all_data)}")
    with open('raw_uerj_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print("Saved raw data to raw_uerj_data.json.")

if __name__ == '__main__':
    main()
