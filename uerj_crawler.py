import requests
from bs4 import BeautifulSoup
import urllib3
import re
import json
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def fetch_url(url, timeout=10):
    try:
        r = requests.get(url, verify=False, headers=headers, timeout=timeout)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return None

def parse_iprj_profile(item):
    name, profile_url = item['name'], item['url']
    if any(k in name.lower() for k in ['sobre', 'curso', 'manual', 'estudante', 'fluxograma', 'disciplinas', 'pos-graduacao', 'graduacao']):
        return None

    html = fetch_url(profile_url)
    if not html:
        return None
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text('\n', strip=True)

    if len(name.split()) < 2:
        return None

    email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    email = email_match.group(1) if email_match else "secretaria@iprj.uerj.br"

    lattes_a = soup.find('a', href=re.compile(r'lattes\.cnpq\.br'))
    lattes_url = lattes_a['href'] if lattes_a else profile_url

    dept = "IPRJ - Nova Friburgo"
    if "DEMEC" in text or "Departamento de Engenharia Mecânica" in text:
        dept = "IPRJ/DEMEC - Nova Friburgo"
    elif "DEMAT" in text or "Departamento de Ciência dos Materiais" in text:
        dept = "IPRJ/DEMAT - Nova Friburgo"
    elif "DMC" in text or "Departamento de Modelagem Computacional" in text:
        dept = "IPRJ/DMC - Nova Friburgo"

    lab = "Laboratório de Modelagem Computacional / IPRJ"
    if "LABTRAN" in text:
        lab = "LABTRAN - Laboratório de Modelagem Multiescala e Transporte de Partículas"
    elif "Escola de Sagres" in text or "Supercomputador" in text:
        lab = "Supercomputador Escola de Sagres / High Performance Computing Lab"

    return {
        'name': name,
        'email': email,
        'unit': dept,
        'lab': lab,
        'lattes_url': lattes_url,
        'profile_url': profile_url,
        'source': 'https://www.iprj.uerj.br/docentes/'
    }

def crawl_iprj():
    print("Crawling IPRJ docentes...")
    html = fetch_url("https://www.iprj.uerj.br/docentes/")
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')

    items = []
    ignore_list = ['home', 'institucional', 'sobre', 'histórico', 'departamentos', 'secretarias', 'conselho',
                   'biblioteca', 'ensino', 'graduação', 'pós-graduação', 'pesquisa', 'extensão', 'corpo docente',
                   'notícias', 'atendimento', 'voltar', 'manual', 'fluxogramas', 'disciplinas', 'todos', 'demec', 'demat', 'dmc', 'ppgmc', 'ppgctm', 'categoria']

    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.text.strip()
        if 'iprj.uerj.br/' in href and len(text) > 4:
            if not any(ig == text.lower() or ig in href.lower() for ig in ignore_list):
                if not href.endswith('/docentes/') and not href.endswith('/category/'):
                    items.append({'name': text, 'url': href})

    unique_items = {it['url']: it for it in items}.values()
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for res in executor.map(parse_iprj_profile, unique_items):
            if res:
                results.append(res)
    return results

def parse_fen_profile(prof_id):
    url = f"http://www.eng.uerj.br/prof/{prof_id}"
    try:
        r = requests.get(url, headers=headers, timeout=4)
        if r.status_code == 200 and len(r.content) > 2000:
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.get_text('\n', strip=True)

            # Find name
            name = None
            for line in text.split('\n'):
                if line.startswith("PROFESSOR:"):
                    name = line.replace("PROFESSOR:", "").strip()
                    name = re.sub(r'\(.*?\)', '', name).strip()
                    break

            if not name or name == "0" or len(name.split()) < 2:
                return None

            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
            email = email_match.group(1) if email_match else "secfen@eng.uerj.br"

            # Dept
            dept_code = "FEN - Faculdade de Engenharia (Maracanã)"
            for line in text.split('\n'):
                if "Depto.:" in line:
                    idx = text.split('\n').index(line)
                    if idx + 1 < len(text.split('\n')):
                        dept_code = text.split('\n')[idx+1].strip()
                    break

            dept_map = {
                'MECAN': 'FEN/MECAN - Depto. de Engenharia Mecânica (Maracanã)',
                'ELE': 'FEN/DEEL - Depto. de Engenharia Elétrica (Maracanã)',
                'DETEL': 'FEN/DEEL - Depto. de Eletrônica e Telecomunicações (Maracanã)',
                'DEIN': 'FEN/DEPRO - Depto. de Engenharia de Produção e Industrial (Maracanã)',
                'ESTR': 'FEN/Civil - Depto. de Estruturas e Fundações (Maracanã)',
                'DCCT': 'FEN/Civil - Depto. de Construção Civil e Transportes (Maracanã)',
                'DESMA': 'FEN/DESMA - Depto. de Engenharia Sanitária e Meio Ambiente (Maracanã)',
                'CARTO': 'FEN/CARTO - Depto. de Engenharia Cartográfica (Maracanã)'
            }
            dept = dept_map.get(dept_code, f"FEN/{dept_code} - Maracanã")

            lattes_a = soup.find('a', href=re.compile(r'lattes\.cnpq\.br'))
            lattes_url = lattes_a['href'] if lattes_a else url

            return {
                'name': name,
                'email': email,
                'unit': dept,
                'lab': 'Laboratórios FEN Maracanã',
                'lattes_url': lattes_url,
                'profile_url': url,
                'source': url
            }
    except Exception:
        pass
    return None

def crawl_fen():
    print("Crawling FEN Maracanã docentes...")
    results = []
    with ThreadPoolExecutor(max_workers=15) as executor:
        for res in executor.map(parse_fen_profile, range(1, 400)):
            if res:
                results.append(res)
    return results

if __name__ == '__main__':
    iprj_results = crawl_iprj()
    print(f"Extracted {len(iprj_results)} valid records from IPRJ.")
    fen_results = crawl_fen()
    print(f"Extracted {len(fen_results)} valid records from FEN.")

    all_raw = iprj_results + fen_results
    with open('uerj_raw_all.json', 'w', encoding='utf-8') as f:
        json.dump(all_raw, f, ensure_ascii=False, indent=2)
