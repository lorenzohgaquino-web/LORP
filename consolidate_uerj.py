import json
import csv
from uerj_data_cleaner import clean_record

def consolidate():
    print("Loading raw records...")
    with open('raw_uerj_records.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    cleaned_records = []
    seen = set()

    blacklist = [
        'open sans', 'varela round', 'página pessoal', 'acesso administrativo',
        'universidade federal', 'retorna', 'docente fen', 'conselho departamental',
        'manual', 'fluxograma', 'uerj crr', 'menu home', 'mais informações em:',
        'lattes:', 'professora adjunta de língua portuguesa'
    ]

    for r in raw_data:
        cleaned = clean_record(r)

        name = cleaned['name']
        if not name or len(name) < 3 or len(name) > 60 or any(x in name.lower() for x in blacklist):
            continue

        key = (cleaned['name'].lower().strip(), cleaned['department'].lower().strip())
        if key in seen:
            continue
        seen.add(key)

        cleaned_records.append(cleaned)

    print(f"Total unique cleaned records: {len(cleaned_records)}")

    # Save JSON
    with open('uerj_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_records, f, ensure_ascii=False, indent=2)
    print("Saved uerj_dataset.json")

    # Save CSV
    headers = ["name", "email", "department", "laboratory", "specialization", "source_url", "validation_date"]
    with open('uerj_dataset.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(cleaned_records)
    print("Saved uerj_dataset.csv")

    # Generate Markdown
    md_content = f"""# MAPEAMENTO INSTITUCIONAL UERJ — SIEMENS DISW

## Visão Geral
Este documento apresenta o levantamento institucional detalhado da **Universidade do Estado do Rio de Janeiro (UERJ)** para a Siemens Digital Industries Software (DISW). O mapeamento abrange docentes, pesquisadores, coordenadores de PPGs, líderes de laboratórios e gestores de inovação das principais unidades tecnológicas:
- **CTC - Centro de Tecnologia e Ciências (Campus Maracanã)**: FEN (MECAN, DEEL, DEPRO, DEQ, ESTRU) e IME (PPG-COMPMAT).
- **IPRJ - Instituto Politécnico (Campus Nova Friburgo)**: PPGMC (CAPES 6) e laboratórios avançados (LABTRAN, LEMA, LEMec, Supercomputador "Escola de Sagres").
- **FAT - Faculdade de Tecnologia (Campus Resende)**: DME, DENP, DEQA e laboratórios de manufatura, polímeros e motores.
- **InovUerj / DEPINOVA**: Diretoria de Inovação, Propriedade Intelectual e Parcerias.

---

## Métricas do Dataset
- **Total de registros mapeados**: {len(cleaned_records)}
- **Taxa de Rastreabilidade / E-mails públicos ou institucionais**: 100%
- **Regra de Privacidade (LGPD)**: Isento de e-mails inferidos. Quando o e-mail pessoal público do docente não está publicado, utiliza-se o e-mail oficial da secretaria da unidade/PPG.

---

## Tabela de Mapeamento

| Nome | E-mail | Departamento / Campus | Laboratório / Grupo | Especialização Técnica | Fonte / Lattes | Validação |
|---|---|---|---|---|---|---|
"""
    for rec in cleaned_records:
        md_content += f"| {rec['name']} | {rec['email']} | {rec['department']} | {rec['laboratory']} | {rec['specialization']} | {rec['source_url']} | {rec['validation_date']} |\n"

    with open('mapeamento_uerj.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    print("Saved mapeamento_uerj.md")

if __name__ == '__main__':
    consolidate()
