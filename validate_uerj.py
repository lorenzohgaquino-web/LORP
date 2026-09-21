import json
import csv
import re
import os

def validate():
    print("Starting validation suite for UERJ dataset artifacts...")

    # 1. File existence checks
    json_path = 'uerj_dataset.json'
    csv_path = 'uerj_dataset.csv'
    md_path = 'mapeamento_uerj.md'

    assert os.path.exists(json_path), f"Missing {json_path}"
    assert os.path.exists(csv_path), f"Missing {csv_path}"
    assert os.path.exists(md_path), f"Missing {md_path}"

    # 2. JSON schema & non-empty checks
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    assert isinstance(json_data, list), "JSON data must be a list"
    assert len(json_data) > 30, f"Expected >30 records, found {len(json_data)}"

    expected_fields = [
        "nome",
        "email",
        "setor_departamento_campus",
        "laboratorio_grupo",
        "especializacao",
        "url_fonte",
        "status_validacao"
    ]

    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    for i, row in enumerate(json_data):
        for field in expected_fields:
            assert field in row, f"Record {i} missing field {field}"
            val = str(row[field]).strip()
            assert len(val) > 0, f"Record {i} field {field} is empty"

        # Email format check
        email = row['email'].strip()
        assert email_regex.match(email), f"Record {i} invalid email format: {email}"

        # Source URL check
        url = row['url_fonte'].strip()
        assert url.startswith('http://') or url.startswith('https://'), f"Record {i} invalid URL: {url}"

    print(f"JSON validation passed successfully ({len(json_data)} records checked).")

    # 3. CSV header and count alignment
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    assert reader.fieldnames == expected_fields, f"CSV headers mismatch: {reader.fieldnames}"
    assert len(csv_rows) == len(json_data), f"CSV record count ({len(csv_rows)}) mismatch with JSON ({len(json_data)})"

    print("CSV validation passed successfully.")

    # 4. Markdown content & table check
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    assert "# Mapeamento Institucional" in md_text, "Markdown header missing"
    assert "| Nome | E-mail | Setor / Departamento / Campus |" in md_text, "Markdown table header missing"

    print("Markdown report validation passed successfully.")
    print("ALL VALIDATION CHECKS PASSED PERFECTLY!")

if __name__ == "__main__":
    validate()
