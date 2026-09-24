import json
import csv
import re
import os

REQUIRED_FIELDS = [
    "nome",
    "email_institucional",
    "setor_departamento",
    "laboratorio_grupo",
    "especializacao_tecnica",
    "fonte_validacao",
    "status_validacao",
    "data_acesso"
]

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def validate():
    print("--- STARTING UERJ DATASET VALIDATION ---")

    # 1. Check file existence
    files = ["uerj_dataset.json", "uerj_dataset.csv", "mapeamento_uerj.md"]
    for f in files:
        assert os.path.exists(f), f"Missing required output file: {f}"
        print(f"File exists: {f}")

    # 2. Validate JSON schema & fields
    with open("uerj_dataset.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)

    assert len(json_data) > 0, "JSON dataset is empty!"
    print(f"JSON record count: {len(json_data)}")

    for idx, row in enumerate(json_data):
        for field in REQUIRED_FIELDS:
            assert field in row, f"Missing field '{field}' in JSON record {idx}"
            assert str(row[field]).strip() != "", f"Empty field '{field}' in JSON record {idx}"

        # Email validation
        email = row["email_institucional"]
        assert re.match(EMAIL_REGEX, email), f"Invalid email format '{email}' in record {idx}"

    # 3. Validate CSV schema & fields
    with open("uerj_dataset.csv", "r", encoding="utf-8") as f:
        csv_data = list(csv.DictReader(f))

    assert len(csv_data) == len(json_data), f"CSV record count ({len(csv_data)}) does not match JSON count ({len(json_data)})"
    print(f"CSV record count: {len(csv_data)}")

    for idx, row in enumerate(csv_data):
        for field in REQUIRED_FIELDS:
            assert field in row, f"Missing field '{field}' in CSV record {idx}"
            assert str(row[field]).strip() != "", f"Empty field '{field}' in CSV record {idx}"

    # 4. Check Markdown presence
    with open("mapeamento_uerj.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    assert "# MAPEAMENTO INSTITUCIONAL APROFUNDADO — UERJ" in md_text, "Markdown header missing"
    assert "SUMÁRIO EXECUTIVO" in md_text, "Executive summary missing"
    assert "| Nome Completo | E-mail Institucional |" in md_text, "Markdown table missing"

    print("--- ALL VALIDATION CHECKS PASSED SUCCESSFULLY (100%) ---")

if __name__ == "__main__":
    validate()
