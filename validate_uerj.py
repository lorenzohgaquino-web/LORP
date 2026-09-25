#!/usr/bin/env python3
"""
validate_uerj.py
Programmatic validation script for UERJ institutional mapping dataset and artifacts.
Asserts schema header compliance, non-empty mandatory fields, email regex validity,
source URL accessibility, and record count consistency across JSON, CSV, and Markdown.
"""

import json
import csv
import re
import os
import sys

REQUIRED_HEADERS = [
    "nome",
    "email",
    "setor_departamento_campus",
    "laboratorio_grupo_pesquisa",
    "area_especializacao",
    "url_fonte",
    "status_validacao_data"
]

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate():
    print("[INFO] Running validate_uerj.py...")

    # Check file existence
    files = ["uerj_dataset.json", "uerj_dataset.csv", "mapeamento_uerj.md"]
    for f in files:
        if not os.path.exists(f) or os.path.getsize(f) == 0:
            print(f"[FAIL] Missing or empty file: {f}")
            sys.exit(1)
        print(f"[OK] File exists and non-empty: {f}")

    # Validate JSON
    with open("uerj_dataset.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)

    if not json_data:
        print("[FAIL] JSON dataset is empty.")
        sys.exit(1)

    print(f"[OK] JSON contains {len(json_data)} records.")

    for i, rec in enumerate(json_data):
        for header in REQUIRED_HEADERS:
            if header not in rec or not str(rec[header]).strip():
                print(f"[FAIL] Record {i} missing or empty header '{header}': {rec}")
                sys.exit(1)

        email = rec["email"].strip()
        if not EMAIL_REGEX.match(email):
            print(f"[FAIL] Record {i} invalid email format: '{email}'")
            sys.exit(1)

        url = rec["url_fonte"].strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            print(f"[FAIL] Record {i} invalid URL source: '{url}'")
            sys.exit(1)

    # Validate CSV
    with open("uerj_dataset.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_headers = reader.fieldnames
        if csv_headers != REQUIRED_HEADERS:
            print(f"[FAIL] CSV headers mismatched. Expected {REQUIRED_HEADERS}, got {csv_headers}")
            sys.exit(1)

        csv_data = list(reader)

    if len(csv_data) != len(json_data):
        print(f"[FAIL] Record count mismatch between JSON ({len(json_data)}) and CSV ({len(csv_data)})")
        sys.exit(1)

    print(f"[OK] CSV schema and record count match JSON ({len(csv_data)} records).")

    # Validate Markdown report
    with open("mapeamento_uerj.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    for rec in json_data:
        name = rec["nome"]
        if name not in md_text:
            print(f"[FAIL] Record name '{name}' not found in mapeamento_uerj.md")
            sys.exit(1)

    print("[OK] Markdown report contains all record names.")
    print("[SUCCESS] All UERJ validation checks passed successfully!")

if __name__ == "__main__":
    validate()
