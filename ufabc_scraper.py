import urllib.request
import urllib.error
import re
import json
import time
import concurrent.futures

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def decode_spambot_email(html_text):
    # Normalize escaped single quotes
    normalized = html_text.replace("\\'", "'")

    # Find all strings inside single quotes
    parts = re.findall(r"'([^']+)'", normalized)
    if not parts:
        parts = re.findall(r'"([^"]+)"', normalized)

    decoded_parts = []
    for part in parts:
        # Decode HTML decimal entities
        decoded_part = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), part)
        decoded_parts.append(decoded_part)

    combined = "".join(decoded_parts)
    email_match = re.search(r'([\w\.\-]+@(?:[\w\-]+\.)*ufabc\.edu\.br)', combined, re.IGNORECASE)
    if email_match:
        return email_match.group(1).lower().strip()
    return None

def fetch_url(url, retries=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=headers)
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                return response.read().decode('utf-8', errors='ignore')
        except urllib.error.URLError as e:
            time.sleep(1)
    return None

def scrape_docentes_geral():
    print("Scraping docentes geral...")
    url = "https://www.ufabc.edu.br/ensino/docentes"
    html = fetch_url(url)
    if not html:
        return []

    docentes = []
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
    for row in rows:
        tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
        if len(tds) >= 3:
            name_html = tds[0]
            area = clean_html(tds[1])
            centro = clean_html(tds[2])

            # Match both absolute and relative URLs
            link_match = re.search(r'href="((?:https://www.ufabc.edu.br)?/ensino/docentes/[\w\-]+)"', name_html, re.IGNORECASE)
            if link_match:
                path = link_match.group(1)
                full_url = path if path.startswith("http") else "https://www.ufabc.edu.br" + path
                name = clean_html(name_html)
                docentes.append({
                    "nome": name,
                    "area": area,
                    "centro": centro,
                    "url": full_url
                })

    # Fallback pattern if rows didn't match
    if not docentes:
        fallback_pattern = re.compile(r'href="((?:https://www.ufabc.edu.br)?/ensino/docentes/([\w\-]+))"[^>]*>(.*?)</a>', re.IGNORECASE)
        matches = fallback_pattern.findall(html)
        for path, slug, name in matches:
            full_url = path if path.startswith("http") else "https://www.ufabc.edu.br" + path
            docentes.append({
                "nome": clean_html(name),
                "area": "Indisponível",
                "centro": "Indisponível",
                "url": full_url
            })

    print(f"Mapeados {len(docentes)} docentes do portal geral.")
    return docentes

def scrape_cecs_docentes():
    print("Scraping CECS docentes...")
    url = "https://cecs.ufabc.edu.br/corpo-docente-2-0"
    html = fetch_url(url)
    if not html:
        return []

    cecs_docentes = []
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
    for row in rows:
        tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
        if len(tds) >= 2:
            name_html = tds[0]
            email_html = tds[1]
            name = clean_html(name_html)

            # Extract email using decoding of obfuscated spambot script or plain text
            email = None
            if "spambot" in email_html or "cloak" in email_html:
                email = decode_spambot_email(email_html)

            if not email:
                email_match = re.search(r'href="mailto:([\w\.\-]+@ufabc\.edu\.br)"', email_html, re.IGNORECASE)
                if email_match:
                    email = email_match.group(1)
                else:
                    plain_email_match = re.search(r'([\w\.\-]+@ufabc\.edu\.br)', clean_html(email_html), re.IGNORECASE)
                    if plain_email_match:
                        email = plain_email_match.group(1)

            if name and name != "Nome" and email:
                cecs_docentes.append({
                    "nome": name,
                    "email": email.strip().lower(),
                    "centro": "CECS",
                    "url_fonte": url
                })
    print(f"Mapeados {len(cecs_docentes)} docentes do CECS.")
    return cecs_docentes

def scrape_sigaa_programas():
    programs = {
        "PPGCC": 198,
        "PPGEE": 206,
        "PPGEM": 207,
        "PPGMAT": 213,
        "PPGFIS": 212,
        "PPGBIS": 196,
        "PPGBTC": 197,
        "PPGCTQ": 199,
        "PPGNCG": 195,
        "PPGPPU": 217,
        "PEHCM": 209,
        "PPGEBM": 203
    }

    sigaa_docentes = []

    for prog, prog_id in programs.items():
        print(f"Scraping SIGAA program {prog} (ID {prog_id})...")
        url = f"https://sig.ufabc.edu.br/sigaa/public/programa/equipe.jsf?lc=pt_BR&id={prog_id}"
        html = fetch_url(url)
        if not html:
            continue

        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
        for row in rows:
            mailto_match = re.search(r'href="mailto:([\w\.\-]+@(?:[\w\-]+\.)*ufabc\.edu\.br)"', row, re.IGNORECASE)
            if mailto_match:
                email = mailto_match.group(1).strip().lower()

                lattes = "Não Disponível"
                lattes_match = re.search(r'href="(http://lattes\.cnpq\.br/\d+|http://buscatextual\.cnpq\.br/[^"]+)"', row, re.IGNORECASE)
                if lattes_match:
                    lattes = lattes_match.group(1)

                tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
                if len(tds) >= 3:
                    name = clean_html(tds[0])
                    vinculo = clean_html(tds[1])
                    nivel = clean_html(tds[2])

                    name = re.sub(r'^\s*-\s*', '', name)
                    name = name.strip()

                    if name and name != "Nome":
                        sigaa_docentes.append({
                            "nome": name,
                            "email": email,
                            "programa": prog,
                            "vinculo": vinculo,
                            "nivel": nivel,
                            "lattes": lattes,
                            "url_fonte": url
                        })

    print(f"Mapeados {len(sigaa_docentes)} docentes através do SIGAA.")
    return sigaa_docentes

def fetch_email_from_profile(doc):
    url = doc['url']
    html = fetch_url(url, retries=2)
    if not html:
        return doc['nome'], None, "Não Disponível"

    # Try decoding of spambot obfuscated email
    email = decode_spambot_email(html)
    if not email:
        # Check for plain mailto
        m = re.search(r'href="mailto:([\w\.\-]+@ufabc\.edu\.br)"', html, re.IGNORECASE)
        if m:
            email = m.group(1)
        else:
            # Check for plain text email
            m2 = re.search(r'E-mail:\s*([\w\.\-]+@ufabc\.edu\.br)', html, re.IGNORECASE)
            if m2:
                email = m2.group(1)

    # Extract Lattes link
    lattes = "Não Disponível"
    lattes_match = re.search(r'href="(http://lattes\.cnpq\.br/\d+|http://buscatextual\.cnpq\.br/[^"]+)"', html, re.IGNORECASE)
    if lattes_match:
        lattes = lattes_match.group(1)

    return doc['nome'], email, lattes

def main():
    print("Iniciando a raspagem da UFABC...")

    docentes_geral = scrape_docentes_geral()
    cecs_docentes = scrape_cecs_docentes()
    sigaa_docentes = scrape_sigaa_programas()

    # Combine verified emails to see what's missing
    emails_by_name = {}
    lattes_by_name = {}
    for item in cecs_docentes:
        emails_by_name[item['nome'].lower().strip()] = item['email']
    for item in sigaa_docentes:
        emails_by_name[item['nome'].lower().strip()] = item['email']
        if item['lattes'] != "Não Disponível":
            lattes_by_name[item['nome'].lower().strip()] = item['lattes']

    # Find which ones from the general list are still missing emails
    missing = [doc for doc in docentes_geral if doc['nome'].lower().strip() not in emails_by_name]
    print(f"Docentes com e-mails ausentes: {len(missing)}")

    # Concurrently fetch individual profile pages
    fetched_emails = []
    print("Iniciando a busca concorrente de e-mails nos perfis individuais...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(fetch_email_from_profile, missing))

    for name, email, lattes in results:
        if email:
            emails_by_name[name.lower().strip()] = email
        if lattes != "Não Disponível":
            lattes_by_name[name.lower().strip()] = lattes

    # Enrich the general list with discovered emails and lattes links
    enriched_geral = []
    for doc in docentes_geral:
        key = doc['nome'].lower().strip()
        email = emails_by_name.get(key, "Não Disponível")
        lattes = lattes_by_name.get(key, "Não Disponível")
        enriched_geral.append({
            "nome": doc['nome'],
            "area": doc['area'],
            "centro": doc['centro'],
            "email": email,
            "lattes": lattes,
            "url_fonte": doc['url']
        })

    # Save raw outputs
    with open("docentes_geral_raw.json", "w", encoding="utf-8") as f:
        json.dump(enriched_geral, f, ensure_ascii=False, indent=2)

    with open("cecs_docentes_raw.json", "w", encoding="utf-8") as f:
        json.dump(cecs_docentes, f, ensure_ascii=False, indent=2)

    with open("sigaa_docentes_raw.json", "w", encoding="utf-8") as f:
        json.dump(sigaa_docentes, f, ensure_ascii=False, indent=2)

    print(f"Raspagem concluída. Total de e-mails mapeados: {len([x for x in enriched_geral if x['email'] != 'Não Disponível'])} de {len(enriched_geral)} docentes.")

if __name__ == "__main__":
    main()
