import urllib.request
import ssl
import re
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def decode_response(res):
    raw = res.read()
    content_type = res.headers.get('Content-Type', '')
    charset = None
    if 'charset=' in content_type:
        charset = content_type.split('charset=')[-1].split(';')[0].strip()

    if charset:
        try:
            return raw.decode(charset)
        except Exception:
            pass

    # Try utf-8 first
    try:
        return raw.decode('utf-8')
    except Exception:
        pass

    # Fallback to iso-8859-1 / latin1 which preserves accents
    try:
        return raw.decode('iso-8859-1')
    except Exception:
        return raw.decode('utf-8', errors='ignore')

def fetch_fen_single(i):
    url = f'https://www.eng.uerj.br/deptos/mostra_prof.php?id={i}'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        res = urllib.request.urlopen(req, context=ctx, timeout=4)
        html = decode_response(res)
        if 'Informações de Contato' in html or 'Depto.:' in html or 'Possui graduação' in html or 'Graduação em' in html:
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()

            # Title / Name
            title = soup.title.string if soup.title else ''
            name = title.replace('FEN/UERJ -', '').replace('Docente -', '').strip()
            if not name or name == '0' or name.isdigit():
                return None

            # Depto
            depto_match = re.search(r'Depto\.\:\s*([A-Za-z0-9\s/]+)', text)
            depto = depto_match.group(1).strip() if depto_match else 'FEN'

            # Email
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
            clean_emails = [e for e in list(set(emails)) if not e.endswith(('.png', '.jpg', '.gif', '.css', '.js'))]

            # Lattes link
            lattes_matches = re.findall(r'lattes\.cnpq\.br/[0-9]+', html)

            return {
                'source': 'FEN Maracanã',
                'id': i,
                'name': name,
                'depto': depto,
                'emails': clean_emails,
                'lattes': [f'http://{l}' for l in set(lattes_matches)],
                'url': url,
                'html_summary': text[:1000]
            }
    except Exception:
        return None

def fetch_fen():
    print("[1/6] Crawling FEN (Faculdade de Engenharia Maracanã)...")
    fen_records = []
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(fetch_fen_single, i) for i in range(1, 500)]
        for future in as_completed(futures):
            res = future.result()
            if res:
                fen_records.append(res)
    print(f"-> FEN: extracted {len(fen_records)} active faculty profiles.")
    return fen_records

def fetch_iprj():
    print("[2/6] Crawling IPRJ & PPGMC (Nova Friburgo)...")
    records = []
    url = 'https://www.iprj.uerj.br/docentes/'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        res = urllib.request.urlopen(req, context=ctx, timeout=10)
        html = decode_response(res)
        soup = BeautifulSoup(html, 'html.parser')

        for container in soup.find_all(['div', 'article', 'tr', 'p', 'li']):
            c_text = container.get_text()
            if ('Prof' in c_text or 'Dr' in c_text or 'Departamento' in c_text or 'PPGMC' in c_text):
                lines = [l.strip() for l in c_text.split('\n') if l.strip()]
                for line in lines:
                    line_clean = re.sub(r'saiba mais', '', line, flags=re.IGNORECASE).strip()
                    if (line_clean.startswith('Prof') or line_clean.startswith('Dr') or (len(line_clean.split()) >= 2 and len(line_clean) < 60)):
                        if any(kw in line_clean.lower() for kw in ['pesquisa', 'departamento', 'publicações', 'disciplinas', 'horário', 'atendimento', 'conheça', 'corpo docente', 'filtre', 'proteção de dados', 'ouvidoria', 'moodle', 'calendário', 'reserva']):
                            continue
                        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', c_text)
                        lattes = re.findall(r'lattes\.cnpq\.br/[0-9]+', c_text)
                        records.append({
                            'source': 'IPRJ Nova Friburgo',
                            'name': line_clean,
                            'depto': 'IPRJ / PPGMC',
                            'emails': list(set(emails)),
                            'lattes': [f'http://{l}' for l in set(lattes)],
                            'url': url,
                            'context': c_text[:500]
                        })
    except Exception as e:
        print(f"IPRJ fetch error: {e}")

    print(f"-> IPRJ raw candidates: {len(records)}")
    return records

def fetch_fat():
    print("[3/6] Crawling FAT (Faculdade de Tecnologia Resende)...")
    records = []
    url = 'https://www.fat.uerj.br/'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        res = urllib.request.urlopen(req, context=ctx, timeout=10)
        html = decode_response(res)
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if any(k in href.lower() for k in ['prof', 'docente', 'equipe', 'departamento', 'dme', 'denp', 'deqa']):
                sub_url = href if href.startswith('http') else f'https://www.fat.uerj.br{href}'
                try:
                    s_req = urllib.request.Request(sub_url, headers=HEADERS)
                    s_res = urllib.request.urlopen(s_req, context=ctx, timeout=5)
                    s_html = decode_response(s_res)
                    s_soup = BeautifulSoup(s_html, 'html.parser')
                    s_text = s_soup.get_text()
                    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', s_html)
                    lattes = re.findall(r'lattes\.cnpq\.br/[0-9]+', s_html)
                    records.append({
                        'source': 'FAT Resende',
                        'name': text or 'FAT Faculty',
                        'depto': 'FAT Resende',
                        'emails': list(set(emails)),
                        'lattes': [f'http://{l}' for l in set(lattes)],
                        'url': sub_url,
                        'context': s_text[:500]
                    })
                except Exception:
                    pass
    except Exception as e:
        print(f"FAT fetch error: {e}")

    print(f"-> FAT raw candidates: {len(records)}")
    return records

def fetch_gesar():
    print("[4/6] Crawling GESAR (Grupo de Simulação em Eng. e Cienc. Ambientais)...")
    records = []
    url = 'http://www.gesar.uerj.br/equipe/equipe-gesar.html'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        res = urllib.request.urlopen(req, context=ctx, timeout=10)
        html = decode_response(res)
        soup = BeautifulSoup(html, 'html.parser')

        for p in soup.find_all(['p', 'div', 'tr', 'li']):
            pt = p.get_text(strip=True)
            pt_clean = re.sub(r'saiba mais', '', pt, flags=re.IGNORECASE).strip()
            if len(pt_clean) > 10 and ('Prof' in pt_clean or 'Dr' in pt_clean or 'Pesquisador' in pt_clean):
                pe = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', str(p))
                pl = re.findall(r'lattes\.cnpq\.br/[0-9]+', str(p))
                records.append({
                    'source': 'GESAR Maracanã',
                    'name': pt_clean[:80],
                    'depto': 'GESAR / FEN',
                    'emails': list(set(pe)),
                    'lattes': [f'http://{l}' for l in set(pl)],
                    'url': url,
                    'context': pt_clean
                })
    except Exception as e:
        print(f"GESAR fetch error: {e}")

    print(f"-> GESAR raw candidates: {len(records)}")
    return records

def fetch_ime_compmat():
    print("[5/6] Crawling IME / PPG-COMPMAT (Matemática e Computação)...")
    records = []
    url = 'https://www.ime.uerj.br/professores/'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        res = urllib.request.urlopen(req, context=ctx, timeout=10)
        html = decode_response(res)
        soup = BeautifulSoup(html, 'html.parser')

        for li in soup.find_all(['li', 'tr', 'div', 'p']):
            lt = li.get_text()
            if '@ime.uerj.br' in lt or '@uerj.br' in lt or 'Prof' in lt:
                emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', lt)
                records.append({
                    'source': 'IME / PPG-COMPMAT',
                    'name': lt[:80].strip(),
                    'depto': 'IME',
                    'emails': list(set(emails)),
                    'lattes': [],
                    'url': url,
                    'context': lt[:300]
                })
    except Exception as e:
        print(f"IME fetch error: {e}")

    print(f"-> IME raw candidates: {len(records)}")
    return records

def fetch_inovuerj():
    print("[6/6] Fetching InovUerj / DEPINOVA info...")
    records = [{
        'source': 'InovUerj / DEPINOVA',
        'name': 'Diretoria de Inovação (InovUerj / DEPINOVA)',
        'depto': 'PR2 / InovUerj',
        'emails': ['inovuerj@uerj.br', 'depinova@pr2.uerj.br'],
        'lattes': [],
        'url': 'https://www.pr2.uerj.br/',
        'context': 'Diretoria de Inovação da UERJ - Gestão de Propriedade Intelectual, Transferência de Tecnologia e Incubadoras'
    }]
    print(f"-> InovUerj records: {len(records)}")
    return records

def main():
    raw_data = {
        'fen': fetch_fen(),
        'iprj': fetch_iprj(),
        'fat': fetch_fat(),
        'gesar': fetch_gesar(),
        'ime': fetch_ime_compmat(),
        'inovuerj': fetch_inovuerj()
    }

    with open('uerj_raw_extraction.json', 'w', encoding='utf-8') as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)
    print("Raw extraction saved to uerj_raw_extraction.json")

if __name__ == '__main__':
    main()
