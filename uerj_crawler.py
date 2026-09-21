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

def fetch_html(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        return urllib.request.urlopen(req, context=ctx, timeout=timeout).read().decode('utf-8', errors='ignore')
    except Exception as e:
        return ""

def process_fen_prof(item):
    name, link = item
    prof_html = fetch_html(link)
    if not prof_html:
        return None
    psoup = BeautifulSoup(prof_html, 'html.parser')
    text = psoup.get_text()

    dept_match = re.search(r'Depto\.\s*:\s*([A-Z0-9_-]+)', text)
    dept = dept_match.group(1).strip() if dept_match else "FEN - Geral"

    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', prof_html)
    valid_emails = [e for e in emails if not e.endswith('uerj.br/prof/') and ('eng.uerj.br' in e or 'uerj.br' in e or 'gmail.com' in e or 'crea-rj.org.br' in e)]
    email = valid_emails[0] if valid_emails else ""

    lattes_a = psoup.find('a', href=re.compile(r'lattes\.cnpq\.br'))
    lattes = lattes_a['href'] if lattes_a else link

    clean_name = re.sub(r'^(Prof\.|Profa\.|Profª\.|Dr\.|Dra\.|Eng\.)\s*', '', name, flags=re.IGNORECASE).strip()

    return {
        "nome": clean_name,
        "email": email,
        "setor_departamento_campus": f"FEN/{dept} - Maracanã",
        "laboratorio_grupo": "Faculdade de Engenharia (FEN/UERJ)",
        "resumo_lattes": text[:500].replace('\n', ' ').strip(),
        "url_fonte": link,
        "lattes_url": lattes
    }

def crawl_fen():
    print("Crawling FEN Maracanã...")
    results = []
    base_url = "https://www.eng.uerj.br/prof/"
    html = fetch_html(base_url)
    if not html:
        return results

    soup = BeautifulSoup(html, 'html.parser')
    prof_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/prof/' in href and href != base_url:
            prof_links.append((a.get_text(strip=True), href))

    seen_links = set()
    unique_links = []
    for name, link in prof_links:
        if link not in seen_links:
            seen_links.add(link)
            unique_links.append((name, link))

    print(f"Found {len(unique_links)} professor links in FEN.")

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_fen_prof, item) for item in unique_links]
        for f in as_completed(futures):
            res = f.result()
            if res:
                results.append(res)
    return results

def process_iprj_prof(item):
    name, link = item
    p_html = fetch_html(link)
    if not p_html:
        return None
    psoup = BeautifulSoup(p_html, 'html.parser')
    text = psoup.get_text()
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', p_html)
    email = emails[0] if emails else ""

    lattes_a = psoup.find('a', href=re.compile(r'lattes\.cnpq\.br'))
    lattes = lattes_a['href'] if lattes_a else link

    clean_name = re.sub(r'^(Prof\.|Profa\.|Profª\.|Dr\.|Dra\.|Eng\.)\s*', '', name, flags=re.IGNORECASE).strip()

    # Check department in category
    dept = "IPRJ"
    if "DEMEC" in text or "demec" in link.lower():
        dept = "IPRJ/DEMEC"
    elif "DMC" in text or "dmc" in link.lower():
        dept = "IPRJ/DMC"
    elif "DEMAT" in text or "demat" in link.lower():
        dept = "IPRJ/DEMAT"

    return {
        "nome": clean_name,
        "email": email,
        "setor_departamento_campus": f"{dept} - Nova Friburgo",
        "laboratorio_grupo": "Instituto Politécnico (IPRJ / PPGMC)",
        "resumo_lattes": text[:500].replace('\n', ' ').strip(),
        "url_fonte": link,
        "lattes_url": lattes
    }

def crawl_iprj():
    print("Crawling IPRJ Nova Friburgo...")
    results = []
    url = "https://www.iprj.uerj.br/docentes/"
    html = fetch_html(url)
    if not html:
        return results

    soup = BeautifulSoup(html, 'html.parser')
    prof_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'iprj.uerj.br/' in href and not any(x in href for x in ['/category/', '/tag/', '/mecanica/', '/docentes/', '/feed/']):
            text = a.get_text(strip=True)
            if len(text) > 3 and not text.startswith('Graduação') and not text.startswith('Pós-Graduação'):
                prof_links.append((text, href))

    seen_links = set()
    unique_links = []
    for name, link in prof_links:
        if link not in seen_links:
            seen_links.add(link)
            unique_links.append((name, link))

    print(f"Found {len(unique_links)} professor links in IPRJ.")

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_iprj_prof, item) for item in unique_links]
        for f in as_completed(futures):
            res = f.result()
            if res:
                results.append(res)
    return results

def crawl_ime_ccomp():
    print("Crawling IME PPG-COMPMAT...")
    results = []
    url = "https://ccomp.ime.uerj.br/corpo-docente-mestrado-e-doutorado/"
    html = fetch_html(url)
    if not html:
        return results

    soup = BeautifulSoup(html, 'html.parser')
    for p in soup.find_all(['p', 'li']):
        text = p.get_text(strip=True)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        a_lattes = p.find('a', href=re.compile(r'lattes\.cnpq\.br'))
        if a_lattes or emails or ('Prof' in text and ('D.Sc' in text or 'Dr' in text or 'Ph.D' in text)):
            lattes = a_lattes['href'] if a_lattes else url
            clean_name = text.split('–')[0].split('-')[0].split('(')[0].strip()
            clean_name = re.sub(r'^(Prof\.|Profa\.|Profª\.|Dr\.|Dra\.|Eng\.)\s*', '', clean_name, flags=re.IGNORECASE).strip()
            if len(clean_name) > 5 and len(clean_name) < 60:
                results.append({
                    "nome": clean_name,
                    "email": emails[0] if emails else "",
                    "setor_departamento_campus": "IME/PPG-COMPMAT - Maracanã",
                    "laboratorio_grupo": "Ciências Computacionais e Modelagem Matemática",
                    "resumo_lattes": text,
                    "url_fonte": url,
                    "lattes_url": lattes
                })
    return results

if __name__ == "__main__":
    fen_data = crawl_fen()
    iprj_data = crawl_iprj()
    ime_data = crawl_ime_ccomp()

    all_raw = fen_data + iprj_data + ime_data
    with open('raw_crawled_uerj.json', 'w', encoding='utf-8') as f:
        json.dump(all_raw, f, ensure_ascii=False, indent=2)
    print(f"Crawl finished. Saved {len(all_raw)} total raw records.")
