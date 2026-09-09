import json
import csv
import re
import os

def validate():
    print("Starting UERJ Dataset Validation...")

    # 1. Check file existence
    files = ['uerj_dataset.json', 'uerj_dataset.csv', 'mapeamento_uerj.md']
    for f in files:
        if not os.path.exists(f):
            raise FileNotFoundError(f"Missing required file: {f}")
        if os.path.getsize(f) == 0:
            raise ValueError(f"File {f} is empty")

    # 2. Validate JSON schema & content
    with open('uerj_dataset.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    print(f"JSON record count: {len(json_data)}")
    if len(json_data) == 0:
        raise ValueError("JSON dataset contains 0 records!")

    required_keys = ["name", "email", "department", "laboratory", "specialization", "source_url", "validation_date"]
    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    for idx, rec in enumerate(json_data):
        for k in required_keys:
            if k not in rec or not str(rec[k]).strip():
                raise ValueError(f"Record {idx} ({rec.get('name')}) missing mandatory field: {k}")
        if not email_regex.match(rec['email']):
            raise ValueError(f"Record {idx} ({rec.get('name')}) has invalid email format: {rec['email']}")
        if not (rec['source_url'].startswith('http://') or rec['source_url'].startswith('https://')):
            raise ValueError(f"Record {idx} ({rec.get('name')}) has invalid URL format: {rec['source_url']}")

    # 3. Validate CSV consistency
    with open('uerj_dataset.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)

    print(f"CSV record count: {len(csv_rows)}")
    if len(csv_rows) != len(json_data):
        raise ValueError(f"Mismatch between JSON count ({len(json_data)}) and CSV count ({len(csv_rows)})")

    # 4. Validate Markdown content
    with open('mapeamento_uerj.md', 'r', encoding='utf-8') as f:
        md_text = f.read()

    md_rows = [line for line in md_text.splitlines() if line.startswith('|') and not line.startswith('| Nome') and not line.startswith('|---')]
    print(f"Markdown table row count: {len(md_rows)}")
    if len(md_rows) != len(json_data):
        raise ValueError(f"Mismatch between JSON count ({len(json_data)}) and Markdown rows ({len(md_rows)})")

    print("SUCCESS: All validation checks passed perfectly!")

if __name__ == '__main__':
    validate()
