import json
import csv
import re
import sys

def validate():
    print("=== Starting Validation for UERJ Dataset Artifacts ===")

    # 1. Load JSON
    with open("uerj_dataset.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
    print(f"JSON record count: {len(json_data)}")

    # 2. Load CSV
    with open("uerj_dataset.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_data = list(reader)
    print(f"CSV record count: {len(csv_data)}")

    assert len(json_data) == len(csv_data), f"Mismatch: JSON ({len(json_data)}) vs CSV ({len(csv_data)})"
    assert len(json_data) > 0, "Dataset is empty!"

    mandatory_fields = [
        "nome", "email", "unidade_departamento", "campus",
        "laboratorio_grupo", "especializacao_tecnica",
        "url_fonte", "status_validacao", "data_acesso"
    ]

    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    # Validate each JSON record
    for idx, rec in enumerate(json_data):
        for field in mandatory_fields:
            val = rec.get(field, "").strip()
            assert val != "", f"Record #{idx} missing mandatory field '{field}'"

        email = rec["email"]
        assert email_regex.match(email), f"Record #{idx} ({rec['nome']}) has invalid email format: '{email}'"

        url = rec["url_fonte"]
        assert url.startswith("http://") or url.startswith("https://"), f"Record #{idx} invalid URL: '{url}'"

    # Validate Markdown file existence & content
    with open("mapeamento_uerj.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    assert "# Mapeamento Institucional e Ecossistema de Pesquisa — UERJ" in md_text, "Markdown header missing"
    assert "Sumário Executivo" in md_text, "Executive summary missing from Markdown"
    assert len(md_text) > 2000, "Markdown content appears incomplete"

    print("✅ All validation checks PASSED successfully!")

if __name__ == "__main__":
    validate()
