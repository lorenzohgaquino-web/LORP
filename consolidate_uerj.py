import json
import re
from uerj_data_cleaner import clean_academic_title, sanitize_string

def map_siemens_disw_specialization(record):
    name = record["nome"]
    dept = record["setor_departamento_campus"]
    spec = record["especializacao_tecnica"]
    lab = record["laboratorio_grupo"]

    # Specific key professors / roles mapping
    name_lower = name.lower()

    if "norberto mangiavacchi" in name_lower or "gustavo rabello" in name_lower or "josé da rocha miranda pontes" in name_lower:
        return "CFD (STAR-CCM+), Escoamentos Multifásicos, Fenômenos de Transporte, Métodos Numéricos & HPC"
    if "daniel" in name_lower and "chalhub" in name_lower:
        return "CFD, Fabricação Digital (FabLab), Transformada Integral & Soluções Analítico-Numéricas"
    if "knupp" in name_lower:
        return "Simulação Térmica, Problemas Inversos, Transformada Integral & Métodos Numéricos"
    if "souto" in name_lower:
        return "CFD, Meios Porosos, Transporte de Partículas, HPC & Supercomputação (Escola de Sagres)"
    if "stutz" in name_lower:
        return "Simcenter (Vibrações & Acústica), Análise Estrutural, Controle Ativo & Dinâmica de Sistemas"
    if "vellasco" in name_lower:
        return "Simcenter / FEA (Análise de Estruturas Mistas, Elementos Finitos) & Inteligência Artificial Aplicada"
    if "soeiro" in name_lower:
        return "FEA (Elementos Finitos), Mecânica dos Sólidos, Otimização Estrutural & Algoritmos Genéticos"
    if "roux" in name_lower:
        return "Sistemas de Controle, Automação Industrial, Controle Extremante & Robótica"
    if "spiegel" in name_lower:
        return "Otimização de Processos, Pesquisa Operacional, BPMN & Engenharia de Serviços"
    if "erika de queiros" in name_lower or "eugenio" in name_lower:
        return "gPROMS / Simulação de Processos Químicos, Bioprocessos & Valoração Tecnológica"

    # Sector based taxonomy refinement
    if "MECAN" in dept or "DME" in dept or "Mecânica" in dept:
        return "CFD (STAR-CCM+), Termofluidodinâmica, Mecânica dos Sólidos & Simulação Multifísica (Simcenter)"
    elif "IPRJ" in dept or "PPGMC" in dept:
        return "Modelagem Computacional, CFD, Meios Porosos, HPC & Método dos Elementos Finitos (FEA)"
    elif "DEEL" in dept or "ELE" in dept or "DETEL" in dept:
        return "Sistemas de Controle, Eletrônica de Potência, Automação & Robótica Industrial"
    elif "DEPRO" in dept or "DENP" in dept:
        return "Otimização de Processos, Logística Industrial, Pesquisa Operacional & Simulação de Eventos Discretos"
    elif "DEQ" in dept or "DEQA" in dept:
        return "gPROMS / Simulação de Reatores e Processos Químicos, Termodinâmica & Fenômenos Interfaciais"
    elif "ESTR" in dept or "Civil" in dept:
        return "FEA (Análise de Estruturas), Métodos Numéricos em Geotecnia & Mecânica dos Sólidos"
    elif "CARTO" in dept:
        return "Geoprocessamento, Sensoriamento Remoto, Fotogrametria Digital & Análise Espacial"
    elif "COMPMAT" in dept or "IME" in dept or "DMFC" in dept:
        return "Computação Científica, HPC, Inteligência Artificial, Analytics & Métodos Numéricos Aplicados"
    elif "InovUerj" in dept or "DEPINOVA" in dept:
        return "Gestão de Propriedade Intelectual, Transferência de Tecnologia, Parcerias Universidade-Empresa & Incubação"

    return "Simulação e Modelagem Computacional Aplicada à Engenharia"

def main():
    with open("raw_uerj_scraped.json", "r", encoding="utf-8") as f:
        raw_records = json.load(f)

    consolidated = []
    seen = set()

    for r in raw_records:
        name = clean_academic_title(r["nome"])
        dept = sanitize_string(r["setor_departamento_campus"])

        # Deduplication key
        key = (name.lower(), dept.lower())
        if key in seen:
            continue
        seen.add(key)

        email = sanitize_string(r["email"])
        lab = sanitize_string(r["laboratorio_grupo"])
        url = sanitize_string(r["url_fonte"])
        val = sanitize_string(r["status_validacao"])
        dt = sanitize_string(r["data_acesso"])

        refined_spec = map_siemens_disw_specialization(r)

        consolidated.append({
            "nome": name,
            "email": email,
            "setor_departamento_campus": dept,
            "laboratorio_grupo": lab,
            "especializacao_tecnica": refined_spec,
            "url_fonte": url,
            "status_validacao": val,
            "data_acesso": dt
        })

    # Sort by campus / sector then name
    consolidated.sort(key=lambda x: (x["setor_departamento_campus"], x["nome"]))

    print(f"Total consolidated records: {len(consolidated)}")

    with open("uerj_dataset.json", "w", encoding="utf-8") as f:
        json.dump(consolidated, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
