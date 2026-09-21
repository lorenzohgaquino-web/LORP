import json
import csv
import os
import sys
import re

REQUIRED_FIELDS = [
    "id_lattes",
    "nome_completo",
    "cargo_funcao",
    "unidade_instituto",
    "departamento_ppg",
    "linhas_de_pesquisa",
    "email_institucional",
    "url_fonte_oficial",
    "status_validacao"
]

VALID_STATUSES = [
    "Verificado Portal",
    "Verificado Artigo/Lattes",
    "Pendente E-mail"
]

def validate_lattes_id(lattes_id):
    if lattes_id == "N/D":
        return True
    return bool(re.match(r"^\d{16}$", lattes_id))

def validate_csv(filepath):
    print(f"Validating CSV: {filepath}")
    assert os.path.exists(filepath), f"File {filepath} does not exist"
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        assert headers == REQUIRED_FIELDS, f"CSV headers mismatch: {headers} vs {REQUIRED_FIELDS}"
        rows = list(reader)
        assert len(rows) > 0, f"CSV {filepath} is empty"
        for idx, r in enumerate(rows):
            for field in REQUIRED_FIELDS:
                val = r.get(field, "").strip()
                assert val != "", f"Row {idx} field {field} is empty in {filepath}"
            status = r.get("status_validacao", "")
            assert status in VALID_STATUSES, f"Row {idx} invalid status {status} in {filepath}"
            lattes_id = r.get("id_lattes", "").strip()
            assert validate_lattes_id(lattes_id), f"Row {idx} invalid id_lattes: '{lattes_id}'"
    print(f"CSV {filepath} is VALID. ({len(rows)} rows)")
    return len(rows)

def validate_json(filepath):
    print(f"Validating JSON: {filepath}")
    assert os.path.exists(filepath), f"File {filepath} does not exist"
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list), f"JSON {filepath} root must be a list"
    assert len(data) > 0, f"JSON {filepath} is empty"
    for idx, r in enumerate(data):
        assert isinstance(r, dict), f"Item {idx} is not a dict in {filepath}"
        assert list(r.keys()) == REQUIRED_FIELDS, f"Item {idx} keys mismatch in {filepath}: {list(r.keys())}"
        for field in REQUIRED_FIELDS:
            val = str(r.get(field, "")).strip()
            assert val != "", f"Item {idx} field {field} is empty in {filepath}"
        status = r.get("status_validacao", "")
        assert status in VALID_STATUSES, f"Item {idx} invalid status {status} in {filepath}"
        lattes_id = str(r.get("id_lattes", "")).strip()
        assert validate_lattes_id(lattes_id), f"Item {idx} invalid id_lattes: '{lattes_id}'"
    print(f"JSON {filepath} is VALID. ({len(data)} items)")
    return len(data)

def main():
    files_to_check = [
        "dataset_completo.csv",
        "dataset_completo.json",
        "dataset.csv",
        "dataset.json"
    ]

    counts = []
    for f in files_to_check:
        if f.endswith(".csv"):
            c = validate_csv(f)
        else:
            c = validate_json(f)
        counts.append(c)

    assert len(set(counts)) == 1, f"Record count discrepancy across dataset files: {counts}"
    print(f"\nALL DATASETS ARE VALIDATED SUCCESSFULLY! ({counts[0]} total records)")

if __name__ == "__main__":
    main()
