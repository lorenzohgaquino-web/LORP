import requests
from bs4 import BeautifulSoup
import urllib3
import re
import json
import ftfy
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def clean_text(t):
    if not t:
        return ""
    return re.sub(r'\s+', ' ', t).strip()

def extract_email(text):
    if not text:
        return None
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if match:
        return match.group(0).lower()
    return None

def extract_lattes(soup_or_text):
    if isinstance(soup_or_text, str):
        match = re.search(r'http://lattes\.cnpq\.br/(\d{10,16})', soup_or_text)
        return f"http://lattes.cnpq.br/{match.group(1)}" if match else None
    for a in soup_or_text.find_all('a', href=True):
        if 'lattes.cnpq.br' in a['href']:
            match = re.search(r'\d{10,16}', a['href'])
            if match:
                return f"http://lattes.cnpq.br/{match.group(0)}"
    return None

def clean_person_name(raw_name):
    if not raw_name:
        return ""
    # Strip honorifics
    name = re.sub(r'^(Prof\.?|Profa\.?|Dr\.?|Dra\.?|Ph\.?D\.?|Eng\.?)\s+', '', raw_name, flags=re.IGNORECASE)
    # Cut off Depto or biography sentences
    name = re.split(r'\b(Depto\.?|Departamento|Possui|Gradua|Doutor|Doutora|Mestre|Profess|Engenhar|Obteve)\b', name, flags=re.IGNORECASE)[0]
    name = name.split('(')[0].split(' - ')[0].split(',')[0].strip()
    return name

def fetch_fen_profile(link):
    try:
        pr = requests.get(link, headers=headers, verify=False, timeout=8)
        pr.encoding = 'iso-8859-1'
        ptext = ftfy.fix_text(pr.text)
        psoup = BeautifulSoup(ptext, 'html.parser')
        text_content = psoup.get_text().replace('\xa0', ' ')

        name_match = re.search(r'PROFESSOR:\s*([^,(\n\r]+)', text_content)
        if name_match:
            raw_n = clean_text(name_match.group(1))
        else:
            h1 = psoup.find('h1')
            raw_n = clean_text(h1.get_text()) if h1 else ""

        name = clean_person_name(raw_n)

        if not name or len(name) < 3 or any(x in name.lower() for x in ['fen/uerj', 'docente', 'retorna', 'conselho', 'página', 'aluno', 'manual', 'fluxograma', 'graduação']):
            return None

        dept_code = "FEN - Campus Maracanã"
        dept_match = re.search(r'Depto\.:\s*([A-Z0-9]+)', text_content)
        if dept_match:
            dcode = dept_match.group(1)
            dept_map = {
                "MECAN": "FEN/MECAN (Engenharia Mecânica) - Campus Maracanã",
                "DEEL": "FEN/DEEL (Engenharia Eletrônica e Telecomunicações) - Campus Maracanã",
                "DEPRO": "FEN/DEPRO (Engenharia de Produção) - Campus Maracanã",
                "DEQ": "FEN/DEQ (Engenharia Química) - Campus Maracanã",
                "ESTRU": "FEN/ESTRU (Engenharia Civil/Estruturas) - Campus Maracanã",
                "SAN": "FEN/DESMA (Engenharia Sanitária e Meio Ambiente) - Campus Maracanã"
            }
            dept_code = dept_map.get(dcode, f"FEN/{dcode} - Campus Maracanã")

        email = extract_email(text_content)
        lattes = extract_lattes(psoup) or extract_lattes(text_content)

        lab = "Laboratórios FEN"
        if "GESAR" in text_content:
            lab = "GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais)"
        elif "LAMMAC" in text_content:
            lab = "LAMMAC (Laboratório de Modelagem Matemática e Computacional)"
        elif "LaCaM" in text_content:
            lab = "LaCaM (Laboratório de Computação Aplicada à Engenharia Mecânica)"
        elif "LFT" in text_content or "Fenômenos de Transporte" in text_content:
            lab = "LFT (Laboratório de Fenômenos de Transporte)"
        elif "LFM" in text_content or "Fluidos e Motores" in text_content:
            lab = "LFM (Laboratório de Fluidos e Motores)"
        elif "LMES" in text_content or "Estruturas" in text_content:
            lab = "LMES (Laboratório de Mecânica de Estruturas e Sólidos)"

        spec = "Engenharia e Modelagem Numérica"
        if "MECAN" in dept_code or "fluidos" in text_content.lower() or "cfd" in text_content.lower():
            spec = "Termofluidodinâmica, CFD, Mecânica dos Sólidos & Vibrações"
        elif "DEEL" in dept_code or "controle" in text_content.lower() or "automação" in text_content.lower():
            spec = "Sistemas de Controle, Automação & Eletrônica de Potência"
        elif "DEPRO" in dept_code or "otimização" in text_content.lower():
            spec = "Otimização de Processos, Logística & Pesquisa Operacional"
        elif "DEQ" in dept_code or "química" in text_content.lower() or "termodinâmica" in text_content.lower():
            spec = "Termodinâmica, Processos Químicos & Simulação de Reatores"
        elif "ESTRU" in dept_code or "estruturas" in text_content.lower():
            spec = "Mecânica das Estruturas, Elementos Finitos & Métodos Numéricos"

        if not email:
            if "MECAN" in dept_code:
                email = "mecanica@eng.uerj.br"
            elif "DEEL" in dept_code:
                email = "eletronica@eng.uerj.br"
            elif "DEPRO" in dept_code:
                email = "producao@eng.uerj.br"
            elif "DEQ" in dept_code:
                email = "quimica@eng.uerj.br"
            else:
                email = "secretaria@eng.uerj.br"

        return {
            "name": name,
            "email": email,
            "department": dept_code,
            "laboratory": lab,
            "specialization": spec,
            "source_url": lattes or link,
            "validation_date": "2026-03-09"
        }
    except Exception:
        return None

def crawl_fen():
    print("Crawling FEN (Faculty of Engineering - Maracanã)...")
    fen_records = []
    url = 'https://www.eng.uerj.br/prof'
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        prof_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/prof/' in href:
                full_url = href if href.startswith('http') else f"https://www.eng.uerj.br/prof/{href.split('/prof/')[-1]}"
                if full_url not in prof_links:
                    prof_links.append(full_url)

        print(f"Fetching {len(prof_links)} FEN profile pages concurrently...")
        with ThreadPoolExecutor(max_workers=25) as executor:
            futures = [executor.submit(fetch_fen_profile, link) for link in prof_links]
            for future in as_completed(futures):
                res = future.result()
                if res:
                    fen_records.append(res)
    except Exception as e:
        print(f"Error crawling FEN: {e}")
    return fen_records

def crawl_iprj():
    print("Crawling IPRJ (Nova Friburgo)...")
    iprj_records = []
    url = 'https://www.iprj.uerj.br/docentes/'
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        prof_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('https://www.iprj.uerj.br/') and href not in prof_links and href != url and not any(x in href for x in ['/category/', '/tag/', '/page/', 'artigo', 'noticias', 'ensino', 'graduacao', 'pos', 'pesquisa', 'laboratorios', 'extensao', 'atendimento']):
                slug = href.strip('/').split('/')[-1]
                if '-' in slug and len(slug) > 5:
                    prof_links.append(href)

        for link in prof_links:
            try:
                pr = requests.get(link, headers=headers, verify=False, timeout=8)
                ptext = ftfy.fix_text(pr.text)
                psoup = BeautifulSoup(ptext, 'html.parser')
                text_content = psoup.get_text()

                h1 = psoup.find('h1')
                raw_n = clean_text(h1.get_text()) if h1 else link.strip('/').split('/')[-1].replace('-', ' ').title()
                name = clean_person_name(raw_n)

                if not name or len(name) < 3 or any(x in name.lower() for x in ['docente', 'conheça', 'notícias', 'conselho departamental', 'manual', 'fluxograma']):
                    continue

                email = extract_email(text_content)
                if not email:
                    for ma in psoup.find_all('a', href=True):
                        if 'mailto:' in ma['href']:
                            email = ma['href'].replace('mailto:', '').strip().split('?')[0]
                            break

                lattes = extract_lattes(psoup) or extract_lattes(text_content)

                dept = "IPRJ - Nova Friburgo"
                if "DEMEC" in text_content or "Engenharia Mecânica" in text_content:
                    dept = "IPRJ/DEMEC - Nova Friburgo"
                elif "DMC" in text_content or "Modelagem Computacional" in text_content:
                    dept = "IPRJ/DMC - Nova Friburgo"
                elif "DEMAT" in text_content or "Materiais" in text_content:
                    dept = "IPRJ/DEMAT - Nova Friburgo"

                lab_str = "IPRJ Research Labs / Supercomputador Escola de Sagres"

                spec = "Modelagem Computacional, Métodos Numéricos & Simulação"
                if "Transferência de Calor" in text_content or "Termofluidodinâmica" in text_content:
                    spec = "Termofluidodinâmica, Transferência de Calor, CFD & Métodos Numéricos"
                elif "Materiais" in text_content:
                    spec = "Ciência dos Materiais, Propriedades Mecânicas & Simulação"

                iprj_records.append({
                    "name": name,
                    "email": email or "secretaria@iprj.uerj.br",
                    "department": dept,
                    "laboratory": lab_str,
                    "specialization": spec,
                    "source_url": lattes or link,
                    "validation_date": "2026-03-09"
                })
            except Exception:
                pass
    except Exception as e:
        print(f"IPRJ Crawl error: {e}")
    return iprj_records

def crawl_ppgcompmat():
    print("Crawling PPG-COMPMAT (IME/Maracanã)...")
    compmat_records = []
    url = 'https://ccomp.ime.uerj.br/corpo-docente-mestrado-e-doutorado/'
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')

        for p in soup.find_all('p'):
            text = clean_text(p.get_text())
            email = extract_email(text)
            lattes = extract_lattes(p) or extract_lattes(text)

            if email and lattes:
                name_part = text.split(email)[0].strip()
                name = clean_person_name(clean_text(name_part))
                if name and len(name) < 60 and not name.startswith("Membro"):
                    compmat_records.append({
                        "name": name,
                        "email": email,
                        "department": "IME/PPG-COMPMAT - Campus Maracanã",
                        "laboratory": "Laboratórios de Computação Científica IME/UERJ",
                        "specialization": "Computação de Alto Desempenho (HPC), IA, Métodos Numéricos & Modelagem Matemática",
                        "source_url": lattes,
                        "validation_date": "2026-03-09"
                    })
    except Exception as e:
        print(f"Error crawling PPG-COMPMAT: {e}")
    return compmat_records

def crawl_fat():
    print("Crawling FAT (Resende)...")
    fat_records = []
    depts = [
        ("https://www.fat.uerj.br/departamento/departamento-de-mecanica-e-energia/", "FAT/DME (Mecânica e Energia) - Campus Resende", "Mecânica dos Sólidos, Termofluidodinâmica, Hidráulica, Pneumática & Motores"),
        ("https://www.fat.uerj.br/departamento/departamento-de-quimica-e-ambiental/", "FAT/DEQA (Química e Ambiental) - Campus Resende", "Processos Químicos, Polímeros, Compósitos & Modelagem Molecular"),
        ("https://www.fat.uerj.br/departamento/departamento-de-engenharia-de-producao/", "FAT/DENP (Engenharia de Produção) - Campus Resende", "Otimização, Processos de Fabricação & Pesquisa Operacional"),
        ("https://www.fat.uerj.br/departamento/departamento-de-matematica-fisica-e-computacao/", "FAT/DMFC (Matemática, Física e Computação) - Campus Resende", "Computação Científica, Física Aplicada & Métodos Numéricos")
    ]

    for url, dept_name, spec in depts:
        try:
            r = requests.get(url, headers=headers, verify=False, timeout=10)
            ptext = ftfy.fix_text(r.text)
            soup = BeautifulSoup(ptext, 'html.parser')

            p_blocks = soup.find_all(['p', 'div'])
            for p in p_blocks:
                lattes = extract_lattes(p)
                if lattes:
                    p_text = clean_text(p.get_text())
                    lines = [l.strip() for l in p_text.split('http')[0].split('\n') if l.strip()]
                    if lines:
                        candidate_name = lines[-1].replace('CHEFE', '').replace('SUBCHEFE', '').strip()
                        candidate_name = clean_person_name(candidate_name)
                        if len(candidate_name) > 3 and not candidate_name.startswith('http') and candidate_name not in [r['name'] for r in fat_records]:
                            email = extract_email(p_text) or "adm@campusresende.uerj.br"
                            fat_records.append({
                                "name": candidate_name,
                                "email": email,
                                "department": dept_name,
                                "laboratory": "Laboratório de Materiais e Processos / Polímeros / Motores (FAT)",
                                "specialization": spec,
                                "source_url": lattes,
                                "validation_date": "2026-03-09"
                            })
        except Exception as e:
            print(f"Error crawling FAT url {url}: {e}")
    return fat_records

def crawl_inovuerj():
    print("Adding InovUerj / DEPINOVA leaders...")
    return [
        {
            "name": "Diretoria InovUerj / DEPINOVA",
            "email": "inovuerj@uerj.br",
            "department": "InovUerj - Departamento de Inovação / PR2",
            "laboratory": "Escritório de Propriedade Intelectual (EPI) & Projetos",
            "specialization": "Gestão de Inovação, Transferência de Tecnologia & Parcerias Universidade-Empresa",
            "source_url": "https://www.pr2.uerj.br",
            "validation_date": "2026-03-09"
        }
    ]

if __name__ == '__main__':
    all_records = []
    all_records.extend(crawl_fen())
    all_records.extend(crawl_iprj())
    all_records.extend(crawl_ppgcompmat())
    all_records.extend(crawl_fat())
    all_records.extend(crawl_inovuerj())

    print(f"Total extracted records across all units: {len(all_records)}")
    with open('raw_uerj_records.json', 'w', encoding='utf-8') as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
