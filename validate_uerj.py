import json
import csv
import re
import os

def validate():
    print("=== STARTING UERJ DATASET VALIDATION ===")

    # 1. Check file existence
    files = ["uerj_dataset.json", "uerj_dataset.csv", "mapeamento_uerj.md"]
    for f in files:
        assert os.path.exists(f), f"File missing: {f}"
        assert os.path.getsize(f) > 0, f"File empty: {f}"
        print(f"[OK] File present and non-empty: {f} ({os.path.getsize(f)} bytes)")

    # 2. Check JSON structure & schema
    with open("uerj_dataset.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)

    assert isinstance(json_data, list), "JSON root must be a list"
    assert len(json_data) > 0, "JSON dataset cannot be empty"
    print(f"[OK] JSON dataset contains {len(json_data)} records")

    expected_keys = {
        "nome", "email", "setor_departamento", "laboratorio_grupo",
        "especializacao_tecnica", "url_fonte", "status_validacao", "data_acesso"
    }

    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    for idx, row in enumerate(json_data):
        # Validate keys
        keys = set(row.keys())
        assert keys == expected_keys, f"Record {idx} missing/extra keys: {keys ^ expected_keys}"

        # Validate non-empty mandatory fields
        for k in expected_keys:
            val = str(row[k]).strip()
            assert val != "", f"Record {idx} has empty field: {k}"

        # Validate email format
        email = row["email"].strip()
        assert email_regex.match(email), f"Record {idx} has invalid email format: {email}"

        # Check no inferred dummy emails or prohibited placeholders
        assert not email.endswith("@inferred.com"), f"Record {idx} contains inferred email"

    print("[OK] All JSON records passed schema, non-empty, and valid email format checks")

    # 3. Check CSV format & header conformity
    with open("uerj_dataset.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_headers = set(reader.fieldnames)
        assert csv_headers == expected_keys, f"CSV headers mismatch: {csv_headers ^ expected_keys}"

        csv_rows = list(reader)
        assert len(csv_rows) == len(json_data), f"CSV row count ({len(csv_rows)}) differs from JSON ({len(json_data)})"

    print("[OK] CSV file matches JSON schema and record count")

    # 4. Check Markdown report completeness
    with open("mapeamento_uerj.md", "r", encoding="utf-8") as f:
        md_text = f.read()

    assert "# MAPEAMENTO INSTITUCIONAL APROFUNDADO — UERJ" in md_text, "Markdown missing title"
    assert "MECAN" in md_text, "Markdown missing FEN/MECAN"
    assert "IPRJ" in md_text, "Markdown missing IPRJ"
    assert "FAT" in md_text, "Markdown missing FAT"
    assert "GESAR" in md_text, "Markdown missing GESAR"
    assert "InovUerj" in md_text, "Markdown missing InovUerj"

    print("[OK] Markdown report verified for required sections and keywords")
    print("=== VALIDATION SUCCESSFUL: ALL CHECKS PASSED ===")

if __name__ == "__main__":
    validate()
