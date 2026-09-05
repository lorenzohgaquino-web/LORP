import json
import csv
import re
import os
import sys

MANDATORY_FIELDS = [
    "Nome Completo",
    "E-mail Institucional Público",
    "Setor / Departamento / Campus",
    "Laboratório / Grupo de Pesquisa",
    "Área de Especialização Técnica",
    "URL da Fonte de Validação",
    "Status de Validação",
    "Data de Acesso"
]

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

BLACKLIST_NAME_PATTERNS = [
    'open sans', 'varela round', 'página pessoal', 'acesso administrativo',
    'universidade federal', 'faculdade de engenharia', 'departamento de'
]

def validate_all():
    print("=== STARTING UERJ DATASET VALIDATION ===")

    # 1. Check file existence
    files = ['uerj_dataset.json', 'uerj_dataset.csv', 'mapeamento_uerj.md']
    for f in files:
        if not os.path.exists(f):
            print(f"FAILED: File {f} does not exist.")
            sys.exit(1)
        print(f"✓ Found {f}")

    # 2. Validate JSON
    with open('uerj_dataset.json', 'r', encoding='utf-8') as f:
        data_json = json.load(f)

    json_count = len(data_json)
    print(f"✓ uerj_dataset.json loaded with {json_count} records.")

    for idx, rec in enumerate(data_json):
        # Check mandatory fields
        for field in MANDATORY_FIELDS:
            if field not in rec:
                print(f"FAILED record {idx}: missing mandatory field '{field}'")
                sys.exit(1)
            # Allow Laboratório / Grupo de Pesquisa to be empty, others non-empty
            if field != "Laboratório / Grupo de Pesquisa" and not str(rec[field]).strip():
                print(f"FAILED record {idx}: empty mandatory field '{field}'")
                sys.exit(1)

        # Email regex check
        email = rec["E-mail Institucional Público"]
        if not re.match(EMAIL_REGEX, email):
            print(f"FAILED record {idx}: invalid email format '{email}'")
            sys.exit(1)

        # Name blacklist check
        name = rec["Nome Completo"].lower()
        for bl in BLACKLIST_NAME_PATTERNS:
            if bl in name:
                print(f"FAILED record {idx}: blacklisted string '{bl}' in name '{rec['Nome Completo']}'")
                sys.exit(1)

    # 3. Validate CSV
    with open('uerj_dataset.csv', 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))

    csv_count = len(reader)
    print(f"✓ uerj_dataset.csv loaded with {csv_count} records.")

    if csv_count != json_count:
        print(f"FAILED: CSV count ({csv_count}) does not match JSON count ({json_count})")
        sys.exit(1)

    for idx, row in enumerate(reader):
        for field in MANDATORY_FIELDS:
            if field not in row:
                print(f"FAILED CSV row {idx}: missing field '{field}'")
                sys.exit(1)

    # 4. Validate Markdown
    with open('mapeamento_uerj.md', 'r', encoding='utf-8') as f:
        md_text = f.read()

    md_rows = [line for line in md_text.splitlines() if line.startswith('|') and '[Fonte]' in line]
    md_count = len(md_rows)
    print(f"✓ mapeamento_uerj.md loaded with {md_count} table records.")

    if md_count != json_count:
        print(f"FAILED: Markdown table count ({md_count}) does not match JSON count ({json_count})")
        sys.exit(1)

    print("\n==========================================")
    print(f" SUCCESS: ALL 3 DATASETS VALIDATED SUCCESSFULLY! ({json_count} RECORDS)")
    print("==========================================\n")

if __name__ == '__main__':
    validate_all()
