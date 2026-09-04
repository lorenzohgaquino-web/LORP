#!/usr/bin/env python3
"""
validate_uerj.py
Validation script to check schema conformity, mandatory non-empty fields, email regex format,
and record count consistency across uerj_dataset.json, uerj_dataset.csv, and mapeamento_uerj.md.
"""

import json
import csv
import re
import sys

EXPECTED_FIELDS = [
    'Nome Completo',
    'E-mail Institutional Publico',
    'Setor / Departamento / Campus',
    'Laboratorio / Grupo de Pesquisa',
    'Area de Especializacao Tecnica',
    'URL Fonte de Validacao',
    'Status de Validacao',
    'Data de Acesso'
]

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_json(filepath):
    print(f"[VALIDATION] Checking {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON top-level structure must be a list.")

    if len(data) == 0:
        raise ValueError("JSON dataset is empty.")

    for idx, row in enumerate(data):
        for field in EXPECTED_FIELDS:
            if field not in row:
                raise ValueError(f"Missing field '{field}' at row {idx}")
            val = str(row[field]).strip()
            if not val:
                raise ValueError(f"Empty value for field '{field}' at row {idx} ({row.get('Nome Completo')})")

        email = row['E-mail Institutional Publico']
        if not EMAIL_REGEX.match(email):
            raise ValueError(f"Invalid email format '{email}' at row {idx}")

    print(f"[SUCCESS] JSON validation passed! Total records: {len(data)}")
    return len(data)

def validate_csv(filepath, expected_count):
    print(f"[VALIDATION] Checking {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        if headers != EXPECTED_FIELDS:
            raise ValueError(f"CSV headers mismatch.\nExpected: {EXPECTED_FIELDS}\nGot: {headers}")

        rows = list(reader)
        if len(rows) != expected_count:
            raise ValueError(f"CSV record count mismatch. Expected {expected_count}, got {len(rows)}")

        for idx, row in enumerate(rows):
            for field in EXPECTED_FIELDS:
                val = str(row[field]).strip()
                if not val:
                    raise ValueError(f"Empty CSV value for '{field}' at row {idx}")
            email = row['E-mail Institutional Publico']
            if not EMAIL_REGEX.match(email):
                raise ValueError(f"Invalid CSV email format '{email}' at row {idx}")

    print(f"[SUCCESS] CSV validation passed! Total records: {len(rows)}")

def validate_markdown(filepath, expected_count):
    print(f"[VALIDATION] Checking {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if "# Mapeamento Institucional e Ecossistema de Pesquisa — UERJ" not in content:
        raise ValueError("Markdown missing main header.")

    # Count rows in section 3 main table (rows with 6 columns)
    dataset_table_rows = [line for line in content.split('\n') if line.startswith('| ') and line.count('|') == 7 and not line.startswith('| Nome Completo') and not line.startswith('| :---')]

    if len(dataset_table_rows) != expected_count:
        raise ValueError(f"Markdown dataset table row count mismatch. Expected {expected_count}, got {len(dataset_table_rows)}")

    print(f"[SUCCESS] Markdown validation passed! Total table rows: {len(dataset_table_rows)}")

def main():
    try:
        count = validate_json('uerj_dataset.json')
        validate_csv('uerj_dataset.csv', count)
        validate_markdown('mapeamento_uerj.md', count)
        print("\nALL VALIDATIONS PASSED PERFECTLY! DELIVERABLES ARE VERIFIED AND READY.")
    except Exception as e:
        print(f"\n[VALIDATION ERROR] {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
