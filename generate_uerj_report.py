#!/usr/bin/env python3
"""
generate_uerj_report.py
Generates the comprehensive Markdown report `mapeamento_uerj.md` from `uerj_dataset.json`.
Formats records into Markdown tables grouped by strategic UERJ units (FEN Maracanã, IPRJ Nova Friburgo,
FAT Resende, IME/PPG-COMPMAT, InovUerj / DEPINOVA). Includes Executive Summary and Methodology.
"""

import json

def generate_report():
    print("[INFO] Generating Markdown report mapeamento_uerj.md...")
    with open("uerj_dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # Group records by strategic unit
    groups = {
        "1. FEN — Faculdade de Engenharia (Campus Maracanã)": [],
        "2. IPRJ — Instituto Politécnico (Campus Regional de Nova Friburgo)": [],
        "3. FAT — Faculdade de Tecnologia (Campus Regional de Resende)": [],
        "4. IME — Instituto de Matemática e Estatística & PPG-COMPMAT (Maracanã)": [],
        "5. InovUerj / DEPINOVA — Diretoria de Inovação e Ecossistema": [],
        "6. Outras Unidades e Grupos de Pesquisa UERJ": []
    }

    for item in dataset:
        dept = item.get("setor_departamento_campus", "")
        if "FEN" in dept or "Engenharia" in dept and "Resende" not in dept and "Friburgo" not in dept:
            groups["1. FEN — Faculdade de Engenharia (Campus Maracanã)"].append(item)
        elif "IPRJ" in dept or "Nova Friburgo" in dept or "PPGMC" in dept:
            groups["2. IPRJ — Instituto Politécnico (Campus Regional de Nova Friburgo)"].append(item)
        elif "FAT" in dept or "Resende" in dept:
            groups["3. FAT — Faculdade de Tecnologia (Campus Regional de Resende)"].append(item)
        elif "IME" in dept or "COMPMAT" in dept:
            groups["4. IME — Instituto de Matemática e Estatística & PPG-COMPMAT (Maracanã)"].append(item)
        elif "InovUerj" in dept or "DEPINOVA" in dept or "PR2" in dept:
            groups["5. InovUerj / DEPINOVA — Diretoria de Inovação e Ecossistema"].append(item)
        else:
            groups["6. Outras Unidades e Grupos de Pesquisa UERJ"].append(item)

    report = []
    report.append("# MAPEAMENTO INSTITUCIONAL APROFUNDADO — UERJ (UNIVERSIDADE DO ESTADO DO RIO DE JANEIRO)")
    report.append("**Foco Estratégico:** Siemens Digital Industries Software (DISW) — Simulação, Modelagem Numérica, CFD, Elementos Finitos, HPC, Manufatura e Inovação.")
    report.append("")
    report.append("---")
    report.append("")
    report.append("## SUMÁRIO EXECUTIVO")
    report.append("Este documento apresenta o mapeamento completo e detalhado do corpo docente, pesquisadores, coordenadores de programas de pós-graduação (PPGs), líderes de laboratórios e gestores de inovação da **Universidade do Estado do Rio de Janeiro (UERJ)**.")
    report.append("")
    report.append(f"Ao todo, foram identificados e verificados **{len(dataset)} registros estratégicos** distribuídos entre os principais campi da instituição: **Maracanã (Rio de Janeiro)**, **Nova Friburgo (IPRJ)** e **Resende (FAT)**.")
    report.append("")
    report.append("### Principais Destaques Por Unidade Estratégica:")
    report.append("1. **IPRJ — Instituto Politécnico (Nova Friburgo):** Centro de excelência internacional em modelagem computacional (PPGMC CAPES 6). Abriga o Supercomputador *Escola de Sagres* e o LABTRAN (Transporte de Partículas e Meios Porosos), com uso intensivo de CFD e métodos numéricos avançados.")
    report.append("2. **FEN — Faculdade de Engenharia (Maracanã):** Destaque para o **GESAR** (Grupo de Simulação em Engenharia e Ciências Ambientais - CFD), **LAMMAC**, **LaCaM**, **LFT** e **LMES**, abrangendo MECAN, DEEL, DEPRO, DEQ e Civil.")
    report.append("3. **FAT — Faculdade de Tecnologia (Resende):** Foco em manufatura, materiais sintéticos, polímeros, compósitos, robótica, hidráulica e pneumática industrial.")
    report.append("4. **IME / PPG-COMPMAT (Maracanã):** Pós-graduação em Ciências Computacionais e Modelagem Matemática focada em Inteligência Artificial, Analytics e HPC.")
    report.append("5. **InovUerj / DEPINOVA:** Gestão da Propriedade Intelectual, transferência de tecnologia e projetos de P&D universidade-empresa.")
    report.append("")
    report.append("---")
    report.append("")
    report.append("## METODOLOGIA E RASTREABILIDADE")
    report.append("- **Regra Crítica de Contato:** Garantia de 100% de rastreabilidade. Nenhum e-mail foi inferido ou gerado por adivinhação. Todos os contatos listados provêm de portais oficiais da UERJ (`uerj.br`, `eng.uerj.br`, `iprj.uerj.br`, `fat.uerj.br`, `ime.uerj.br`, `pr2.uerj.br`) ou secretarias departamentais/PPG públicas.")
    report.append("- **Taxonomia de Especialização:** Classificação técnica direcionada às soluções do portfólio Siemens DISW (Simcenter STAR-CCM+, Femap/Simcenter 3D, Amesim, NX CAD/CAM, gPROMS, Tecnomatix, MindSphere/Opcenter).")
    report.append("")
    report.append("---")
    report.append("")

    for title, items in groups.items():
        if not items:
            continue
        report.append(f"## {title}")
        report.append("")
        report.append("| Nome Completo | E-mail Institucional | Setor / Depto / Campus | Laboratório / Grupo | Área de Especialização Técnica | Fonte de Validação | Status / Data |")
        report.append("|---|---|---|---|---|---|---|")
        for rec in items:
            row = f"| **{rec['nome']}** | `{rec['email']}` | {rec['setor_departamento_campus']} | {rec['laboratorio_grupo_pesquisa']} | {rec['area_especializacao']} | [{rec['url_fonte']}]({rec['url_fonte']}) | {rec['status_validacao_data']} |"
            report.append(row)
        report.append("")

    report_content = "\n".join(report)
    with open("mapeamento_uerj.md", "w", encoding="utf-8") as f:
        f.write(report_content)

    print("[INFO] Markdown report generated successfully: mapeamento_uerj.md")

if __name__ == "__main__":
    generate_report()
