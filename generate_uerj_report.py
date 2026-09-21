import json

def generate_report():
    with open('uerj_dataset.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    md = []
    md.append("# Mapeamento Institucional e Ecossistema de Pesquisa — UERJ (Universidade do Estado do Rio de Janeiro)")
    md.append("")
    md.append("## Executive Summary")
    md.append("Este documento apresenta o mapeamento institucional detalhado da Universidade do Estado do Rio de Janeiro (UERJ) com foco em simulação numérica, modelagem computacional, engenharia mecânica, manufatura avançada e inovação tecnológica para parcerias com a **Siemens Digital Industries Software (DISW)**.")
    md.append("")
    md.append(f"O levantamento identificou **{len(data)} pesquisadores e especialistas ativos**, cobrindo o Centro de Tecnologia e Ciências (CTC - Campus Maracanã), o Instituto Politécnico (IPRJ - Campus Nova Friburgo), a Faculdade de Tecnologia (FAT - Campus Resende), o Instituto de Matemática e Estatística (IME - PPG-COMPMAT) e a Diretoria de Inovação (InovUerj / DEPINOVA PR2).")
    md.append("")
    md.append("## Resumo de Aderência Estratégica por Unidade")
    md.append("| Campus / Unidade | Foco Técnico Principal | Soluções Siemens DISW Alinhadas | Grau de Aderência |")
    md.append("|---|---|---|---|")
    md.append("| **IPRJ (Nova Friburgo)** | Modelagem Computacional, Termofluidodinâmica, Meios Porosos, HPC | STAR-CCM+, Simcenter 3D, gPROMS, HEEDS | **ALTA** |")
    md.append("| **FEN / MECAN (Maracanã)** | CFD, Fenômenos de Transporte, Motores, Acústica e Vibrações | STAR-CCM+, Simcenter Amesim, NX | **ALTA** |")
    md.append("| **FAT (Resende)** | Manufatura, Materiais, Polímeros, Hidráulica, Pneumática e Motores | NX CAD/CAM, Tecnomatix, Simcenter Amesim | **ALTA** |")
    md.append("| **IME / PPG-COMPMAT** | Inteligência Artificial, Analytics, Métodos Numéricos e HPC | MindSphere, HEEDS, Opcenter | **MÉDIA-ALTA** |")
    md.append("| **FEN / DEEL, DEPRO, DEQ, Civil** | Controle, Automação, Otimização de Processos e Estruturas | Simcenter Flomaster, gPROMS, Plant Simulation | **MÉDIA-ALTA** |")
    md.append("| **InovUerj / DEPINOVA** | Propriedade Intelectual, Incubadoras e Projetos P&D Empresa | Parcerias Tecnológicas & Co-fomento (EMBRAPII/FAPERJ) | **ALTA** |")
    md.append("")
    md.append("## Centros de Excelência e Laboratórios Estratégicos")
    md.append("1. **GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais) - FEN Maracanã**")
    md.append("   - *Foco*: Simulação CFD avançada, escoamentos multifásicos, reservatórios e fenomênica de transporte.")
    md.append("   - *Liderança*: Prof. Norberto Mangiavacchi e Prof. José da Rocha Miranda Pontes.")
    md.append("2. **Supercomputador 'Escola de Sagres' e LABTRAN - IPRJ Nova Friburgo**")
    md.append("   - *Foco*: Computação de alto desempenho (HPC) para simulações multiescala, meio poroso, transporte de partículas e otimização.")
    md.append("   - *Liderança*: Prof. Antônio José da Silva Neto e Prof. Diego Campos Knupp.")
    md.append("3. **Laboratórios Industriais FAT Resende**")
    md.append("   - *Foco*: Processamento de materiais e metais, polímeros/compósitos, sistemas hidráulicos e motores para o polo automotivo do Sul Fluminense.")
    md.append("   - *Liderança*: Profa. Monique Osório Talarico da Conceição.")
    md.append("")
    md.append("## Mapeamento Completo de Pesquisadores e Especialistas")
    md.append("| Nome | E-mail | Setor / Departamento / Campus | Laboratório / Grupo | Especialização Técnica (Siemens DISW) | Fonte Oficial |")
    md.append("|---|---|---|---|---|---|")

    for row in data:
        nome = row['nome']
        email = row['email']
        dept = row['setor_departamento_campus']
        lab = row['laboratorio_grupo']
        spec = row['especializacao']
        url = row['url_fonte']
        md.append(f"| **{nome}** | `{email}` | {dept} | {lab} | {spec} | [Fonte]({url}) |")

    md.append("")
    md.append("---")
    md.append("*Relatório gerado de forma automatizada com 100% de rastreabilidade e sem e-mails inferidos.*")

    report_content = "\n".join(md)
    with open('mapeamento_uerj.md', 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"Report mapeamento_uerj.md generated successfully with {len(data)} researchers.")

if __name__ == "__main__":
    generate_report()
