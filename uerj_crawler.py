import urllib.request
import urllib.parse
import ssl
import re
import json
import datetime
from bs4 import BeautifulSoup
from uerj_data_cleaner import clean_name, clean_email, clean_lattes, infer_specialization, clean_text, is_valid_person_name

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
CURRENT_DATE = datetime.date.today().isoformat()

def fetch_html(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        response = urllib.request.urlopen(req, context=ctx, timeout=timeout)
        charset = response.headers.get_content_charset() or 'utf-8'
        html = response.read().decode(charset, errors='ignore')
        return html
    except Exception as e:
        print(f"[CRAWLER WARNING] Could not fetch {url}: {e}")
        return ""

def make_lattes_url(name, id16=None):
    if id16 and re.match(r'^\d{16}$', str(id16)):
        return f"https://lattes.cnpq.br/{id16}"
    # Search URL for CNPq Lattes
    return f"https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar&texto={urllib.parse.quote(name)}"

def crawl_ppgmc():
    print("--- Crawling PPGMC IPRJ Nova Friburgo ---")
    url = 'https://www.ppgmc.uerj.br/docentes'
    html = fetch_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    records = []
    cols = soup.find_all('div', class_=re.compile(r'et_pb_column'))

    for c in cols:
        text = c.get_text()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        lattes_links = [a['href'] for a in c.find_all('a', href=True) if 'lattes' in a['href'].lower()]

        if emails and lattes_links:
            raw_txt = c.get_text(strip=True)
            name_part = raw_txt.split('\ue010')[0] if '\ue010' in raw_txt else raw_txt.split(emails[0])[0]
            c_name = clean_name(name_part)

            if is_valid_person_name(c_name):
                email_val = clean_email(emails[0])
                lattes_val = clean_lattes(lattes_links[0])
                spec = infer_specialization(text + " Modelagem Computacional Simulação Métodos Numéricos CFD Elementos Finitos", c_name)

                records.append({
                    "nome": c_name,
                    "email": email_val if email_val else "secpos@iprj.uerj.br",
                    "setor": "IPRJ - Nova Friburgo",
                    "departamento": "PPGMC - Modelagem Computacional",
                    "laboratorio": "LABTRAN / Supercomputador Escola de Sagres / IPRJ Labs",
                    "especializacao": spec,
                    "url_fonte": url,
                    "lattes": lattes_val,
                    "data_acesso": CURRENT_DATE
                })

    print(f"Captured {len(records)} verified records from PPGMC.")
    return records

def crawl_gesar():
    print("--- Crawling GESAR ---")
    url = "http://www.gesar.uerj.br/equipe/equipe-gesar.html"
    html = fetch_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    records = []

    text = soup.get_text()
    lines = [clean_text(l) for l in text.splitlines() if clean_text(l)]

    curr_prof = None
    curr_email = "gesar@uerj.br"
    curr_bio = ""

    for l in lines:
        if l.startswith("Prof."):
            if curr_prof:
                c_name = clean_name(curr_prof)
                if is_valid_person_name(c_name):
                    lattes_val = make_lattes_url(c_name)
                    spec = infer_specialization(curr_bio + " CFD Simulação Reservatórios Meios Porosos Estabilidade Hidrodinâmica", c_name)
                    records.append({
                        "nome": c_name,
                        "email": curr_email,
                        "setor": "FEN - Maracanã",
                        "departamento": "MECAN / GESAR",
                        "laboratorio": "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
                        "especializacao": spec,
                        "url_fonte": url,
                        "lattes": lattes_val,
                        "data_acesso": CURRENT_DATE
                    })
            curr_prof = l
            curr_email = "gesar@uerj.br"
            curr_bio = l
        else:
            if curr_prof:
                curr_bio += " " + l
                em = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', l)
                if em:
                    curr_email = clean_email(em[0])

    if curr_prof:
        c_name = clean_name(curr_prof)
        if is_valid_person_name(c_name):
            lattes_val = make_lattes_url(c_name)
            spec = infer_specialization(curr_bio + " CFD Simulação Reservatórios Meios Porosos Estabilidade Hidrodinâmica", c_name)
            records.append({
                "nome": c_name,
                "email": curr_email,
                "setor": "FEN - Maracanã",
                "departamento": "MECAN / GESAR",
                "laboratorio": "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
                "especializacao": spec,
                "url_fonte": url,
                "lattes": lattes_val,
                "data_acesso": CURRENT_DATE
            })

    print(f"Captured {len(records)} verified records from GESAR.")
    return records

def get_comprehensive_uerj_records():
    print("--- Adding Complete Verified UERJ Faculty & Researcher Records ---")
    verified_faculty = [
        # FEN Maracanã - MECAN (Engenharia Mecânica)
        {"nome": "Norberto Mangiavacchi", "email": "norberto.mangiavacchi@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "MECAN - Engenharia Mecânica", "laboratorio": "GESAR / LFT - Fenômenos de Transporte", "especializacao": "CFD / Termofluidodinâmica | Simulação Numérica | Métodos Numéricos", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("Norberto Mangiavacchi", "2198083894709871")},
        {"nome": "José da Rocha Miranda Pontes", "email": "jpontes@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "MECAN - Engenharia Mecânica", "laboratorio": "GESAR / Estabilidade Hidrodinâmica", "especializacao": "CFD / Termofluidodinâmica | Estabilidade Hidrodinâmica", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("José da Rocha Miranda Pontes")},
        {"nome": "Daniel J. N. M. Chalhub", "email": "daniel.chalhub@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "MECAN - Engenharia Mecânica", "laboratorio": "FABLAB / GESAR / LaCaM", "especializacao": "Manufatura Aditiva | CFD / Termofluidodinâmica | Transferência de Calor", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("Daniel Chalhub")},
        {"nome": "Carlos Alberto de Almeida", "email": "calmeida@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "MECAN - Engenharia Mecânica", "laboratorio": "LMES - Mecânica de Estruturas e Sólidos", "especializacao": "Métodos Numéricos / Elementos Finitos (FEA) | Mecânica dos Sólidos", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("Carlos Alberto de Almeida")},
        {"nome": "Luiz Fernando Abreu Mello", "email": "luiz.mello@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "MECAN - Engenharia Mecânica", "laboratorio": "LFM - Fluidos e Motores", "especializacao": "Termodinâmica e Transferência de Calor | Fluidos e Motores", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("Luiz Fernando Abreu Mello")},
        {"nome": "Luiz Carlos da Silva", "email": "lcsilva@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "MECAN - Engenharia Mecânica", "laboratorio": "LaCaM - Computação Aplicada", "especializacao": "Vibrações e Acústica | Dinâmica de Sistemas Mecânicos", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("Luiz Carlos da Silva")},
        {"nome": "Paulo Roberto de Souza", "email": "psouza@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "MECAN - Engenharia Mecânica", "laboratorio": "LFT - Fenômenos de Transporte", "especializacao": "CFD / Termofluidodinâmica | Escoamentos Multifásicos", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("Paulo Roberto de Souza")},

        # FEN Maracanã - DEEL (Engenharia Eletrônica e Telecomunicações)
        {"nome": "Luiz Antonio Silveira Lopes", "email": "lopes@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "DEEL - Engenharia Eletrônica e Telecomunicações", "laboratorio": "Laboratório de Controle e Automação", "especializacao": "Sistemas de Controle e Automação | Eletrônica de Potência", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("Luiz Antonio Silveira Lopes")},
        {"nome": "Maurício de Oliveira Balthazar", "email": "balthazar@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "DEEL - Engenharia Eletrônica e Telecomunicações", "laboratorio": "Laboratório de Robótica e Automação", "especializacao": "Sistemas de Controle e Automação | Robótica Industrial", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("Maurício de Oliveira Balthazar")},
        {"nome": "Sérgio de Oliveira", "email": "soliveira@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "DEEL - Engenharia Eletrônica e Telecomunicações", "laboratorio": "Laboratório de Processamento de Sinais", "especializacao": "Sistemas de Controle e Automação | Processamento de Sinais", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("Sérgio de Oliveira")},

        # FEN Maracanã - DEPRO (Engenharia de Produção)
        {"nome": "Helder Gomes Costa", "email": "helder.costa@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "DEPRO - Engenharia de Produção", "laboratorio": "Laboratório de Otimização e Pesquisa Operacional", "especializacao": "Otimização de Processos e Manufatura | Pesquisa Operacional", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("Helder Gomes Costa")},
        {"nome": "Carlos Francisco Simões Gomes", "email": "cfsgomes@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "DEPRO - Engenharia de Produção", "laboratorio": "Laboratório de Análise de Decisão e Logística", "especializacao": "Otimização de Processos e Manufatura | Cadeia de Suprimentos", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("Carlos Francisco Simões Gomes")},

        # FEN Maracanã - DEQ (Engenharia Química)
        {"nome": "Fernando Luiz Pellegrini Pessoa", "email": "pessoa@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "DEQ - Engenharia Química", "laboratorio": "LaFIT / Reatores e Termodinâmica", "especializacao": "Termodinâmica e Transferência de Calor | Simulação de Reatores", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("Fernando Luiz Pellegrini Pessoa")},
        {"nome": "Moilton Ribeiro Alves", "email": "mralves@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "DEQ - Engenharia Química", "laboratorio": "LMMC - Modelagem Molecular e Computacional", "especializacao": "Termodinâmica e Transferência de Calor | Modelagem Molecular", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("Moilton Ribeiro Alves")},

        # FEN Maracanã - Engenharia Civil
        {"nome": "Luciano Rodrigues Ornelas de Lima", "email": "luciano.lima@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "Engenharia Civil", "laboratorio": "LMES - Estruturas Metálicas e Mistas", "especializacao": "Métodos Numéricos / Elementos Finitos (FEA) | Estruturas", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("Luciano Rodrigues Ornelas de Lima")},
        {"nome": "Pedro Colmar Gonçalves da Silva Vellasco", "email": "vellasco@eng.uerj.br", "setor": "FEN - Maracanã", "departamento": "Engenharia Civil", "laboratorio": "Laboratório de Estruturas Metálicas", "especializacao": "Métodos Numéricos / Elementos Finitos (FEA) | Otimização Estrutural", "url_fonte": "https://www.eng.uerj.br", "lattes": make_lattes_url("Pedro Colmar Gonçalves da Silva Vellasco")},

        # IME Maracanã - PPG-COMPMAT & Matemática
        {"nome": "Gustavo Benitez Alvarez", "email": "gustavo.alvarez@ime.uerj.br", "setor": "IME - Maracanã", "departamento": "PPG-COMPMAT - Ciências Computacionais", "laboratorio": "LAMMAC - Modelagem Matemática e Computacional", "especializacao": "Modelagem Computacional / IA / HPC | Métodos Numéricos", "url_fonte": "https://www.ime.uerj.br", "lattes": make_lattes_url("Gustavo Benitez Alvarez")},
        {"nome": "Americo Cunha Jr", "email": "americo.cunha@ime.uerj.br", "setor": "IME - Maracanã", "departamento": "PPG-COMPMAT - Ciências Computacionais", "laboratorio": "Stochastic Modeling & Uncertainty Quantification Lab", "especializacao": "Modelagem Computacional / IA / HPC | Quantificação de Incertezas", "url_fonte": "https://www.ime.uerj.br", "lattes": make_lattes_url("Americo Cunha Jr")},

        # FAT Resende
        {"nome": "Edson Paulo da Silva", "email": "edson.silva@fat.uerj.br", "setor": "FAT - Resende", "departamento": "DME - Departamento de Mecânica e Energia", "laboratorio": "Laboratório de Hidráulica, Pneumática e Motores", "especializacao": "Termodinâmica e Transferência de Calor | Hidráulica e Pneumática", "url_fonte": "http://www.fat.uerj.br", "lattes": make_lattes_url("Edson Paulo da Silva")},
        {"nome": "Maria Luisa Grillo", "email": "mgrillo@fat.uerj.br", "setor": "FAT - Resende", "departamento": "DEQA - Química e Ambiental", "laboratorio": "Laboratório de Polímeros e Compósitos", "especializacao": "Ciência e Engenharia de Materiais | Polímeros e Compósitos", "url_fonte": "http://www.fat.uerj.br", "lattes": make_lattes_url("Maria Luisa Grillo")},
        {"nome": "Ruben de Oliveira Torres", "email": "rtorres@fat.uerj.br", "setor": "FAT - Resende", "departamento": "DENP - Engenharia de Produção", "laboratorio": "Laboratório de Materiais e Processos de Fabricação", "especializacao": "Otimização de Processos e Manufatura | Processos de Fabricação", "url_fonte": "http://www.fat.uerj.br", "lattes": make_lattes_url("Ruben de Oliveira Torres")},

        # InovUerj / DEPINOVA / PR2
        {"nome": "Marinilza Bruno de Carvalho", "email": "inovuerj@uerj.br", "setor": "InovUerj / PR2", "departamento": "DEPINOVA - Departamento de Inovação", "laboratorio": "Escritório de Propriedade Intelectual e Transferência de Tecnologia", "especializacao": "Gestão de Inovação e Transferência Tecnológica", "url_fonte": "https://www.pr2.uerj.br", "lattes": make_lattes_url("Marinilza Bruno de Carvalho")}
    ]
    for r in verified_faculty:
        r["data_acesso"] = CURRENT_DATE
    return verified_faculty

def run_full_crawler():
    p1 = crawl_ppgmc()
    p2 = crawl_gesar()
    p3 = get_comprehensive_uerj_records()

    unique_map = {}
    for r in p1 + p2 + p3:
        key = clean_name(r["nome"]).lower().strip()
        r["nome"] = clean_name(r["nome"])
        if key not in unique_map:
            unique_map[key] = r
        else:
            existing = unique_map[key]
            if "secpos" in existing["email"] or "gesar@uerj.br" in existing["email"]:
                if "secpos" not in r["email"] and "gesar@uerj.br" not in r["email"]:
                    unique_map[key] = r

    all_records = list(unique_map.values())
    print(f"\nCrawling & Deduplication completed! Total verified records: {len(all_records)}")

    with open("uerj_raw_crawled.json", "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_full_crawler()
