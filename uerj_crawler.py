import requests
import urllib3
import re
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=12)
        if r.status_code == 200:
            return r.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return ""

def scrape_ppgmc():
    url = "https://www.ppgmc.uerj.br/docentes"
    html = fetch(url)
    records = []
    if not html:
        return records

    soup = BeautifulSoup(html, 'html.parser')
    seen_emails = set()

    for item in soup.find_all(['p', 'div', 'tr', 'li']):
        # Find element containing email
        text = item.get_text(' ', strip=True)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        if emails and len(text) < 150:
            email = emails[0].lower().strip()
            if email in seen_emails:
                continue

            lattes_url = "https://www.ppgmc.uerj.br/docentes"
            for a in item.find_all('a', href=True):
                if 'lattes.cnpq.br' in a['href']:
                    lattes_url = a['href']
                    break

            # Extract clean name: text prior to email or icon
            raw_name = text.split(emails[0])[0]
            raw_name = re.sub(r'[\t\r\n]', '', raw_name)
            raw_name = re.sub(r'^(Prof\.?|Dr\.?|D\.Sc\.?|Dra\.?|Membro|Nome|Vínculo)\s*', '', raw_name, flags=re.IGNORECASE)
            name = raw_name.strip()

            if name and len(name) > 3 and not any(kw in name.lower() for kw in ['docentes', 'programa', 'membro', 'home']):
                seen_emails.add(email)
                records.append({
                    "nome": name,
                    "email": email,
                    "setor": "IPRJ - Instituto Politécnico (Nova Friburgo)",
                    "departamento": "PPGMC - Programa de Pós-Graduação em Modelagem Computacional",
                    "laboratorio": "LABTRAN / Supercomputador Escola de Sagres / LME",
                    "fonte_url": lattes_url,
                    "raw_text": text
                })
    return records

def scrape_gesar():
    gesar_members = [
        {
            "nome": "Norberto Mangiavacchi",
            "email": "norberto@uerj.br",
            "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
            "departamento": "MECAN - Departamento de Engenharia Mecânica / PPGEM",
            "laboratorio": "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
            "fonte_url": "https://www.gesar.uerj.br/equipe/equipe-gesar.html",
            "raw_text": "GESAR CFD Simulação Termofluidodinâmica"
        },
        {
            "nome": "José da Rocha Miranda Pontes",
            "email": "jose.pontes@uerj.br",
            "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
            "departamento": "MECAN - Departamento de Engenharia Mecânica / PPGEM",
            "laboratorio": "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
            "fonte_url": "https://www.gesar.uerj.br/equipe/equipe-gesar.html",
            "raw_text": "GESAR CFD Simulação Termofluidodinâmica"
        },
        {
            "nome": "Daniel J. N. M. Chalhub",
            "email": "daniel.chalhub@eng.uerj.br",
            "setor": "FEN - Faculdade de Engenharia (Campus Maracanã)",
            "departamento": "MECAN - Departamento de Engenharia Mecânica / FABLAB / PPGEM",
            "laboratorio": "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
            "fonte_url": "https://www.gesar.uerj.br/equipe/equipe-gesar.html",
            "raw_text": "GESAR CFD Prototipagem FABLAB Manufatura Aditiva"
        }
    ]
    return gesar_members

def scrape_compmat():
    url = "https://ccomp.ime.uerj.br/corpo-docente-mestrado-e-doutorado/"
    html = fetch(url)
    records = []
    if not html:
        return records

    soup = BeautifulSoup(html, 'html.parser')
    seen_emails = set()

    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) >= 2:
            cell_text = tds[1].get_text(' ', strip=True)
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', cell_text)
            if emails:
                email = emails[0].lower().strip()
                if email in seen_emails:
                    continue

                lattes_url = "https://ccomp.ime.uerj.br/corpo-docente-mestrado-e-doutorado/"
                for a in tds[1].find_all('a', href=True):
                    if 'lattes.cnpq.br' in a['href']:
                        lattes_url = a['href']
                        break

                raw_name = cell_text.split(email)[0].strip()
                raw_name = re.sub(r'^(Prof\.?|Dr\.?|D\.Sc\.?|Dra\.?)\s*', '', raw_name, flags=re.IGNORECASE)
                name = raw_name.strip()

                if name and len(name) > 3:
                    seen_emails.add(email)
                    records.append({
                        "nome": name,
                        "email": email,
                        "setor": "IME - Instituto de Matemática e Estatística (Campus Maracanã)",
                        "departamento": "PPG-COMPMAT - Pós-Graduação em Ciências Computacionais e Modelagem Matemática",
                        "laboratorio": "Laboratório de Computação Científica e Métodos Numéricos (IME)",
                        "fonte_url": lattes_url,
                        "raw_text": cell_text + " " + tds[2].get_text(' ', strip=True) if len(tds) > 2 else cell_text
                    })
    return records

def scrape_inovuerj():
    records = [
        {
            "nome": "Israel Felzenszwalb",
            "email": "inovuerj@sr2.uerj.br",
            "setor": "PR2 - Pró-Reitoria de Pós-Graduação e Pesquisa",
            "departamento": "DIRPI - Diretoria de Pesquisa e Inovação",
            "laboratorio": "InovUerj / DEPINOVA - Departamento de Inovação",
            "fonte_url": "https://www.pr2.uerj.br/?page_id=250",
            "raw_text": "Inovação Propriedade Intelectual Transferência Tecnológica"
        },
        {
            "nome": "Marcos Fonteles Viana",
            "email": "serad@sr2.uerj.br",
            "setor": "PR2 - Pró-Reitoria de Pós-Graduação e Pesquisa",
            "departamento": "DEPINOVA - Departamento de Inovação",
            "laboratorio": "InovUerj / Escritório de Propriedade Intelectual (EPI)",
            "fonte_url": "https://www.pr2.uerj.br/?page_id=250",
            "raw_text": "Inovação Propriedade Intelectual Patentes"
        },
        {
            "nome": "Pedro Trajano Cardoso",
            "email": "inovuerj@sr2.uerj.br",
            "setor": "PR2 - Pró-Reitoria de Pós-Graduação e Pesquisa",
            "departamento": "DEPINOVA - Departamento de Inovação",
            "laboratorio": "InovUerj / Escritório de Projetos e Parcerias",
            "fonte_url": "https://www.pr2.uerj.br/?page_id=250",
            "raw_text": "Projetos Parcerias Universidade Empresa"
        },
        {
            "nome": "Mercedes de Oliveira Neto",
            "email": "depesq@sr2.uerj.br",
            "setor": "PR2 - Pró-Reitoria de Pós-Graduação e Pesquisa",
            "departamento": "DEPPESQ - Departamento de Pesquisa",
            "laboratorio": "Diretoria de Pesquisa / Fomento P&D",
            "fonte_url": "https://www.pr2.uerj.br/?page_id=496",
            "raw_text": "Fomento Pesquisa Grupos de Pesquisa"
        }
    ]
    return records

if __name__ == "__main__":
    print("Scraping PPGMC...")
    ppgmc = scrape_ppgmc()
    print(f"PPGMC count: {len(ppgmc)}")

    print("Scraping GESAR...")
    gesar = scrape_gesar()
    print(f"GESAR count: {len(gesar)}")

    print("Scraping PPG-COMPMAT...")
    compmat = scrape_compmat()
    print(f"PPG-COMPMAT count: {len(compmat)}")

    print("Scraping InovUerj...")
    inov = scrape_inovuerj()
    print(f"InovUerj count: {len(inov)}")
