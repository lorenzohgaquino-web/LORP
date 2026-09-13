import requests
import re
import json
import urllib3
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

def crawl_fen():
    print("Crawling FEN Maracanã...")
    results = []
    try:
        r = requests.get('http://www.eng.uerj.br/prof/', headers=HEADERS, verify=False, timeout=10)
        r.encoding = 'latin1'
        soup = BeautifulSoup(r.text, 'html.parser')
        prof_links = []
        for a in soup.find_all('a'):
            href = a.get('href')
            if href and '/prof/' in href:
                if href.startswith('/'):
                    href = 'http://www.eng.uerj.br' + href
                elif href.startswith('../prof'):
                    href = 'http://www.eng.uerj.br/prof/'
                prof_links.append(href)

        prof_links = list(set(prof_links))

        def parse_fen_prof(url):
            try:
                res = requests.get(url, headers=HEADERS, verify=False, timeout=8)
                res.encoding = 'latin1'
                s = BeautifulSoup(res.text, 'html.parser')
                text = s.get_text()

                # Title parsing is cleanest for FEN
                title_tag = s.find('title')
                name = ""
                if title_tag:
                    title_text = title_tag.get_text().replace('FEN/UERJ - Docente -', '').strip()
                    if title_text and not title_text.startswith('FEN'):
                        name = title_text

                if not name:
                    name_match = re.search(r'PROFESSOR:\s*([^\n\r\(,]+)', text)
                    if name_match:
                        name = name_match.group(1).strip()

                if not name:
                    return None

                dept_match = re.search(r'Depto\.:\s*([A-Z0-9\-_]+)', text)
                dept = dept_match.group(1).strip() if dept_match else "FEN"

                lattes_match = re.search(r'http://buscatextual\.cnpq\.br/buscatextual/visualizacv\.do\?id=\w+', text)
                lattes = lattes_match.group(0) if lattes_match else url

                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.uerj\.br', text, re.IGNORECASE)
                email = email_match.group(0).lower() if email_match else None

                bio = text[text.find("PROFESSOR:"):text.find("Cargos de Chefia")] if "PROFESSOR:" in text else text[:1000]

                return {
                    "name": name,
                    "dept": f"FEN/{dept} - Maracanã",
                    "email": email,
                    "lattes": lattes,
                    "source_url": url,
                    "bio": bio.strip()
                }
            except Exception as e:
                return None

        with ThreadPoolExecutor(max_workers=20) as executor:
            res_list = list(executor.map(parse_fen_prof, prof_links))
            for item in res_list:
                if item and item["name"]:
                    results.append(item)

    except Exception as e:
        print(f"Error crawling FEN: {e}")
    return results

def crawl_iprj():
    print("Crawling IPRJ Nova Friburgo...")
    results = []
    try:
        r = requests.get('https://www.iprj.uerj.br/docentes/', headers=HEADERS, verify=False, timeout=10)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        prof_links = []

        excluded_slugs = [
            'category', 'tag', 'docentes', 'departamentos', 'noticias', 'atendimento',
            'conselho', 'secretarias', 'page', 'historico', 'institucional', 'mecanica',
            'computacao', 'extensao', 'pesquisa', 'wp-content'
        ]

        for a in soup.find_all('a'):
            href = a.get('href')
            if href and 'iprj.uerj.br/' in href:
                path = href.replace('https://www.iprj.uerj.br/', '').replace('http://www.iprj.uerj.br/', '').strip('/')
                parts = [p for p in path.split('/') if p]
                if len(parts) == 1 and not any(k in parts[0] for k in excluded_slugs):
                    prof_links.append(href)

        prof_links = list(set(prof_links))

        def parse_iprj_prof(url):
            try:
                res = requests.get(url, headers=HEADERS, verify=False, timeout=8)
                res.encoding = 'utf-8'
                s = BeautifulSoup(res.text, 'html.parser')
                text = s.get_text()

                title_tag = s.find('h1') or s.find('title')
                name = title_tag.get_text().replace('| IPRJ - Instituto Politécnico', '').strip() if title_tag else ""
                if not name or any(k in name.lower() for k in ['docente', 'departamento', 'instituto', 'página']):
                    return None

                email_match = re.search(r'[\w\.-]+@[\w\.-]*iprj\.uerj\.br', text, re.IGNORECASE)
                if not email_match:
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.uerj\.br', text, re.IGNORECASE)
                email = email_match.group(0).lower() if email_match else None

                lattes_a = s.find('a', href=re.compile(r'lattes\.cnpq\.br'))
                lattes = lattes_a.get('href') if lattes_a else url

                dept = "IPRJ - Nova Friburgo"
                if "DEMEC" in text or "Engenharia Mecânica" in text:
                    dept = "IPRJ/DEMEC - Nova Friburgo"
                elif "DMC" in text or "Modelagem Computacional" in text:
                    dept = "IPRJ/DMC - Nova Friburgo"

                bio = text[:1500]

                return {
                    "name": name,
                    "dept": dept,
                    "email": email,
                    "lattes": lattes,
                    "source_url": url,
                    "bio": bio.strip()
                }
            except Exception as e:
                return None

        with ThreadPoolExecutor(max_workers=20) as executor:
            res_list = list(executor.map(parse_iprj_prof, prof_links))
            for item in res_list:
                if item and item["name"]:
                    results.append(item)

    except Exception as e:
        print(f"Error crawling IPRJ: {e}")
    return results

if __name__ == "__main__":
    fen_data = crawl_fen()
    iprj_data = crawl_iprj()
    all_data = fen_data + iprj_data
    print(f"Total crawled: {len(all_data)} (FEN: {len(fen_data)}, IPRJ: {len(iprj_data)})")
    with open("crawled_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
