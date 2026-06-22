import json

def format_table(events):
    headers = ["Nome do Evento", "Tipo", "Data / Período", "Local", "Vertical / Tema principal", "Soluções DSW", "Público-alvo", "Organização", "Site / URL", "Relevância", "Justificativa", "Oportunidade"]

    rows = []
    # Header
    rows.append("| " + " | ".join(headers) + " |")
    rows.append("|" + "|".join(["---"] * len(headers)) + "|")

    for e in events:
        row = [
            e.get("Nome do Evento", ""),
            e.get("Tipo", ""),
            e.get("Data / Período", ""),
            e.get("Local", ""),
            e.get("Vertical / Tema principal", ""),
            e.get("Soluções DSW com aderência", ""),
            e.get("Público-alvo", ""),
            e.get("Organização responsável", ""),
            e.get("Site / URL", ""),
            e.get("Nível de relevância", ""),
            e.get("Justificativa Relevância", ""),
            e.get("Oportunidade de atuação", "")
        ]
        rows.append("| " + " | ".join(row) + " |")

    return "\n".join(rows)

def main():
    with open('events_data.json', 'r', encoding='utf-8') as f:
        events = json.load(f)

    # Top 10 Selection logic
    top_10_names = [
        "Hannover Messe 2026",
        "11º Congresso de Inovação da Indústria",
        "FEIMEC 2026",
        "Realize LIVE Americas 2026",
        "Hospitalar 2026",
        "LAAD Defence & Security 2026",
        "ROG.e (Rio Oil & Gas) 2026",
        "Embedded World 2026",
        "The smarter E South America 2026",
        "Future Digital Twin & AI USA 2026"
    ]

    top_10 = [e for e in events if e["Nome do Evento"] in top_10_names]

    report = f"""# Relatório de Mapeamento de Eventos - Siemens Digital Industries Software (DISW)

## 1. Resumo Executivo: Top 10 Eventos Estratégicos
Este levantamento identificou os 10 eventos com maior potencial de retorno e aderência técnica ao portfólio Siemens Xcelerator, priorizando liderança em Indústria 4.0, transformação digital e verticais estratégicas.

| Evento | Motivação Estratégica |
|---|---|
| **Hannover Messe 2026** | Principal palco global de transformação industrial e vitrine para o ecossistema Siemens Xcelerator. |
| **11º Congresso de Inovação** | Liderança em inovação industrial no Brasil, com foco em deep techs e novas políticas industriais. |
| **FEIMEC 2026** | Evento central para prospecção no setor de máquinas e manufatura avançada na América Latina. |
| **Realize LIVE Americas 2026** | Principal fórum de usuários e parceiros Siemens, focado na comunidade técnica e decisores de engenharia. |
| **Hospitalar 2026** | Essencial para a vertical MedTech, focando em design de dispositivos médicos e conformidade (Polarion/NX). |
| **LAAD Defence & Security 2026** | Foco na vertical Aeroespacial & Defesa, setor de alta complexidade técnica e longos ciclos de vida (PLM). |
| **ROG.e (Rio Oil & Gas) 2026** | Central para o setor de energia, com fortes oportunidades em Gêmeo Digital e IoT Industrial para offshore. |
| **Embedded World 2026** | Evento técnico de referência para sistemas embarcados, crucial para o crescimento de Polarion (ALM) e EDA. |
| **The smarter E South America** | Hub de transição energética e e-Mobility, verticais de rápido crescimento no mercado brasileiro. |
| **Future Digital Twin & AI USA** | Nicho de alta tecnologia em Houston, focado na aplicação prática de simulação multifísica e IA industrial. |

---

## 2. Tabela Consolidada de Eventos (2025-2026)
Total de {len(events)} eventos mapeados e validados.

{format_table(events)}

---

## 3. Análise de Lacunas (Gaps) e Oportunidades
Abaixo, identificamos 4 áreas onde a cobertura de eventos atual pode ser expandida para fortalecer a presença da Siemens DISW:

1. **Baixa densidade de Low-code Industrial no Brasil:** Embora existam eventos de tecnologia genérica (Web Summit) e startups (South Summit), há uma carência de um fórum brasileiro focado exclusivamente em *Industrial Low-code* para acelerar apps de fábrica via Mendix.
2. **Semicondutores e EDA na América Latina:** Com o programa "Nova Indústria Brasil" estimulando o setor de semicondutores, existe uma lacuna de eventos técnicos de alto nível focados em design eletrônico (EDA) e verificação de IC no Brasil.
3. **Workshops Especializados em Simulação Multifísica:** A maioria do conteúdo de simulação está diluída em grandes feiras. Workshops regionais ultra-focados em CFD/Simulação Estrutural para as indústrias automotiva e de energia poderiam destacar o Simcenter frente à concorrência.
4. **Digitalização Profunda na Construção Industrializada (AEC):** O setor de construção offsite está crescendo, mas a integração técnica de PLM e manufatura (industrialização da construção) ainda é pouco explorada em eventos de AEC no Brasil.

---

*Relatório gerado em 2025 para planejamento estratégico de 2026.*
"""

    with open('relatorio_eventos_siemens.md', 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == "__main__":
    main()
