import json
import csv
import re
import os

def validate_uerj_artifacts():
    print("Validating UERJ dataset artifacts...")

    json_path = 'uerj_dataset.json'
    csv_path = 'uerj_dataset.csv'
    md_path = 'mapeamento_uerj.md'

    assert os.path.exists(json_path), f"Missing {json_path}"
    assert os.path.exists(csv_path), f"Missing {csv_path}"
    assert os.path.exists(md_path), f"Missing {md_path}"

    with open(json_path, 'r', encoding='utf-8') as f:
        jdata = json.load(f)

    assert len(jdata) > 0, "JSON dataset is empty!"
    print(f"✓ JSON record count: {len(jdata)}")

    mandatory_fields = [
        "nome", "email", "setor", "campus", "laboratorio",
        "especializacao", "lattes_url", "fonte_url",
        "status_validacao", "data_acesso"
    ]

    for idx, rec in enumerate(jdata):
        for field in mandatory_fields:
            assert field in rec, f"Record {idx} missing field {field}"
            assert str(rec[field]).strip() != "", f"Record {idx} has empty field {field}"

        # Email check
        email = rec['email']
        if email != "não disponível publicamente":
            assert re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email), f"Invalid email format in record {idx}: {email}"

        # URL check
        url = rec['lattes_url']
        assert url.startswith('http://') or url.startswith('https://'), f"Invalid URL in record {idx}: {url}"

    # CSV Validation
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    assert len(csv_rows) == len(jdata), f"CSV row count ({len(csv_rows)}) does not match JSON count ({len(jdata)})"
    print(f"✓ CSV record count: {len(csv_rows)}")

    # MD Validation
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    assert "# Mapeamento Institucional Exaustivo — UERJ" in md_text
    assert "Resumo Executivo" in md_text
    assert "Tabela Completa do Dataset Institucional" in md_text

    table_rows = [line for line in md_text.split('\n') if line.startswith('|') and '|' in line[1:]]
    # Subtract header and separator row
    data_table_rows = len(table_rows) - 2
    assert data_table_rows == len(jdata), f"Markdown table rows ({data_table_rows}) does not match JSON count ({len(jdata)})"
    print(f"✓ Markdown table rows: {data_table_rows}")

    print("ALL VALIDATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    validate_uerj_artifacts()
