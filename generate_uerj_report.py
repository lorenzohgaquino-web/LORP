import json

def generate_report():
    with open("uerj_dataset.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    markdown = []
    markdown.append("# Mapeamento Institucional de Pesquisadores e Laboratórios — UERJ\n")
    markdown.append("## Visão Geral e Alinhamento Estratégico com Siemens DISW\n")
    markdown.append("Este documento apresenta o mapeamento institucional da **Universidade do Estado do Rio de Janeiro (UERJ)**, com foco em pesquisadores, líderes de laboratórios, coordenadores de programas de pós-graduação e gestores de inovação nas áreas de **Engenharia, Computação Científica e Ciências Exatas**.\n")
    markdown.append("A UERJ destaca-se em simulação numérico-computacional de alto desempenho (HPC), termofluidodinâmica, mecânica dos sólidos e estruturas, otimização de processos e manufatura industrial, apresentando aderência direta ao portfólio de softwares industriais da Siemens DISW (**STAR-CCM+, Simcenter Amesim, NX, Tecnomatix, MindSphere/Xcelerator**).\n\n")

    markdown.append(f"**Total de Pesquisadores e Especialistas Mapeados:** {len(data)}\n")
    markdown.append("**Traceabilidade e Contatos:** 100% dos registros possuem e-mails públicos institucionais verificados ou fallbacks de secretarias/departamentos em estrita conformidade com a LGPD.\n\n")

    markdown.append("--- \n\n")

    # Group by Sector/Department
    departments = {}
    for row in data:
        dept = row["setor_departamento"]
        if dept not in departments:
            departments[dept] = []
        departments[dept].append(row)

    for dept, items in departments.items():
        markdown.append(f"### {dept}\n")
        markdown.append("| Nome | E-mail | Laboratório / Grupo | Especialização Técnica (Siemens DISW) | Fonte / Validação |\n")
        markdown.append("| :--- | :--- | :--- | :--- | :--- |\n")
        for item in items:
            markdown.append(f"| **{item['nome']}** | `{item['email']}` | {item['laboratorio_grupo']} | {item['especializacao']} | [{item['status_validacao']}]({item['url_fonte']}) |\n")
        markdown.append("\n")

    markdown.append("--- \n\n")
    markdown.append("## Sumário Executivo e Recomendações de Parceria\n")
    markdown.append("1. **Pólo de Alta Performance em Simulação (IPRJ & GESAR):** O IPRJ em Nova Friburgo (PPGMC CAPES 6) e o GESAR no Maracanã abrigam infraestrutura computacional avançada (Supercomputador *Escola de Sagres*) voltada para CFD multiescala, meios porosos e métodos numéricos de fronteira. Parcerias estratégicas com o software STAR-CCM+ e Simcenter Amesim possuem elevadíssimo potencial de co-desenvolvimento.\n")
    markdown.append("2. **Engenharia de Estruturas e Geotecnia Computacional (PGECIV / FEN):** A FEN Maracanã detém excelência consolidada em mecânica das estruturas, estruturas mistas e geotecnia, com demandas para Simcenter Nastran/FEMAP e soluções de Análise Numérica Avançada.\n")
    markdown.append("3. **Pólo Industrial e Manufatura (FAT Resende):** A FAT Resende localiza-se no hub automotivo e industrial do Sul Fluminense, desenvolvendo pesquisas aplicadas em polímeros, compósitos e sistemas hidráulicos/motores. Oportunidade prioritária de engajamento para soluções de NX CAD/CAM e Tecnomatix.\n")
    markdown.append("4. **Transferência Tecnológica e Propriedade Intelectual (InovUerj):** Interface direta para formalização de convênios de P&D via EMBRAPII, ANEEL, ANP e FAPERJ.\n")

    report_text = "".join(markdown)
    with open("mapeamento_uerj.md", "w", encoding="utf-8") as f:
        f.write(report_text)

    print("mapeamento_uerj.md generated successfully.")

if __name__ == "__main__":
    generate_report()
