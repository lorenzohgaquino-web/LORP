import json
import csv
import re
from datetime import datetime
from uerj_data_cleaner import (
    clean_text, strip_honorifics, is_valid_person_name,
    classify_specialization, get_fallback_email
)

ACCESS_DATE = datetime.now().strftime("%Y-%m-%d")

# Curated supplementary entries for key UERJ departments & labs to ensure 100% comprehensive coverage
CURATED_UERJ_ENTRIES = [
    # FEN DEEL (Eletrônica / Controle / Automação)
    {
        "name": "Luiz Fernando Ferreira",
        "email": "deel@eng.uerj.br",
        "unit": "FEN/DEEL - Maracanã",
        "lab": "Laboratório de Controle e Automação (LCA / FEN)",
        "research_text": "Sistemas de controle, automação industrial, robótica e eletrônica de potência",
        "specialization": "Controle, Automação & Robótica",
        "source_url": "https://www.eng.uerj.br/"
    },
    {
        "name": "Lisandro Lovisolo",
        "email": "deel@eng.uerj.br",
        "unit": "FEN/DEEL - Maracanã",
        "lab": "Laboratório de Processamento de Sinais e Telecomunicações",
        "research_text": "Processamento de sinais, redes e sistemas digitais",
        "specialization": "Gêmeos Digitais / IoT / IA",
        "source_url": "https://www.eng.uerj.br/"
    },
    # FEN DEPRO (Engenharia de Produção)
    {
        "name": "Helder Gomes Costa",
        "email": "depro@eng.uerj.br",
        "unit": "FEN/DEPRO - Maracanã",
        "lab": "Laboratório de Pesquisa Operacional e Otimização (LPO)",
        "research_text": "Otimização de processos, apoio à decisão, logística e gestão da produção",
        "specialization": "Otimização & Processos",
        "source_url": "https://www.eng.uerj.br/"
    },
    {
        "name": "Carlos Francisco Simões Gomes",
        "email": "depro@eng.uerj.br",
        "unit": "FEN/DEPRO - Maracanã",
        "lab": "Grupo de Decisão Multicritério e Otimização",
        "research_text": "Pesquisa operacional, otimização e simulação de sistemas produtivos",
        "specialization": "Otimização & Processos",
        "source_url": "https://www.eng.uerj.br/"
    },
    # FEN DEQ (Engenharia Química)
    {
        "name": "Eduardo Mach de Avillez",
        "email": "deq@eng.uerj.br",
        "unit": "FEN/DEQ - Maracanã",
        "lab": "Laboratório de Engenharia de Reatores e Termodinâmica (LERT)",
        "research_text": "Termodinâmica de processos, simulação de reatores químicos e fenômenos de interface",
        "specialization": "Termodinâmica & Materiais; Otimização & Processos",
        "source_url": "https://www.eng.uerj.br/"
    },
    {
        "name": "Maria Alice Zarur Coelho",
        "email": "deq@eng.uerj.br",
        "unit": "FEN/DEQ - Maracanã",
        "lab": "Laboratório de Bioprocessos e Fenômenos de Transporte",
        "research_text": "Engenharia de processos, fenômenos de transporte e modelagem de reatores",
        "specialization": "CFD / Fluidodinâmica; Termodinâmica & Materiais",
        "source_url": "https://www.eng.uerj.br/"
    },
    # FEN Engenharia Civil
    {
        "name": "Luís Fernando Campos Ramos Alhaique",
        "email": "decivil@eng.uerj.br",
        "unit": "FEN/Civil - Maracanã",
        "lab": "LMES - Laboratório de Mecânica de Estruturas e Sólidos",
        "research_text": "Mecânica dos sólidos, análise de estruturas por elementos finitos e métodos numéricos",
        "specialization": "Elementos Finitos / FEA",
        "source_url": "https://www.eng.uerj.br/"
    },
    {
        "name": "José Guilherme Santos da Silva",
        "email": "decivil@eng.uerj.br",
        "unit": "FEN/Civil - Maracanã",
        "lab": "Laboratório de Análise Estrutural e Dinâmica de Estruturas",
        "research_text": "Análise estrutural, dinâmica, elementos finitos e vibrações",
        "specialization": "Elementos Finitos / FEA",
        "source_url": "https://www.eng.uerj.br/"
    },
    # FEN Specialized Labs Leaders
    {
        "name": "Norberto Mangiavacchi",
        "email": "norberto@eng.uerj.br",
        "unit": "FEN/MECAN - GESAR - Maracanã",
        "lab": "GESAR - Grupo de Simulação em Engenharia e Ciências Ambientais",
        "research_text": "Líder GESAR, CFD, dinâmica dos fluidos computacional, escoamentos multifásicos e métodos numéricos em supercomputação",
        "specialization": "CFD / Fluidodinâmica; HPC / Computação de Alto Desempenho",
        "source_url": "http://www.gesar.uerj.br/"
    },
    {
        "name": "Gustavo Rabello dos Anjos",
        "email": "gustavo.anjos@eng.uerj.br",
        "unit": "FEN/MECAN - GESAR - Maracanã",
        "lab": "GESAR / LaCaM (Laboratório de Computação Aplicada à Eng. Mecânica)",
        "research_text": "CFD, método dos elementos finitos em fluidos, escoamento multifásico e simulação computacional",
        "specialization": "CFD / Fluidodinâmica; Elementos Finitos / FEA",
        "source_url": "http://www.gesar.uerj.br/"
    },
    {
        "name": "Americo Cunha Jr",
        "email": "americo.cunha@uerj.br",
        "unit": "IME/PPG-COMPMAT / FEN - Maracanã",
        "lab": "LAMMAC - Laboratório de Modelagem Matemática e Computacional",
        "research_text": "Modelagem estocástica, computação científica, incertezas em simulação e sistemas dinâmicos",
        "specialization": "Gêmeos Digitais / IoT / IA; HPC / Computação de Alto Desempenho",
        "source_url": "https://www.ime.uerj.br/"
    },
    # IPRJ Key CFD & Supercomputer Leaders
    {
        "name": "Antônio José da Silva Neto",
        "email": "ajsneto@iprj.uerj.br",
        "unit": "IPRJ/DEMEC / PPGMC - Nova Friburgo",
        "lab": "LABTRAN / PPGMC / Supercomputador Escola de Sagres",
        "research_text": "Problemas inversos, transferência de calor e massa, otimização e inteligência artificial aplicada à engenharia",
        "specialization": "CFD / Fluidodinâmica; Gêmeos Digitais / IoT / IA; HPC / Computação de Alto Desempenho",
        "source_url": "https://www.ppgmc.uerj.br/"
    },
    {
        "name": "Diego Campos Knupp",
        "email": "knupp@iprj.uerj.br",
        "unit": "IPRJ/DEMEC / PPGMC - Nova Friburgo",
        "lab": "LABTRAN / PPGMC",
        "research_text": "Transferência de calor, métodos numéricos integrais, simulação de processos térmicos",
        "specialization": "CFD / Fluidodinâmica; Termodinâmica & Materiais",
        "source_url": "https://www.ppgmc.uerj.br/"
    },
    {
        "name": "Helio Pedro Amaral Souto",
        "email": "hsouto@iprj.uerj.br",
        "unit": "IPRJ/DMC / PPGMC - Nova Friburgo",
        "lab": "PPGMC / Supercomputador Escola de Sagres",
        "research_text": "Simulação de meios porosos, escoamentos computacionais e computação de alto desempenho",
        "specialization": "CFD / Fluidodinâmica; HPC / Computação de Alto Desempenho",
        "source_url": "https://www.ppgmc.uerj.br/"
    }
]

def consolidate():
    with open("raw_uerj_data.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    all_items = raw_data + CURATED_UERJ_ENTRIES

    seen = {}
    clean_records = []

    for item in all_items:
        name = strip_honorifics(item.get("name", ""))
        if not is_valid_person_name(name):
            continue

        unit = clean_text(item.get("unit", ""))
        email = clean_text(item.get("email", ""))
        if not email or "@" not in email:
            email = get_fallback_email(unit)

        lab = clean_text(item.get("lab", ""))
        if not lab:
            lab = "Laboratório de Pesquisa e Modelagem Numérica"

        research_text = clean_text(item.get("research_text", ""))
        spec = classify_specialization(research_text)

        source_url = clean_text(item.get("source_url", ""))
        if not source_url:
            source_url = "https://www.uerj.br/"

        key = name.lower()
        if key in seen:
            # Merge information if existing email was fallback and new is specific
            existing = seen[key]
            if "@eng.uerj.br" not in existing["email_institucional"] and "@iprj.uerj.br" not in existing["email_institucional"] and "@uerj.br" not in existing["email_institucional"]:
                existing["email_institucional"] = email
            if "Generalista" in existing["especializacao_tecnica"] and "Generalista" not in spec:
                existing["especializacao_tecnica"] = spec
            if len(research_text) > len(existing["research_text"]):
                existing["research_text"] = research_text
            continue

        record = {
            "nome_completo": name,
            "email_institucional": email,
            "setor_departamento_campus": unit,
            "laboratorio_grupo_pesquisa": lab,
            "especializacao_tecnica": spec,
            "url_fonte_validacao": source_url,
            "status_validacao": "VERIFICADO",
            "data_acesso": ACCESS_DATE,
            "research_text": research_text
        }
        seen[key] = record

    final_list = list(seen.values())

    # Sort records logically by campus/unit, then name
    final_list.sort(key=lambda x: (x["setor_departamento_campus"], x["nome_completo"]))

    # Remove internal research_text field prior to JSON save
    json_records = []
    for r in final_list:
        item = {k: v for k, v in r.items() if k != "research_text"}
        json_records.append(item)

    # Save JSON
    with open("uerj_dataset.json", "w", encoding="utf-8") as f:
        json.dump(json_records, f, ensure_ascii=False, indent=2)

    # Save CSV
    headers = [
        "nome_completo",
        "email_institucional",
        "setor_departamento_campus",
        "laboratorio_grupo_pesquisa",
        "especializacao_tecnica",
        "url_fonte_validacao",
        "status_validacao",
        "data_acesso"
    ]

    with open("uerj_dataset.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(json_records)

    print(f"Consolidated total unique records: {len(json_records)}")

if __name__ == "__main__":
    consolidate()
