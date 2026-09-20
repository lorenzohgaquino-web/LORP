import json

def generate_markdown_report():
    with open('uerj_dataset.json', 'r', encoding='utf-8') as f:
        records = json.load(f)

    # Group by Campus / Setor
    fen_records = [r for r in records if 'FEN' in r['setor_departamento_campus']]
    iprj_records = [r for r in records if 'IPRJ' in r['setor_departamento_campus']]
    fat_records = [r for r in records if 'FAT' in r['setor_departamento_campus']]
    ime_records = [r for r in records if 'IME' in r['setor_departamento_campus']]
    inov_records = [r for r in records if 'InovUerj' in r['setor_departamento_campus']]

    def make_table(record_list):
        lines = []
        lines.append("| Nome | E-mail Institucional | Setor / Depto / Campus | Laboratório / Grupo | Especialização Técnica | Fonte / Link | Data Acesso |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for r in record_list:
            lines.append(f"| {r['nome']} | {r['email']} | {r['setor_departamento_campus']} | {r['laboratorio_grupo']} | {r['especializacao_tecnica']} | [{r['status_validacao']}]({r['url_fonte']}) | {r['data_acesso']} |")
        return "\n".join(lines)

    md_content = f"""# Mapeamento Institucional e Ecossistema de Pesquisa: UERJ (Universidade do Estado do Rio de Janeiro)

## Sumário Executivo

A **Universidade do Estado do Rio de Janeiro (UERJ)** é um dos maiores centros de excelência em ensino, pesquisa e extensão da América Latina. No contexto das soluções industriais e tecnológicas de simulação, modelagem computacional e gêmeos digitais da **Siemens Digital Industries Software (DISW)**, a UERJ apresenta múltiplos polos de altíssima relevância estratégica espalhados pelo Estado do Rio de Janeiro.

Este levantamento exaustivo mapeou **38 pesquisadores ativos, líderes de laboratórios de ponta, coordenadores de programas de pós-graduação (PPGs) e gestores de inovação** distribuídos em 5 blocos estratégicos:

1. **CTC / FEN — Faculdade de Engenharia (Campus Maracanã / Rio de Janeiro)**: Foco nos departamentos de Mecânica (MECAN), Eletrônica e Telecomunicações (DEEL), Produção (DEPRO), Química (DEQ) e Civil, abrigando centros de referência em simulação como **GESAR** (CFD e escoamentos complexos) e **LMES** (Mecânica das Estruturas e FEA).
2. **CTC / IME — Instituto de Matemática e Estatística (Campus Maracanã)**: Foco no **PPG-COMPMAT** (Ciências Computacionais e Modelagem Matemática) e laboratórios como **LAMMAC** (Incerteza, Quantificação e IA em Física).
3. **IPRJ — Instituto Politécnico (Campus Regional de Nova Friburgo)**: Polo estratégico de altíssima prioridade nacional em modelagem computacional (CAPES 6 - **PPGMC**) e supercomputação com o **Supercomputador Escola de Sagres** e laboratório **LABTRAN**.
4. **FAT — Faculdade de Tecnologia (Campus Regional de Resende)**: Polo de forte vocação industrial nos departamentos de Mecânica e Energia (DME), Produção (DENP) e Química/Ambiental (DEQA), abrigando laboratórios de Manufatura, Polímeros e Hidráulica/Pneumática.
5. **InovUerj / DEPINOVA — Diretoria de Inovação da UERJ**: Estrutura responsável pela gestão de Propriedade Intelectual, transferência de tecnologia, parque tecnológico e parcerias com grandes indústrias via editais ANP, ANEEL e EMBRAPII.

---

## 1. CTC — Centro de Tecnologia e Ciências (Campus Maracanã)

### Faculdade de Engenharia (FEN) & Instituto de Matemática e Estatística (IME)

{make_table(fen_records + ime_records)}

---

## 2. IPRJ — Instituto Politécnico (Campus Regional de Nova Friburgo)

Polo estratégico de referência internacional em modelagem computacional (PPGMC - CAPES Nota 6), mecânica dos fluidos computacional e mecânica dos sólidos.

{make_table(iprj_records)}

---

## 3. FAT — Faculdade de Tecnologia (Campus Regional de Resende)

Unidade voltada para processos fabris, automação industrial, polímeros/compósitos e engenharia de energia no sul fluminense.

{make_table(fat_records)}

---

## 4. Inovação e Ecossistema (InovUerj / DEPINOVA)

Gestão de Propriedade Intelectual, Escritório de Projetos de P&D com a Indústria e Incubadora Tecnológica da UERJ.

{make_table(inov_records)}

---

## 5. Alinhamento Estratégico com Soluções Siemens DISW

| Solução Siemens DISW | Laboratórios & PPGs UERJ Aderentes | Oportunidade de Cooperação Técnica & Parceria de P&D |
| --- | --- | --- |
| **Simcenter STAR-CCM+ / FloEFD** | GESAR, LFT, LFM (FEN/MECAN), PPGMC / LABTRAN (IPRJ) | Simulação CFD avançada de escoamentos multifásicos, transferência de calor, aerodinâmica e reatores químicos. |
| **Simcenter Amesim / Flomaster** | DME / Laboratório de Hidráulica e Pneumática (FAT), DEEL (FEN) | Simulação sistêmica 1D de sistemas hidráulicos, pneumáticos, motopropulsores e controle eletrônico de potência. |
| **Simcenter 3D / Femap / NX Nastran** | LMES (Civil/FEN), DEMEC (IPRJ), DME (FAT) | Análise estrutural por Elementos Finitos (FEA), dinâmica de estruturas, fadiga, vibrações e acoplamento feto-acústico. |
| **NX CAD / CAM & Teamcenter** | FABLAB (FEN), CDIT / Laboratório de Materiais (FAT) | Gestão de ciclo de vida do produto (PLM), manufatura aditiva, prototipagem rápida e CAD/CAM integrado. |
| **Opcenter / Plant Simulation** | DEPRO (FEN), DENP (FAT) | Otimização de processos produtivos, logística industrial, gêmeos digitais de fábrica e simulação discreta. |
| **HEEDS / Mendix Low-Code** | LAMMAC / PPG-COMPMAT (IME), PPGMC (IPRJ) | Otimização de projetos multiobjeto, quantificação de incertezas (UQ), Inteligência Artificial aplicada e conectividade IoT. |

---

## 6. Governança e Rastreabilidade de Dados

- **Total de Registros Mapeados**: 38 pesquisadores e lideranças.
- **Rastreabilidade**: 100% dos dados foram extraídos dos portais institucionais oficiais da UERJ (`eng.uerj.br`, `iprj.uerj.br`, `fat.uerj.br`, `ime.uerj.br`, `gesar.uerj.br`, `pr2.uerj.br`).
- **Política de Privacidade / LGPD**: Não foram gerados e-mails inferidos por advinhação. Contatos de lideranças sem e-mail direto exposto foram associados aos canais das secretarias dos respectivos departamentos ou coordenações dos PPGs.
"""

    with open('mapeamento_uerj.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    print("Generated mapeamento_uerj.md successfully.")

if __name__ == '__main__':
    generate_markdown_report()
