import json
import csv

def generate_artifacts():
    with open('uerj_consolidated.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Generating artifacts for {len(data)} records...")

    # 1. uerj_dataset.json
    with open('uerj_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved uerj_dataset.json")

    # 2. uerj_dataset.csv
    headers = [
        "Nome Completo",
        "E-mail Institucional",
        "Setor / Departamento / Campus",
        "Laboratório / Grupo de Pesquisa",
        "Área de Especialização Técnica",
        "URL Fonte de Validação",
        "Status de Validação",
        "Data de Acesso"
    ]

    with open('uerj_dataset.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in data:
            writer.writerow([
                r['nome'],
                r['email'],
                r['unidade_departamento'],
                r['laboratorio_grupo'],
                r['especializacao_tecnica'],
                r['url_fonte'],
                r['status_validacao'],
                r['data_acesso']
            ])
    print("Saved uerj_dataset.csv")

    # 3. mapeamento_uerj.md
    md_content = []
    md_content.append("# Mapeamento Institucional e Científico — UERJ (Universidade do Estado do Rio de Janeiro)")
    md_content.append("\n## Sumário Executivo")
    md_content.append(f"Este documento apresenta o mapeamento institucional aprofundado da **Universidade do Estado do Rio de Janeiro (UERJ)**, com foco estratégico nas soluções de software industrial, simulação e modelagem computacional da **Siemens Digital Industries Software (DISW)** (Simcenter STAR-CCM+, Simcenter Amesim, NX, Tecnomatix, MindSphere/mendix, gPROMS).")
    md_content.append(f"Ao todo, foram identificados e validados **{len(data)} docentes e pesquisadores ativos**, líderes de laboratórios, coordenadores de programas de pós-graduação e gestores de inovação espalhados pelo Campus Maracanã (FEN e IME), Campus Regional de Nova Friburgo (IPRJ) e Campus Regional de Resende (FAT).")

    md_content.append("\n### Distribuição por Unidade / Departamento")

    # Calculate counts
    units_count = {}
    for r in data:
        u = r['unidade_departamento']
        units_count[u] = units_count.get(u, 0) + 1

    for u, count in sorted(units_count.items(), key=lambda x: x[1], reverse=True):
        md_content.append(f"- **{u}**: {count} pesquisadores mapeados")

    md_content.append("\n## Destaques por Núcleo Estratégico (Foco Siemens DISW)")
    md_content.append("1. **IPRJ Nova Friburgo & PPGMC (CAPES 6)**: Centro de excelência internacional em modelagem computacional, CFD, meios porosos, dinâmica e supercomputação ('Escola de Sagres'). Oportunidade prioritária para Simcenter STAR-CCM+, Amesim e gPROMS.")
    md_content.append("2. **FEN Maracanã (MECAN, DEEL, DEPRO, DEQ, CIVIL)**: Destaque para o **GESAR** (simulação CFD e ambiental), **LAMMAC**, **LaCaM**, **LFT/LFM**, **LMES** e **LaFIT**, cobrindo mecânica dos fluidos, vibrações, estruturas, otimização industrial e processos químicos.")
    md_content.append("3. **FAT Resende**: Foco em manufatura avançada, polímeros, compósitos, mecânica, energia, hidráulica e pneumática, com forte integração à cadeia automobilística do Sul Fluminense.")
    md_content.append("4. **IME / PPG-COMPMAT**: Pesquisas em inteligência artificial, computação de alto desempenho (HPC) e métodos numéricos aplicados a problemas complexos de engenharia.")
    md_content.append("5. **InovUerj / DEPINOVA**: Diretoria de Inovação da UERJ, responsável pela gestão de propriedade intelectual, transferência de tecnologia, parcerias universidade-empresa e acompanhamento de incubadoras.")

    md_content.append("\n## Tabela Completa do Dataset Institucional UERJ")
    md_content.append("| Nome Completo | E-mail Institucional | Setor / Departamento / Campus | Laboratório / Grupo de Pesquisa | Área de Especialização Técnica | URL Fonte de Validação | Status de Validação | Data de Acesso |")
    md_content.append("| --- | --- | --- | --- | --- | --- | --- | --- |")

    for r in data:
        row_str = f"| {r['nome']} | {r['email']} | {r['unidade_departamento']} | {r['laboratorio_grupo']} | {r['especializacao_tecnica']} | {r['url_fonte']} | {r['status_validacao']} | {r['data_acesso']} |"
        md_content.append(row_str)

    with open('mapeamento_uerj.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    print("Saved mapeamento_uerj.md")

if __name__ == '__main__':
    generate_artifacts()
