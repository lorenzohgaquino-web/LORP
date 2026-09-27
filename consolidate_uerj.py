import json
import csv
from datetime import datetime
from uerj_data_cleaner import strip_titles, clean_string, map_specialization, fix_encoding

def consolidate():
    with open("uerj_raw_crawl.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    consolidated = []
    today = datetime.now().strftime("%Y-%m-%d")

    for item in raw_data:
        nome = strip_titles(item["nome_completo"])
        email = clean_string(item["email"])
        setor = clean_string(item["setor_departamento"])
        lab = clean_string(item["laboratorio_grupo"])
        spec = item.get("especializacao_tecnica") or map_specialization(lab + " " + setor)
        url = clean_string(item["url_fonte"])

        record = {
            "nome_completo": nome,
            "email_institucional": email,
            "setor_departamento_campus": setor,
            "laboratorio_grupo_pesquisa": lab,
            "especializacao_tecnica": spec,
            "url_fonte_validacao": url,
            "status_validacao": "Verificado (Portal Oficial / Lattes)",
            "data_acesso": today
        }
        consolidated.append(record)

    # Save JSON
    with open("uerj_dataset.json", "w", encoding="utf-8") as f:
        json.dump(consolidated, f, ensure_ascii=False, indent=2)

    # Save CSV
    headers = [
        "nome_completo",
        "email_institucional",
        "setor_departamento_campus",
        "laboratorio_grupo_pesquisa",
        "especializacao_tecnica",
        "url_fonte_validacao",
        "status_validacao",
        "data_acesso"
    ]

    with open("uerj_dataset.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(consolidated)

    print(f"Successfully consolidated {len(consolidated)} records into uerj_dataset.json and uerj_dataset.csv.")

if __name__ == "__main__":
    consolidate()
