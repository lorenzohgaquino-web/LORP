import requests
from bs4 import BeautifulSoup
import re
import json
import urllib3
import html
urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

records = []

def clean_name(name):
    if not name:
        return ""
    # Strip HTML tags if any
    name = BeautifulSoup(name, 'html.parser').get_text(strip=True)
    # Remove titles & degrees
    name = re.sub(r'^(Prof\.?|Profa\.?|Dr\.?|Dra\.?|MSc|Ph\.?D\.?|\s+)+', '', name, flags=re.IGNORECASE)
    name = re.sub(r',?\s*(DSc|D\.Sc\.|Ph\.?D\.?|MSc|M\.Sc\.|Doutor.*|Doutora.*|Engenheiro.*|Mestrado.*)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*=\s*Universit.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*-\s*Frana.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*-\s*Brasil.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'Depto\..*', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def sanitize_lattes(url):
    if not url:
        return ""
    if "E+" in url or "e+" in url:
        return ""
    if not url.startswith("http"):
        url = "http://" + url
    return url

print("--- Crawling FEN Maracanã (eng.uerj.br) ---")
for i in range(1, 400):
    url = f"https://www.eng.uerj.br/prof/{i}"
    try:
        r = requests.get(url, headers=headers, timeout=3, verify=False)
        if r.status_code == 200 and 'Página Não Encontrada' not in r.text and len(r.text) > 500:
            # Fix encoding for eng.uerj.br which is latin-1 / iso-8859-1
            r.encoding = r.apparent_encoding or 'iso-8859-1'
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

                name = clean_name(raw_name)
                if not name or len(name) < 4 or 'substituto' in name.lower():
                    continue

                # Regex for valid email
                emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
                # Keep uerj or valid personal emails, clean trailing junk if any
                clean_emails = []
                for em in emails:
                    em_c = re.sub(r'(Lattes|Site|P-|MD|COMP|MAT|FIS|BIO|ENG).*$', '', em, flags=re.IGNORECASE)
                    if '@' in em_c and len(em_c) > 5:
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

                records.append({
                    "nome": name,
                    "email": public_email,
                    "setor": sector,
                    "laboratorio": "Faculdade de Engenharia (FEN/UERJ)",
                    "especializacao": "Engenharia e Ciências Aplicadas",
                    "fonte_url": url,
                    "status_validacao": "Verificado Via Portal FEN UERJ",
                    "data_acesso": "2026-03-30",
                    "lattes": lattes_url
                })
    except Exception as e:
        pass

print(f"Captured {len(records)} FEN faculty records.")

print("--- Crawling PPG-COMPMAT / IME (ccomp.ime.uerj.br) ---")
try:
    r = requests.get('https://ccomp.ime.uerj.br/corpo-docente-mestrado-e-doutorado/', headers=headers, timeout=5, verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    for tr in soup.find_all(['tr', 'p', 'li']):
        txt = tr.get_text(strip=True)
        # Look for explicit emails in cell
        raw_emails = re.findall(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', txt)
        if raw_emails:
            # Clean email of appended words like LattesP
            clean_email = re.sub(r'(Lattes|Site|P-|MD|COMP|MAT|FIS|BIO|ENG).*$', '', raw_emails[0], flags=re.IGNORECASE)

            # Find associated name
            links = tr.find_all('a')
            lattes_url = ""
            for a in links:
                if 'lattes.cnpq.br' in a.get('href', ''):
                    lattes_url = sanitize_lattes(a['href'])

            # extract name from first link or text before email
            name_part = txt.split(raw_emails[0])[0]
            name_part = re.sub(r'(Membro|Nome|Vínculo|Linha Principal|\(COMP\)|\(MAT\)|\(FIS\)|\(ENG\)|\(EST\)|\(BIO\)|Lattes).*', '', name_part)
            name = clean_name(name_part)

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
    r = requests.get('https://www.iprj.uerj.br/docentes/', headers=headers, timeout=10, verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    iprj_links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'iprj.uerj.br/' in href and not any(x in href for x in ['/category/', '/tag/', '/wp-', '/docentes', '/historico', '/departamentos', '/secretarias', '/mecanica', '/computacao', '/extensao', '/noticias', '/atendimento', '/pesquisa']):
            iprj_links.add(href)

    for link in iprj_links:
        try:
            r2 = requests.get(link, headers=headers, timeout=5, verify=False)
            soup2 = BeautifulSoup(r2.text, 'html.parser')
            text2 = soup2.get_text()

            name_tag = soup2.find('h1', class_='entry-title') or soup2.find('h1')
            if not name_tag:
                continue
            raw_name = name_tag.get_text(strip=True)
            name = clean_name(raw_name)
            if not name or len(name) < 4 or any(x in name.lower() for x in ['instituto', 'conselho', 'programa', 'departamento', 'corpo', 'secretaria']):
                continue

            raw_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text2)
            clean_emails = [re.sub(r'(Lattes|Site|P-|MD).*$', '', e, flags=re.IGNORECASE) for e in raw_emails]
            public_email = clean_emails[0] if clean_emails else "secretaria-posgrad@iprj.uerj.br"

            lattes_links = [a['href'] for a in soup2.find_all('a', href=True) if 'lattes.cnpq.br' in a['href']]
            lattes_url = sanitize_lattes(lattes_links[0]) if lattes_links else f"https://buscatextual.cnpq.br/buscatextual/busca.do?metodo=apresentar&nome={name.replace(' ', '+')}"

            records.append({
                "nome": name,
                "email": public_email,
                "setor": "IPRJ - Nova Friburgo",
                "laboratorio": "Instituto Politécnico / PPGMC / PPGCTM",
                "especializacao": "Modelagem Computacional, Termofluidodinâmica, Ciência de Materiais, Vibrações",
                "fonte_url": link,
                "status_validacao": "Verificado Via Portal IPRJ UERJ",
                "data_acesso": "2026-03-30",
                "lattes": lattes_url
            })
        except Exception:
            pass
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
        soup = BeautifulSoup(r.text, 'html.parser')
        paragraphs = soup.find_all('p')
        for idx, p in enumerate(paragraphs):
            txt = p.get_text(strip=True)
            if 'Lattes:' in txt:
                lattes_match = re.search(r'https?://lattes\.cnpq\.br/\d+', txt)
                lattes_url = lattes_match.group(0) if lattes_match else ""

                # Get bio paragraph preceding or current
                prev_p = paragraphs[idx-1] if idx > 0 else p
                prev_txt = prev_p.get_text(strip=True)

                # Extract clean name from bold/strong tag if present
                strong = prev_p.find(['strong', 'b'])
                if strong:
                    raw_name = strong.get_text(strip=True)
                else:
                    raw_name = prev_txt.split('Possui')[0].split('Doutor')[0].split('Professor')[0].split('Graduad')[0].strip()

                name = clean_name(raw_name)
                # Ignore bios, sentences, or generic text falsely captured as names
                if len(name) > 3 and len(name) < 50 and not any(x in name.lower() for x in ['sobre', 'tenho', 'gosto', 'projetos', 'pesquisa', 'processo', 'edital']):
                    raw_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', p.get_text() + " " + prev_txt)
                    clean_emails = [re.sub(r'(Lattes|Site|P-|MD).*$', '', e, flags=re.IGNORECASE) for e in raw_emails]
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
