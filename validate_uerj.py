import json
import csv
import re
import os
import sys

MANDATORY_FIELDS = [
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

def validate_json(filepath):
    print(f"--- Validating JSON: {filepath} ---")
    if not os.path.exists(filepath):
        print(f"Error: {filepath} does not exist!")
        return False, 0

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list) or len(data) == 0:
        print("Error: JSON is empty or not a list!")
        return False, 0

    for idx, record in enumerate(data):
        for field in MANDATORY_FIELDS:
            if field not in record or not str(record[field]).strip():
                print(f"Error in JSON record {idx}: Missing or empty mandatory field '{field}'!")
                return False, 0

        email = record["email_institucional"]
        if not re.match(EMAIL_REGEX, email):
            print(f"Error in JSON record {idx}: Invalid email format '{email}' for {record['nome_completo']}!")
            return False, 0

    print(f"JSON Validation PASSED ({len(data)} valid records).")
    return True, len(data)

def validate_csv(filepath, expected_count):
    print(f"--- Validating CSV: {filepath} ---")
    if not os.path.exists(filepath):
        print(f"Error: {filepath} does not exist!")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        if headers != MANDATORY_FIELDS:
            print(f"Error: CSV headers {headers} do not match expected mandatory fields {MANDATORY_FIELDS}!")
            return False

        count = 0
        for idx, row in enumerate(reader):
            count += 1
            for field in MANDATORY_FIELDS:
                if field not in row or not str(row[field]).strip():
                    print(f"Error in CSV row {idx}: Missing or empty mandatory field '{field}'!")
                    return False
            email = row["email_institucional"]
            if not re.match(EMAIL_REGEX, email):
                print(f"Error in CSV row {idx}: Invalid email format '{email}' for {row['nome_completo']}!")
                return False

    if count != expected_count:
        print(f"Error: CSV record count ({count}) does not match expected JSON count ({expected_count})!")
        return False

    print(f"CSV Validation PASSED ({count} valid records).")
    return True

def validate_markdown(filepath, expected_count):
    print(f"--- Validating Markdown: {filepath} ---")
    if not os.path.exists(filepath):
        print(f"Error: {filepath} does not exist!")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "# Mapeamento Institucional e Ecossistema de Pesquisa - UERJ" not in content:
        print("Error: Markdown missing expected main header!")
        return False

    lines = content.splitlines()
    table_rows = [line for line in lines if line.startswith("|") and not line.startswith("|---") and not line.startswith("| Nome Completo")]

    if len(table_rows) != expected_count:
        print(f"Error: Markdown table row count ({len(table_rows)}) does not match expected count ({expected_count})!")
        return False

    print(f"Markdown Validation PASSED ({len(table_rows)} valid rows).")
    return True

def main():
    json_ok, count = validate_json("uerj_dataset.json")
    if not json_ok:
        sys.exit(1)

    csv_ok = validate_csv("uerj_dataset.csv", count)
    if not csv_ok:
        sys.exit(1)

    md_ok = validate_markdown("mapeamento_uerj.md", count)
    if not md_ok:
        sys.exit(1)

    print("\nALL VALIDATIONS PASSED SUCCESSFULLY! UERJ DATASET IS COMPLIANT.")

if __name__ == "__main__":
    main()
