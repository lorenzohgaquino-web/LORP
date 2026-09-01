import json
import csv
import re
import os
import sys

MANDATORY_FIELDS = [
    'nome',
    'email',
    'setor_departamento_campus',
    'laboratorio_grupo',
    'especializacao_tecnica',
    'url_validacao',
    'status_validacao',
    'data_acesso'
]

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def validate_json():
    print("[VALIDATOR] Validating uerj_dataset.json...")
    if not os.path.exists('uerj_dataset.json'):
        print("[ERROR] uerj_dataset.json does not exist!")
        return False, 0

    with open('uerj_dataset.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list) or len(data) == 0:
        print("[ERROR] JSON dataset is empty or not a list!")
        return False, 0

    for idx, item in enumerate(data):
        for field in MANDATORY_FIELDS:
            if field not in item:
                print(f"[ERROR] Record {idx} missing field: {field}")
                return False, 0
            val = str(item[field]).strip()
            if not val:
                print(f"[ERROR] Record {idx} field {field} is empty!")
                return False, 0

        # Validate email
        email = item['email'].strip()
        if not re.match(EMAIL_REGEX, email):
            print(f"[ERROR] Record {idx} invalid email format: {email}")
            return False, 0

    print(f"[VALIDATOR] JSON validation PASSED ({len(data)} records).")
    return True, len(data)

def validate_csv(json_count):
    print("[VALIDATOR] Validating uerj_dataset.csv...")
    if not os.path.exists('uerj_dataset.csv'):
        print("[ERROR] uerj_dataset.csv does not exist!")
        return False

    with open('uerj_dataset.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        if headers != MANDATORY_FIELDS:
            print(f"[ERROR] CSV headers mismatch: {headers} vs {MANDATORY_FIELDS}")
            return False

        rows = list(reader)
        if len(rows) != json_count:
            print(f"[ERROR] CSV row count mismatch: {len(rows)} vs JSON {json_count}")
            return False

        for idx, row in enumerate(rows):
            for field in MANDATORY_FIELDS:
                val = str(row[field]).strip()
                if not val:
                    print(f"[ERROR] CSV row {idx} field {field} is empty!")
                    return False

    print(f"[VALIDATOR] CSV validation PASSED ({len(rows)} records).")
    return True

def validate_markdown(json_count):
    print("[VALIDATOR] Validating mapeamento_uerj.md...")
    if not os.path.exists('mapeamento_uerj.md'):
        print("[ERROR] mapeamento_uerj.md does not exist!")
        return False

    with open('mapeamento_uerj.md', 'r', encoding='utf-8') as f:
        content = f.read()

    lines = [l.strip() for l in content.split('\n') if l.strip().startswith('|') and not l.strip().startswith('|---') and not 'Nome | E-mail' in l]

    if len(lines) != json_count:
        print(f"[ERROR] Markdown table row count mismatch: {len(lines)} vs JSON {json_count}")
        return False

    print(f"[VALIDATOR] Markdown validation PASSED ({len(lines)} table rows).")
    return True

def run_all_validations():
    j_ok, j_count = validate_json()
    if not j_ok:
        sys.exit(1)

    c_ok = validate_csv(j_count)
    if not c_ok:
        sys.exit(1)

    m_ok = validate_markdown(j_count)
    if not m_ok:
        sys.exit(1)

    print("\n[ALL VALIDATIONS PASSED SUCCESSFULLY!]")

if __name__ == '__main__':
    run_all_validations()
