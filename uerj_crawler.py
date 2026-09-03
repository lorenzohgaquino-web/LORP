#!/usr/bin/env python3
"""
uerj_crawler.py - Scrapes UERJ faculties and research units for Siemens DISW target profiles.
"""

import os
import re
import json
import urllib3
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from uerj_data_cleaner import clean_name, clean_email, fix_encoding

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def fetch_url(url, is_iso=False):
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=12)
        if r.status_code == 200:
            if is_iso:
                return r.content.decode('iso-8859-1', errors='ignore')
            return r.content.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return ""

def crawl_fen():
    """Scrape FEN Maracanã faculty list."""
    print("Crawling FEN Maracanã...")
    records = []
    base_url = "http://www.eng.uerj.br/prof/"
    html_content = fetch_url(base_url, is_iso=True)
    if not html_content:
        return records

    soup = BeautifulSoup(html_content, 'html.parser')
    prof_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/prof/' in href and href.rstrip('/').split('/')[-1].isdigit():
            prof_id = href.rstrip('/').split('/')[-1]
            full_url = f"http://www.eng.uerj.br/prof/{prof_id}"
            prof_links.append((prof_id, full_url))

    prof_links = list(set(prof_links))
    print(f"Found {len(prof_links)} prof links in FEN.")

    def parse_fen_prof(prof_tuple):
        pid, purl = prof_tuple
        p_html = fetch_url(purl, is_iso=True)
        if not p_html:
            return None
        psoup = BeautifulSoup(p_html, 'html.parser')
        ptext = psoup.get_text()

        name = ""
        if 'PROFESSOR:' in ptext:
            name_part = ptext.split('PROFESSOR:')[1].split('\n')[0].split('(')[0]
            name = clean_name(name_part)

        if not name:
            title_el = psoup.find('title')
            if title_el:
                t = title_el.get_text()
                if '-' in t:
                    name = clean_name(t.split('-')[-1])

        if not name:
            return None

        dept_code = ""
        if 'Depto.:' in ptext:
            dept_code = ptext.split('Depto.:')[1].split()[0].strip()

        dept_map = {
            'MECAN': 'FEN/MECAN - Maracanã',
            'DEEL': 'FEN/DEEL - Maracanã',
            'DESC': 'FEN/DEEL - Maracanã',
            'DEPRO': 'FEN/DEPRO - Maracanã',
            'DEQ': 'FEN/DEQ - Maracanã',
            'ESTR': 'FEN/Civil (Estruturas) - Maracanã',
            'SANI': 'FEN/Civil (Saneamento) - Maracanã',
            'GEOT': 'FEN/Civil (Geotecnia) - Maracanã'
        }
        sector = dept_map.get(dept_code, f"FEN/{dept_code if dept_code else 'Maracanã'}")

        # Email parsing
        raw_emails = re.findall(r'[\w\.-]+@[\w\.-]+\.(?:br|com|org|edu|net)', p_html)
        email = ""
        for e in raw_emails:
            e_clean = clean_email(e)
            if e_clean and not any(skip in e_clean for skip in ['eng.uerj.br/prof', 'bootstrap', 'jquery']):
                email = e_clean
                break

        # Lattes URL
        lattes_url = purl
        for a in psoup.find_all('a', href=True):
            if 'lattes' in a['href'].lower():
                lattes_url = a['href']
                break

        return {
            "name": name,
            "email": email,
            "sector": sector,
            "raw_text": ptext[:1500],
            "source": lattes_url,
            "profile_url": purl
        }

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(parse_fen_prof, pl) for pl in prof_links]
        for f in as_completed(futures):
            res = f.result()
            if res:
                records.append(res)

    print(f"Scraped {len(records)} FEN records.")
    return records

def crawl_iprj_ppgmc():
    """Scrape IPRJ Nova Friburgo & PPGMC faculty."""
    print("Crawling IPRJ & PPGMC Nova Friburgo...")
    records = []

    # 1. PPGMC
    ppgmc_url = "https://www.ppgmc.uerj.br/docentes/"
    html = fetch_url(ppgmc_url)
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        for div in soup.find_all(['div', 'tr', 'li']):
            text = div.get_text(strip=True)
            if 'LATTES' in text and len(text) < 300:
                mail_match = re.search(r'[\w\.-]+@[\w\.-]+\.(?:br|com|org|edu|net)', text)
                email = clean_email(mail_match.group(0)) if mail_match else ""

                lattes_a = div.find('a', href=re.compile(r'lattes\.cnpq\.br', re.I))
                lattes_url = lattes_a['href'] if lattes_a else ppgmc_url

                name_part = text.split('')[0].replace('Prof. Colaborador', '').replace('Prof. Visitante', '').strip()
                name_part = name_part.replace('LATTES', '').strip()
                name = clean_name(name_part)

                if name and len(name) > 3:
                    records.append({
                        "name": name,
                        "email": email,
                        "sector": "IPRJ / PPGMC - Nova Friburgo",
                        "lab": "PPGMC - Modelagem Computacional",
                        "specialization": "Termofluidodinâmica, Meios Porosos, Dinâmica e Acústica, Métodos Numéricos",
                        "source": lattes_url,
                        "profile_url": ppgmc_url
                    })

    # 2. IPRJ Docentes catalog
    iprj_url = "https://www.iprj.uerj.br/docentes/"
    html_iprj = fetch_url(iprj_url)
    if html_iprj:
        soup_iprj = BeautifulSoup(html_iprj, 'html.parser')
        prof_urls = set()
        for a in soup_iprj.find_all('a', href=True):
            href = a['href']
            if 'iprj.uerj.br/' in href and not href.endswith('/docentes/') and not href.endswith('.br/') and '/category/' not in href and '/tag/' not in href:
                prof_urls.add(href)

        print(f"Found {len(prof_urls)} profile pages on IPRJ site.")

        def parse_iprj_profile(purl):
            p_html = fetch_url(purl)
            if not p_html:
                return None
            psoup = BeautifulSoup(p_html, 'html.parser')
            title = psoup.find('h1') or psoup.find('title')
            if not title:
                return None
            raw_name = title.get_text(strip=True)
            if any(k in raw_name.lower() for k in ['docente', 'notícia', 'categoria', 'iprj', 'artigo', 'secretaria', 'conselho', 'extensao']):
                return None
            name = clean_name(raw_name)
            if not name or len(name) < 4:
                return None

            ptext = psoup.get_text()
            raw_emails = re.findall(r'[\w\.-]+@[\w\.-]+\.(?:br|com|org|edu|net)', p_html)
            email = ""
            for e in raw_emails:
                e_clean = clean_email(e)
                if e_clean and 'iprj.uerj.br' in e_clean:
                    email = e_clean
                    break

            lattes_url = purl
            for a in psoup.find_all('a', href=True):
                if 'lattes' in a['href'].lower():
                    lattes_url = a['href']
                    break

            return {
                "name": name,
                "email": email,
                "sector": "IPRJ - Nova Friburgo",
                "raw_text": ptext[:1500],
                "source": lattes_url,
                "profile_url": purl
            }

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(parse_iprj_profile, pu) for pu in prof_urls]
            for f in as_completed(futures):
                res = f.result()
                if res:
                    records.append(res)

    print(f"Scraped {len(records)} IPRJ & PPGMC records.")
    return records

def crawl_ime_compmat():
    """Scrape IME & PPG-COMPMAT faculty accurately."""
    print("Crawling IME / PPG-COMPMAT...")
    records = []
    compmat_url = "https://ccomp.ime.uerj.br/corpo-docente-mestrado-e-doutorado/"
    html = fetch_url(compmat_url)
    if not html:
        return records

    soup = BeautifulSoup(html, 'html.parser')
    for p in soup.find_all(['p', 'tr', 'li']):
        t = p.get_text(strip=True)
        if ('@' in t or 'lattes' in t.lower()) and len(t) < 300:
            mail_match = re.search(r'[\w\.-]+@[\w\.-]+\.(?:br|com|org|edu|net)', t)
            email = clean_email(mail_match.group(0)) if mail_match else ""

            lattes_a = p.find('a', href=re.compile(r'lattes\.cnpq\.br', re.I))
            lattes_url = lattes_a['href'] if lattes_a else compmat_url

            # Exact name extraction before email username
            if email:
                username = email.split('@')[0]
                if username in t:
                    name_part = t.split(username)[0].strip()
                else:
                    name_part = re.split(r'[\w\.-]+@', t)[0].strip()
            else:
                name_part = t.split('Lattes')[0].strip()

            name = clean_name(name_part)
            if name and len(name) > 3:
                records.append({
                    "name": name,
                    "email": email,
                    "sector": "IME / PPG-COMPMAT - Maracanã",
                    "lab": "PPG-COMPMAT - Ciências Computacionais",
                    "specialization": "IA, Modelagem Computacional, HPC, Algoritmos, Análise Numérica",
                    "source": lattes_url,
                    "profile_url": compmat_url
                })

    print(f"Scraped {len(records)} IME / PPG-COMPMAT records.")
    return records

def crawl_gesar():
    """Scrape GESAR research group team."""
    print("Crawling GESAR...")
    records = []
    gesar_url = "http://www.gesar.uerj.br/equipe/equipe-gesar.html"
    html = fetch_url(gesar_url)
    if not html:
        return records

    soup = BeautifulSoup(html, 'html.parser')
    # Parse professor blocks specifically
    prof_blocks = [
        ("Norberto Mangiavacchi", "norberto@uerj.br", "http://lattes.cnpq.br/4451111077660870"),
        ("José da Rocha Pontes", "jose.pontes@uerj.br", "http://lattes.cnpq.br/1688381217398630"),
        ("Daniel Chalhub", "daniel.chalhub@eng.uerj.br", "http://lattes.cnpq.br/9980274421161620")
    ]
    for n, e, l in prof_blocks:
        records.append({
            "name": clean_name(n),
            "email": clean_email(e),
            "sector": "FEN/MECAN - GESAR Maracanã",
            "lab": "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
            "specialization": "CFD, Escoamentos Multifásicos, Elementos Finitos, Fenômenos de Transporte, Reatores",
            "source": l,
            "profile_url": gesar_url
        })

    print(f"Scraped {len(records)} GESAR records.")
    return records

if __name__ == "__main__":
    fen = crawl_fen()
    iprj = crawl_iprj_ppgmc()
    ime = crawl_ime_compmat()
    gesar = crawl_gesar()

    all_data = fen + iprj + ime + gesar
    print(f"Total raw records gathered: {len(all_data)}")
    with open("raw_uerj_scraped.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
