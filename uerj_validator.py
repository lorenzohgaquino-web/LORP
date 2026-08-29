"""
uerj_validator.py - Automated validation script for UERJ dataset artifacts.
Checks JSON, CSV, and Markdown report for schema completeness, email formatting,
URL validity, non-empty fields, and count consistency.
"""

import json
import csv
import re
import sys

REQUIRED_FIELDS = [
    "nome_completo",
    "email_institucional",
    "setor_departamento_campus",
    "laboratorio_grupo_pesquisa",
    "area_especializacao_tecnica",
    "url_fonte_validacao",
    "status_validacao",
    "data_acesso"
]

def validate_uerj_data():
    print("=== STARTING UERJ DATASET VALIDATION ===")
    errors = []

    # 1. Validate JSON
    json_file = "uerj_dataset.json"
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            json_records = json.load(f)
        print(f"[OK] JSON loaded successfully: {len(json_records)} records.")
    except Exception as e:
        errors.append(f"Failed to read/parse {json_file}: {e}")
        json_records = []

    # Validate JSON schema and rules
    for idx, record in enumerate(json_records):
        for field in REQUIRED_FIELDS:
            if field not in record:
                errors.append(f"Record {idx} missing required field '{field}'")
            elif not str(record[field]).strip():
                errors.append(f"Record {idx} has empty field '{field}'")

        email = record.get("email_institucional", "")
        if "@" not in email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append(f"Record {idx} ({record.get('nome_completo')}) has invalid email: '{email}'")

        url = record.get("url_fonte_validacao", "")
        if not url.startswith("http://") and not url.startswith("https://"):
            errors.append(f"Record {idx} ({record.get('nome_completo')}) has invalid URL: '{url}'")

    # 2. Validate CSV
    csv_file = "uerj_dataset.csv"
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
        print(f"[OK] CSV loaded successfully: {len(reader)} records.")

        if len(reader) != len(json_records):
            errors.append(f"Record count mismatch: JSON ({len(json_records)}) vs CSV ({len(reader)})")

        if reader:
            csv_headers = list(reader[0].keys())
            if csv_headers != REQUIRED_FIELDS:
                errors.append(f"CSV headers mismatch. Expected {REQUIRED_FIELDS}, got {csv_headers}")
    except Exception as e:
        errors.append(f"Failed to read/parse {csv_file}: {e}")

    # 3. Validate Markdown Table
    md_file = "mapeamento_uerj.md"
    try:
        with open(md_file, "r", encoding="utf-8") as f:
            md_content = f.read()

        # Count data rows in markdown table
        table_lines = [line for line in md_content.splitlines() if line.startswith("| **")]
        print(f"[OK] Markdown table parsed: {len(table_lines)} data rows found.")

        if len(table_lines) != len(json_records):
            errors.append(f"Record count mismatch: JSON ({len(json_records)}) vs Markdown Table ({len(table_lines)})")

    except Exception as e:
        errors.append(f"Failed to read {md_file}: {e}")

    # Summary
    print("\n=== VALIDATION RESULTS ===")
    if errors:
        print(f"FAILED with {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(f"SUCCESS! All {len(json_records)} records strictly validated across JSON, CSV, and Markdown.")
        sys.exit(0)

if __name__ == "__main__":
    validate_uerj_data()
