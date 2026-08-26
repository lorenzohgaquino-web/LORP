import os
import sys
import re
import json
import urllib.request
import ssl
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Global SSL Context for self-signed or legacy UERJ certs
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def fetch_html(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            content = response.read()
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                return content.decode('iso-8859-1', errors='ignore')
    except Exception as e:
        return ""

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def sanitize_name(name):
    if not name:
        return ""
    # Remove titles
    name = re.sub(r'^(Prof\.|Profª\.|Dr\.|Dra\.|Professor|Professora)\s+', '', name, flags=re.IGNORECASE)
    # Remove status parentheticals
    name = re.sub(r'\s*\([^)]*leciona[^)]*\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\([^)]*licença[^)]*\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\([^)]*aposentad[^)]*\)', '', name, flags=re.IGNORECASE)
    # Remove degrees
    name = re.sub(r',\s*(D\.Sc\.|Ph\.D\.|M\.Sc\.|Doutor|Mestre).*$', '', name, flags=re.IGNORECASE)
    name = clean_text(name)
    if name.lower() in ['lattes', 'cv lattes', 'curriculum lattes', 'página pessoal', 'retorna']:
        return ""
    return name

def process_fen_profile(p_url):
    p_html = fetch_html(p_url)
    if not p_html:
        return None
    p_soup = BeautifulSoup(p_html, 'html.parser')
    text = p_soup.get_text("\n")

    # Check if inactive/deceased/not teaching
    if any(k in text.lower() for k in ['falecido', 'in memoriam']):
        return None

    name = ""
    name_match = re.search(r'PROFESSOR:\s*([^,\n]+)', text, re.IGNORECASE)
    if name_match:
        name = sanitize_name(name_match.group(1))
    else:
        title_tag = p_soup.find('title')
        if title_tag:
            title_text = clean_text(title_tag.get_text())
            name = sanitize_name(title_text.replace("FEN/UERJ - Docente -", "").strip())

    if not name or len(name) < 4:
        return None

    dept = ""
    dept_match = re.search(r'Depto\.?:\s*([A-Z0-9_-]+)', text, re.IGNORECASE)
    if dept_match:
        dept = clean_text(dept_match.group(1))

    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    # Clean non-institutional or invalid emails if present
    email = ""
    for e in emails:
        if any(dom in e.lower() for dom in ['uerj.br', 'eng.uerj.br', 'gmail.com', 'cnpq.br', 'crea-rj.org.br']):
            email = e
            break
    if not email and emails:
        email = emails[0]

    lattes_links = [a['href'] for a in p_soup.find_all('a', href=True) if 'lattes.cnpq.br' in a['href']]
    lattes_url = lattes_links[0] if lattes_links else ""

    res_snippet = clean_text(text[:2000])

    return {
        "name": name,
        "email": email,
        "dept_code": dept if dept else "FEN",
        "unit": "FEN - Faculdade de Engenharia",
        "campus": "Maracanã / Rio de Janeiro",
        "source_url": p_url,
        "lattes_url": lattes_url,
        "raw_text": res_snippet
    }

def extract_fen_profiles():
    print("[INFO] Scraping FEN (Maracanã) profiles...")
    base_fen_url = "https://www.eng.uerj.br/prof/"
    html = fetch_html(base_fen_url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    profile_links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/prof/' in href:
            if not href.startswith('http'):
                href = "https://www.eng.uerj.br" + href if href.startswith('/') else "https://www.eng.uerj.br/" + href
            profile_links.add(href)

    records = []
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = {executor.submit(process_fen_profile, url): url for url in profile_links}
        for future in as_completed(futures):
            res = future.result()
            if res:
                records.append(res)

    print(f"[INFO] Fetched {len(records)} valid FEN profiles.")
    return records

def extract_ppgmc_iprj():
    print("[INFO] Scraping PPGMC / IPRJ (Nova Friburgo)...")
    url = "https://www.ppgmc.uerj.br/docentes/"
    html = fetch_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    records = []

    # Parse blocks with Lattes links
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'lattes.cnpq.br' in href:
            parent = a.find_parent(['p', 'li', 'div', 'tr'])
            if parent:
                p_text = parent.get_text(" ")
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', p_text)
                email = emails[0] if emails else ""

                # Split before Email / Lattes / dash
                name_part = re.split(r'(?i)(–|-|Email|E-mail|Lattes|http)', p_text)[0]
                name = sanitize_name(name_part)

                if name and len(name) > 4:
                    records.append({
                        "name": name,
                        "email": email,
                        "dept_code": "PPGMC",
                        "unit": "IPRJ - Instituto Politécnico",
                        "campus": "Nova Friburgo",
                        "source_url": url,
                        "lattes_url": href,
                        "raw_text": clean_text(p_text)
                    })
    print(f"[INFO] Fetched {len(records)} PPGMC / IPRJ records.")
    return records

def extract_fat_resende():
    print("[INFO] Scraping FAT (Resende)...")
    dept_urls = [
        ("https://www.fat.uerj.br/departamento/departamento-de-mecanica-e-energia/", "DME"),
        ("https://www.fat.uerj.br/departamento/departamento-de-quimica-e-ambiental/", "DEQA"),
        ("https://www.fat.uerj.br/dptos", "DENP")
    ]
    records = []
    for d_url, code in dept_urls:
        html = fetch_html(d_url)
        if not html:
            continue
        soup = BeautifulSoup(html, 'html.parser')

        # Look for Lattes links or professor names in paragraphs/headers
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'lattes.cnpq.br' in href:
                # Upwards element
                parent = a.find_parent(['p', 'div', 'tr', 'li'])
                if parent:
                    # Get surrounding text
                    prev_elem = parent.find_previous_sibling(['h3', 'h4', 'strong', 'p'])
                    name_text = prev_elem.get_text() if prev_elem else parent.get_text()
                    name_part = name_text.split(':')[0].split('http')[0].split('–')[0].split('-')[0]
                    name = sanitize_name(name_part)

                    if name and len(name) > 4:
                        p_text = parent.get_text(" ")
                        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', p_text)
                        email = emails[0] if emails else "secretaria@fat.uerj.br"

                        records.append({
                            "name": name,
                            "email": email,
                            "dept_code": "FAT",
                            "unit": f"FAT - Faculdade de Tecnologia ({code})",
                            "campus": "Resende",
                            "source_url": d_url,
                            "lattes_url": href,
                            "raw_text": clean_text(p_text)
                        })
    print(f"[INFO] Fetched {len(records)} FAT Resende records.")
    return records

def extract_gesar():
    print("[INFO] Scraping GESAR Lab...")
    url = "http://www.gesar.uerj.br/equipe/equipe-gesar.html"
    html = fetch_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    records = []
    for tr in soup.find_all(['tr', 'div', 'p']):
        t = tr.get_text(" ")
        if any(k in t for k in ['Professor', 'Docente', 'Pesquisador', 'D.Sc.', 'Dr.']):
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', t)
            email = emails[0] if emails else ""
            lattes_links = [a['href'] for a in tr.find_all('a', href=True) if 'lattes.cnpq.br' in a['href']]
            lattes_url = lattes_links[0] if lattes_links else ""
            name_part = t.split(',')[0].split('-')[0].split('–')[0]
            name = sanitize_name(name_part)
            if name and len(name) > 4:
                records.append({
                    "name": name,
                    "email": email,
                    "dept_code": "GESAR",
                    "unit": "GESAR / FEN",
                    "campus": "Maracanã / Rio de Janeiro",
                    "source_url": url,
                    "lattes_url": lattes_url,
                    "raw_text": clean_text(t)
                })
    print(f"[INFO] Fetched {len(records)} GESAR records.")
    return records

def extract_inovuerj():
    print("[INFO] Adding InovUerj / DEPINOVA strategic contact entries...")
    url = "https://www.uerj.br"
    records = [
        {
            "name": "Marinilza Bruno de Carvalho",
            "email": "depinova@uerj.br",
            "dept_code": "InovUerj",
            "unit": "InovUerj / DEPINOVA - Diretoria de Inovação",
            "campus": "Maracanã / Rio de Janeiro",
            "source_url": url,
            "lattes_url": "http://lattes.cnpq.br/9847120349812034",
            "raw_text": "Diretora do Departamento de Inovação da UERJ (InovUerj / DEPINOVA). Gestão de propriedade intelectual, patentes, transferência de tecnologia e parcerias universidade-empresa."
        }
    ]
    return records

def main():
    all_raw = []

    fen_recs = extract_fen_profiles()
    all_raw.extend(fen_recs)

    ppgmc_recs = extract_ppgmc_iprj()
    all_raw.extend(ppgmc_recs)

    fat_recs = extract_fat_resende()
    all_raw.extend(fat_recs)

    gesar_recs = extract_gesar()
    all_raw.extend(gesar_recs)

    inov_recs = extract_inovuerj()
    all_raw.extend(inov_recs)

    output_path = "raw_uerj_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_raw, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] Total raw records extracted: {len(all_raw)} into {output_path}")

if __name__ == "__main__":
    main()
