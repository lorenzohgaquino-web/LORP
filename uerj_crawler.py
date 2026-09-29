#!/usr/bin/env python3
"""
uerj_crawler.py - Crawls official UERJ web pages and collects structured raw data.
"""

import os
import json
import re
import requests
import urllib3
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

RAW_TARGETS = [
    {
        "unit": "IPRJ - Nova Friburgo",
        "dept_lab": "PPGMC - Programa de Pós-Graduação em Modelagem Computacional",
        "url": "https://www.ppgmc.uerj.br/docentes/",
        "fallback_email": "sec.pgmc@iprj.uerj.br"
    },
    {
        "unit": "IPRJ - Nova Friburgo",
        "dept_lab": "DEMEC - Departamento de Engenharia Mecânica e Energia",
        "url": "https://www.iprj.uerj.br/departamentos/",
        "fallback_email": "demecc@iprj.uerj.br"
    },
    {
        "unit": "IPRJ - Nova Friburgo",
        "dept_lab": "DMC - Departamento de Modelagem Computacional",
        "url": "https://www.iprj.uerj.br/departamentos/",
        "fallback_email": "dmc-chefia@iprj.uerj.br"
    },
    {
        "unit": "IPRJ - Nova Friburgo",
        "dept_lab": "DEMAT - Departamento de Engenharia de Materiais",
        "url": "https://www.iprj.uerj.br/departamentos/",
        "fallback_email": "dematc@iprj.uerj.br"
    },
    {
        "unit": "FEN / CTC Maracanã",
        "dept_lab": "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
        "url": "http://www.gesar.uerj.br/equipe/equipe-gesar.html",
        "fallback_email": "gesar@uerj.br"
    },
    {
        "unit": "IME / CTC Maracanã",
        "dept_lab": "PPG-COMPMAT - Ciências Computacionais e Modelagem Matemática",
        "url": "https://www.ime.uerj.br/pos-graduacao/",
        "fallback_email": "secime@ime.uerj.br"
    },
    {
        "unit": "FAT - Resende",
        "dept_lab": "DME / DENP / DEQA - Faculdade de Tecnologia",
        "url": "https://www.fat.uerj.br/grupos-de-pesquisa-no-cnpq/",
        "fallback_email": "secretaria@fat.uerj.br"
    }
]

def fetch_page(target):
    url = target["url"]
    try:
        res = requests.get(url, verify=False, timeout=10, headers=HEADERS)
        if res.status_code == 200:
            return {
                "target": target,
                "status": "success",
                "html": res.text
            }
        else:
            return {
                "target": target,
                "status": f"http_{res.status_code}",
                "html": ""
            }
    except Exception as e:
        return {
            "target": target,
            "status": f"error: {e}",
            "html": ""
        }

def crawl_all():
    print("Starting crawl of UERJ targets...")
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_page, target) for target in RAW_TARGETS]
        for f in futures:
            results.append(f.result())

    os.makedirs("data_raw", exist_ok=True)
    with open("data_raw/uerj_crawl_raw.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Crawl complete. Saved to data_raw/uerj_crawl_raw.json")

if __name__ == "__main__":
    crawl_all()
