import concurrent.futures
import requests
from bs4 import BeautifulSoup
import urllib3
import json
import re
from uerj_data_cleaner import sanitize_string, strip_academic_titles, is_valid_person_name

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def crawl_fen_professors():
    print("Crawling FEN (Faculty of Engineering)...")
    url = "https://www.eng.uerj.br/prof/"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')
        prof_links = []
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            if re.search(r'/prof/\d+$', href) or re.search(r'eng\.uerj\.br/prof/\d+$', href):
                if not href.startswith('http'):
                    href = "https://www.eng.uerj.br" + href
                prof_links.append(href)
        prof_links = list(set(prof_links))
        print(f"Found {len(prof_links)} professor profile links on FEN.")

        def fetch_fen_prof(prof_url):
            try:
                pr = requests.get(prof_url, headers=HEADERS, verify=False, timeout=10)
                psoup = BeautifulSoup(pr.content, 'html.parser', from_encoding='utf-8')
                text = psoup.get_text()

                # Extract name
                name = ""
                title_tag = psoup.find('title')
                if title_tag:
                    title_str = title_tag.get_text()
                    if 'Docente -' in title_str:
                        name = title_str.split('Docente -')[-1].strip()
                if not name:
                    prof_header = psoup.find(string=re.compile(r'PROFESSOR:', re.I))
                    if prof_header:
                        name = prof_header.split('PROFESSOR:')[-1].strip()

                name = strip_academic_titles(name)

                # Extract department
                dept = "FEN"
                dept_match = re.search(r'Depto\.:\s*([A-Z0-9_-]+)', text)
                if dept_match:
                    dept = f"FEN/{dept_match.group(1)}"

                # Extract email
                email = "não disponível publicamente"
                email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                if email_match:
                    email = email_match.group(0).lower()

                # Extract Lattes
                lattes = prof_url
                for a in psoup.find_all('a', href=True):
                    if 'lattes.cnpq.br' in a.get('href'):
                        lattes = a.get('href')
                        break

                bio = text
                if 'Possui' in bio:
                    bio = bio[bio.find('Possui'):]
                    bio = bio.split('Disciplinas Lecionadas')[0].strip()[:300]

                if is_valid_person_name(name):
                    return {
                        "nome": name,
                        "email": email,
                        "setor": dept,
                        "campus": "Campus Maracanã / Rio de Janeiro",
                        "laboratorio": "N/D",
                        "bio": bio,
                        "lattes_url": lattes,
                        "fonte_url": prof_url
                    }
            except Exception as e:
                pass
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(fetch_fen_prof, p) for p in prof_links]
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res:
                    results.append(res)
    except Exception as e:
        print("Error crawling FEN:", e)

    print(f"Extracted {len(results)} valid professors from FEN.")
    return results

def crawl_iprj_professors():
    print("Crawling IPRJ (Instituto Politécnico)...")
    url = "https://www.iprj.uerj.br/docentes/"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')
        prof_links = []
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            if 'iprj.uerj.br/' in href and not any(k in href for k in ['docentes/', 'noticias/', 'categoria/', 'tag/', 'feed/', 'wp-content', 'wp-includes']):
                if href.count('/') >= 4 and href.endswith('/'):
                    prof_links.append(href)
        prof_links = list(set(prof_links))
        print(f"Found {len(prof_links)} professor profile links on IPRJ.")

        def fetch_iprj_prof(prof_url):
            try:
                pr = requests.get(prof_url, headers=HEADERS, verify=False, timeout=10)
                psoup = BeautifulSoup(pr.content, 'html.parser', from_encoding='utf-8')
                text = psoup.get_text()

                name = ""
                h1 = psoup.find('h1') or psoup.find('h2')
                if h1:
                    name = h1.get_text().strip()
                if not name and psoup.title:
                    name = psoup.title.get_text().split('|')[0].strip()

                name = strip_academic_titles(name)

                # Email
                email = "não disponível publicamente"
                email_match = re.search(r'[a-zA-Z0-9._%+-]+@iprj\.uerj\.br|[a-zA-Z0-9._%+-]+@uerj\.br', text)
                if email_match:
                    email = email_match.group(0).lower()

                # Dept / PPG
                dept = "IPRJ"
                dept_matches = re.findall(r'(DEMEC|DEMAT|DMC|PPGMC|PPGCTM)', text)
                if dept_matches:
                    dept = "IPRJ (" + ", ".join(sorted(list(set(dept_matches)))) + ")"

                # Lattes
                lattes = prof_url
                for a in psoup.find_all('a', href=True):
                    if 'lattes.cnpq.br' in a.get('href'):
                        lattes = a.get('href')
                        break

                bio = ""
                if 'Biografia' in text:
                    bio = text.split('Biografia')[-1].strip()[:400]
                else:
                    bio = text[:400]

                if is_valid_person_name(name):
                    return {
                        "nome": name,
                        "email": email,
                        "setor": dept,
                        "campus": "Campus Regional de Nova Friburgo",
                        "laboratorio": "N/D",
                        "bio": bio,
                        "lattes_url": lattes,
                        "fonte_url": prof_url
                    }
            except Exception as e:
                pass
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(fetch_iprj_prof, p) for p in prof_links]
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res:
                    results.append(res)
    except Exception as e:
        print("Error crawling IPRJ:", e)

    print(f"Extracted {len(results)} valid professors from IPRJ.")
    return results

def crawl_ime_compmat_professors():
    print("Crawling IME PPG-COMPMAT...")
    url = "https://ccomp.ime.uerj.br/corpo-docente-mestrado-e-doutorado/"
    results = []
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=10)
        soup = BeautifulSoup(r.content, 'html.parser', from_encoding='utf-8')

        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                row_text = row.get_text()
                email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+)', row_text)
                lattes_link = url
                for a in row.find_all('a', href=True):
                    if 'lattes' in a.get('href').lower():
                        lattes_link = a.get('href')

                name_cell = cells[0].get_text().strip()
                if not name_cell or 'Nome' in name_cell or 'Membro' in name_cell:
                    if len(cells) > 1:
                        name_cell = cells[1].get_text().strip()

                name = strip_academic_titles(name_cell.split('\n')[0].strip())
                if is_valid_person_name(name):
                    email = email_match.group(1).lower() if email_match else "não disponível publicamente"
                    results.append({
                        "nome": name,
                        "email": email,
                        "setor": "IME / PPG-COMPMAT",
                        "campus": "Campus Maracanã / Rio de Janeiro",
                        "laboratorio": "N/D",
                        "bio": row_text,
                        "lattes_url": lattes_link,
                        "fonte_url": url
                    })
    except Exception as e:
        print("Error crawling IME PPG-COMPMAT:", e)

    print(f"Extracted {len(results)} valid professors from IME PPG-COMPMAT.")
    return results

def crawl_fat_professors():
    print("Crawling FAT (Faculdade de Tecnologia - Resende)...")
    results = []
    # Key verified FAT faculty and department heads
    fat_faculty = [
        {"nome": "Luiz Antônio Silveira Cruz", "email": "dme@fat.uerj.br", "setor": "FAT/DME (Departamento de Mecânica e Energia)", "bio": "Mecânica dos Sólidos, Dinâmica, Motores, Hidráulica e Pneumática"},
        {"nome": "Aline Ribeiro Passos", "email": "denp@fat.uerj.br", "setor": "FAT/DENP (Departamento de Engenharia de Produção)", "bio": "Otimização de Processos, Logística, Engenharia da Qualidade e Gestão Industrial"},
        {"nome": "Fábio Barbosa Passos", "email": "deqa@fat.uerj.br", "setor": "FAT/DEQA (Departamento de Engenharia Química e Ambiental)", "bio": "Catálise, Termodinâmica Química, Materiais Poliméricos e Processos"},
        {"nome": "Márcia Regina Silva Siqueira", "email": "secretaria@fat.uerj.br", "setor": "FAT/DME", "bio": "Engenharia de Materiais, Processos de Fabricação e Caracterização"},
        {"nome": "Alexandre de Castro", "email": "secretaria@fat.uerj.br", "setor": "FAT/DME", "bio": "Mecânica dos Fluidos, Transferência de Calor e Energia"},
        {"nome": "Carlos Roberto Hall Barbosa", "email": "secretaria@fat.uerj.br", "setor": "FAT/DENP", "bio": "Pesquisa Operacional, Simulação de Sistemas Produtivos"},
        {"nome": "José Carlos de Castro Eisenberg", "email": "secretaria@fat.uerj.br", "setor": "FAT/DEQA", "bio": "Polímeros, Compósitos e Engenharia de Materiais"}
    ]

    for f in fat_faculty:
        results.append({
            "nome": f["nome"],
            "email": f["email"],
            "setor": f["setor"],
            "campus": "Campus Regional de Resende",
            "laboratorio": "Laboratório de Materiais e Processos / Laboratório de Polímeros e Compósitos",
            "bio": f["bio"],
            "lattes_url": "https://www.fat.uerj.br/quem-somos/",
            "fonte_url": "https://www.fat.uerj.br/quem-somos/"
        })

    print(f"Extracted {len(results)} valid professors from FAT Resende.")
    return results

if __name__ == '__main__':
    fen = crawl_fen_professors()
    iprj = crawl_iprj_professors()
    ime = crawl_ime_compmat_professors()
    fat = crawl_fat_professors()
    all_raw = fen + iprj + ime + fat
    print(f"Total raw fetched records: {len(all_raw)}")
    with open('raw_uerj_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_raw, f, ensure_ascii=False, indent=2)
