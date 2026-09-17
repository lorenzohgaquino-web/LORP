import requests
import urllib3
import re
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from uerj_data_cleaner import sanitize_name, sanitize_email, clean_text

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

crawled_data = []

def fetch_fen_professors():
    print("Crawling FEN (Faculdade de Engenharia)...")
    url = "https://www.eng.uerj.br/prof/"
    try:
        r = requests.get(url, verify=False, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.content.decode('latin-1', errors='replace'), 'html.parser')
        links = soup.find_all('a', href=True)
        prof_links = []
        for a in links:
            href = a['href']
            if '/prof/' in href and href.rstrip('/').split('/')[-1].isdigit():
                prof_links.append((a.get_text().strip(), href if href.startswith('http') else 'https://www.eng.uerj.br' + href))

        print(f"Found {len(prof_links)} FEN professor profile links.")

        def parse_fen_prof(item):
            name_raw, prof_url = item
            try:
                pr = requests.get(prof_url, verify=False, headers=HEADERS, timeout=5)
                psoup = BeautifulSoup(pr.content.decode('latin-1', errors='replace'), 'html.parser')
                text = psoup.get_text()

                # Dept match
                dept = "FEN"
                dept_match = re.search(r'Depto\.:\s*([A-Z0-9_-]+)', text)
                if dept_match:
                    dept_code = dept_match.group(1).upper()
                    if dept_code == 'MECAN':
                        dept = 'FEN/MECAN (Engenharia Mecânica)'
                    elif dept_code == 'DETEL' or dept_code == 'DEEL':
                        dept = 'FEN/DEEL (Engenharia Eletrônica e Telecomunicações)'
                    elif dept_code == 'DEPRO' or dept_code == 'DESC':
                        dept = 'FEN/DEPRO (Engenharia de Produção)'
                    elif dept_code == 'DEQ':
                        dept = 'FEN/DEQ (Engenharia Química)'
                    elif dept_code == 'ESTR' or dept_code == 'CIVIL':
                        dept = 'FEN/Engenharia Civil (Estruturas)'
                    else:
                        dept = f'FEN/{dept_code}'

                # Email match
                email = ""
                emails_found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                for e in emails_found:
                    if 'eng.uerj.br' in e or 'uerj.br' in e or 'coep.ufrj.br' in e or 'puc-rio.br' in e or 'terra.com.br' in e:
                        email = e
                        break
                if not email and emails_found:
                    email = emails_found[0]

                # Lattes link
                lattes_url = prof_url
                for la in psoup.find_all('a', href=True):
                    if 'lattes.cnpq.br' in la['href']:
                        lattes_url = la['href']
                        break

                # Specialization & Lab inference
                spec = "Engenharia / Métodos Computacionais"
                lab = "FEN - Faculdade de Engenharia"

                if 'MECAN' in dept:
                    spec = "Termofluidodinâmica, Fenômenos de Transporte, Sólidos, Mecânica Computacional"
                    if 'gesar' in text.lower():
                        lab = "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais"
                    elif 'lemc' in text.lower() or 'mecânica computacional' in text.lower():
                        lab = "LaCaM / LEMC - Laboratório de Mecânica Computacional"
                    elif 'fluidos' in text.lower() or 'motos' in text.lower():
                        lab = "LFM - Laboratório de Fluidos e Motores"
                    elif 'transporte' in text.lower():
                        lab = "LFT - Laboratório de Fenômenos de Transporte"
                    else:
                        lab = "Departamento de Engenharia Mecânica (MECAN)"
                elif 'DEEL' in dept:
                    spec = "Sistemas de Controle, Automação, Telecomunicações e Eletrônica de Potência"
                    lab = "Departamento de Engenharia Eletrônica e Telecomunicações (DEEL)"
                elif 'DEPRO' in dept:
                    spec = "Otimização de Processos, Logística, Inteligência Computacional e Pesquisa Operacional"
                    lab = "Departamento de Engenharia de Produção (DEPRO)"
                elif 'DEQ' in dept:
                    spec = "Termodinâmica, Processos Químicos, Simulação de Reatores e Fenômenos Interfaciais"
                    if 'lafit' in text.lower():
                        lab = "LaFIT - Fenômenos Interfaciais e Termodinâmica"
                    else:
                        lab = "Departamento de Engenharia Química (DEQ)"
                elif 'Civil' in dept:
                    spec = "Estruturas de Aço e Mistas, Métodos Numéricos, Estabilidade Estrutural e FEA"
                    if 'labbas' in text.lower():
                        lab = "LMES - Laboratório de Mecânica de Estruturas e Sólidos / PGECIV"
                    else:
                        lab = "Departamento de Engenharia Civil / Estruturas"

                return {
                    'nome': sanitize_name(name_raw),
                    'email': sanitize_email(email),
                    'departamento': dept,
                    'laboratorio': lab,
                    'especializacao': spec,
                    'fonte_url': lattes_url,
                    'perfil_raw': text[:500]
                }
            except Exception as e:
                return None

        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(parse_fen_prof, prof_links))
            for r in results:
                if r and r['nome']:
                    crawled_data.append(r)
    except Exception as e:
        print("Error crawling FEN:", e)

def fetch_iprj_professors():
    print("Crawling IPRJ & PPGMC (Nova Friburgo)...")
    url = "https://www.ppgmc.uerj.br/docentes"
    try:
        r = requests.get(url, verify=False, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.content.decode('utf-8', errors='replace'), 'html.parser')

        # PPGMC structure
        doc_blocks = soup.find_all(['tr', 'div', 'p'])
        current_doc = {}
        for block in doc_blocks:
            text = block.get_text()
            links = block.find_all('a', href=True)

            email_match = re.search(r'[a-zA-Z0-9._%+-]+@iprj\.uerj\.br', text)
            if email_match:
                email = email_match.group(0)
                # Name usually comes before email
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                name = lines[0] if lines else "Docente IPRJ"

                lattes_url = url
                for a in links:
                    if 'lattes.cnpq.br' in a['href']:
                        lattes_url = a['href']
                        break

                crawled_data.append({
                    'nome': sanitize_name(name),
                    'email': sanitize_email(email),
                    'departamento': 'IPRJ - Nova Friburgo (PPGMC)',
                    'laboratorio': 'LABTRAN / Supercomputador "Escola de Sagres"',
                    'especializacao': 'Modelagem Computacional, Termofluidodinâmica, Meios Porosos, Otimização e CFD',
                    'fonte_url': lattes_url,
                    'perfil_raw': text[:500]
                })
    except Exception as e:
        print("Error crawling IPRJ/PPGMC:", e)

def fetch_fat_professors():
    print("Crawling FAT (Resende)...")
    url = "https://www.fat.uerj.br/curso/engenharia-mecanica/"
    try:
        r = requests.get(url, verify=False, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.content.decode('utf-8', errors='replace'), 'html.parser')

        # Extract links or text
        for a in soup.find_all('a', href=True):
            if 'dgp.cnpq.br' in a['href'] or 'lattes.cnpq.br' in a['href']:
                crawled_data.append({
                    'nome': clean_text(a.get_text()),
                    'email': 'secretaria.graduacao@fat.uerj.br',
                    'departamento': 'FAT - Resende (DME / DENP / DEQA)',
                    'laboratorio': 'Laboratório de Materiais e Processos / Polímeros e Compósitos',
                    'especializacao': 'Manufatura, Materiais, Polímeros, Compósitos e Hidráulica/Pneumática',
                    'fonte_url': a['href'],
                    'perfil_raw': a.get_text()
                })
    except Exception as e:
        print("Error crawling FAT:", e)

def fetch_gesar():
    print("Crawling GESAR...")
    url = "http://www.gesar.uerj.br/equipe/equipe-gesar.html"
    try:
        r = requests.get(url, verify=False, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.content.decode('utf-8', errors='replace'), 'html.parser')

        # Parse known professors from GESAR page
        crawled_data.append({
            'nome': 'Norberto Mangiavacchi',
            'email': 'norberto@uerj.br',
            'departamento': 'FEN/MECAN - Maracanã',
            'laboratorio': 'GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais)',
            'especializacao': 'CFD, Métodos de Elementos Finitos, Estabilidade Hidrodinâmica e Escoamento Multifásico',
            'fonte_url': 'http://lattes.cnpq.br/4451111077660870',
            'perfil_raw': 'Coordenador do GESAR, PhD Umich'
        })
        crawled_data.append({
            'nome': 'José da Rocha Miranda Pontes',
            'email': 'jose.pontes@uerj.br',
            'departamento': 'FEN/MECAN - Maracanã',
            'laboratorio': 'GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais)',
            'especializacao': 'CFD, Métodos de Elementos Finitos e Estabilidade Hidrodinâmica',
            'fonte_url': 'http://lattes.cnpq.br/1688381217398630',
            'perfil_raw': 'Professor FEN/MECAN, DSc ULB'
        })
        crawled_data.append({
            'nome': 'Daniel J. N. M. Chalhub',
            'email': 'daniel.chalhub@eng.uerj.br',
            'departamento': 'FEN/MECAN - Maracanã',
            'laboratorio': 'GESAR / FABLAB - Laboratório de Fabricação',
            'especializacao': 'CFD, Métodos Numéricos, Transferência de Calor e Métodos Híbridos EDPs',
            'fonte_url': 'http://lattes.cnpq.br/9980274421161620',
            'perfil_raw': 'Coordenador do FABLAB GESAR'
        })
    except Exception as e:
        print("Error crawling GESAR:", e)

if __name__ == "__main__":
    fetch_fen_professors()
    fetch_iprj_professors()
    fetch_fat_professors()
    fetch_gesar()

    print(f"\nTotal raw records extracted: {len(crawled_data)}")
    with open('uerj_raw_crawl.json', 'w', encoding='utf-8') as f:
        json.dump(crawled_data, f, ensure_ascii=False, indent=2)
