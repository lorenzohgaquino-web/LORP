import json, csv, re, os

def validate():
    print("=== STARTING UERJ DATASET VALIDATION ===")

    # 1. Check files existence
    files = ['uerj_dataset.json', 'uerj_dataset.csv', 'mapeamento_uerj.md']
    for f in files:
        if not os.path.exists(f):
            raise FileNotFoundError(f"Missing mandatory output file: {f}")
        if os.path.getsize(f) == 0:
            raise ValueError(f"File {f} is empty!")
        print(f"[✓] File exists and non-empty: {f}")

    # 2. Check JSON content & schema
    with open('uerj_dataset.json', 'r', encoding='utf-8') as f:
        data_json = json.load(f)

    required_keys = ["name", "email", "campus", "sector", "lab_group", "specialization", "source_url", "validation_status", "access_date"]

    if len(data_json) == 0:
        raise ValueError("JSON dataset contains 0 records!")

    for idx, item in enumerate(data_json):
        for k in required_keys:
            if k not in item:
                raise KeyError(f"Record {idx} missing field {k}")
            if not str(item[k]).strip():
                raise ValueError(f"Record {idx} field {k} is empty!")

        # Email format or fallback check
        email = item['email']
        if '@' not in email:
            raise ValueError(f"Record {idx} invalid email/contact format: {email}")

        # Ensure URL starts with http
        if not item['source_url'].startswith('http'):
            raise ValueError(f"Record {idx} invalid source_url: {item['source_url']}")

    print(f"[✓] JSON Schema & Data Validity Verified ({len(data_json)} records).")

    # 3. Check CSV parity
    with open('uerj_dataset.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    if len(csv_rows) != len(data_json):
        raise ValueError(f"Parity mismatch: JSON count ({len(data_json)}) != CSV count ({len(csv_rows)})")

    for k in required_keys:
        if k not in reader.fieldnames:
            raise KeyError(f"CSV header missing column {k}")

    print(f"[✓] CSV Header & Record Count Parity Verified ({len(csv_rows)} records).")

    # 4. Check Markdown table
    with open('mapeamento_uerj.md', 'r', encoding='utf-8') as f:
        md_text = f.read()

    table_lines = [line for line in md_text.split('\n') if line.startswith('|') and not line.startswith('|---') and not line.startswith('| Nome Completo')]

    if len(table_lines) != len(data_json):
        raise ValueError(f"Parity mismatch: JSON count ({len(data_json)}) != MD Table count ({len(table_lines)})")

    print(f"[✓] Markdown Table Parity Verified ({len(table_lines)} rows).")
    print("=== ALL VALIDATION CHECKS PASSED SUCCESSFULLY ===")

if __name__ == '__main__':
    validate()
