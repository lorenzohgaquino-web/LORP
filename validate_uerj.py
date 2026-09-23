import json
import csv
import re
import os

EXPECTED_HEADERS = [
    "nome_completo",
    "email_institucional",
    "setor_departamento_campus",
    "laboratorio_grupo_pesquisa",
    "especializacao_tecnica",
    "url_fonte_validacao",
    "status_validacao",
    "data_acesso"
]

EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'

def validate():
    print("Starting UERJ Dataset Validation...")

    # 1. Check file existence
    json_path = "uerj_dataset.json"
    csv_path = "uerj_dataset.csv"
    report_path = "mapeamento_uerj.md"

    for path in [json_path, csv_path, report_path]:
        assert os.path.exists(path), f"File missing: {path}"
        assert os.path.getsize(path) > 0, f"File empty: {path}"

    # 2. Validate JSON structure & content
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    assert isinstance(json_data, list), "JSON data must be a list"
    assert len(json_data) > 0, "JSON dataset cannot be empty"

    for idx, row in enumerate(json_data):
        for header in EXPECTED_HEADERS:
            assert header in row, f"Missing header '{header}' in JSON record {idx}"
            val = str(row[header]).strip()
            assert len(val) > 0, f"Empty field '{header}' in JSON record {idx}"

        email = row["email_institucional"]
        assert re.match(EMAIL_REGEX, email), f"Invalid email format '{email}' in JSON record {idx}"

    # 3. Validate CSV headers & row count
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        csv_rows = list(reader)

    csv_headers = csv_rows[0]
    assert csv_headers == EXPECTED_HEADERS, f"CSV headers mismatch: {csv_headers} vs {EXPECTED_HEADERS}"
    assert len(csv_rows) - 1 == len(json_data), f"Count mismatch between CSV ({len(csv_rows)-1}) and JSON ({len(json_data)})"

    # 4. Validate Markdown Report
    with open(report_path, "r", encoding="utf-8") as f:
        report_text = f.read()

    assert "# MAPEAMENTO INSTITUCIONAL APROFUNDADO DA UERJ" in report_text, "Report title missing"
    assert "## 3. DATASET ESTRUTURADO COMPLETO" in report_text, "Report table section missing"

    print(f"VALIDATION SUCCESSFUL! All {len(json_data)} records pass schema, email regex, and consistency assertions.")

if __name__ == "__main__":
    validate()
