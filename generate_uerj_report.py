import json
import csv

def main():
    with open("uerj_dataset.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Export CSV
    headers = [
        "nome",
        "email",
        "setor_departamento_campus",
        "laboratorio_grupo",
        "especializacao_tecnica",
        "url_fonte",
        "status_validacao",
        "data_acesso"
    ]

    with open("uerj_dataset.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

    print(f"Exported {len(data)} records to uerj_dataset.csv")

    # 2. Generate Markdown Executive Report
    md = []
    md.append("# MAPEAMENTO INSTITUCIONAL APROFUNDADO — UERJ (UNIVERSIDADE DO ESTADO DO RIO DE JANEIRO)")
    md.append("**Foco Estratégico Siemens Digital Industries Software (DISW)**\n")
    md.append(f"**Total de Pesquisadores / Especialistas Mapeados:** {len(data)}\n")

    md.append("## RESUMO EXECUTIVO DA ESTRUTURA UERJ")
    md.append("O mapeamento da Universidade do Estado do Rio de Janeiro (UERJ) contemplou os 3 campi estratégicos de Engenharia e Ciências Exatas, além do ecossistema de inovação central:\n")
    md.append("1. **CTC / FEN (Campus Maracanã - Rio de Janeiro)**: Foco nos departamentos MECAN, DEEL/DETEL, DEPRO/DEIN, DEQ e ESTRUTURAS/CIVIL, agregando laboratórios de ponta como GESAR, LMES, LaFIT e LFM.")
    md.append("2. **IPRJ (Campus Nova Friburgo)**: Polo estratégico para simulação numérica em alta fidelidade e mecânica computacional. Agrupa o Programa de Pós-Graduação em Modelagem Computacional (PPGMC - CAPES 6), os departamentos DEMEC e DMC, o laboratório LABTRAN e o supercomputador 'Escola de Sagres'.")
    md.append("3. **FAT (Campus Resende)**: Foco industrial e manufatura com os departamentos DME, DEQA, DENP e DMFC, com linhas aplicadas em polímeros, compósitos, hidráulica, pneumática e simulação de processos.")
    md.append("4. **IME (Campus Maracanã)**: Programa de Pós-Graduação em Ciências Computacionais e Modelagem Matemática (PPG-COMPMAT), focado em Inteligência Artificial, Analytics e Computação de Alto Desempenho (HPC).")
    md.append("5. **InovUerj / DEPINOVA**: Diretoria de Inovação responsável pela gestão de propriedade intelectual, escritórios de projetos e transferência de tecnologia universidade-empresa.\n")

    md.append("## TABELA COMPLETA DE PESQUISADORES E ESPECIALISTAS MAPEADOS")
    md.append("| Nome | E-mail Institucional | Setor / Departamento / Campus | Laboratório / Grupo | Especialização Técnica (Taxonomia Siemens DISW) | URL Fonte / Validação |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    for r in data:
        nome = r['nome'].replace('|', '\\|')
        email = r['email'].replace('|', '\\|')
        setor = r['setor_departamento_campus'].replace('|', '\\|')
        lab = r['laboratorio_grupo'].replace('|', '\\|')
        spec = r['especializacao_tecnica'].replace('|', '\\|')
        url = r['url_fonte']

        md.append(f"| **{nome}** | `{email}` | {setor} | {lab} | {spec} | [Fonte Oficial]({url}) |")

    md.append("\n---\n*Relatório gerado automaticamente via pipeline de raspagem e consolidação validado em 2026-03-30.*")

    with open("mapeamento_uerj.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("Generated mapeamento_uerj.md successfully.")

if __name__ == "__main__":
    main()
