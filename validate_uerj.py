import json
import csv
import re
import os

REQUIRED_FIELDS = [
    "nome", "email", "setor_departamento", "laboratorio_grupo",
    "especializacao", "url_fonte", "status_validacao", "data_acesso"
]

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def validate_all():
    print("Starting UERJ Dataset Validation...")

    # 1. Check File Existence
    for filepath in ["uerj_dataset.json", "uerj_dataset.csv", "mapeamento_uerj.md"]:
        assert os.path.exists(filepath), f"File missing: {filepath}"
        print(f"✓ File exists: {filepath}")

    # 2. Validate JSON Schema and Fields
    with open("uerj_dataset.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)

    assert len(json_data) > 0, "JSON dataset is empty!"
    print(f"✓ JSON record count: {len(json_data)}")

    for i, record in enumerate(json_data):
        for field in REQUIRED_FIELDS:
            assert field in record, f"Record {i} missing field: {field}"
            assert str(record[field]).strip() != "", f"Record {i} has empty field: {field}"

        # Email format validation
        email = record["email"]
        assert re.match(EMAIL_REGEX, email), f"Record {i} has invalid email format: {email}"

    # 3. Validate CSV Integrity
    with open("uerj_dataset.csv", "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    assert len(reader) == len(json_data), f"CSV row count ({len(reader)}) does not match JSON count ({len(json_data)})"
    print(f"✓ CSV row count matches JSON: {len(reader)}")

    # 4. Validate Markdown Report
    with open("mapeamento_uerj.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    assert "Mapeamento Institucional" in md_text, "Markdown report header missing!"
    assert "| Nome | E-mail |" in md_text, "Markdown table structure missing!"
    assert "Sumário Executivo" in md_text, "Markdown executive summary missing!"
    print("✓ Markdown report verified.")

    print("\nALL VALIDATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    validate_all()
