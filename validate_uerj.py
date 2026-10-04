import json
import csv
import re
import os

EXPECTED_FIELDS = [
    "nome_completo",
    "email_institucional",
    "unidade_campus",
    "departamento",
    "laboratorio_grupo",
    "area_especializacao_tecnica",
    "url_fonte_validacao",
    "status_validacao",
    "data_acesso"
]

EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

def validate():
    print("=== STARTING UERJ DATASET VALIDATION ===")

    # 1. Check file existence
    for fname in ["uerj_dataset.json", "uerj_dataset.csv", "mapeamento_uerj.md"]:
        if not os.path.exists(fname):
            raise FileNotFoundError(f"Missing required output file: {fname}")
        print(f"File exists: {fname} ({os.path.getsize(fname)} bytes)")

    # 2. Validate JSON
    with open("uerj_dataset.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)

    json_count = len(json_data)
    print(f"JSON record count: {json_count}")
    if json_count < 50:
        raise ValueError(f"JSON record count ({json_count}) is less than expected minimum 50 records")

    for i, row in enumerate(json_data):
        for field in EXPECTED_FIELDS:
            if field not in row:
                raise KeyError(f"Row {i} in JSON missing key: {field}")
            val = str(row[field]).strip()
            if not val:
                raise ValueError(f"Row {i} in JSON has empty field: {field}")

        # Email check
        email = row["email_institucional"]
        if not EMAIL_REGEX.match(email):
            raise ValueError(f"Row {i} has invalid email format: {email}")

        # URL check
        url = row["url_fonte_validacao"]
        if not (url.startswith("http://") or url.startswith("https://")):
            raise ValueError(f"Row {i} has invalid URL: {url}")

    # 3. Validate CSV
    with open("uerj_dataset.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != EXPECTED_FIELDS:
            raise ValueError(f"CSV fieldnames mismatch. Expected {EXPECTED_FIELDS}, got {reader.fieldnames}")
        csv_rows = list(reader)

    csv_count = len(csv_rows)
    print(f"CSV record count: {csv_count}")
    if csv_count != json_count:
        raise ValueError(f"CSV record count ({csv_count}) does not match JSON record count ({json_count})")

    # 4. Validate Markdown
    with open("mapeamento_uerj.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    md_table_rows = [line for line in md_text.splitlines() if line.startswith("| **")]
    md_count = len(md_table_rows)
    print(f"Markdown table record count: {md_count}")
    if md_count != json_count:
        raise ValueError(f"Markdown table record count ({md_count}) does not match JSON count ({json_count})")

    print("=== ALL VALIDATIONS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    validate()
