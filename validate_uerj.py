import json
import csv
import re
import os
import sys

def validate_dataset():
    print("=== STARTING UERJ DATASET VALIDATION ===")

    json_path = "uerj_dataset.json"
    csv_path = "uerj_dataset.csv"
    md_path = "mapeamento_uerj.md"

    # Check file existence
    for path in [json_path, csv_path, md_path]:
        if not os.path.exists(path):
            print(f"FAILED: File {path} does not exist!")
            sys.exit(1)
        if os.path.getsize(path) == 0:
            print(f"FAILED: File {path} is empty!")
            sys.exit(1)

    print("[OK] Output files exist and are non-empty.")

    # 1. Validate JSON
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    expected_fields = [
        "Nome", "E-mail", "Setor_Departamento_Campus", "Laboratorio_Grupo",
        "Especializacao_Tecnica", "URL_Fonte", "Status_Validacao", "Data_Acesso"
    ]

    if len(records) < 50:
        print(f"FAILED: Record count too low ({len(records)})")
        sys.exit(1)

    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(,\s*[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})*$')

    for idx, r in enumerate(records):
        for field in expected_fields:
            if field not in r:
                print(f"FAILED: Record #{idx} missing field '{field}'")
                sys.exit(1)
            if not str(r[field]).strip():
                print(f"FAILED: Record #{idx} has empty field '{field}'")
                sys.exit(1)

        # Email format check
        email = r["E-mail"].strip()
        if not email_regex.match(email):
            print(f"FAILED: Record #{idx} ('{r['Nome']}') has invalid email format: '{email}'")
            sys.exit(1)

    print(f"[OK] JSON validation passed with {len(records)} verified records.")

    # 2. Validate CSV header and row count
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        csv_rows = list(reader)

    csv_headers = csv_rows[0]
    if csv_headers != expected_fields:
        print(f"FAILED: CSV headers mismatch. Expected {expected_fields}, got {csv_headers}")
        sys.exit(1)

    if len(csv_rows) - 1 != len(records):
        print(f"FAILED: CSV row count ({len(csv_rows)-1}) does not match JSON record count ({len(records)})")
        sys.exit(1)

    print("[OK] CSV validation passed.")

    # 3. Validate Markdown table
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    if "# MAPEAMENTO INSTITUCIONAL APROFUNDADO — UERJ" not in md_content:
        print("FAILED: Markdown report title missing.")
        sys.exit(1)

    if "| Nome | E-mail |" not in md_content:
        print("FAILED: Markdown table header missing.")
        sys.exit(1)

    print("[OK] Markdown validation passed.")
    print("=== ALL UERJ VALIDATION CHECKS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    validate_dataset()
