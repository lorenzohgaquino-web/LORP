import requests
import json
import re
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=12)
        if r.status_code == 200:
            return r.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return ""

def crawl_gesar():
    print("Crawling GESAR...")
    html = fetch("http://www.gesar.uerj.br/equipe/equipe-gesar.html")
    soup = BeautifulSoup(html, 'html.parser')
    members = []

    # Each member is inside div or block
    for mailto in soup.find_all('a', href=re.compile(r'mailto:')):
        email = mailto['href'].replace('mailto:', '').strip()
        # Find name and lattes in parent/ancestor
        parent = mailto.parent
        for _ in range(5):
            if parent and parent.parent:
                parent = parent.parent

        text = parent.get_text() if parent else ""
        lattes = parent.find('a', href=re.compile(r'lattes\.cnpq\.br'))
        lattes_url = lattes['href'] if lattes else ""

        # Name
        h3 = parent.find(['h2', 'h3', 'h4', 'strong', 'b'])
        name = h3.get_text(strip=True) if h3 else ""

        members.append({
            "nome": name,
            "email": email,
            "lattes": lattes_url,
            "unidade": "CTC / FEN / GESAR",
            "departamento": "MECAN",
            "lab": "GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais)",
            "source": "http://www.gesar.uerj.br/equipe/equipe-gesar.html"
        })
    print(f"GESAR members: {len(members)}")
    return members

def crawl_ppgmc():
    print("Crawling PPGMC...")
    html = fetch("https://www.ppgmc.uerj.br/docentes/")
    soup = BeautifulSoup(html, 'html.parser')

    # PPGMC lists name, email, lattes
    text = soup.get_text('\n')
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    records = []
    # Pattern matching in PPGMC: Name followed by email and LATTES link
    # Let's inspect soup directly for structured divs or paragraphs
    for p in soup.find_all(['p', 'div']):
        p_text = p.get_text(' ')
        if '@' in p_text and 'LATTES' in p_text:
            lattes_a = p.find('a', href=re.compile(r'lattes\.cnpq\.br'))
            if lattes_a:
                lattes_url = lattes_a['href']
                # extract name and email
                email_m = re.search(r'([\w\.-]+@[\w\.-]+\.\w+)', p_text)
                email = email_m.group(1) if email_m else ""

                # Name is before email
                before_email = p_text.split(email)[0] if email else p_text
                # Clean title / prof
                before_email = re.sub(r'Prof\.|Colaborador|Visitante|Docentes|Home.*Docentes', '', before_email).strip()
                # Extract uppercase name
                name_m = re.search(r'([A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]{6,50})', before_email)
                name = name_m.group(1).strip() if name_m else before_email.strip()

                if name and email and not any(r['email'] == email for r in records):
                    records.append({
                        "nome": name,
                        "email": email,
                        "lattes": lattes_url,
                        "unidade": "IPRJ Nova Friburgo",
                        "departamento": "PPGMC",
                        "lab": "Laboratório de Modelagem Computacional / IPRJ",
                        "source": "https://www.ppgmc.uerj.br/docentes/"
                    })
    print(f"PPGMC records: {len(records)}")
    return records

if __name__ == "__main__":
    gesar = crawl_gesar()
    ppgmc = crawl_ppgmc()
    print("GESAR sample:", gesar)
    print("PPGMC sample count:", len(ppgmc))
