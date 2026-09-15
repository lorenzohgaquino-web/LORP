import json
import csv
import re
import os

def validate():
    print("=== STARTING PROGRAMMATIC VALIDATION FOR UERJ DATASET ===")

    # 1. Check file existence
    files = ['uerj_dataset.json', 'uerj_dataset.csv', 'mapeamento_uerj.md']
    for f in files:
        assert os.path.exists(f), f"Missing required file: {f}"
        assert os.path.getsize(f) > 0, f"File is empty: {f}"
        print(f"✓ File {f} exists ({os.path.getsize(f)} bytes)")

    # 2. Validate JSON schema & non-empty fields
    with open('uerj_dataset.json', 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    expected_fields = ['nome', 'email', 'campus_setor', 'laboratorio_grupo', 'especializacao_tecnica', 'url_fonte', 'status_validacao', 'data_acesso']

    email_regex = re.compile(r'^([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$')

    for idx, row in enumerate(json_data):
        for field in expected_fields:
            assert field in row, f"Record {idx} missing field {field}"
            assert str(row[field]).strip() != "", f"Record {idx} field {field} is empty"

        # Verify valid email pattern
        assert email_regex.match(row['email']), f"Record {idx} email invalid: {row['email']}"
        # Verify traceable URL
        assert row['url_fonte'].startswith('http'), f"Record {idx} URL invalid: {row['url_fonte']}"

    print(f"✓ JSON Schema valid! Verified {len(json_data)} records.")

    # 3. Validate CSV consistency & header
    with open('uerj_dataset.csv', 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))

    assert len(reader) == len(json_data), f"CSV count ({len(reader)}) != JSON count ({len(json_data)})"
    assert list(reader[0].keys()) == expected_fields, f"CSV headers do not match expected schema!"

    print(f"✓ CSV Schema valid and consistent with JSON ({len(reader)} rows).")

    # 4. Validate Markdown structure and count
    with open('mapeamento_uerj.md', 'r', encoding='utf-8') as f:
        md_text = f.read()

    assert "# Mapeamento Institucional UERJ" in md_text, "Markdown missing main title!"
    assert "| Nome | E-mail Institucional Público |" in md_text, "Markdown missing data table header!"
    assert "IPRJ (Nova Friburgo)" in md_text, "Markdown missing IPRJ section!"
    assert "FEN (Maracanã)" in md_text, "Markdown missing FEN section!"
    assert "FAT (Resende)" in md_text, "Markdown missing FAT section!"
    assert "IME (PPG-COMPMAT)" in md_text, "Markdown missing IME section!"
    assert "InovUerj" in md_text, "Markdown missing InovUerj section!"

    table_rows = [line for line in md_text.split('\n') if line.startswith('| ') and not line.startswith('| Nome ') and not line.startswith('|---')]
    assert len(table_rows) == len(json_data), f"Markdown table rows ({len(table_rows)}) != JSON records ({len(json_data)})"

    print(f"✓ Markdown validation passed! Table contains {len(table_rows)} verified rows.")
    print("=== ALL PROGRAMMATIC VALIDATION CHECKS PASSED SUCCESSFULLY! ===")

if __name__ == '__main__':
    validate()
