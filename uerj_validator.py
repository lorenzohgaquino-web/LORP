import json
import csv
import re
import sys

mandatory_fields = [
    "nome",
    "email",
    "setor_departamento_campus",
    "laboratorio_grupo",
    "especializacao_tecnica",
    "url_fonte_validacao",
    "status_validacao",
    "data_acesso"
]

email_regex = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

print("=== STARTING UERJ DATASET VALIDATION ===")

# 1. Validate JSON
json_path = "uerj_dataset.json"
try:
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    print(f"[OK] JSON loaded successfully. Total records: {len(json_data)}")
except Exception as e:
    print(f"[FAIL] Error loading JSON: {e}")
    sys.exit(1)

if not isinstance(json_data, list) or len(json_data) == 0:
    print("[FAIL] JSON dataset is empty or not a list.")
    sys.exit(1)

json_errors = 0
for idx, rec in enumerate(json_data):
    for mf in mandatory_fields:
        if mf not in rec or not str(rec[mf]).strip():
            print(f"[ERROR] JSON Record {idx} ({rec.get('nome', 'UNKNOWN')}) missing or empty field: {mf}")
            json_errors += 1

    email = rec.get("email", "").strip()
    if not email_regex.match(email):
        print(f"[ERROR] JSON Record {idx} ({rec.get('nome', 'UNKNOWN')}) has invalid email format: {email}")
        json_errors += 1

if json_errors == 0:
    print("[OK] JSON validation passed with 0 errors!")

# 2. Validate CSV
csv_path = "uerj_dataset.csv"
try:
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)
    print(f"[OK] CSV loaded successfully. Total rows: {len(csv_rows)}")
except Exception as e:
    print(f"[FAIL] Error loading CSV: {e}")
    sys.exit(1)

csv_errors = 0
if len(csv_rows) != len(json_data):
    print(f"[ERROR] Count mismatch! JSON has {len(json_data)} records, CSV has {len(csv_rows)} rows.")
    csv_errors += 1

for idx, row in enumerate(csv_rows):
    for mf in mandatory_fields:
        if mf not in row or not str(row[mf]).strip():
            print(f"[ERROR] CSV Row {idx} ({row.get('nome', 'UNKNOWN')}) missing or empty field: {mf}")
            csv_errors += 1

if csv_errors == 0:
    print("[OK] CSV validation passed with 0 errors!")

# 3. Validate Markdown (mapeamento_uerj.md)
md_path = "mapeamento_uerj.md"
try:
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    print(f"[OK] Markdown report loaded successfully. Length: {len(md_content)} characters.")
except Exception as e:
    print(f"[FAIL] Error loading Markdown: {e}")
    sys.exit(1)

table_rows = [line for line in md_content.splitlines() if line.startswith("|") and not line.startswith("| ---") and "Nome | E-mail" not in line]

print(f"[OK] Markdown table contains {len(table_rows)} data rows.")
if len(table_rows) != len(json_data):
    print(f"[WARNING] Markdown table row count ({len(table_rows)}) differs from JSON record count ({len(json_data)}).")

print("=== UERJ VALIDATION COMPLETED SUCCESSFULLY ===")
