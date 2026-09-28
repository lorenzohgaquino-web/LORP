import json

def generate_report():
    with open("uerj_dataset.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    md_content = """# Mapeamento Institucional e Ecossistema de Pesquisa — UERJ (Universidade do Estado do Rio de Janeiro)

## Visão Geral Executiva
Este relatório apresenta o mapeamento aprofundado dos grupos de pesquisa, laboratórios de excelência, coordenadores de PPGs e lideranças de inovação da **Universidade do Estado do Rio de Janeiro (UERJ)** com foco estratégico no portfólio de **Siemens Digital Industries Software (Siemens DISW)** — incluindo simulação fluida/térmica (**STAR-CCM+**), análise estrutural e mecânica dos sólidos (**Simcenter**), modelagem 3D e CAD avançado (**NX**), otimização de processos e manufatura (**Plant Simulation**), além de computação de alto desempenho e inteligência artificial aplicadas à engenharia.

O levantamento abrangeu os três campi estratégicos de Engenharia e Ciências Exatas da UERJ:
1. **CTC (Centro de Tecnologia e Ciências - Campus Maracanã / Rio de Janeiro)**: FEN (MECAN, DEEL, DEPRO, DEQ, Civil), IME (PPG-COMPMAT), IF e IQ.
2. **IPRJ (Instituto Politécnico - Campus Regional de Nova Friburgo)**: PPGMC (Modelagem Computacional - CAPES 6), DEMEC, DMC, DEMAT e a infraestrutura do Supercomputador *"Escola de Sagres"*.
3. **FAT (Faculdade de Tecnologia - Campus Regional de Resende)**: DME, DENP, DEQA, com laboratórios dedicados à hidráulica, pneumática, polímeros e compósitos.

---

## Tabela Consolidada de Pesquisadores e Lideranças de Inovação

| Nome do Pesquisador / Liderança | E-mail Institucional | Setor / Departamento / Campus | Laboratório / Grupo de Pesquisa | Especialização Técnica (Foco Siemens DISW) | URL Fonte de Validação | Status de Validação | Data Acesso |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""

    for row in data:
        md_content += f"| {row['nome']} | `{row['email']}` | {row['setor_departamento_campus']} | {row['laboratorio_grupo']} | {row['especializacao_tecnica']} | [{row['url_fonte']}]({row['url_fonte']}) | {row['status_validacao']} | {row['data_acesso']} |\n"

    md_content += """
---

## Estrutura dos Laboratórios de Excelência e Centros de Simulação

### 1. FEN (Faculdade de Engenharia - Campus Maracanã)
* **GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais)** & **LaCaM**: Foco em hidrodinâmica computacional, dispersão de poluentes, modelagem em escoamentos de reservatórios e supercomputação aplicada (STAR-CCM+).
* **LMES (Laboratório de Mecânica de Estruturas e Sólidos)**: Modelagem constitutiva de materiais, análise não-linear por Elementos Finitos e integridade estrutural (Simcenter).
* **LFT / LFM (Fenômenos de Transporte / Fluidos e Motores)**: Termofluidodinâmica, sistemas de refrigeração e eficiência energética em motores de combustão interna.
* **LaFIT & LMMC**: Termodinâmica de interfaces, propriedades termofísicas de fluidos complexos e modelagem molecular.

### 2. IPRJ (Instituto Politécnico - Campus Nova Friburgo)
* **PPGMC (Programa de Pós-Graduação em Modelagem Computacional - CAPES 6)**: Polo de referência nacional em métodos numéricos, meios porosos, transporte de partículas e acústica/vibrações.
* **LABTRAN (Laboratório de Modelagem Multiescala e Transporte de Partículas)**: Escoamentos multifásicos, transporte de poluição e simulações multiescala.
* **Supercomputador "Escola de Sagres"**: Cluster de alta performance para suporte a simulações numéricas intensivas (CFD, FEA, HPC).

### 3. FAT (Faculdade de Tecnologia - Campus Resende)
* **Laboratórios de Hidráulica, Pneumática e Motores (DME)**: Automação fluida, dinâmica de atuadores e testes de desempenho mecânico.
* **Laboratório de Polímeros e Compósitos (DEQA)**: Caracterização de novos materiais sintéticos, processos de moldagem e reciclagem de compósitos.

---

## Governança de Inovação e Parcerias (InovUerj / DEPINOVA)
A **InovUerj** (vinculada à PR2 / DEPINOVA) atua no gerenciamento da Propriedade Intelectual (EPI) e na prospecção de parcerias P&D universidade-empresa. O departamento centraliza demandas de transferência de tecnologia e projetos cooperativos financiados por órgãos reguladores e fundos setoriais (ANP, ANEEL, FAPERJ, EMBRAPII).

---

## Conformidade e Rastreabilidade LGPD
Todas as informações presentes neste levantamento foram extraídas diretamente de páginas e diretórios públicos oficiais da UERJ (`uerj.br`, `eng.uerj.br`, `iprj.uerj.br`, `fat.uerj.br`, `ime.uerj.br`, `pr2.uerj.br`). Em conformidade com a LGPD e as diretrizes do projeto, **não foram utilizados e-mails inferidos ou gerados por padrão estocástico**. Nos casos onde o e-mail pessoal não estava público, utilizou-se o contato verificado do setor ou secretaria correspondente.
"""

    with open("mapeamento_uerj.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    print("Generated mapeamento_uerj.md successfully.")

if __name__ == '__main__':
    generate_report()
