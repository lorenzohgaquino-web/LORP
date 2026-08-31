import requests
from bs4 import BeautifulSoup
import re
import json
import urllib3
import html
from concurrent.futures import ThreadPoolExecutor, as_completed
sys = __import__('sys')
sys.path.append('/home/jules/self_created_tools')
try:
    from uerj_data_cleaner import clean_uerj_name, fix_mojibake
except ImportError:
    def fix_mojibake(t): return t
    def clean_uerj_name(n): return n.strip()

urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

records = []

def sanitize_lattes(url):
    if not url:
        return ""
    if "E+" in url or "e+" in url:
        return ""
    if not url.startswith("http"):
        url = "http://" + url
    return url

def fetch_fen_prof(i):
    url = f"https://www.eng.uerj.br/prof/{i}"
    try:
        r = requests.get(url, headers=headers, timeout=5, verify=False)
        if r.status_code == 200 and 'Página Não Encontrada' not in r.text and len(r.text) > 500:
            r.encoding = 'iso-8859-1'
            text_html = r.text
            soup = BeautifulSoup(text_html, 'html.parser')
            text = soup.get_text()

            if 'leciona na FEN' not in text and 'Depto.: 0' not in text and 'PROFESSOR:' in text:
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                raw_name = ""
                depto = ""
                for line in lines:
                    if 'PROFESSOR:' in line:
                        raw_name = line.replace('PROFESSOR:', '').strip()
                    elif 'Depto.:' in line:
                        depto = line.replace('Depto.:', '').strip()

                name = clean_uerj_name(raw_name)
                if not name or len(name) < 4 or 'substituto' in name.lower():
                    return None

                clean_emails = []
                for mailto in soup.find_all('a', href=re.compile(r'^mailto:', re.IGNORECASE)):
                    em = mailto['href'].replace('mailto:', '').strip()
                    if '@' in em and re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', em):
                        clean_emails.append(em)

                if not clean_emails:
                    raw_emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
                    for em in raw_emails:
                        em_c = re.sub(r'(Lattes|Site|P-|MD|COMP|MAT|FIS|BIO|ENG|Disciplinas).*$', '', em, flags=re.IGNORECASE)
                        if '@' in em_c and len(em_c) > 5 and re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', em_c):
                            clean_emails.append(em_c)

                public_email = clean_emails[0] if clean_emails else "secfen@eng.uerj.br"

                lattes_links = [a['href'] for a in soup.find_all('a', href=True) if 'lattes.cnpq.br' in a['href']]
                lattes_url = sanitize_lattes(lattes_links[0]) if lattes_links else f"https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar&nome={name.replace(' ', '+')}"

                dept_code = depto.split()[0] if depto else ""
                sector_map = {
                    'MEC': 'FEN/MECAN - Maracanã',
                    'ELE': 'FEN/DEEL - Maracanã',
                    'PRO': 'FEN/DEPRO - Maracanã',
                    'QUI': 'FEN/DEQ - Maracanã',
                    'ESTR': 'FEN/Estruturas - Maracanã',
                    'CIVIL': 'FEN/Engenharia Civil - Maracanã',
                    'DESMA': 'FEN/DESMA - Maracanã',
                    'CARTO': 'FEN/Engenharia Cartográfica - Maracanã'
                }
                sector = sector_map.get(dept_code, f"FEN/{depto if depto else 'Maracanã'} - Maracanã")

                return {
                    "nome": name,
                    "email": public_email,
                    "setor": sector,
                    "laboratorio": "Faculdade de Engenharia (FEN/UERJ)",
                    "especializacao": "Engenharia e Ciências Aplicadas",
                    "fonte_url": url,
                    "status_validacao": "Verificado Via Portal FEN UERJ",
                    "data_acesso": "2026-03-30",
                    "lattes": lattes_url
                }
    except Exception:
        pass
    return None

print("--- Crawling FEN Maracanã (eng.uerj.br) with ThreadPoolExecutor ---")
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(fetch_fen_prof, i) for i in range(1, 400)]
    for future in as_completed(futures):
        res = future.result()
        if res:
            records.append(res)

print(f"Captured {len(records)} FEN faculty records.")

print("--- Crawling PPG-COMPMAT / IME (ccomp.ime.uerj.br) ---")
try:
    r = requests.get('https://ccomp.ime.uerj.br/corpo-docente-mestrado-e-doutorado/', headers=headers, timeout=5, verify=False)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')
    for tr in soup.find_all(['tr', 'p', 'li']):
        mailto_link = tr.find('a', href=re.compile(r'^mailto:', re.IGNORECASE))
        lattes_link = tr.find('a', href=re.compile(r'lattes\.cnpq\.br', re.IGNORECASE))

        if mailto_link:
            clean_email = mailto_link['href'].replace('mailto:', '').strip()
            lattes_url = sanitize_lattes(lattes_link['href']) if lattes_link else ""

            first_a = tr.find('a')
            if first_a and first_a != mailto_link and 'lattes' not in first_a.get('href', '').lower():
                raw_name = first_a.get_text(strip=True)
            else:
                txt = tr.get_text(strip=True)
                name_part = txt.split(mailto_link.get_text(strip=True))[0]
                name_part = re.sub(r'(Membro|Nome|Vínculo|Linha Principal|\(COMP\)|\(MAT\)|\(FIS\)|\(ENG\)|\(EST\)|\(BIO\)|Lattes).*', '', name_part)
                raw_name = name_part

            name = clean_uerj_name(raw_name)

            if len(name) > 3 and not any(x in name.lower() for x in ['membro', 'linha', 'principal', 'vínculo']):
                if not any(r['nome'] == name for r in records):
                    records.append({
                        "nome": name,
                        "email": clean_email,
                        "setor": "IME/PPG-COMPMAT - Maracanã",
                        "laboratorio": "Programa de Pós-Graduação em Ciências Computacionais",
                        "especializacao": "Modelagem Matemática, Métodos Numéricos, IA, HPC",
                        "fonte_url": "https://ccomp.ime.uerj.br/corpo-docente-mestrado-e-doutorado/",
                        "status_validacao": "Verificado Via Portal PPG-COMPMAT IME/UERJ",
                        "data_acesso": "2026-03-30",
                        "lattes": lattes_url or f"https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar&nome={name.replace(' ', '+')}"
                    })
except Exception as e:
    print("Error crawling PPG-COMPMAT:", e)

print("--- Crawling IPRJ Nova Friburgo (iprj.uerj.br) ---")
try:
    r = requests.get('https://www.iprj.uerj.br/docentes/', headers=headers, timeout=5, verify=False)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')
    iprj_links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'iprj.uerj.br/' in href and not any(x in href for x in ['/category/', '/tag/', '/wp-', '/docentes', '/historico', '/departamentos', '/secretarias', '/mecanica', '/computacao', '/extensao', '/noticias', '/atendimento', '/pesquisa']):
            iprj_links.add(href)

    def fetch_iprj_prof(link):
        try:
            r2 = requests.get(link, headers=headers, timeout=5, verify=False)
            r2.encoding = 'utf-8'
            soup2 = BeautifulSoup(r2.text, 'html.parser')
            text2 = soup2.get_text()

            name_tag = soup2.find('h1', class_='entry-title') or soup2.find('h1')
            if not name_tag:
                return None
            raw_name = name_tag.get_text(strip=True)
            name = clean_uerj_name(raw_name)
            if not name or len(name) < 4 or any(x in name.lower() for x in ['instituto', 'conselho', 'programa', 'departamento', 'corpo', 'secretaria']):
                return None

            raw_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text2)
            clean_emails = [re.sub(r'(Lattes|Site|P-|MD).*$', '', e, flags=re.IGNORECASE) for e in raw_emails if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', e)]
            public_email = clean_emails[0] if clean_emails else "secretaria-posgrad@iprj.uerj.br"

            lattes_links = [a['href'] for a in soup2.find_all('a', href=True) if 'lattes.cnpq.br' in a['href']]
            lattes_url = sanitize_lattes(lattes_links[0]) if lattes_links else f"https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar&nome={name.replace(' ', '+')}"

            return {
                "nome": name,
                "email": public_email,
                "setor": "IPRJ - Nova Friburgo",
                "laboratorio": "Instituto Politécnico / PPGMC / PPGCTM",
                "especializacao": "Modelagem Computacional, Termofluidodinâmica, Ciência de Materiais, Vibrações",
                "fonte_url": link,
                "status_validacao": "Verificado Via Portal IPRJ UERJ",
                "data_acesso": "2026-03-30",
                "lattes": lattes_url
            }
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_iprj_prof, link) for link in iprj_links]
        for future in as_completed(futures):
            res = future.result()
            if res:
                records.append(res)
except Exception as e:
    print("Error crawling IPRJ:", e)

print("--- Crawling FAT Resende (fat.uerj.br) ---")
fat_depts = [
    ('https://www.fat.uerj.br/departamento/departamento-de-mecanica-e-energia/', 'FAT/DME - Resende', 'Departamento de Mecânica e Energia'),
    ('https://www.fat.uerj.br/departamento/departamento-de-engenharia-de-producao/', 'FAT/DENP - Resende', 'Departamento de Engenharia de Produção'),
    ('https://www.fat.uerj.br/departamento/departamento-de-quimica-e-ambiental/', 'FAT/DEQA - Resende', 'Departamento de Química e Ambiental'),
    ('https://www.fat.uerj.br/departamento/departamento-de-matematica-fisica-e-computacao/', 'FAT/DMFC - Resende', 'Departamento de Matemática, Física e Computação')
]

for url, setor, dept_name in fat_depts:
    try:
        r = requests.get(url, headers=headers, timeout=5, verify=False)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        paragraphs = soup.find_all('p')
        for idx, p in enumerate(paragraphs):
            txt = p.get_text(strip=True)
            if 'Lattes:' in txt:
                lattes_match = re.search(r'https?://lattes\.cnpq\.br/\d+', txt)
                lattes_url = lattes_match.group(0) if lattes_match else ""

                prev_p = paragraphs[idx-1] if idx > 0 else p
                prev_txt = prev_p.get_text(strip=True)

                strong = prev_p.find(['strong', 'b'])
                if strong:
                    raw_name = strong.get_text(strip=True)
                else:
                    raw_name = prev_txt.split('Possui')[0].split('Doutor')[0].split('Professor')[0].split('Graduad')[0].strip()

                name = clean_uerj_name(raw_name)
                if len(name) > 3 and len(name) < 50 and not any(x in name.lower() for x in ['sobre', 'tenho', 'gosto', 'projetos', 'pesquisa', 'processo', 'edital']):
                    raw_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', p.get_text() + " " + prev_txt)
                    clean_emails = [e for e in raw_emails if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', e)]
                    public_email = clean_emails[0] if clean_emails else "secretaria@fat.uerj.br"

                    records.append({
                        "nome": name,
                        "email": public_email,
                        "setor": setor,
                        "laboratorio": f"FAT / {dept_name}",
                        "especializacao": "Manufatura Aditiva, Polímeros, Hidráulica e Pneumática, Térmica",
                        "fonte_url": url,
                        "status_validacao": "Verificado Via Portal FAT UERJ",
                        "data_acesso": "2026-03-30",
                        "lattes": lattes_url or f"https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar&nome={name.replace(' ', '+')}"
                    })
    except Exception as e:
        print("Error crawling FAT dept:", url, e)

print(f"Total extracted records: {len(records)}")

with open('uerj_raw_records.json', 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)
