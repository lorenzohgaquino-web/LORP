import json
import csv
import os
import sys
import re

print("=== STARTING ADVANCED UERJ DATASET VALIDATION ===")

expected_fields = [
    "nome", "email", "setor", "laboratorio", "especializacao",
    "fonte_url", "status_validacao", "data_acesso"
]

blacklist_name_substrings = [
    'sobre', 'tenho', 'gosto', 'projetos', 'pesquisa', 'processo', 'edital',
    'substituto', 'desma', 'membro', 'linha', 'principal', 'vínculo', 'página',
    'open sans', 'varela round', 'acesso', 'universidade'
]

# 1. Validate JSON
json_path = 'uerj_dataset.json'
if not os.path.exists(json_path):
    print(f"ERROR: {json_path} does not exist.")
    sys.exit(1)

with open(json_path, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

if not json_data or not isinstance(json_data, list):
    print(f"ERROR: {json_path} is empty or invalid format.")
    sys.exit(1)

print(f"JSON Record Count: {len(json_data)}")

email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

for idx, rec in enumerate(json_data):
    for field in expected_fields:
        if field not in rec or not str(rec[field]).strip():
            print(f"ERROR in JSON record {idx} ('{rec.get('nome')}'): missing or empty field '{field}'")
            sys.exit(1)

    # Check email validity strict regex
    email = rec["email"].strip()
    if not email_regex.match(email):
        print(f"ERROR in JSON record {idx}: invalid email format '{email}' for '{rec['nome']}'")
        sys.exit(1)

    # Check replacement character corruption (\ufffd)
    name = rec["nome"].strip()
    if "\ufffd" in name or "\ufffd" in rec["setor"]:
        print(f"ERROR in JSON record {idx}: replacement character found in name/setor '{name}'")
        sys.exit(1)

    # Check blacklist
    if any(sub in name.lower() for sub in blacklist_name_substrings):
        print(f"ERROR in JSON record {idx}: blacklisted/invalid string in name '{name}'")
        sys.exit(1)

# 2. Validate CSV
csv_path = 'uerj_dataset.csv'
if not os.path.exists(csv_path):
    print(f"ERROR: {csv_path} does not exist.")
    sys.exit(1)

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    csv_headers = reader.fieldnames
    if csv_headers != expected_fields:
        print(f"ERROR: CSV headers mismatch. Got {csv_headers}, expected {expected_fields}")
        sys.exit(1)

    rows = list(reader)
    print(f"CSV Record Count: {len(rows)}")

    if len(rows) != len(json_data):
        print(f"ERROR: Record count mismatch between JSON ({len(json_data)}) and CSV ({len(rows)})")
        sys.exit(1)

# 3. Validate Markdown Report
md_path = 'mapeamento_uerj.md'
if not os.path.exists(md_path):
    print(f"ERROR: {md_path} does not exist.")
    sys.exit(1)

with open(md_path, 'r', encoding='utf-8') as f:
    md_text = f.read()

if len(md_text) < 1000:
    print(f"ERROR: {md_path} content is too short ({len(md_text)} chars).")
    sys.exit(1)

print("SUCCESS: All strict UERJ dataset validation checks passed cleanly!")
