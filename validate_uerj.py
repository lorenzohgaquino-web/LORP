import json
import csv
import re
import os

REQUIRED_HEADERS = [
    'nome', 'email', 'departamento_setor_campus', 'laboratorio_grupo_pesquisa',
    'especializacao_tecnica', 'url_fonte_validacao', 'status_validacao', 'data_acesso'
]

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def validate_datasets():
    print("=== Starting UERJ Dataset Validation ===")

    # 1. Check file existence
    json_path = 'uerj_dataset.json'
    csv_path = 'uerj_dataset.csv'

    assert os.path.exists(json_path), "JSON dataset missing!"
    assert os.path.exists(csv_path), "CSV dataset missing!"

    # 2. Validate JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    assert isinstance(json_data, list), "JSON data must be a list of records!"
    assert len(json_data) > 0, "JSON dataset is empty!"
    print(f"✓ JSON loaded successfully with {len(json_data)} records.")

    for idx, record in enumerate(json_data):
        for header in REQUIRED_HEADERS:
            assert header in record, f"Record {idx} missing header: {header}"
            val = str(record[header]).strip()
            assert len(val) > 0, f"Record {idx} has empty field for {header}"

        # Email validity check
        email = record['email']
        assert re.match(EMAIL_REGEX, email), f"Invalid email format in record {idx}: {email}"

        # URL validity check
        url = record['url_fonte_validacao']
        assert url.startswith('http://') or url.startswith('https://'), f"Invalid URL in record {idx}: {url}"

    print("✓ All JSON record fields, emails, and URLs validated.")

    # 3. Validate CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_headers = reader.fieldnames
        assert csv_headers == REQUIRED_HEADERS, f"CSV headers mismatch! Got {csv_headers}"

        csv_data = list(reader)

    assert len(csv_data) == len(json_data), f"Mismatch between JSON count ({len(json_data)}) and CSV count ({len(csv_data)})"
    print(f"✓ CSV loaded successfully with {len(csv_data)} records and matching headers.")

    # 4. Check priority department representation
    depts = [r['departamento_setor_campus'] for r in json_data]
    depts_str = " ".join(depts)

    priority_units = ['FEN', 'MECAN', 'DEEL', 'DEPRO', 'DEQ', 'Civil', 'IPRJ', 'PPGMC', 'FAT', 'IME', 'InovUerj']
    for unit in priority_units:
        assert unit in depts_str, f"Priority unit {unit} missing from mapped departments!"
    print("✓ All 5 priority organizational sections fully represented.")

    print("\nSUCCESS: All UERJ dataset validations passed cleanly!")

if __name__ == "__main__":
    validate_datasets()
