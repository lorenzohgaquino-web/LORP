#!/usr/bin/env python3
"""
Automated Validation Script for ANP SIPED Dataset
Programmatically asserts schema headers, non-empty criteria, file integrity,
and minimum record counts across all JSON and CSV extraction artifacts.
"""

import os
import sys
import json
import csv

TABLE_EXPECTATIONS = {
    "DM_SIPED_PROJETO": {
        "csv_filename": "siped_projetos.csv",
        "min_count": 12000,
        "required_fields": ["NUM_PROJETO_ANP", "DSC_TITULO", "NOM_AREA", "NOM_TEMA", "NOM_SUB_TEMA"]
    },
    "DM_SIPED_EXECUTOR": {
        "csv_filename": "siped_executores.csv",
        "min_count": 100,
        "required_fields": ["SK_SEQ_EXECUTOR", "NOM_PESSOA", "NUM_CNPJ"]
    },
    "DM_SIPED_PROPONENTE": {
        "csv_filename": "siped_proponentes.csv",
        "min_count": 100,
        "required_fields": ["NK_SEQ_PROPONENTE", "NOM_FANTASIA"]
    },
    "DM_SIPED_UNIDADE_PESQUISA": {
        "csv_filename": "siped_unidades.csv",
        "min_count": 50,
        "required_fields": ["SK_SEQ_UNIDADE_PESQUISA", "NOM_UNIDADE_PESQUISA"]
    },
    "DM_SIPED_PALAVRA_CHAVE": {
        "csv_filename": "siped_palavras_chave.csv",
        "min_count": 100,
        "required_fields": ["SK_SEQ_PALAVRA_CHAVE", "DSC_PALAVRA_CHAVE"]
    },
    "DM_SIPED_RESULTADO_ANALISE": {
        "csv_filename": "siped_resultados.csv",
        "min_count": 300,
        "required_fields": ["SK_SEQ_PTR_RSLTO_ANLSE_PTR", "NOM_PESSOA"]
    },
    "DM_SIPED_DESPESA": {
        "csv_filename": "siped_despesas.csv",
        "min_count": 100,
        "required_fields": ["SK_SEQ_DESPESA", "DSC_DESPESA"]
    },
    "FT_SIPED": {
        "csv_filename": "siped_ft.csv",
        "min_count": 100,
        "required_fields": ["SK_SEQ_PROJETO", "VAL_TRATADO"]
    }
}


def validate_json_dataset(json_filepath):
    print(f"\n--- Validating JSON Dataset: {json_filepath} ---")
    if not os.path.exists(json_filepath):
        print(f"FAIL: JSON file missing: {json_filepath}")
        return False

    try:
        with open(json_filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"FAIL: Error reading JSON file: {e}")
        return False

    errors = 0
    for entity, exp in TABLE_EXPECTATIONS.items():
        if entity not in data:
            print(f"FAIL: Table '{entity}' missing from JSON dataset.")
            errors += 1
            continue

        rows = data[entity]
        count = len(rows)
        if count < exp["min_count"]:
            print(f"FAIL: Table '{entity}' count {count} is less than min expected {exp['min_count']}.")
            errors += 1
        else:
            print(f"PASS: JSON Table '{entity:<30}' | Records: {count:<6} (>= {exp['min_count']})")

        if rows:
            sample = rows[0]
            missing_fields = [f for f in exp["required_fields"] if f not in sample]
            if missing_fields:
                print(f"FAIL: Table '{entity}' missing required fields in sample: {missing_fields}")
                errors += 1

    return errors == 0


def validate_csv_datasets(base_dir="."):
    print("\n--- Validating Individual CSV Datasets ---")
    errors = 0
    for entity, exp in TABLE_EXPECTATIONS.items():
        csv_path = os.path.join(base_dir, exp["csv_filename"])
        if not os.path.exists(csv_path):
            print(f"FAIL: CSV file missing: {csv_path}")
            errors += 1
            continue

        try:
            with open(csv_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                rows = list(reader)

            count = len(rows)
            if count < exp["min_count"]:
                print(f"FAIL: CSV '{exp['csv_filename']}' count {count} < min {exp['min_count']}.")
                errors += 1
            else:
                print(f"PASS: CSV '{exp['csv_filename']:<25}' | Rows: {count:<6} | Headers: {len(headers)}")

            missing_fields = [f for f in exp["required_fields"] if f not in headers]
            if missing_fields:
                print(f"FAIL: CSV '{exp['csv_filename']}' missing required headers: {missing_fields}")
                errors += 1

        except Exception as e:
            print(f"FAIL: Error reading CSV '{csv_path}': {e}")
            errors += 1

    return errors == 0


def main():
    json_ok = validate_json_dataset("siped_dataset_completo.json")
    csv_ok = validate_csv_datasets(".")

    if json_ok and csv_ok:
        print("\nALL DATASET VALIDATION ASSERTS PASSED SUCCESSFULLY! (0 Errors)")
        sys.exit(0)
    else:
        print("\nVALIDATION FAILED! Check error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
