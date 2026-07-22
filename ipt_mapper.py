import requests
from bs4 import BeautifulSoup
import json
import os
import time
import concurrent.futures

def fetch_html(url):
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                return r.text
        except Exception as e:
            time.sleep(1)
    return None

def crawl_somos():
    base_url = "https://somos.ipt.br"
    index_url = "https://somos.ipt.br/indicadores"

    print("Starting crawl from indicators page...")
    html = fetch_html(index_url)
    if not html:
        print("Error accessing index page.")
        return []

    soup = BeautifulSoup(html, 'html.parser')
    centers = []
    for a in soup.find_all('a', href=True):
        if '/unidades_academicas/view/' in a['href']:
            center_id = a['href'].split('/')[-1]
            center_name = a.text.strip()
            centers.append((center_id, center_name))

    print(f"Found {len(centers)} Academic Centers (unidades acadêmicas).")

    # We want to parallelize the crawling of center pages to discover all labs/sectors
    print("\nDiscovering labs/sectors in parallel...")
    labs_to_crawl = []

    def process_center(center_id, center_name):
        center_url = f"{base_url}/unidades_academicas/view/{center_id}"
        html_center = fetch_html(center_url)
        if not html_center:
            return []
        soup_center = BeautifulSoup(html_center, 'html.parser')
        center_labs = []
        for a in soup_center.find_all('a', href=True):
            if '/setores_academicos/view/' in a['href']:
                lab_id = a['href'].split('/')[-1]
                li = a.find_parent('li')
                lab_name = ""
                if li:
                    first_a = li.find('a')
                    if first_a:
                        lab_name = first_a.text.strip()
                if not lab_name:
                    lab_name = a.text.strip()
                lab_name = lab_name.replace('+', '').strip()
                if lab_name.endswith('mais informações sobre este departamento'):
                    lab_name = lab_name.replace('mais informações sobre este departamento', '').strip()
                center_labs.append((lab_id, lab_name, center_name))
        return center_labs

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_center = {executor.submit(process_center, cid, cname): (cid, cname) for cid, cname in centers}
        for future in concurrent.futures.as_completed(future_to_center):
            res = future.result()
            labs_to_crawl.extend(res)

    # Deduplicate labs by ID
    unique_labs = []
    seen_lab_ids = set()
    for l_id, l_name, c_name in labs_to_crawl:
        if l_id not in seen_lab_ids:
            seen_lab_ids.add(l_id)
            unique_labs.append((l_id, l_name, c_name))

    print(f"Total unique sectors/laboratories discovered: {len(unique_labs)}")

    # Discover all professors/researchers in parallel
    print("\nDiscovering researchers in parallel...")
    prof_to_crawl = []

    def process_lab(lab_id, lab_name, center_name):
        lab_url = f"{base_url}/setores_academicos/view/{lab_id}"
        html_lab = fetch_html(lab_url)
        if not html_lab:
            return []
        soup_lab = BeautifulSoup(html_lab, 'html.parser')
        lab_profs = []
        for a in soup_lab.find_all('a', href=True):
            if '/professores/view/' in a['href']:
                prof_id = a['href'].split('/')[-1]
                prof_name = a.text.strip()
                lab_profs.append((prof_id, prof_name, lab_name, center_name))
        return lab_profs

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_lab = {executor.submit(process_lab, lid, lname, cname): (lid, lname, cname) for lid, lname, cname in unique_labs}
        for future in concurrent.futures.as_completed(future_to_lab):
            res = future.result()
            prof_to_crawl.extend(res)

    # Deduplicate professors by ID
    unique_profs = []
    seen_prof_ids = set()
    for pid, pname, lname, cname in prof_to_crawl:
        if pid not in seen_prof_ids:
            seen_prof_ids.add(pid)
            unique_profs.append((pid, pname, lname, cname))

    print(f"Total unique researchers discovered: {len(unique_profs)}")

    # Crawl individual professor profiles in parallel
    print("\nCrawling researcher profiles in parallel...")
    scraped_records = []

    def process_prof(prof_id, prof_name, lab_name, center_name):
        prof_url = f"{base_url}/professores/view/{prof_id}"
        html_prof = fetch_html(prof_url)
        if not html_prof:
            return None
        soup_prof = BeautifulSoup(html_prof, 'html.parser')

        # Find Lattes URL
        lattes_a = soup_prof.find('a', href=lambda h: h and 'lattes.cnpq.br' in h)
        lattes_url = lattes_a['href'] if lattes_a else "Não disponível"

        # Specialties
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

        return {
            "nome": prof_name,
            "id": prof_id,
            "unidade": center_name,
            "laboratorio": lab_name,
            "lattes": lattes_url,
            "especialidade": specialty_str,
            "url_fonte": prof_url,
            "data_acesso": "2026-05-30"
        }

    # Crawl in parallel with max_workers=20 to speed up but be safe
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_prof = {executor.submit(process_prof, pid, pname, lname, cname): pid for pid, pname, lname, cname in unique_profs}
        for future in concurrent.futures.as_completed(future_to_prof):
            res = future.result()
            if res:
                scraped_records.append(res)
                if len(scraped_records) % 50 == 0:
                    print(f"  Crawled {len(scraped_records)} of {len(unique_profs)} profiles...")

    # Save raw scrape
    with open("raw_somos_scrape.json", "w", encoding="utf-8") as f:
        json.dump(scraped_records, f, ensure_ascii=False, indent=2)

    print(f"\nScraping complete! Total records collected: {len(scraped_records)}")
    return scraped_records

if __name__ == "__main__":
    crawl_somos()
