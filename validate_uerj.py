import json
import csv
import re
import os

REQUIRED_HEADERS = [
    "nome",
    "email",
    "setor_departamento_campus",
    "laboratorio_grupo",
    "especializacao_tecnica",
    "url_fonte",
    "status_validacao",
    "data_acesso"
]

def validate_uerj_dataset():
    print("=== Validating UERJ Dataset ===")

    json_path = 'uerj_dataset.json'
    csv_path = 'uerj_dataset.csv'
    md_path = 'mapeamento_uerj.md'

    assert os.path.exists(json_path), f"Missing {json_path}"
    assert os.path.exists(csv_path), f"Missing {csv_path}"
    assert os.path.exists(md_path), f"Missing {md_path}"

    # 1. Validate JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    assert isinstance(json_data, list), "JSON data must be a list"
    assert len(json_data) > 0, "JSON dataset must not be empty"
    print(f"JSON record count: {len(json_data)}")

    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    for idx, rec in enumerate(json_data):
        for header in REQUIRED_HEADERS:
            assert header in rec, f"Missing key '{header}' in record {idx}"
            assert str(rec[header]).strip() != "", f"Empty value for key '{header}' in record {idx}"

        email = rec['email']
        assert email_regex.match(email) or email == "Não disponível publicamente", f"Invalid email format '{email}' at record {idx}"

    # 2. Validate CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == REQUIRED_HEADERS, f"CSV headers mismatch. Expected {REQUIRED_HEADERS}, got {reader.fieldnames}"
        csv_rows = list(reader)

    assert len(csv_rows) == len(json_data), f"Count mismatch between JSON ({len(json_data)}) and CSV ({len(csv_rows)})"
    print(f"CSV record count: {len(csv_rows)}")

    # 3. Validate Markdown Report
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    assert "# Mapeamento Institucional e Ecossistema de Pesquisa: UERJ" in md_content, "Markdown title missing"
    assert "## Sumário Executivo" in md_content, "Markdown executive summary missing"

    # Ensure key researchers are present in markdown
    sample_names = [r['nome'] for r in json_data[:5]]
    for name in sample_names:
        assert name in md_content, f"Researcher {name} missing from Markdown report"

    print("SUCCESS: All validation checks passed cleanly!")

if __name__ == '__main__':
    validate_uerj_dataset()
