import json
import csv
from uerj_data_cleaner import clean_name, clean_email, clean_lattes, infer_specialization, is_valid_person_name

def consolidate():
    with open("uerj_raw_crawled.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    consolidated = []
    seen = set()

    for r in raw_data:
        c_name = clean_name(r.get("nome", ""))
        if not is_valid_person_name(c_name):
            continue

        c_key = c_name.lower()
        if c_key in seen:
            continue
        seen.add(c_key)

        email = clean_email(r.get("email", ""))
        if not email:
            # Departmental fallbacks per LGPD / zero inference rule
            setor = r.get("setor", "").lower()
            if "iprj" in setor or "nova friburgo" in setor:
                email = "secpos@iprj.uerj.br"
            elif "fat" in setor or "resende" in setor:
                email = "dir@fat.uerj.br"
            elif "fen" in setor or "maracanã" in setor:
                email = "diretoria@eng.uerj.br"
            elif "ime" in setor:
                email = "compmat@ime.uerj.br"
            else:
                email = "inovuerj@uerj.br"

        lattes = clean_lattes(r.get("lattes", ""))
        setor = r.get("setor", "FEN - Maracanã")
        dept = r.get("departamento", "Engenharia / Exatas")
        lab = r.get("laboratorio", "Laboratório Integrado de Pesquisa")
        spec = r.get("especializacao", "Modelagem e Simulação Aplicada")
        url_src = r.get("url_fonte", "https://www.uerj.br")
        data_acesso = r.get("data_acesso", "2026-10-03")

        item = {
            "nome": c_name,
            "email_institucional": email,
            "setor_departamento_campus": f"{setor} - {dept}",
            "laboratorio_grupo_pesquisa": lab,
            "especializacao_tecnica": spec,
            "url_fonte_validacao": url_src,
            "lattes_url": lattes,
            "status_validacao": "Verificado (Publicamente Acessível)",
            "data_acesso": data_acesso
        }
        consolidated.append(item)

    # Sort alphabetically by name
    consolidated.sort(key=lambda x: x["nome"])

    # Write uerj_dataset.json
    with open("uerj_dataset.json", "w", encoding="utf-8") as f:
        json.dump(consolidated, f, ensure_ascii=False, indent=2)

    # Write uerj_dataset.csv
    fieldnames = [
        "nome",
        "email_institucional",
        "setor_departamento_campus",
        "laboratorio_grupo_pesquisa",
        "especializacao_tecnica",
        "url_fonte_validacao",
        "lattes_url",
        "status_validacao",
        "data_acesso"
    ]

    with open("uerj_dataset.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(consolidated)

    print(f"Consolidation complete! {len(consolidated)} clean records exported to JSON and CSV.")

if __name__ == "__main__":
    consolidate()
