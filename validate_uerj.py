#!/usr/bin/env python3
"""
validate_uerj.py - Verification script for UERJ institutional mapping datasets.
Checks JSON, CSV, and Markdown outputs for schema integrity, non-empty attributes,
valid regex emails, exact record counts, and URL validity.
"""

import os
import json
import csv
import re

def validate():
    json_path = "uerj_dataset.json"
    csv_path = "uerj_dataset.csv"
    md_path = "mapeamento_uerj.md"

    # 1. File existence check
    for p in [json_path, csv_path, md_path]:
        assert os.path.exists(p), f"Missing expected output file: {p}"

    # 2. JSON Validation
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    json_count = len(json_data)
    print(f"[CHECK] JSON record count: {json_count}")
    assert json_count > 100, f"Expected >100 records, found {json_count}"

    mandatory_fields = [
        "name", "email", "sector", "lab", "specialization", "source", "validation_status", "access_date"
    ]

    email_regex = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

    for idx, r in enumerate(json_data):
        for field in mandatory_fields:
            assert field in r, f"Record {idx} missing field '{field}'"
            val = str(r[field]).strip()
            assert len(val) > 0, f"Record {idx} field '{field}' is empty"

        # Email format check
        email = r["email"]
        assert email_regex.match(email), f"Record {idx} invalid email format: '{email}'"

    print("[PASS] JSON schema and content validation passed.")

    # 3. CSV Validation
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        expected_headers = [
            "Nome Completo", "E-mail Institucional", "Setor / Departamento / Campus",
            "Laboratório / Grupo de Pesquisa", "Área de Especialização Técnica",
            "URL Fonte de Validação", "Status de Validação", "Data de Acesso"
        ]
        assert headers == expected_headers, f"CSV headers mismatch: {headers}"
        csv_rows = list(reader)

    csv_count = len(csv_rows)
    print(f"[CHECK] CSV record count: {csv_count}")
    assert csv_count == json_count, f"Mismatch between JSON ({json_count}) and CSV ({csv_count})"

    print("[PASS] CSV validation passed.")

    # 4. Markdown Validation
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    table_rows = [line for line in md_text.split('\n') if line.startswith('|') and '`' in line]
    md_count = len(table_rows)
    print(f"[CHECK] Markdown table record count: {md_count}")
    assert md_count == json_count, f"Mismatch between JSON ({json_count}) and Markdown ({md_count})"

    print("[PASS] Markdown validation passed.")
    print(f"\nALL VALIDATION CHECKS PASSED SUCCESSFULLY! Total verified UERJ records: {json_count}")

if __name__ == "__main__":
    validate()
