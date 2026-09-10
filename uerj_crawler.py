import requests
from bs4 import BeautifulSoup
import re
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from uerj_data_cleaner import clean_string, sanitize_email

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/115.0.0.0 Safari/537.36'
}

raw_records = []

def fetch_fen_prof(pid):
    url = f"http://www.eng.uerj.br/prof/{pid}"
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=5)
        if r.status_code == 200:
            # Properly decode ISO-8859-1 encoding used by FEN web server
            r.encoding = 'iso-8859-1'
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.get_text()

            name_match = re.search(r"PROFESSOR:\s*([^,\n\r]+)", text, re.IGNORECASE)
            if not name_match:
                return None
            name = clean_string(name_match.group(1))
            if not name or len(name) < 3 or name.lower().startswith("universidade"):
                return None

            # Blacklist non-person placeholders
            if any(p in name.lower() for p in ['subst', 'substituto', 'vago', 'professor', 'teste', 'open sans', 'varela']):
                return None

            depto_match = re.search(r"Depto\.:\s*([A-Za-z0-9]+)", text, re.IGNORECASE)
            depto_code = depto_match.group(1).upper() if depto_match else "FEN"

            depto_map = {
                'MEC': 'FEN/MECAN - Depto. de Engenharia Mecânica (Maracanã)',
                'MECAN': 'FEN/MECAN - Depto. de Engenharia Mecânica (Maracanã)',
                'ELE': 'FEN/DEEL - Depto. de Engenharia Eletrônica e de Telecomunicações (Maracanã)',
                'DEEL': 'FEN/DEEL - Depto. de Engenharia Eletrônica e de Telecomunicações (Maracanã)',
                'PRO': 'FEN/DEPRO - Depto. de Engenharia de Produção (Maracanã)',
                'DEPRO': 'FEN/DEPRO - Depto. de Engenharia de Produção (Maracanã)',
                'QUI': 'FEN/DEQ - Depto. de Engenharia Química (Maracanã)',
                'DEQ': 'FEN/DEQ - Depto. de Engenharia Química (Maracanã)',
                'ESTR': 'FEN/DEC - Depto. de Engenharia Civil e Estruturas (Maracanã)',
                'DEC': 'FEN/DEC - Depto. de Engenharia Civil e Estruturas (Maracanã)',
                'SAN': 'FEN/DESMA - Depto. de Engenharia Sanitária e Meio Ambiente (Maracanã)'
            }
            mapped_depto = depto_map.get(depto_code, f"FEN - Depto. {depto_code} (Maracanã)")

            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
            valid_email = ""
            for em in emails:
                s_em = sanitize_email(em)
                if s_em and not any(black in s_em for black in ['webmail', 'example', 'domain']):
                    valid_email = s_em
                    break

            return {
                'nome': name,
                'email': valid_email,
                'setor_departamento': mapped_depto,
                'laboratorio_grupo': 'FEN - Maracanã',
                'especializacao': text, # Send complete text for accurate specialization classification
                'fonte_validacao': url,
                'status_validacao': 'Verificado',
                'data_acesso': '2026-03-06'
            }
    except Exception:
        return None

def crawl_all():
    print("Starting concurrent crawling of FEN Maracanã...")
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(fetch_fen_prof, pid) for pid in range(1, 500)]
        for future in as_completed(futures):
            res = future.result()
            if res:
                raw_records.append(res)

    print(f"Captured {len(raw_records)} records from FEN.")

    with open("raw_uerj_records.json", "w", encoding="utf-8") as f:
        json.dump(raw_records, f, ensure_ascii=False, indent=2)
    print("Saved raw_uerj_records.json successfully.")

if __name__ == "__main__":
    crawl_all()
