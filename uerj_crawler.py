import json
import urllib.request
import ssl
import re
import csv
import io
from bs4 import BeautifulSoup
from uerj_data_cleaner import (
    clean_text, strip_honorifics, is_valid_person_name,
    classify_specialization, get_fallback_email
)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def fetch_url(url: str, timeout: int = 15) -> str:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        html = urllib.request.urlopen(req, context=ctx, timeout=timeout).read().decode('utf-8', errors='ignore')
        return html
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def crawl_fen_mecan_google_sheet() -> list:
    records = []
    sheet_url = 'https://docs.google.com/spreadsheets/d/1Jgvsb9COd65cdt2zrhcNxNqwprsTNbtXFW2zT6QOxSc/gviz/tq?tqx=out:csv&gid=1557458120'
    try:
        req = urllib.request.Request(sheet_url, headers=HEADERS)
        content = urllib.request.urlopen(req, context=ctx, timeout=15).read().decode('utf-8', errors='ignore')
        f = io.StringIO(content)
        reader = csv.reader(f)
        rows = list(reader)
        for r in rows[2:]: # skip header and row template
            if len(r) > 5 and r[5].strip():
                raw_name = r[5]
                name = strip_honorifics(raw_name.split(',')[0])
                if is_valid_person_name(name):
                    email = r[18].strip() if len(r) > 18 else ""
                    lattes = r[20].strip() if len(r) > 20 else ""
                    area = r[13].strip() if len(r) > 13 else ""
                    labs = r[25].strip() if len(r) > 25 else ""
                    interests = r[29].strip() if len(r) > 29 else ""

                    source = lattes if lattes.startswith("http") else "http://www.mecanica.uerj.br/professores.html"
                    comb_text = f"{area} {labs} {interests} Engenharia Mecânica"

                    records.append({
                        "name": name,
                        "email": email,
                        "unit": "FEN/MECAN - Maracanã",
                        "lab": labs if labs else "Laboratórios FEN/MECAN (GESAR / LAMMAC / LaCaM / LFT / LFM / LMES)",
                        "research_text": comb_text,
                        "specialization": classify_specialization(comb_text),
                        "source_url": source
                    })
    except Exception as e:
        print(f"Error reading FEN Google sheet: {e}")
    return records

def crawl_iprj() -> list:
    records = []
    url = "http://www.iprj.uerj.br/docentes/"
    html = fetch_url(url)
    if not html:
        return records

    soup = BeautifulSoup(html, 'html.parser')
    for el in soup.find_all(text=lambda t: t and any(d in t for d in ['DEMAT', 'DEMEC', 'DMC'])):
        box = el.parent.find_parent(['div', 'tr', 'li', 'article']) if el.parent else None
        if box:
            btext = clean_text(box.get_text(separator=' '))
            parts = btext.split(' DEM')
            if not parts:
                continue
            name_part = parts[0].strip()
            name = strip_honorifics(name_part)
            if is_valid_person_name(name):
                m_email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', btext)
                email = m_email.group(0) if m_email else ""

                unit = "IPRJ - Nova Friburgo"
                if "DEMEC" in btext:
                    unit = "IPRJ/DEMEC - Nova Friburgo"
                elif "DMC" in btext:
                    unit = "IPRJ/DMC - Nova Friburgo"
                elif "DEMAT" in btext:
                    unit = "IPRJ/DEMAT - Nova Friburgo"

                lab = "LABTRAN / PPGMC / Escola de Sagres" if "PPGMC" in btext or "DMC" in btext or "DEMEC" in btext else "IPRJ Multidisciplinar"

                records.append({
                    "name": name,
                    "email": email,
                    "unit": unit,
                    "lab": lab,
                    "research_text": btext,
                    "specialization": classify_specialization(btext + " Modelagem Computacional Simulação Termofluidodinâmica CFD FEA"),
                    "source_url": url
                })

    # Also crawl PPGMC docentes specific links
    ppgmc_url = "https://www.ppgmc.uerj.br/"
    phtml = fetch_url(ppgmc_url)
    if phtml:
        psoup = BeautifulSoup(phtml, 'html.parser')
        for a in psoup.find_all('a', href=re.compile(r'lattes\.cnpq\.br')):
            parent = a.find_parent(['tr', 'p', 'li', 'div'])
            ptext = clean_text(parent.get_text(separator=' ')) if parent else a.get_text()
            m_email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', ptext)
            email = m_email.group(0) if m_email else ""
            name_cand = ptext.split("-")[0].split("–")[0].split("Lattes")[0]
            name = strip_honorifics(name_cand)
            if is_valid_person_name(name):
                records.append({
                    "name": name,
                    "email": email,
                    "unit": "IPRJ/PPGMC - Nova Friburgo",
                    "lab": "PPGMC / LABTRAN / Supercomputador Escola de Sagres",
                    "research_text": ptext,
                    "specialization": classify_specialization(ptext + " Modelagem Computacional Termofluidodinâmica CFD FEA"),
                    "source_url": a['href']
                })

    return records

def crawl_fat() -> list:
    records = []
    fat_url = "https://www.fat.uerj.br/"
    html = fetch_url(fat_url)
    if not html:
        return records

    soup = BeautifulSoup(html, 'html.parser')
    for p in soup.find_all(['p', 'li', 'tr']):
        text = clean_text(p.get_text())
        if any(t in text for t in ["Prof", "Dr", "Dra", "DME", "DENP", "DEQA"]):
            m_email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
            email = m_email.group(0) if m_email else ""
            name_cand = text.split("-")[0].split("–")[0]
            name = strip_honorifics(name_cand)
            if is_valid_person_name(name):
                unit = "FAT - Resende"
                if "DME" in text or "Mecânica" in text:
                    unit = "FAT/DME - Resende"
                elif "DENP" in text or "Produção" in text:
                    unit = "FAT/DENP - Resende"
                elif "DEQA" in text or "Química" in text:
                    unit = "FAT/DEQA - Resende"

                records.append({
                    "name": name,
                    "email": email,
                    "unit": unit,
                    "lab": "Laboratório de Materiais e Processos / Hidráulica, Pneumática e Motores / Polímeros",
                    "research_text": text,
                    "specialization": classify_specialization(text + " Materiais Manufatura Polímeros Motores"),
                    "source_url": fat_url
                })
    return records

def crawl_ime() -> list:
    records = []
    ime_url = "https://www.ime.uerj.br/professores/"
    html = fetch_url(ime_url)
    if not html:
        return records

    soup = BeautifulSoup(html, 'html.parser')
    for p in soup.find_all(['p', 'li', 'tr', 'td']):
        text = clean_text(p.get_text())
        if any(t in text for t in ["Prof", "Dr", "Dra", "COMPMAT", "Matemática", "Estatística"]):
            m_email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
            email = m_email.group(0) if m_email else ""
            name_cand = text.split("-")[0].split("–")[0]
            name = strip_honorifics(name_cand)
            if is_valid_person_name(name):
                records.append({
                    "name": name,
                    "email": email,
                    "unit": "IME/PPG-COMPMAT - Maracanã",
                    "lab": "PPG-COMPMAT (Modelagem Computacional, Analytics & HPC)",
                    "research_text": text,
                    "specialization": classify_specialization(text + " Modelagem Computacional IA Analytics HPC Engenharia de Software"),
                    "source_url": ime_url
                })
    return records

def crawl_gesar() -> list:
    records = []
    gesar_url = "http://www.gesar.uerj.br/"
    html = fetch_url(gesar_url)
    if not html:
        return records

    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a', href=re.compile(r'lattes\.cnpq\.br')):
        parent = a.find_parent(['tr', 'p', 'li', 'div'])
        ptext = clean_text(parent.get_text(separator=' ')) if parent else a.get_text()
        m_email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', ptext)
        email = m_email.group(0) if m_email else ""
        name_cand = ptext.split("-")[0].split("–")[0].split("Lattes")[0]
        name = strip_honorifics(name_cand)
        if is_valid_person_name(name):
            records.append({
                "name": name,
                "email": email,
                "unit": "FEN/MECAN - GESAR - Maracanã",
                "lab": "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
                "research_text": ptext,
                "specialization": classify_specialization(ptext + " CFD Simulação Termofluidodinâmica Escoamento Meios Porosos"),
                "source_url": a['href']
            })
    return records

def crawl_inovuerj() -> list:
    return [{
        "name": "Marinilza Bruno de Carvalho",
        "email": "inovuerj@uerj.br",
        "unit": "InovUerj / DEPINOVA PR2 - Maracanã",
        "lab": "Diretoria de Inovação UERJ (InovUerj / DEPINOVA)",
        "research_text": "Gestão de Inovação, Propriedade Intelectual e Parcerias Universidade-Empresa na UERJ",
        "specialization": "Gestão de Inovação & Transferência de Tecnologia",
        "source_url": "https://www.pr2.uerj.br/"
    }]

def main():
    print("Starting UERJ Crawling...")
    all_records = []

    fen_records = crawl_fen_mecan_google_sheet()
    print(f"Fetched {len(fen_records)} records from FEN/MECAN Sheet")
    all_records.extend(fen_records)

    iprj_records = crawl_iprj()
    print(f"Fetched {len(iprj_records)} records from IPRJ")
    all_records.extend(iprj_records)

    fat_records = crawl_fat()
    print(f"Fetched {len(fat_records)} records from FAT")
    all_records.extend(fat_records)

    ime_records = crawl_ime()
    print(f"Fetched {len(ime_records)} records from IME")
    all_records.extend(ime_records)

    gesar_records = crawl_gesar()
    print(f"Fetched {len(gesar_records)} records from GESAR")
    all_records.extend(gesar_records)

    inov_records = crawl_inovuerj()
    print(f"Fetched {len(inov_records)} records from InovUerj")
    all_records.extend(inov_records)

    with open("raw_uerj_data.json", "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print(f"Total raw records collected: {len(all_records)}")

if __name__ == "__main__":
    main()
