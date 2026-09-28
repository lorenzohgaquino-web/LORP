import json
import re
import ssl
import urllib.request
from bs4 import BeautifulSoup

def fetch_url(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def crawl_uerj_sources():
    print("Starting UERJ crawling across official portals...")
    # Fetch sample pages to verify connectivity
    fen_html = fetch_url('http://www.eng.uerj.br/professor/')
    iprj_html = fetch_url('https://www.iprj.uerj.br/docentes/')
    fat_html = fetch_url('https://www.fat.uerj.br/dptos')
    gesar_html = fetch_url('http://www.gesar.uerj.br/')

    print(f"FEN HTML size: {len(fen_html)}")
    print(f"IPRJ HTML size: {len(iprj_html)}")
    print(f"FAT HTML size: {len(fat_html)}")
    print(f"GESAR HTML size: {len(gesar_html)}")

if __name__ == '__main__':
    crawl_uerj_sources()
