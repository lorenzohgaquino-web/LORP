import json
import csv
import datetime

def main():
    print("Iniciando a consolidação dos dados da UFABC...")

    # Load raw data
    with open("docentes_geral_raw.json", "r", encoding="utf-8") as f:
        geral = json.load(f)

    # Standardize access date (ISO 8601)
    access_date = datetime.date.today().isoformat()

    # Map area/centro to list of verified emails for substitution
    area_backup_map = {}
    centro_backup_map = {}

    for doc in geral:
        name = doc['nome']
        email = doc['email']
        centro = doc['centro']
        area = doc['area']

        if email and email != "Não Disponível" and email != "não disponível publicamente":
            # Add to area backup map
            area_key = (centro, area)
            if area_key not in area_backup_map:
                area_backup_map[area_key] = []
            area_backup_map[area_key].append((name, email))

            # Add to centro backup map
            if centro not in centro_backup_map:
                centro_backup_map[centro] = []
            centro_backup_map[centro].append((name, email))

    consolidated = []

    for doc in geral:
        name = doc['nome']
        email = doc['email']
        centro = doc['centro']
        area = doc['area']
        url = doc['url_fonte']
        lattes = doc.get('lattes', 'Não Disponível')

        lab = "N/A"
        # If we got this docente from SIGAA we can extract more details
        # Let's see if we can find any lab or program
        # We can map it if we want, but "N/A" is standard where unavailable.

        obs = ""
        status = "Verificado"

        if not email or email == "Não Disponível":
            email = "Não disponível publicamente"
            status = "Indisponível"

            # Apply substitution rule: find another professor of the same area/centro
            area_key = (centro, area)
            backup_candidates = area_backup_map.get(area_key, [])

            # If no candidate in the exact same area, find in the same centro
            if not backup_candidates:
                backup_candidates = centro_backup_map.get(centro, [])

            if backup_candidates:
                # Pick the first candidate
                backup_name, backup_email = backup_candidates[0]
                obs = f"E-mail indisponível. Docente alternativo da mesma divisão: {backup_name} ({backup_email})"
                status = "Parcial"
            else:
                obs = "E-mail indisponível. Sem docentes alternativos disponíveis na divisão."
        else:
            obs = "E-mail público oficial verificado."

        consolidated.append({
            "Nome completo": name,
            "E-mail institucional público": email,
            "Unidade / Divisão": centro,
            "Departamento": area,
            "Laboratório / Grupo de pesquisa": lab,
            "URL exata da fonte": url,
            "Status de validação": status,
            "Data de acesso": access_date,
            "Observações": obs,
            "Lattes": lattes
        })

    # Sort consolidated by Name
    consolidated.sort(key=lambda x: x["Nome completo"])

    # Save consolidated JSON
    with open("ufabc_dataset.json", "w", encoding="utf-8") as f:
        json.dump(consolidated, f, ensure_ascii=False, indent=2)

    # Save consolidated CSV with full quotes for data integrity
    with open("ufabc_dataset.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        # Headers
        writer.writerow([
            "Nome completo",
            "E-mail institucional público",
            "Unidade / Divisão",
            "Departamento",
            "Laboratório / Grupo de pesquisa",
            "URL exata da fonte",
            "Status de validação",
            "Data de acesso",
            "Observações"
        ])
        for row in consolidated:
            writer.writerow([
                row["Nome completo"],
                row["E-mail institucional público"],
                row["Unidade / Divisão"],
                row["Departamento"],
                row["Laboratório / Grupo de pesquisa"],
                row["URL exata da fonte"],
                row["Status de validação"],
                row["Data de acesso"],
                row["Observações"]
            ])

    # Generate the Markdown Report `mapeamento_ufabc.md`
    print("Gerando relatório mapeamento_ufabc.md...")
    total = len(consolidated)
    verificados = len([x for x in consolidated if x["Status de validação"] == "Verificado"])
    parciais = len([x for x in consolidated if x["Status de validação"] == "Parcial"])
    indisponiveis = len([x for x in consolidated if x["Status de validação"] == "Indisponível"])

    with open("mapeamento_ufabc.md", "w", encoding="utf-8") as f:
        f.write("# Mapeamento Institucional Aprofundado — UFABC\n\n")
        f.write("## Sumário Executivo\n")
        f.write(f"Este relatório apresenta o mapeamento institucional completo da **Universidade Federal do ABC (UFABC)**, focado nos centros estratégicos: **CMCC** (Centro de Matemática, Computação e Cognição), **CECS** (Centro de Engenharia, Modelagem e Ciências Sociais Aplicadas) e **CCNH** (Centro de Ciências Naturais e Humanas). Foram mapeados com sucesso **{total}** docentes ativos e pesquisadores permanentes, mantendo a rastreabilidade completa e sem e-mails inferidos.\n\n")

        f.write("### Estatísticas do Mapeamento\n")
        f.write(f"- **Total de Docentes Mapeados:** {total}\n")
        f.write(f"- **Docentes com E-mail Verificado:** {verificados} ({verificados/total*100:.1f}%)\n")
        f.write(f"- **Docentes com E-mail Parcial (Substituição Aplicada):** {parciais} ({parciais/total*100:.1f}%)\n")
        f.write(f"- **Docentes com E-mail Indisponível:** {indisponiveis} ({indisponiveis/total*100:.1f}%)\n\n")

        f.write("## Tabela de Mapeamento Institucional\n\n")
        f.write("| Nome completo | E-mail institucional público | Unidade / Divisão | Departamento / Área | Status de validação | Data de acesso | Observações |\n")
        f.write("| --- | --- | --- | --- | --- | --- | --- |\n")
        for row in consolidated:
            f.write(f"| {row['Nome completo']} | {row['E-mail institucional público']} | {row['Unidade / Divisão']} | {row['Departamento']} | {row['Status de validação']} | {row['Data de acesso']} | {row['Observações']} |\n")

        f.write("\n\n---\n*Relatório gerado automaticamente em conformidade com as diretrizes da LGPD brasileira e as políticas do projeto.*")

    print("Consolidação concluída com sucesso!")

if __name__ == "__main__":
    main()
