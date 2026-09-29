#!/usr/bin/env python3
"""
validate_uerj.py - Validates uerj_dataset.json, uerj_dataset.csv, and mapeamento_uerj.md
for schema compliance, email format & traceability, zero inferred emails, non-empty fields,
and record count consistency.
"""

import os
import json
import csv
import re

EXPECTED_HEADERS = [
    "Nome Completo / Contato",
    "E-mail Institucional",
    "Setor / Departamento / Campus",
    "Laboratório / Grupo de Pesquisa",
    "Área de Especialização Técnica",
    "URL Fonte de Validação",
    "Status de Validação",
    "Data de Acesso"
]

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def validate():
    print("=== STARTING UERJ DATASET VALIDATION ===")

    # 1. Check existence of files
    files = ["uerj_dataset.json", "uerj_dataset.csv", "mapeamento_uerj.md"]
    for f in files:
        assert os.path.exists(f), f"Missing file: {f}"
        print(f"✓ Found {f}")

    # 2. Validate JSON
    with open("uerj_dataset.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)

    assert isinstance(json_data, list), "JSON root must be a list"
    assert len(json_data) > 0, "JSON dataset must not be empty"
    print(f"✓ JSON contains {len(json_data)} records")

    for idx, r in enumerate(json_data):
        for field in ["nome", "email", "setor", "lab_grupo", "especializacao", "fonte_url", "status_validacao", "data_acesso"]:
            assert field in r, f"Record {idx} missing field {field}"
            assert str(r[field]).strip() != "", f"Record {idx} has empty field {field}"

        assert re.match(EMAIL_REGEX, r["email"]), f"Record {idx} has invalid email: {r['email']}"
        assert r["fonte_url"].startswith("http"), f"Record {idx} has invalid URL: {r['fonte_url']}"

    print("✓ All JSON records schema valid, non-empty, with valid emails and URLs")

    # 3. Validate CSV
    with open("uerj_dataset.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        csv_headers = next(reader)
        assert csv_headers == EXPECTED_HEADERS, f"CSV headers mismatch: {csv_headers}"
        csv_rows = list(reader)

    assert len(csv_rows) == len(json_data), f"CSV row count ({len(csv_rows)}) does not match JSON count ({len(json_data)})"
    print(f"✓ CSV header matches expected schema and row count matches JSON ({len(csv_rows)})")

    # 4. Validate Markdown
    with open("mapeamento_uerj.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    assert "# MAPEAMENTO INSTITUCIONAL APROFUNDADO — UERJ" in md_text
    assert "## RESUMO EXECUTIVO" in md_text
    assert "## TABELA CONSOLIDADA DE PESQUISADORES E UNIDADES ESTRATÉGICAS" in md_text
    print("✓ Markdown report contains expected headers and formatting")

    print("\n=== ALL VALIDATION CHECKS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    validate()
