#!/usr/bin/env python3
"""
uerj_crawler.py
Crawl official UERJ domains across FEN, IPRJ, FAT, IME, GESAR, and PR2.
Extracts faculty, lab directors, PPG coordinators, and innovation leads.
"""

import json
import re
import ssl
import sys
import urllib.request
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ignore SSL verification for older government/university certs
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}

TARGET_URLS = [
    # FEN - Maracanã
    {"url": "https://www.eng.uerj.br/", "dept": "FEN - Faculdade de Engenharia", "default_email": "diretoria@eng.uerj.br"},
    {"url": "https://www.eng.uerj.br/docentes/", "dept": "FEN - Faculdade de Engenharia", "default_email": "sec.docente@eng.uerj.br"},
    {"url": "http://www.gesar.uerj.br/", "dept": "FEN/GESAR - Maracanã", "default_email": "gesar@uerj.br"},
    {"url": "http://www.gesar.uerj.br/peopled.html", "dept": "FEN/GESAR - Maracanã", "default_email": "gesar@uerj.br"},

    # IPRJ - Nova Friburgo
    {"url": "http://www.iprj.uerj.br/", "dept": "IPRJ - Nova Friburgo", "default_email": "secretaria.iprj@uerj.br"},
    {"url": "http://www.iprj.uerj.br/docentes/", "dept": "IPRJ - Nova Friburgo", "default_email": "secretaria.iprj@uerj.br"},
    {"url": "http://www.iprj.uerj.br/ppgmc/", "dept": "IPRJ/PPGMC - Nova Friburgo", "default_email": "ppgmc@iprj.uerj.br"},
    {"url": "http://www.iprj.uerj.br/ppgmc/corpo-docente/", "dept": "IPRJ/PPGMC - Nova Friburgo", "default_email": "ppgmc@iprj.uerj.br"},

    # FAT - Resende
    {"url": "http://www.fat.uerj.br/", "dept": "FAT - Resende", "default_email": "secretaria@fat.uerj.br"},
    {"url": "http://www.fat.uerj.br/docentes/", "dept": "FAT - Resende", "default_email": "secretaria@fat.uerj.br"},
    {"url": "http://www.fat.uerj.br/corpo-docente/", "dept": "FAT - Resende", "default_email": "secretaria@fat.uerj.br"},

    # IME & COMPMAT - Maracanã
    {"url": "http://www.ime.uerj.br/", "dept": "IME - Instituto de Matemática e Estatística", "default_email": "ime@uerj.br"},
    {"url": "http://www.ppgcompmat.ime.uerj.br/", "dept": "IME/PPG-COMPMAT - Maracanã", "default_email": "ppgcompmat@ime.uerj.br"},

    # InovUerj & PR2
    {"url": "https://www.pr2.uerj.br/", "dept": "PR2 - Pró-Reitoria de Pós-Graduação e Pesquisa", "default_email": "pr2@uerj.br"},
    {"url": "https://www.pr2.uerj.br/inovuerj/", "dept": "InovUerj / DEPINOVA - Maracanã", "default_email": "inovuerj@uerj.br"}
]

def fetch_url(target):
    url = target["url"]
    dept = target["dept"]
    default_email = target["default_email"]
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=12) as response:
            html = response.read().decode('utf-8', errors='ignore')
            return {"url": url, "dept": dept, "default_email": default_email, "html": html, "status": 200}
    except Exception as e:
        print(f"[WARN] Failed fetching {url}: {e}", file=sys.stderr)
        return {"url": url, "dept": dept, "default_email": default_email, "html": "", "status": 500}

def parse_html_to_records(raw_data):
    records = []
    url = raw_data["url"]
    dept = raw_data["dept"]
    default_email = raw_data["default_email"]
    html = raw_data["html"]

    if not html:
        return records

    soup = BeautifulSoup(html, 'html.parser')
    text_content = soup.get_text()

    # Generic mailto and email regex search
    email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    found_emails = set(email_regex.findall(text_content))

    # Look for list elements or paragraphs that look like faculty entries
    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
    for i, line in enumerate(lines):
        if any(keyword in line.lower() for keyword in ["prof", "dr", "pesquisador", "coordenador", "diretor"]):
            # Extract line and next line as context
            context = " ".join(lines[i:min(i+3, len(lines))])
            emails_in_context = email_regex.findall(context)
            email = emails_in_context[0] if emails_in_context else default_email

            records.append({
                "raw_name": line,
                "context": context,
                "email": email,
                "dept": dept,
                "url": url
            })

    return records

def run_crawler():
    print("[INFO] Starting UERJ crawler...")
    raw_results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_url, target) for target in TARGET_URLS]
        for future in as_completed(futures):
            res = future.result()
            raw_results.append(res)
            print(f"[FETCHED] {res['url']} - Status {res['status']}")

    extracted_records = []
    for raw in raw_results:
        extracted_records.extend(parse_html_to_records(raw))

    print(f"[INFO] Total raw records harvested: {len(extracted_records)}")

    with open("raw_uerj_harvest.json", "w", encoding="utf-8") as f:
        json.dump(extracted_records, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_crawler()
