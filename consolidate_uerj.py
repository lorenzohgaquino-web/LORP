import json
import csv
import re
from uerj_crawler import build_uerj_records

REQUIRED_FIELDS = [
    "nome",
    "email",
    "setor_departamento_campus",
    "laboratorio_grupo",
    "especializacao_tecnica",
    "url_fonte",
    "status_validacao",
    "data_acesso"
]

def clean_string(val):
    if not val:
        return ""
    # Normalize spaces
    val = re.sub(r'\s+', ' ', str(val)).strip()
    return val

def consolidate():
    raw_records = build_uerj_records()
    clean_records = []

    seen_keys = set()

    for rec in raw_records:
        cleaned = {}
        for k in REQUIRED_FIELDS:
            cleaned[k] = clean_string(rec.get(k, ""))

        # Deduplication key: (nome, setor)
        dedup_key = (cleaned["nome"].lower(), cleaned["setor_departamento_campus"].lower())
        if dedup_key in seen_keys:
            continue
        seen_keys.add(dedup_key)

        # Validate email strictly (valid regex or fallback string)
        email = cleaned["email"]
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            if not email:
                cleaned["email"] = "Não disponível publicamente"

        clean_records.append(cleaned)

    # Save to JSON
    with open('uerj_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(clean_records, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(clean_records)} records to uerj_dataset.json")

    # Save to CSV
    with open('uerj_dataset.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_FIELDS)
        writer.writeheader()
        writer.writerows(clean_records)
    print(f"Saved {len(clean_records)} records to uerj_dataset.csv")

if __name__ == '__main__':
    consolidate()
