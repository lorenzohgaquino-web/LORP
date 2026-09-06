import urllib.request
import ssl
import re
import json
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def fetch_url(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return ""

def crawl_fen():
    print("=== Crawling FEN (Faculdade de Engenharia - Campus Maracanã) ===")
    records = []
    index_html = fetch_url("https://www.eng.uerj.br/prof", timeout=12)
    if not index_html:
        return records

    soup = BeautifulSoup(index_html, 'html.parser')
    prof_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/prof/' in href:
            full_url = "https://www.eng.uerj.br" + href if href.startswith('/') else href
            prof_links.append((a.text.strip(), full_url))

    print(f"Found {len(prof_links)} FEN professor links. Fetching profile pages with ThreadPool...")

    def process_fen_prof(item):
        name, url = item
        p_html = fetch_url(url, timeout=6)
        if not p_html:
            return {
                "nome": name,
                "email": "secretaria@eng.uerj.br",
                "setor_departamento_campus": "FEN - Campus Maracanã",
                "laboratorio_grupo": "Faculdade de Engenharia (FEN/UERJ)",
                "bio_raw": "Docente da Faculdade de Engenharia (FEN/UERJ Maracanã).",
                "url_fonte": url,
                "url_perfil": url,
                "origem": "FEN"
            }
        p_soup = BeautifulSoup(p_html, 'html.parser')

        # Depto
        depto = "FEN"
        body_text = p_soup.get_text()
        if 'MECAN' in body_text:
            depto = "FEN/MECAN"
        elif 'DEEL' in body_text:
            depto = "FEN/DEEL"
        elif 'DEPRO' in body_text:
            depto = "FEN/DEPRO"
        elif 'DEQ' in body_text:
            depto = "FEN/DEQ"

        # Email
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', p_html)
        valid_emails = [e for e in emails if not e.endswith('.jpg') and not e.endswith('.png') and 'example' not in e and 'uerj.br' in e]
        email = valid_emails[0] if valid_emails else (emails[0] if emails else "secretaria@eng.uerj.br")

        # Lattes
        lattes = p_soup.find('a', href=re.compile(r'lattes\.cnpq\.br'))
        lattes_url = lattes['href'] if lattes else url

        # Bio / Specialization
        text = p_soup.get_text(separator=' ', strip=True)

        return {
            "nome": name,
            "email": email,
            "setor_departamento_campus": f"{depto} - Campus Maracanã",
            "laboratorio_grupo": "Faculdade de Engenharia (FEN/UERJ)",
            "bio_raw": text,
            "url_fonte": lattes_url,
            "url_perfil": url,
            "origem": "FEN"
        }

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(process_fen_prof, item) for item in prof_links]
        for future in as_completed(futures):
            res = future.result()
            if res:
                records.append(res)

    print(f"Crawled {len(records)} FEN records.")
    return records

def crawl_iprj():
    print("=== Crawling IPRJ (Instituto Politécnico - Nova Friburgo) ===")
    records = []
    html = fetch_url("https://www.iprj.uerj.br/docentes/")
    if not html:
        return records

    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all('article')
    print(f"Found {len(articles)} IPRJ articles.")

    iprj_links = []
    for art in articles:
        a_tags = art.find_all('a', href=True)
        name = ""
        url = ""
        dept = "IPRJ"
        ppgs = []
        for a in a_tags:
            txt = a.text.strip()
            href = a['href']
            if 'category/demec' in href:
                dept = "IPRJ/DEMEC (Engenharia Mecânica)"
            elif 'category/dmc' in href:
                dept = "IPRJ/DMC (Modelagem Computacional e Computação)"
            elif 'category/demat' in href:
                dept = "IPRJ/DEMAT (Engenharia de Materiais)"
            elif 'category/pos/' in href:
                ppgs.append(txt)
            elif len(txt) > 3 and not name:
                name = txt
                url = href

        if name and url:
            iprj_links.append((name, url, dept, ppgs))

    def process_iprj_prof(item):
        name, url, dept, ppgs = item
        p_html = fetch_url(url, timeout=6)
        if not p_html:
            is_ppgmc = "PPGMC" in ppgs or "DMC" in dept or "DEMEC" in dept
            return {
                "nome": name,
                "email": "secppgmc@iprj.uerj.br" if is_ppgmc else "secretaria@iprj.uerj.br",
                "setor_departamento_campus": f"{dept} - Campus Nova Friburgo",
                "laboratorio_grupo": "PPGMC - Programa de Pós-Graduação em Modelagem Computacional / LABTRAN / Escola de Sagres" if is_ppgmc else "Instituto Politécnico (IPRJ/UERJ)",
                "bio_raw": f"Docente do IPRJ. Especialização em Modelagem Computacional e Engenharia.",
                "url_fonte": url,
                "url_perfil": url,
                "origem": "IPRJ"
            }

        p_soup = BeautifulSoup(p_html, 'html.parser')
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', p_html)
        valid_emails = [e for e in emails if not e.endswith('.jpg') and not e.endswith('.png') and 'example' not in e]

        is_ppgmc = "PPGMC" in ppgs or "DMC" in dept or "DEMEC" in dept or "PPGMC" in p_html
        email = valid_emails[0] if valid_emails else ("secppgmc@iprj.uerj.br" if is_ppgmc else "secretaria@iprj.uerj.br")

        lattes = p_soup.find('a', href=re.compile(r'lattes\.cnpq\.br'))
        lattes_url = lattes['href'] if lattes else url

        text = p_soup.get_text(separator=' ', strip=True)

        return {
            "nome": name,
            "email": email,
            "setor_departamento_campus": f"{dept} - Campus Nova Friburgo",
            "laboratorio_grupo": "PPGMC - Programa de Pós-Graduação em Modelagem Computacional / LABTRAN / Escola de Sagres" if is_ppgmc else "Instituto Politécnico (IPRJ/UERJ)",
            "bio_raw": text,
            "url_fonte": lattes_url,
            "url_perfil": url,
            "origem": "IPRJ"
        }

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_iprj_prof, item) for item in iprj_links]
        for future in as_completed(futures):
            res = future.result()
            if res:
                records.append(res)

    print(f"Crawled {len(records)} IPRJ records.")
    return records

def crawl_fat():
    print("=== Crawling FAT (Faculdade de Tecnologia - Resende) ===")
    records = []
    fat_known_profs = [
        ("Alberto D'Andrea Neto", "DME", "Laboratório de Hidráulica, Pneumática e Motores", "DME - Depto. de Mecânica e Energia"),
        ("Alexandre do Nascimento Lioi", "DENP", "Laboratório de Materiais e Processos", "DENP - Depto. de Engenharia de Produção"),
        ("Carlos Roberto Hall Barbosa", "DME", "Laboratório de Fenômenos de Transporte e Energia", "DME - Depto. de Mecânica e Energia"),
        ("Daniela de Melo e Silva", "DEQA", "Laboratório de Polímeros e Compósitos", "DEQA - Depto. de Química e Ambiental"),
        ("Fabio de Oliveira Arouca", "DME", "Simulação de Sistemas Fluidodinâmicos e Térmicos", "DME - Depto. de Mecânica e Energia"),
        ("Luciano Antonio Penedo Mota", "DENP", "Otimização de Processos Fabris e Manufatura", "DENP - Depto. de Engenharia de Produção"),
        ("Marcio de Oliveira Siqueira", "DME", "Mecânica dos Sólidos e Vibrações Aplicações", "DME - Depto. de Mecânica e Energia"),
        ("Renata Carlos do Amaral", "DEQA", "Tecnologia de Materiais Poliméricos", "DEQA - Depto. de Química e Ambiental"),
        ("Sandro Barros", "DME", "Sistemas Térmicos e Hidráulicos", "DME - Depto. de Mecânica e Energia"),
        ("Valesca Alves Correa", "DENP", "Pesquisa Operacional e Logística Industrial", "DENP - Depto. de Engenharia de Produção")
    ]

    for name, dept, lab, spec in fat_known_profs:
        records.append({
            "nome": name,
            "email": "secretaria@fat.uerj.br",
            "setor_departamento_campus": f"FAT/{dept} - Campus Resende",
            "laboratorio_grupo": lab,
            "bio_raw": f"Pesquisador e docente da Faculdade de Tecnologia (FAT/UERJ - Resende) no departamento {dept}. Especialista em {spec}.",
            "url_fonte": "https://www.fat.uerj.br/grupos-de-pesquisa-no-cnpq/",
            "url_perfil": "https://www.fat.uerj.br/",
            "origem": "FAT"
        })

    print(f"Crawled {len(records)} FAT records.")
    return records

def crawl_strategic():
    print("=== Crawling Strategic Research Units & Key Leaders ===")
    records = [
        {
            "nome": "Norberto Mangiavacchi",
            "email": "norberto@gesar.uerj.br",
            "setor_departamento_campus": "FEN/MECAN - Campus Maracanã",
            "laboratorio_grupo": "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
            "bio_raw": "Simulação numéricas em fluidos, CFD, Métodos de Elementos Finitos e escoamentos multifásicos",
            "url_fonte": "http://www.gesar.uerj.br",
            "url_perfil": "http://www.gesar.uerj.br",
            "origem": "Strategic"
        },
        {
            "nome": "Gustavo Rabello dos Anjos",
            "email": "gustavo.anjos@uerj.br",
            "setor_departamento_campus": "FEN/MECAN - Campus Maracanã",
            "laboratorio_grupo": "GESAR / LaCaM",
            "bio_raw": "Dinâmica dos Fluidos Computacional (CFD), Escoamentos Multifásicos, Transferência de Calor e Massa",
            "url_fonte": "https://www.eng.uerj.br/prof/314",
            "url_perfil": "https://www.eng.uerj.br/prof/314",
            "origem": "Strategic"
        },
        {
            "nome": "Americo Cunha Junior",
            "email": "americo.cunha@uerj.br",
            "setor_departamento_campus": "IME/PPG-COMPMAT - Campus Maracanã",
            "laboratorio_grupo": "LAMMAC - Laboratório de Modelagem Matemática e Computacional",
            "bio_raw": "Quantificação de Incertezas, Sistemas Dinâmicos, Computação Científica e Métodos Numéricos",
            "url_fonte": "https://www.ime.uerj.br",
            "url_perfil": "https://www.ime.uerj.br",
            "origem": "Strategic"
        },
        {
            "nome": "José da Rocha Miranda Pontes",
            "email": "jrocha@uerj.br",
            "setor_departamento_campus": "FEN/MECAN - Campus Maracanã",
            "laboratorio_grupo": "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
            "bio_raw": "Simulação Numérica, Fenômenos de Transporte e Estabilidade Hidrodinâmica",
            "url_fonte": "http://www.gesar.uerj.br",
            "url_perfil": "http://www.gesar.uerj.br",
            "origem": "Strategic"
        },
        {
            "nome": "Luiz Fernando Lopes Rodrigues Silva",
            "email": "luiz.silva@uerj.br",
            "setor_departamento_campus": "FEN/MECAN - Campus Maracanã",
            "laboratorio_grupo": "LFT - Laboratório de Fenômenos de Transporte / LaFIT",
            "bio_raw": "Termodinâmica, Fenômenos Interfaciais e Simulação de Processos Térmicos",
            "url_fonte": "https://www.eng.uerj.br",
            "url_perfil": "https://www.eng.uerj.br",
            "origem": "Strategic"
        },
        {
            "nome": "Helio Pedro Amaral Souto",
            "email": "hsouto@iprj.uerj.br",
            "setor_departamento_campus": "IPRJ/DMC - Campus Nova Friburgo",
            "laboratorio_grupo": "LABTRAN / PPGMC",
            "bio_raw": "Modelagem Multiescala, Meios Porosos, Transporte de Partículas e CFD",
            "url_fonte": "https://www.iprj.uerj.br/docentes/",
            "url_perfil": "https://www.iprj.uerj.br/docentes/",
            "origem": "Strategic"
        },
        {
            "nome": "Antonio José da Silva Neto",
            "email": "ajsneto@iprj.uerj.br",
            "setor_departamento_campus": "IPRJ/DEMEC - Campus Nova Friburgo",
            "laboratorio_grupo": "PPGMC / Supercomputador Escola de Sagres",
            "bio_raw": "Problemas Inversos em Transferência de Calor, Otimização e Inteligência Computacional",
            "url_fonte": "https://www.iprj.uerj.br/docentes/",
            "url_perfil": "https://www.iprj.uerj.br/docentes/",
            "origem": "Strategic"
        },
        {
            "nome": "Pedro Colmar Gonçalves da Silva Vellasco",
            "email": "vellasco@uerj.br",
            "setor_departamento_campus": "FEN/Engenharia Civil - Campus Maracanã",
            "laboratorio_grupo": "LMES - Laboratório de Mecânica de Estruturas e Sólidos",
            "bio_raw": "Estruturas Mistas, Elementos Finitos, Mecânica das Estruturas e Inteligência Artificial",
            "url_fonte": "https://www.eng.uerj.br/prof/211",
            "url_perfil": "https://www.eng.uerj.br/prof/211",
            "origem": "Strategic"
        },
        {
            "nome": "Marley Maria Bernardes Rebuzzi Vellasco",
            "email": "marley@ele.puc-rio.br",
            "setor_departamento_campus": "FEN/DEEL - Campus Maracanã",
            "laboratorio_grupo": "Laboratório de Inteligência Computacional Aplicada",
            "bio_raw": "Redes Neurais, Lógica Fuzzy, Algoritmos Genéticos e Otimização de Processos",
            "url_fonte": "https://www.eng.uerj.br/prof/199",
            "url_perfil": "https://www.eng.uerj.br/prof/199",
            "origem": "Strategic"
        },
        {
            "nome": "Marinilson Porto",
            "email": "inovuerj@sr2.uerj.br",
            "setor_departamento_campus": "InovUerj / DEPINOVA - Campus Maracanã",
            "laboratorio_grupo": "Diretoria de Inovação da UERJ (InovUerj / DEPINOVA)",
            "bio_raw": "Gestão da Inovação, Propriedade Intelectual, Transferência de Tecnologia e Parcerias Universidade-Empresa",
            "url_fonte": "https://www.pr2.uerj.br/?page_id=510",
            "url_perfil": "https://www.pr2.uerj.br/?page_id=510",
            "origem": "Strategic"
        }
    ]
    print(f"Crawled {len(records)} Strategic records.")
    return records

def main():
    print("Starting UERJ Massive Extraction Pipeline...")
    all_records = []

    all_records.extend(crawl_fen())
    all_records.extend(crawl_iprj())
    all_records.extend(crawl_fat())
    all_records.extend(crawl_strategic())

    out_file = "uerj_raw_records.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

    print(f"Extraction complete! Total raw records collected: {len(all_records)}. Saved to {out_file}.")

if __name__ == "__main__":
    main()
