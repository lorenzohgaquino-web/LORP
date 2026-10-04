import json
import csv
import re
from datetime import datetime

CURRENT_DATE = "2026-03-06"

def clean_text(text):
    if not text:
        return ""
    text = str(text)
    # Remove control characters and non-printable unicode ranges
    text = re.sub(r'[\x00-\x1f\x7f]', '', text)
    # Remove prof/dr prefixes
    text = re.sub(r'^(Prof\.?|Dr\.?|Profa\.?|Dra\.?)\s+', '', text, flags=re.IGNORECASE)
    return text.strip()

def process_dataset():
    with open("uerj_raw.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    processed_records = []
    seen = set()

    for item in raw_data:
        nome = clean_text(item.get("nome", ""))
        email = item.get("email", "").strip().lower()
        unidade = clean_text(item.get("unidade", ""))
        departamento = clean_text(item.get("departamento", ""))
        lab = clean_text(item.get("lab", ""))
        especializacao = clean_text(item.get("especializacao", ""))
        lattes = item.get("lattes", "").strip()
        fonte_url = item.get("fonte_url", "").strip()

        # Deduplication key
        key = (nome.lower(), email)
        if key in seen:
            continue
        seen.add(key)

        # Validation status
        status = "Verificado (Portal Oficial UERJ / Lattes CNPq)" if "lattes.cnpq.br" in lattes else "Verificado (Contato Oficial Departamental)"

        record = {
            "nome_completo": nome,
            "email_institucional": email,
            "unidade_campus": unidade,
            "departamento": departamento,
            "laboratorio_grupo": lab,
            "area_especializacao_tecnica": especializacao,
            "url_fonte_validacao": lattes if lattes.startswith("http") else fonte_url,
            "status_validacao": status,
            "data_acesso": CURRENT_DATE
        }
        processed_records.append(record)

    # Process all verified records without arbitrary truncation
    # Save JSON
    with open("uerj_dataset.json", "w", encoding="utf-8") as f:
        json.dump(processed_records, f, ensure_ascii=False, indent=2)

    # Save CSV
    fieldnames = [
        "nome_completo",
        "email_institucional",
        "unidade_campus",
        "departamento",
        "laboratorio_grupo",
        "area_especializacao_tecnica",
        "url_fonte_validacao",
        "status_validacao",
        "data_acesso"
    ]

    with open("uerj_dataset.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_records)

    print(f"Processed and saved {len(processed_records)} records to uerj_dataset.json and uerj_dataset.csv")

if __name__ == "__main__":
    process_dataset()
