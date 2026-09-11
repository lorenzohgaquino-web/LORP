import json
import csv
import re
import os

def validate():
    json_path = "uerj_dataset.json"
    csv_path = "uerj_dataset.csv"
    md_path = "mapeamento_uerj.md"

    assert os.path.exists(json_path), "JSON dataset missing!"
    assert os.path.exists(csv_path), "CSV dataset missing!"
    assert os.path.exists(md_path), "Markdown mapping missing!"

    # 1. Validate JSON
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    print(f"[JSON] Loaded {len(json_data)} records.")
    assert len(json_data) > 0, "JSON dataset is empty!"

    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    for idx, r in enumerate(json_data):
        assert r.get("nome"), f"Record {idx} missing name"
        assert r.get("email"), f"Record {idx} missing email"
        assert email_regex.match(r["email"]), f"Record {idx} has invalid email: {r['email']}"
        assert r.get("setor"), f"Record {idx} missing sector"
        assert r.get("laboratorio"), f"Record {idx} missing lab"
        assert r.get("especializacao"), f"Record {idx} missing specialization"
        assert r.get("url"), f"Record {idx} missing url"
        assert r["url"].startswith("http"), f"Record {idx} has invalid url: {r['url']}"
        assert r.get("status") == "Verificado", f"Record {idx} status not Verificado"
        assert r.get("data_acesso"), f"Record {idx} missing access date"

    # 2. Validate CSV
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))

    header = reader[0]
    csv_rows = reader[1:]
    expected_header = [
        "Nome",
        "E-mail",
        "Setor / Departamento / Campus",
        "Laboratório / Grupo de Pesquisa",
        "Área de Especialização Técnica",
        "URL de Validação",
        "Status de Validação",
        "Data de Acesso"
    ]
    assert header == expected_header, f"CSV header mismatch: {header}"
    assert len(csv_rows) == len(json_data), f"CSV row count ({len(csv_rows)}) does not match JSON count ({len(json_data)})"
    print(f"[CSV] Verified {len(csv_rows)} rows matching JSON count.")

    # 3. Validate Markdown
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    table_lines = [line for line in md_text.split("\n") if line.startswith("|") and "Nome Completo" not in line and "---" not in line]
    assert len(table_lines) == len(json_data), f"MD table row count ({len(table_lines)}) does not match JSON count ({len(json_data)})"
    print(f"[MD] Verified {len(table_lines)} table rows matching JSON count.")

    print("ALL VALIDATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    validate()
