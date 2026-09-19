import requests
import json
import re
import urllib3
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def scrape_fen():
    print("Scraping FEN Maracanã...")
    results = []
    # FEN departments list
    # We can fetch https://www.eng.uerj.br/alocadepto/ or query deptos directly
    # In FEN, department contact pages/lists:
    dept_urls = [
        ("MECAN", "https://www.eng.uerj.br/deptos/mecanica.php"),
        ("DEEL", "https://www.eng.uerj.br/deptos/eletronica.php"),
        ("DEPRO", "https://www.eng.uerj.br/deptos/producao.php"),
        ("DEQ", "https://www.eng.uerj.br/deptos/quimica.php"),
        ("Civil", "https://www.eng.uerj.br/deptos/civil.php")
    ]

    # Also fetch general professor list
    try:
        r = requests.get("https://www.eng.uerj.br/professor/", headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        # look for tables, links, or options
        for a in soup.find_all('a', href=True):
            if 'prof' in a['href'] or 'docente' in a['href']:
                pass
    except Exception as e:
        print(f"Error FEN main: {e}")

    # Broad search across eng.uerj.br pages
    for dept_name, url in dept_urls:
        try:
            r = requests.get(url, headers=headers, verify=False, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                text = soup.get_text()
                # find emails
                emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@eng\.uerj\.br|[a-zA-Z0-9._%+-]+@uerj\.br', text))
                results.append({"dept": dept_name, "url": url, "emails": list(emails), "raw_text": text[:2000]})
        except Exception as e:
            print(f"Error {dept_name}: {e}")

    return results

def scrape_iprj():
    print("Scraping IPRJ Nova Friburgo...")
    results = []
    urls = [
        "https://www.iprj.uerj.br/docentes/",
        "https://www.ppgmc.uerj.br/docentes",
        "https://www.iprj.uerj.br/departamentos/"
    ]
    for url in urls:
        try:
            r = requests.get(url, headers=headers, verify=False, timeout=15)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                # PPGMC/IPRJ faculty cards
                cards = soup.find_all(['div', 'tr', 'p', 'article'])
                for card in cards:
                    text = card.get_text(separator=" ").strip()
                    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                    if 'LATTES' in text or 'Lattes' in text or emails:
                        # try to find name
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        if lines:
                            results.append({
                                "source": url,
                                "raw_lines": lines[:10],
                                "emails": emails,
                                "text": text
                            })
        except Exception as e:
            print(f"Error IPRJ {url}: {e}")
    return results

def scrape_fat():
    print("Scraping FAT Resende...")
    results = []
    urls = [
        "https://www.fat.uerj.br/grupos-de-pesquisa-no-cnpq/",
        "https://www.fat.uerj.br/curso/engenharia-mecanica/",
        "https://www.fat.uerj.br/posgraduacao/"
    ]
    for url in urls:
        try:
            r = requests.get(url, headers=headers, verify=False, timeout=15)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                text = soup.get_text(separator=" ")
                emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@fat\.uerj\.br|[a-zA-Z0-9._%+-]+@uerj\.br', text))
                results.append({"url": url, "emails": list(emails), "text_sample": text[:3000]})
        except Exception as e:
            print(f"Error FAT {url}: {e}")
    return results

def scrape_ime():
    print("Scraping IME Maracanã...")
    results = []
    urls = [
        "https://www.ime.uerj.br/professores/",
        "https://www.ime.uerj.br/departamentos/",
        "https://www.ime.uerj.br/pos-graduacao/"
    ]
    for url in urls:
        try:
            r = requests.get(url, headers=headers, verify=False, timeout=15)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                text = soup.get_text(separator=" ")
                emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@ime\.uerj\.br|[a-zA-Z0-9._%+-]+@uerj\.br', text))
                results.append({"url": url, "emails": list(emails), "text_sample": text[:3000]})
        except Exception as e:
            print(f"Error IME {url}: {e}")
    return results

def scrape_gesar():
    print("Scraping GESAR...")
    results = []
    urls = [
        "https://www.gesar.uerj.br/",
        "https://www.gesar.uerj.br/labs/laboratorios.html",
        "https://www.gesar.uerj.br/pesquisa/pesquisa-gesar.html"
    ]
    for url in urls:
        try:
            r = requests.get(url, headers=headers, verify=False, timeout=15)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                text = soup.get_text(separator=" ")
                emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))
                results.append({"url": url, "emails": list(emails), "text_sample": text[:3000]})
        except Exception as e:
            print(f"Error GESAR {url}: {e}")
    return results

if __name__ == '__main__':
    raw_data = {
        "fen": scrape_fen(),
        "iprj": scrape_iprj(),
        "fat": scrape_fat(),
        "ime": scrape_ime(),
        "gesar": scrape_gesar()
    }
    with open("uerj_raw_crawl.json", "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)
    print("Crawl complete. Raw output saved to uerj_raw_crawl.json")
