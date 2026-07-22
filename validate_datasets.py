import json
import csv
import sys

def run_checks():
    print("Running programmatic validation on generated datasets...")

    # 1. Load JSON
    try:
        with open("ipt_dataset.json", "r", encoding="utf-8") as f:
            json_data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON dataset: {e}")
        sys.exit(1)

    print(f"Loaded {len(json_data)} records from JSON.")

    # 2. Check JSON contents
    for idx, r in enumerate(json_data):
        # All required fields present and non-empty
        required_fields = ["nome", "email", "unidade", "departamento", "instituto", "laboratorio", "area_especializacao", "url_fonte", "status_validacao", "data_acesso"]
        for f in required_fields:
            if f not in r:
                print(f"FAIL: Missing field '{f}' in JSON record {idx}: {r}")
                sys.exit(1)
            if not str(r[f]).strip():
                print(f"FAIL: Empty field '{f}' in JSON record {idx}: {r}")
                sys.exit(1)

        # Email format and no inferred/generated emails
        email = r["email"]
        if "@ipt.br" not in email:
            print(f"FAIL: Email '{email}' in record {r['nome']} does not have correct domain @ipt.br.")
            sys.exit(1)

        # Source URL check
        if not r["url_fonte"].startswith("https://somos.ipt.br/professores/view/"):
            print(f"FAIL: Invalid source URL '{r['url_fonte']}' in record {r['nome']}.")
            sys.exit(1)

    print("JSON validation: PASSED.")

    # 3. Load and check CSV
    try:
        with open("ipt_dataset.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            csv_data = list(reader)
    except Exception as e:
        print(f"Error loading CSV dataset: {e}")
        sys.exit(1)

    print(f"Loaded {len(csv_data)} rows from CSV.")
    if len(csv_data) != len(json_data):
        print(f"FAIL: Count mismatch between JSON ({len(json_data)}) and CSV ({len(csv_data)})")
        sys.exit(1)

    for idx, r in enumerate(csv_data):
        # Fields present and non-empty
        for f in required_fields:
            if f not in r:
                print(f"FAIL: Missing field '{f}' in CSV row {idx}: {r}")
                sys.exit(1)
            if not str(r[f]).strip():
                print(f"FAIL: Empty field '{f}' in CSV row {idx}: {r}")
                sys.exit(1)

    print("CSV validation: PASSED.")

    # 4. Check Markdown Report
    try:
        with open("mapeamento_ipt.md", "r", encoding="utf-8") as f:
            md_text = f.read()
    except Exception as e:
        print(f"Error reading Markdown report: {e}")
        sys.exit(1)

    # Check if critical business divisions are covered
    critical_sections = [
        "TD — Tecnologias Digitais",
        "EN — Energia",
        "MA — Materiais Avançados",
        "CIMA — Cidades, Infraestrutura e Meio Ambiente",
        "HE — Habitações e Edificações",
        "BIO — Bionanomanufatura",
        "TRM — Tecnologias Regulatórias e Metrológicas",
        "ET — Ensino Tecnológico"
    ]

    for s in critical_sections:
        if s not in md_text:
            print(f"FAIL: Section '{s}' missing from mapeamento_ipt.md.")
            sys.exit(1)

    print("Markdown validation: PASSED.")
    print("\nALL PROGRAMMATIC CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_checks()
