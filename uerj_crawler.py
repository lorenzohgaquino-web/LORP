import urllib.request
import ssl
from bs4 import BeautifulSoup
import re
import json
import time
from concurrent.futures import ThreadPoolExecutor

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def fetch_url(url, retries=2):
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            res = urllib.request.urlopen(req, context=ctx, timeout=15)
            html = res.read().decode('utf-8', errors='ignore')
            return html
        except Exception as e:
            if attempt == retries:
                print(f"Error fetching {url}: {e}")
                return None
            time.sleep(0.5)

def crawl_fen():
    print("Crawling FEN (Maracanã)...")
    url_index = "http://www.eng.uerj.br/prof/"
    html = fetch_url(url_index)
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    prof_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/prof/' in href:
            if not href.startswith('http'):
                href = "http://www.eng.uerj.br" + href if href.startswith('/') else "http://www.eng.uerj.br/prof/" + href
            prof_links.append((a.text.strip(), href))

    # Deduplicate prof links
    prof_links = list(set(prof_links))
    print(f"Found {len(prof_links)} unique professor links in FEN index.")

    results = []
    def scrape_fen_prof(item):
        name, url = item
        p_html = fetch_url(url)
        if not p_html:
            return None
        p_soup = BeautifulSoup(p_html, 'html.parser')
        text = p_soup.get_text(strip=True, separator=' | ')

        # Parse Dept
        dept = "FEN - Maracanã"
        if "Depto.: | " in text:
            dept_part = text.split("Depto.: | ")[1].split(" | ")[0]
            dept = f"FEN/{dept_part} - Maracanã"
        elif "Depto.:" in text:
            dept_part = text.split("Depto.:")[1].split("|")[0].strip()
            dept = f"FEN/{dept_part} - Maracanã"

        # Emails
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', p_html)

        # Extract title/degree
        title = ""
        if "PROFESSOR:" in text:
            prof_info = text.split("PROFESSOR:")[1].split("Depto.:")[0]
            title = prof_info.strip()

        return {
            "name": name,
            "url": url,
            "dept": dept,
            "emails": list(set(emails)),
            "bio": text[:1500],
            "title": title,
            "unit": "FEN Maracanã"
        }

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(scrape_fen_prof, item) for item in prof_links]
        for f in futures:
            res = f.result()
            if res:
                results.append(res)

    return results

def crawl_iprj_ppgmc():
    print("Crawling IPRJ & PPGMC (Nova Friburgo)...")
    results = []

    # 1. PPGMC Docentes
    ppgmc_url = "https://www.ppgmc.uerj.br/docentes"
    html = fetch_url(ppgmc_url)
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        results.append({
            "raw_text": text,
            "emails": list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html))),
            "source": ppgmc_url,
            "unit": "IPRJ / PPGMC - Nova Friburgo"
        })

    # 2. IPRJ Docentes general
    iprj_url = "http://www.iprj.uerj.br/docentes"
    i_html = fetch_url(iprj_url)
    if i_html:
        i_soup = BeautifulSoup(i_html, 'html.parser')
        i_text = i_soup.get_text(separator='\n', strip=True)
        results.append({
            "raw_text": i_text,
            "emails": list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', i_html))),
            "source": iprj_url,
            "unit": "IPRJ Nova Friburgo"
        })

    return results

def crawl_fat():
    print("Crawling FAT (Resende)...")
    results = []
    fat_url = "https://www.fat.uerj.br/dptos"
    html = fetch_url(fat_url)
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        results.append({
            "raw_text": text,
            "emails": list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html))),
            "source": fat_url,
            "unit": "FAT Resende"
        })

    for course_slug in ['engenharia-mecanica', 'engenharia-de-producao', 'engenharia-quimica', 'engenharia-computacional']:
        c_url = f"https://www.fat.uerj.br/curso/{course_slug}/"
        chtml = fetch_url(c_url)
        if chtml:
            csoup = BeautifulSoup(chtml, 'html.parser')
            ctext = csoup.get_text(separator='\n', strip=True)
            results.append({
                "raw_text": ctext,
                "emails": list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', chtml))),
                "source": c_url,
                "unit": f"FAT Resende - {course_slug}"
            })

    return results

def crawl_inovuerj():
    print("Crawling InovUerj / DEPINOVA...")
    results = []
    depinova_url = "https://www.pr2.uerj.br/?page_id=510"
    html = fetch_url(depinova_url)
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        results.append({
            "raw_text": text,
            "emails": list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html))),
            "source": depinova_url,
            "unit": "InovUerj / DEPINOVA - PR2"
        })
    return results

def main():
    fen_data = crawl_fen()
    iprj_data = crawl_iprj_ppgmc()
    fat_data = crawl_fat()
    inov_data = crawl_inovuerj()

    all_raw = {
        "fen": fen_data,
        "iprj_ppgmc": iprj_data,
        "fat": fat_data,
        "inovuerj": inov_data
    }

    with open("raw_uerj_scraped.json", "w", encoding="utf-8") as f:
        json.dump(all_raw, f, ensure_ascii=False, indent=2)

    print(f"Scraping finished. Saved {len(fen_data)} FEN records + unit pages to raw_uerj_scraped.json")

if __name__ == "__main__":
    main()
