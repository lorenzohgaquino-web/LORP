"""
uerj_crawler.py - Official Web Crawler for UERJ Faculty, Researchers, and Innovation Ecosystem
Focus: Siemens DISW thematic areas (Simulation, CFD, FEA, Thermofluids, HPC, AI, Additive Manufacturing, Optimization)
Target Units: CTC/FEN (Maracanã), IPRJ (Nova Friburgo), FAT (Resende), IME (PPG-COMPMAT), IF, IQ, InovUerj.
"""

import re
import json
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def crawl_iprj_docentes():
    print("[+] Crawling IPRJ Nova Friburgo docentes...")
    url = "https://www.iprj.uerj.br/docentes/"
    records = []
    try:
        resp = requests.get(url, headers=HEADERS, verify=False, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = soup.find_all('a', href=True)
            prof_urls = set()
            for a in links:
                href = a['href']
                if href.startswith('https://www.iprj.uerj.br/') and not any(x in href for x in ['category', 'tag', 'noticias', 'eventos', 'ensino', 'graduacao', 'pos', 'ead']):
                    parts = [p for p in href.split('/') if p]
                    if len(parts) == 3: # e.g. https://www.iprj.uerj.br/antonio-jose-da-silva-neto/
                        prof_urls.add(href)

            for prof_url in sorted(prof_urls):
                try:
                    r_prof = requests.get(prof_url, headers=HEADERS, verify=False, timeout=10)
                    if r_prof.status_code == 200:
                        s_prof = BeautifulSoup(r_prof.text, 'html.parser')
                        title = s_prof.find('h1') or s_prof.find('title')
                        name = title.get_text(strip=True).replace('| IPRJ - Instituto Politécnico', '').strip() if title else ""
                        text = s_prof.get_text(separator=' ', strip=True)

                        # Find emails in page
                        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                        valid_emails = [e for e in emails if not any(w in e.lower() for w in ['w3.org', 'wordpress', 'example', 'sentry', 'domain', 'schema'])]

                        # Find dept and ppg mentions
                        dept = "IPRJ - Instituto Politécnico"
                        if "DEMEC" in text:
                            dept = "IPRJ / DEMEC - Depto. de Engenharia Mecânica"
                        elif "DMC" in text:
                            dept = "IPRJ / DMC - Depto. de Modelagem Computacional"
                        elif "DEMAT" in text:
                            dept = "IPRJ / DEMAT - Depto. de Ciência dos Materiais e Metalurgia"

                        ppg = []
                        if "PPGMC" in text or "Modelagem Computacional" in text:
                            ppg.append("PPGMC (Modelagem Computacional - CAPES 6)")
                        if "PPGCTM" in text or "Ciência e Tecnologia de Materiais" in text:
                            ppg.append("PPGCTM (Ciência e Tecnologia de Materiais)")

                        records.append({
                            "name": name,
                            "url": prof_url,
                            "dept": dept,
                            "ppg": ", ".join(ppg) if ppg else "IPRJ Docente",
                            "text_sample": text[:1000],
                            "found_emails": list(set(valid_emails))
                        })
                except Exception as err:
                    print(f"    [-] Error fetching {prof_url}: {err}")
    except Exception as e:
        print(f"[-] Error crawling IPRJ: {e}")

    print(f"[+] Extracted {len(records)} docentes from IPRJ Nova Friburgo.")
    return records

def crawl_fen_maracana():
    print("[+] Crawling FEN Maracanã...")
    # Fetching FEN professors from internal IDs and PPG websites
    records = []
    # Known FEN department & lab endpoints
    # We will populate structured records from FEN departments: MECAN, DEEL, DEPRO, DEQ, Civil, GESAR, LAMMAC, LaCaM, LFT, LFM, LMES, LaFIT, LMMC
    fen_urls = [
        ("https://www.ppgem.uerj.br/professores.html", "FEN / MECAN - Depto. de Engenharia Mecânica", "PPGEM"),
        ("https://www.pel.uerj.br/", "FEN / DEEL - Depto. de Engenharia Eletrônica", "PEL"),
        ("https://www.pgeciv.uerj.br/", "FEN / Engenharia Civil", "PGECIV"),
        ("https://www.peamb.eng.uerj.br/", "FEN / DEAMB - Engenharia Ambiental", "PEAMB")
    ]
    for url, dept, ppg in fen_urls:
        try:
            r = requests.get(url, headers=HEADERS, verify=False, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                valid_emails = [e for e in list(set(emails)) if not any(w in e.lower() for w in ['w3.org', 'wordpress', 'example', 'schema'])]
                records.append({
                    "url": url,
                    "dept": dept,
                    "ppg": ppg,
                    "text_sample": text[:1000],
                    "found_emails": valid_emails
                })
        except Exception as e:
            print(f"[-] Error fetching {url}: {e}")

    return records

def main():
    iprj_records = crawl_iprj_docentes()
    fen_records = crawl_fen_maracana()

    output = {
        "iprj_docentes": iprj_records,
        "fen_records": fen_records
    }

    with open("uerj_raw_crawl.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("[+] Raw crawl completed and saved to uerj_raw_crawl.json")

if __name__ == "__main__":
    main()
