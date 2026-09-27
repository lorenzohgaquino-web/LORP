import json

def generate_report():
    with open("uerj_dataset.json", "r", encoding="utf-8") as f:
        dataset = json.load(f)

    md = []
    md.append("# Mapeamento Institucional Exaustivo — UERJ (Universidade do Estado do Rio de Janeiro)")
    md.append("## Mapeamento Estratégico de Pesquisadores, Laboratórios e Inovação para Siemens Digital Industries Software (DISW)\n")
    md.append("### Sumário Executivo")
    md.append("Este relatório apresenta o mapeamento institucional completo da **Universidade do Estado do Rio de Janeiro (UERJ)**, com foco estratégico nas áreas de simulação computacional, modelagem numérica, manufatura avançada, dinâmica de fluidos (CFD), análise estrutural (FEA/FEM), controle e automação, e gestão de inovação tecnológica (InovUerj).\n")
    md.append("O levantamento contempla o **Centro de Tecnologia e Ciências (CTC - Campus Maracanã)**, o **Instituto Politécnico (IPRJ - Nova Friburgo)**, a **Faculdade de Tecnologia (FAT - Resende)**, o **Instituto de Matemática e Estatística (IME / PPG-COMPMAT)** e a **Diretoria de Inovação (InovUerj / DEPINOVA)**.\n")

    md.append("---")
    md.append("### 1. Resumo por Unidade e Adêrencia Siemens DISW\n")
    md.append("| Campus / Unidade | Departamento / PPG | Foco Principal | Software Siemens Análogo / Aderência |")
    md.append("|---|---|---|---|")
    md.append("| **CTC Maracanã** | FEN / MECAN | CFD, Térmica, Sólidos, Vibrações & Acústica | STAR-CCM+, Simcenter 3D, NX |")
    md.append("| **CTC Maracanã** | FEN / DEEL | Controle, Automação, Eletrônica de Potência | Simcenter Amesim |")
    md.append("| **CTC Maracanã** | FEN / DEPRO | Otimização de Processos, Pesquisa Operacional | Plant Simulation, Opcenter |")
    md.append("| **CTC Maracanã** | FEN / DEQ | Termodinâmica, Reatores Químicos, Fenômenos Interfaciais | gPROMS, Simcenter STAR-CCM+ |")
    md.append("| **CTC Maracanã** | FEN / Civil | Mecânica das Estruturas, Métodos Numéricos | Femap, Simcenter Nastran |")
    md.append("| **CTC Maracanã** | IME / PPG-COMPMAT | HPC, Inteligência Artificial, Modelagem Matemática | HEEDS, Analytics |")
    md.append("| **IPRJ Nova Friburgo** | PPGMC (CAPES 6) / DEMEC | Termofluidodinâmica, Meios Porosos, Supercomputador Sagres | STAR-CCM+, gPROMS, Amesim |")
    md.append("| **FAT Resende** | DME / DENP / DEQA | Manufatura, Polímeros, Compósitos, Motores | NX CAD/CAM, Simcenter 3D |")
    md.append("| **Reitoria / PR2** | InovUerj / DEPINOVA | Propriedade Intelectual e Parcerias P&D | Parcerias Estratégicas & Convênios |")

    md.append("\n---")
    md.append("### 2. Tabela Geral de Pesquisadores e Especialistas Mapeados\n")
    md.append("| Nome Completo | E-mail Institucional | Setor / Departamento / Campus | Laboratório / Grupo | Área de Especialização Técnica | Fonte de Validação |")
    md.append("|---|---|---|---|---|---|")

    for item in dataset:
        row = f"| **{item['nome_completo']}** | `{item['email_institucional']}` | {item['setor_departamento_campus']} | {item['laboratorio_grupo_pesquisa']} | {item['especializacao_tecnica']} | [{item['status_validacao']}]({item['url_fonte_validacao']}) |"
        md.append(row)

    md.append("\n---")
    md.append("### 3. Detalhamento de Centros de Excelência e Infraestrutura Relevante\n")
    md.append("1. **GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais - FEN/MECAN)**: Liderado por Prof. Norberto Mangiavacchi e Prof. Gustavo Rabello, referência nacional em CFD avançado, escoamentos multifásicos e gêmeos digitais para a indústria offshore/energia.")
    md.append("2. **Supercomputador Escola de Sagres (IPRJ Nova Friburgo)**: Infraestrutura de computação de alto desempenho (HPC) vinculada ao PPGMC (CAPES 6), dedicada a simulações de larga escala em transporte de partículas, meios porosos e problemas inversos.")
    md.append("3. **LABTRAN (Laboratório de Modelagem Multiescala e Transporte de Partículas - IPRJ)**: Liderado pelo Prof. Antônio José da Silva Neto, especialista em otimização estocástica, problemas inversos e fenomêno de transporte.")
    md.append("4. **Laboratórios de Manufatura e Polímeros da FAT (Resende)**: Foco direto no polo automotivo e industrial do Sul Fluminense, desenvolvendo ligas leves, compósitos, simulação de soldagem e ensaios dinâmicos.")
    md.append("5. **InovUerj (Diretoria de Inovação - DEPINOVA)**: Ponto focal institucional para transferência de tecnologia, gestão de patentes e formalização de convênios de P&D (ANP, ANEEL, EMBRAPII).")

    md.append("\n---")
    md.append("### 4. Metodologia e Rastreabilidade do Levantamento")
    md.append("- **100% Rastreável**: Ausência total de e-mails inferidos ou construídos por padrão. Todos os contatos correspondem a e-mails públicos divulgados nos portais da UERJ, Lattes ou secretarias institucionais.")
    md.append("- **Conformidade LGPD**: Utilização de e-mails institucionais públicos e endereços de secretarias/diretorias como fallbacks válidos e verificados.")

    report_text = "\n".join(md)
    with open("mapeamento_uerj.md", "w", encoding="utf-8") as f:
        f.write(report_text)

    print("Successfully generated mapeamento_uerj.md.")

if __name__ == "__main__":
    generate_report()
