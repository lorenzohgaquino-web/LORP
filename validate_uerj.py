import json
import csv
import re
import os

REQUIRED_HEADERS = [
    "nome_completo",
    "email_institucional",
    "setor_departamento_campus",
    "laboratorio_grupo_pesquisa",
    "especializacao_tecnica",
    "url_fonte_validacao",
    "status_validacao",
    "data_acesso"
]

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
URL_REGEX = r'^https?://[^\s]+$'

def validate():
    print("Starting UERJ dataset validation...")

    # Check file existence
    assert os.path.exists("uerj_dataset.json"), "uerj_dataset.json does not exist!"
    assert os.path.exists("uerj_dataset.csv"), "uerj_dataset.csv does not exist!"
    assert os.path.exists("mapeamento_uerj.md"), "mapeamento_uerj.md does not exist!"

    # Read JSON
    with open("uerj_dataset.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # Read CSV
    with open("uerj_dataset.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_headers = reader.fieldnames
        csv_data = list(reader)

    # Read Markdown
    with open("mapeamento_uerj.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    # 1. Header Validation
    assert csv_headers == REQUIRED_HEADERS, f"CSV headers mismatch: {csv_headers} vs {REQUIRED_HEADERS}"
    print("✓ CSV Headers validated.")

    # 2. Record Count Consistency
    json_count = len(json_data)
    csv_count = len(csv_data)
    assert json_count > 0, "JSON dataset is empty!"
    assert json_count == csv_count, f"Count mismatch! JSON: {json_count}, CSV: {csv_count}"
    print(f"✓ Record count consistent across JSON and CSV ({json_count} records).")

    # 3. Individual Record Fields & Formatting Check
    emails = []
    names = []
    for idx, record in enumerate(json_data):
        for header in REQUIRED_HEADERS:
            val = record.get(header)
            assert val is not None and str(val).strip() != "", f"Record {idx} missing/empty field: {header}"

        email = record["email_institucional"]
        url = record["url_fonte_validacao"]
        name = record["nome_completo"]

        assert re.match(EMAIL_REGEX, email), f"Invalid email format in record {idx}: {email}"
        assert re.match(URL_REGEX, url), f"Invalid URL format in record {idx}: {url}"

        emails.append(email)
        names.append(name)

    print("✓ Non-empty criteria, email regex, and URL regex validated across all records.")

    # 4. Markdown Table Alignment
    for name in names:
        assert name in md_text, f"Name '{name}' missing from Markdown report!"

    print("✓ All mapped names confirmed present in Markdown report.")
    print("SUCCESS: All UERJ validation assertions passed perfectly!")

if __name__ == "__main__":
    validate()
