import requests
from bs4 import BeautifulSoup
import json
import time

def fetch_html(url):
    for attempt in range(5):
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                return r.text
        except Exception as e:
            time.sleep(2)
    return None

def main():
    base_url = "https://somos.ipt.br"
    missing_labs = [
        # ENERGIA
        {"id": "23", "name": "LABORATÓRIO DE INFRAESTRUTURA EM ENERGIA", "center": "ENERGIA"},
        {"id": "4", "name": "LABORATÓRIO DE BIOENERGIA E EFICIÊNCIA ENERGÉTICA", "center": "ENERGIA"},
        {"id": "33", "name": "LABORATÓRIO DE USOS FINAIS E GESTÃO EM ENERGIA", "center": "ENERGIA"},

        # BIONANOMANUFATURA
        {"id": "20", "name": "LABORATÓRIO DE BIOTECNOLOGIA INDUSTRIAL", "center": "BIONANOMANUFATURA"},
        {"id": "18", "name": "LABORATÓRIO DE TECNOLOGIA TÊXTIL E PRODUTOS DE PROTEÇÃO", "center": "BIONANOMANUFATURA"},
        {"id": "40", "name": "LABORATÓRIO DE PROCESSOS QUÍMICOS E TECNOLOGIA DE PARTÍCULAS", "center": "BIONANOMANUFATURA"},
        {"id": "19", "name": "LABORATÓRIO DE MICROMANUFATURA", "center": "BIONANOMANUFATURA"},
    ]

    extra_records = []

    for lab in missing_labs:
        print(f"Crawling missing lab: {lab['name']}...")
        lab_url = f"{base_url}/setores_academicos/view/{lab['id']}"
        html = fetch_html(lab_url)
        if not html:
            print(f"Failed to fetch lab: {lab['name']}")
            continue

        soup = BeautifulSoup(html, 'html.parser')
        prof_links = []
        for a in soup.find_all('a', href=True):
            if '/professores/view/' in a['href'] and a.text.strip():
                prof_links.append((a['href'].split('/')[-1], a.text.strip()))

        print(f"  Found {len(prof_links)} active professors in {lab['name']}.")

        for p_id, p_name in prof_links:
            prof_url = f"{base_url}/professores/view/{p_id}"
            html_prof = fetch_html(prof_url)
            if not html_prof:
                print(f"    Failed to fetch prof: {p_name}")
                continue

            soup_prof = BeautifulSoup(html_prof, 'html.parser')
            lattes_a = soup_prof.find('a', href=lambda h: h and 'lattes.cnpq.br' in h)
            lattes_url = lattes_a['href'] if lattes_a else "Não disponível"

            specialties = []
            for li in soup_prof.find_all('li', class_='listagem'):
                a_spec = li.find('a', class_='nomeEspecialidade')
                if a_spec:
                    span_texts = [span.text for span in a_spec.find_all('span')]
                    full_text = a_spec.text.strip()
                    for span_t in span_texts:
                        full_text = full_text.replace(span_t, '')
                    full_text = full_text.strip().replace('+', '')
                    if full_text:
                        specialties.append(full_text)

            specialty_str = ', '.join(specialties) if specialties else "Geral / Não especificado"

            record = {
                "nome": p_name,
                "id": p_id,
                "unidade": lab["center"],
                "laboratorio": lab["name"],
                "lattes": lattes_url,
                "especialidade": specialty_str,
                "url_fonte": prof_url,
                "data_acesso": "2026-05-30"
            }
            extra_records.append(record)
            print(f"    Crawled: {p_name}")
            time.sleep(0.1)

    # Load raw_somos_scrape.json if exists
    all_records = []
    try:
        with open("raw_somos_scrape.json", "r", encoding="utf-8") as f:
            all_records = json.load(f)
    except Exception:
        pass

    # Merge and deduplicate by 'id'
    seen_ids = set()
    merged_records = []
    for r in all_records + extra_records:
        if r["id"] not in seen_ids:
            seen_ids.add(r["id"])
            merged_records.append(r)

    with open("raw_somos_scrape.json", "w", encoding="utf-8") as f:
        json.dump(merged_records, f, ensure_ascii=False, indent=2)

    print(f"\nComplementary crawl completed! Total merged records in raw_somos_scrape.json: {len(merged_records)}")

if __name__ == "__main__":
    main()
