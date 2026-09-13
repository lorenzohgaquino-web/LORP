import json
import csv
import re
import os

REQUIRED_FIELDS = [
    "nome_completo",
    "email_institucional",
    "setor_departamento_campus",
    "laboratorio_grupo_pesquisa",
    "especializacao_tecnica",
    "url_fonte_validacao",
    "status_validacao",
    "data_acesso"
]

def validate():
    print("=== RUNNING UERJ DATASET VALIDATION ===")

    # Check files exist
    files = ["uerj_dataset.json", "uerj_dataset.csv", "mapeamento_uerj.md"]
    for f in files:
        if not os.path.exists(f):
            print(f"FAILED: File {f} does not exist.")
            return False

    # Validate JSON
    with open("uerj_dataset.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)

    print(f"JSON Record Count: {len(json_data)}")
    if len(json_data) == 0:
        print("FAILED: JSON dataset is empty.")
        return False

    for idx, record in enumerate(json_data):
        for field in REQUIRED_FIELDS:
            if field not in record:
                print(f"FAILED: Record {idx} missing field {field}.")
                return False
            if not str(record[field]).strip():
                print(f"FAILED: Record {idx} field {field} is empty.")
                return False

        # Validate email format (must contain @ and valid domain or fallback tag)
        email = record["email_institucional"]
        if "@" not in email:
            print(f"FAILED: Invalid email format at record {idx}: {email}")
            return False

    # Validate CSV
    with open("uerj_dataset.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_records = list(reader)

    print(f"CSV Record Count: {len(csv_records)}")
    if len(csv_records) != len(json_data):
        print(f"FAILED: CSV count ({len(csv_records)}) does not match JSON count ({len(json_data)}).")
        return False

    # Validate Markdown
    with open("mapeamento_uerj.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    table_rows = [line for line in md_text.splitlines() if line.startswith("| ") and not line.startswith("| Nome Completo") and not line.startswith("| :---")]
    print(f"Markdown Table Rows: {len(table_rows)}")
    if len(table_rows) != len(json_data):
        print(f"FAILED: Markdown table row count ({len(table_rows)}) does not match JSON count ({len(json_data)}).")
        return False

    print("=== VALIDATION SUCCESSFUL: ALL CHECKS PASSED ===")
    return True

if __name__ == "__main__":
    success = validate()
    if not success:
        exit(1)
