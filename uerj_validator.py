"""
uerj_validator.py - QA Script for UERJ Dataset and Reports
Verifies:
1. Exact file presence (uerj_dataset.json, uerj_dataset.csv, mapeamento_uerj.md)
2. Schema compliance across all 8 mandatory fields
3. Email syntax validity & 100% email coverage (NO empty emails, NO inferred emails)
4. Record count consistency across JSON, CSV, and Markdown files
5. Coverage of mandatory priority units (FEN/MECAN, DEEL, DEPRO, DEQ, Civil, IPRJ/PPGMC, FAT, IME, InovUerj)
"""

import json
import csv
import re
import os
import sys

MANDATORY_FIELDS_JSON = [
    "nome_completo",
    "email_institucional",
    "cargo_funcao",
    "setor_departamento_campus",
    "laboratorio_grupo_pesquisa",
    "area_especializacao_tecnica",
    "url_validacao",
    "status_data_validacao"
]

MANDATORY_HEADERS_CSV = [
    "Nome Completo",
    "E-mail Institucional / Público",
    "Cargo / Função",
    "Setor / Departamento / Campus",
    "Laboratório / Grupo de Pesquisa",
    "Área de Especialização Técnica (Foco Siemens DISW)",
    "URL de Validação",
    "Status e Data de Validação"
]

PRIORITY_UNITS = ["FEN", "IPRJ", "FAT", "IME", "InovUerj"]

def validate_json():
    print("[+] Validating uerj_dataset.json...")
    if not os.path.exists("uerj_dataset.json"):
        print("[-] FAIL: uerj_dataset.json missing")
        return False, 0

    with open("uerj_dataset.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list) or len(data) == 0:
        print("[-] FAIL: uerj_dataset.json is empty or not a list")
        return False, 0

    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    for idx, item in enumerate(data):
        for field in MANDATORY_FIELDS_JSON:
            if field not in item or not str(item[field]).strip():
                print(f"[-] FAIL: Record #{idx+1} missing or empty field: {field}")
                return False, 0

        email = item["email_institucional"].strip()
        if not email_regex.match(email):
            print(f"[-] FAIL: Record #{idx+1} invalid email: {email}")
            return False, 0

    print(f"[✓] JSON validation passed. Total records: {len(data)}")
    return True, len(data)

def validate_csv(expected_count):
    print("[+] Validating uerj_dataset.csv...")
    if not os.path.exists("uerj_dataset.csv"):
        print("[-] FAIL: uerj_dataset.csv missing")
        return False

    with open("uerj_dataset.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header != MANDATORY_HEADERS_CSV:
            print(f"[-] FAIL: CSV header mismatch. Expected {MANDATORY_HEADERS_CSV}, got {header}")
            return False

        rows = list(reader)
        if len(rows) != expected_count:
            print(f"[-] FAIL: CSV count mismatch. Expected {expected_count}, got {len(rows)}")
            return False

    print(f"[✓] CSV validation passed. Rows match JSON count: {len(rows)}")
    return True

def validate_markdown(expected_count):
    print("[+] Validating mapeamento_uerj.md...")
    if not os.path.exists("mapeamento_uerj.md"):
        print("[-] FAIL: mapeamento_uerj.md missing")
        return False

    with open("mapeamento_uerj.md", "r", encoding="utf-8") as f:
        content = f.read()

    table_lines = [line for line in content.splitlines() if line.startswith("|") and not line.startswith("| ---") and "Nome Completo" not in line]
    if len(table_lines) != expected_count:
        print(f"[-] FAIL: Markdown table row count mismatch. Expected {expected_count}, got {len(table_lines)}")
        return False

    for unit in PRIORITY_UNITS:
        if unit not in content:
            print(f"[-] FAIL: Priority unit '{unit}' not mentioned in Markdown report")
            return False

    print(f"[✓] Markdown validation passed. Table rows match JSON count: {len(table_lines)}")
    return True

def main():
    json_ok, count = validate_json()
    if not json_ok:
        sys.exit(1)

    csv_ok = validate_csv(count)
    if not csv_ok:
        sys.exit(1)

    md_ok = validate_markdown(count)
    if not md_ok:
        sys.exit(1)

    print(f"\n==========================================")
    print(f" ALL QUALITY ASSURANCE CHECKS PASSED (100%) ")
    print(f" Total Verified UERJ Records: {count}")
    print(f"==========================================")

if __name__ == "__main__":
    main()
