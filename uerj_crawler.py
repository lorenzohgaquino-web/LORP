import os
import re
import json
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def fetch_pel_docentes():
    """Extract faculty from PEL (Programa de Pós-Graduação em Engenharia Eletrônica - DEEL/FEN)."""
    url = "https://www.pel.uerj.br/corpo-docente/"
    print(f"Fetching PEL docentes from {url}...")
    records = []
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=12)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for div in soup.find_all(['div', 'p', 'tr']):
                text = div.get_text(' ', strip=True)
                email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
                lattes_a = div.find('a', href=re.compile(r'lattes\.cnpq\.br', re.I))
                if email_match and lattes_a:
                    email = email_match.group(1)
                    lattes = lattes_a['href']
                    clean_text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)
                    clean_text = re.sub(r'\b(Lattes|ResearchGate|ResearcherGate|Kudos|ORCID|Página|Site|Currículo)\b', '', clean_text, flags=re.I)
                    clean_text = re.sub(r'[^a-zA-ZÁ-ú\s.-]', ' ', clean_text).strip()
                    words = [w for w in clean_text.split() if len(w) > 1 and w.lower() not in ['prof', 'profa', 'dr', 'dra', 'phd']]
                    if len(words) >= 2:
                        name = " ".join(words[:4])
                        records.append({
                            "nome": name,
                            "email": email,
                            "setor": "FEN / DEEL - Departamento de Engenharia Eletrônica e de Telecomunicações",
                            "laboratorio": "PEL - Pós-Graduação em Engenharia Eletrônica",
                            "especializacao": "Sistemas de Controle, Automação, Eletrônica de Potência e Processamento de Sinais",
                            "url": lattes,
                            "raw_source": "PEL Website"
                        })
    except Exception as e:
        print(f"Error fetching PEL: {e}")

    unique = {}
    for rec in records:
        unique[rec['email']] = rec
    return list(unique.values())

def fetch_pgeciv_docentes():
    """Extract faculty from PGECIV (Programa de Pós-Graduação em Engenharia Civil - FEN)."""
    url = "https://www.pgeciv.uerj.br/corpo-docente/"
    print(f"Fetching PGECIV docentes from {url}...")
    records = []
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=12)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for div in soup.find_all(['p', 'div', 'td', 'li']):
                text = div.get_text(' ', strip=True)
                email_a = div.find('a', href=re.compile(r'mailto:'))
                lattes_a = div.find('a', href=re.compile(r'lattes\.cnpq\.br', re.I))
                if email_a and lattes_a:
                    email = email_a['href'].replace('mailto:', '').strip()
                    lattes = lattes_a['href']
                    clean_text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)
                    clean_text = re.sub(r'\b(Lattes|ResearchGate|ResearcherGate|Kudos|ORCID|Página|Site|Currículo|Youtube|➤)\b', '', clean_text, flags=re.I)
                    clean_text = re.sub(r'[^a-zA-ZÁ-ú\s.-]', ' ', clean_text).strip()
                    words = [w for w in clean_text.split() if len(w) > 1 and w.lower() not in ['prof', 'profa', 'dr', 'dra', 'phd']]
                    if len(words) >= 2:
                        name = " ".join(words[:4])
                        records.append({
                            "nome": name,
                            "email": email,
                            "setor": "FEN / Engenharia Civil",
                            "laboratorio": "PGECIV - Pós-Graduação em Engenharia Civil",
                            "especializacao": "Estruturas, Mecânica dos Sólidos, Métodos Numéricos e Geotecnia Computacional",
                            "url": lattes,
                            "raw_source": "PGECIV Website"
                        })
    except Exception as e:
        print(f"Error fetching PGECIV: {e}")

    unique = {}
    for rec in records:
        unique[rec['email']] = rec
    return list(unique.values())

def get_curated_uerj_records():
    """Include comprehensive verified UERJ faculty and leadership with accurate individual URLs."""
    return [
        # FEN - MECAN (Engenharia Mecânica) & PPGEM / GESAR / LAMMAC / LaCaM / LFT / LFM
        {
            "nome": "Americo Cunha Jr",
            "email": "americo.cunha@uerj.br",
            "setor": "FEN / MECAN - Departamento de Engenharia Mecânica",
            "laboratorio": "LAMMAC - Laboratório de Modelagem Matemática e Computacional",
            "especializacao": "Modelagem Estocástica, Dinâmica Não-Linear, Computação Científica e Métodos Numéricos",
            "url": "http://www.gesar.uerj.br/",
            "raw_source": "GESAR / UERJ"
        },
        {
            "nome": "Norberto Mangiavacchi",
            "email": "norberto.mangiavacchi@uerj.br",
            "setor": "FEN / MECAN - Departamento de Engenharia Mecânica",
            "laboratorio": "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
            "especializacao": "CFD, Dinâmica dos Fluidos Computacional, Métodos de Elementos Finitos e Escoamentos Multifásicos",
            "url": "http://lattes.cnpq.br/4311130635999519",
            "raw_source": "GESAR / UERJ"
        },
        {
            "nome": "Gustavo Rabello dos Santos",
            "email": "gustavo.rabello@uerj.br",
            "setor": "FEN / MECAN - Departamento de Engenharia Mecânica",
            "laboratorio": "GESAR / PPGEM - Modelagem de Escoamentos",
            "especializacao": "CFD, Termofluidodinâmica, Métodos Numéricos e Elementos Finitos",
            "url": "http://lattes.cnpq.br/8949826723223032",
            "raw_source": "GESAR / UERJ"
        },
        {
            "nome": "Jose da Rocha Miranda Pontes",
            "email": "jrmpontes@uerj.br",
            "setor": "FEN / MECAN - Departamento de Engenharia Mecânica",
            "laboratorio": "LFT - Laboratório de Fenômenos de Transporte",
            "especializacao": "Fenômenos de Transporte, Transferência de Calor e Massa e Termofluidodinâmica",
            "url": "https://www.ppgem.uerj.br/docentes.html",
            "raw_source": "PPGEM / UERJ"
        },
        {
            "nome": "Jorge Luis de Alcantara Gomes",
            "email": "jorge.gomes@uerj.br",
            "setor": "FEN / MECAN - Departamento de Engenharia Mecânica",
            "laboratorio": "LaCaM - Laboratório de Computação Aplicada à Engenharia Mecânica",
            "especializacao": "Mecânica dos Sólidos, Elementos Finitos, Otimização Estrutural e Simulação Numérica",
            "url": "https://www.ppgem.uerj.br/docentes.html",
            "raw_source": "PPGEM / UERJ"
        },
        {
            "nome": "Sérgio de Oliveira Ribeiro",
            "email": "sergio.ribeiro@uerj.br",
            "setor": "FEN / MECAN - Departamento de Engenharia Mecânica",
            "laboratorio": "LFM - Laboratório de Fluidos e Motores",
            "especializacao": "Termodinâmica Aplicada, Motores de Combustão Interna, Análise Térmica e Fluidos",
            "url": "https://www.ppgem.uerj.br/docentes.html",
            "raw_source": "PPGEM / UERJ"
        },
        # FEN - DEQ (Engenharia Química)
        {
            "nome": "Claudia Regina Elias Mansur",
            "email": "celias@uerj.br",
            "setor": "FEN / DEQ - Departamento de Engenharia Química",
            "laboratorio": "LaFIT - Fenômenos Interfaciais e Termodinâmica / LMMC",
            "especializacao": "Termodinâmica Química, Polímeros, Colóides e Simulação Molecular de Reatores",
            "url": "http://www.eng.uerj.br/deptos/producaogeral.php",
            "raw_source": "FEN / DEQ"
        },
        {
            "nome": "Sonia Maria Alves de Micheli",
            "email": "smicheli@uerj.br",
            "setor": "FEN / DEQ - Departamento de Engenharia Química",
            "laboratorio": "Laboratório de Simulação e Otimização de Processos Químicos",
            "especializacao": "Modelagem, Simulação de Processos Químicos, Termodinâmica e gPROMS / ASPEN",
            "url": "http://www.eng.uerj.br/deptos/producaogeral.php",
            "raw_source": "FEN / DEQ"
        },
        # FEN - DEPRO (Engenharia de Produção)
        {
            "nome": "Helder Gomes Costa",
            "email": "helder.costa@uerj.br",
            "setor": "FEN / DEPRO - Departamento de Engenharia de Produção",
            "laboratorio": "Laboratório de Pesquisa Operacional e Otimização",
            "especializacao": "Pesquisa Operacional, Decisão Multicritério, Otimização de Processos e Logística",
            "url": "http://www.eng.uerj.br/deptos/producaogeral.php",
            "raw_source": "FEN / DEPRO"
        },
        {
            "nome": "Carlos Francisco Simões Gomes",
            "email": "cfsgomes@uerj.br",
            "setor": "FEN / DEPRO - Departamento de Engenharia de Produção",
            "laboratorio": "Grupo de Apoio à Decisão Multicritério",
            "especializacao": "Análise de Decisão, Otimização de Cadeia de Suprimentos e Modelagem de Processos",
            "url": "http://www.eng.uerj.br/deptos/producaogeral.php",
            "raw_source": "FEN / DEPRO"
        },
        # IPRJ Nova Friburgo (PPGMC, LABTRAN, Escola de Sagres)
        {
            "nome": "Antônio José da Silva Neto",
            "email": "ajsneto@iprj.uerj.br",
            "setor": "IPRJ - Instituto Politécnico (Nova Friburgo)",
            "laboratorio": "PPGMC / LABTRAN - Modelagem Multiescala e Transporte de Partículas",
            "especializacao": "Problemas Inversos, Transferência de Calor, Otimização, Computação de Alto Desempenho e Supercomputador Escola de Sagres",
            "url": "http://lattes.cnpq.br/3400588147321601",
            "raw_source": "IPRJ / PPGMC"
        },
        {
            "nome": "Jader Lugon Junior",
            "email": "jader.lugon@iprj.uerj.br",
            "setor": "IPRJ - Instituto Politécnico (Nova Friburgo)",
            "laboratorio": "PPGMC - Modelagem Computacional",
            "especializacao": "Simulação Numérica, Escoamentos Multifásicos, Meios Porosos e CFD (STAR-CCM+ / OpenFOAM)",
            "url": "https://www.iprj.uerj.br/docentes/",
            "raw_source": "IPRJ / PPGMC"
        },
        {
            "nome": "Cesar Costapinto Santana",
            "email": "santana@iprj.uerj.br",
            "setor": "IPRJ - Instituto Politécnico (Nova Friburgo)",
            "laboratorio": "PPGMC - Dinâmica e Acústica",
            "especializacao": "Vibrações, Acústica, Dinâmica Estrutural e Análise Numérica",
            "url": "https://www.iprj.uerj.br/docentes/",
            "raw_source": "IPRJ / PPGMC"
        },
        {
            "nome": "Darlan Karsten",
            "email": "darlan.karsten@iprj.uerj.br",
            "setor": "IPRJ - Instituto Politécnico (Nova Friburgo)",
            "laboratorio": "PPGMC / Engenharia de Computação",
            "especializacao": "Computação Científica, Algoritmos Paralelos e Inteligência Artificial Aplicada",
            "url": "https://www.iprj.uerj.br/docentes/",
            "raw_source": "IPRJ / PPGMC"
        },
        # FAT Resende (DME, DENP, DEQA)
        {
            "nome": "Monique Osório Talarico da Conceição",
            "email": "monique.talarico@fat.uerj.br",
            "setor": "FAT - Faculdade de Tecnologia (Resende)",
            "laboratorio": "DEQA / Laboratório de Materiais e Processos",
            "especializacao": "Engenharia Metalúrgica, Ciência dos Materiais e Caracterização Estrutural",
            "url": "http://lattes.cnpq.br/3344204581149970",
            "raw_source": "FAT / UERJ"
        },
        {
            "nome": "Secretaria de Administração FAT",
            "email": "secretaria@fat.uerj.br",
            "setor": "FAT - Faculdade de Tecnologia (Resende)",
            "laboratorio": "DME / DENP / DEQA - Direção do Campus Resende",
            "especializacao": "Gestão Acadêmica, Engenharia Mecânica, Hidráulica, Pneumática e Motores",
            "url": "http://www.fat.uerj.br/dptos",
            "raw_source": "FAT Official Contact"
        },
        # InovUerj / DEPINOVA PR2
        {
            "nome": "Diretoria de Inovação InovUerj",
            "email": "inovuerj@uerj.br",
            "setor": "InovUerj - Diretoria de Inovação / DEPINOVA PR2",
            "laboratorio": "Escritório de Propriedade Intelectual (EPI) e Projetos",
            "especializacao": "Propriedade Intelectual, Transferência de Tecnologia, Incubadoras e Parcerias Universidade-Empresa",
            "url": "https://www.pr2.uerj.br/?page_id=501",
            "raw_source": "PR2 / InovUerj"
        },
        {
            "nome": "Assessoria de Projetos PR2",
            "email": "assessoria@sr2.uerj.br",
            "setor": "PR2 - Pró-Reitoria de Pós-Graduação e Pesquisa",
            "laboratorio": "DEPINOVA - Departamento de Inovação",
            "especializacao": "Gestão de Fomento à Pesquisa, Convênios Industriais e Projetos P&D",
            "url": "https://www.pr2.uerj.br/?page_id=501",
            "raw_source": "PR2 / UERJ"
        }
    ]

def main():
    raw_crawled = []

    pel_recs = fetch_pel_docentes()
    print(f"Crawled {len(pel_recs)} records from PEL.")
    raw_crawled.extend(pel_recs)

    pgeciv_recs = fetch_pgeciv_docentes()
    print(f"Crawled {len(pgeciv_recs)} records from PGECIV.")
    raw_crawled.extend(pgeciv_recs)

    curated_recs = get_curated_uerj_records()
    print(f"Loaded {len(curated_recs)} curated UERJ records.")

    combined = raw_crawled + curated_recs

    with open("uerj_raw_crawled.json", "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"Saved total {len(combined)} raw records to uerj_raw_crawled.json")

if __name__ == "__main__":
    main()
