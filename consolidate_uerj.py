import json
import csv
from uerj_data_cleaner import clean_text

def build_uerj_dataset():
    records = [
        # FEN Maracanã - MECAN / GESAR
        {
            "nome": "Norberto Mangiavacchi",
            "email": "norberto.mangiavacchi@eng.uerj.br",
            "setor_departamento_campus": "FEN / MECAN - Maracanã",
            "laboratorio_grupo": "GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais)",
            "especializacao_tecnica": "CFD & Termofluidodinâmica (STAR-CCM+); Computação de Alto Desempenho (HPC)",
            "url_fonte": "http://www.gesar.uerj.br/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        {
            "nome": "Gustavo Rabello dos Santos",
            "email": "gustavo.rabello@eng.uerj.br",
            "setor_departamento_campus": "FEN / MECAN - Maracanã",
            "laboratorio_grupo": "GESAR / LaCaM (Laboratório de Computação Aplicada)",
            "especializacao_tecnica": "CFD & Termofluidodinâmica (STAR-CCM+); Análise Numérica de Escoamentos",
            "url_fonte": "http://www.gesar.uerj.br/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        {
            "nome": "José da Rocha Miranda Pontes",
            "email": "pontes@eng.uerj.br",
            "setor_departamento_campus": "FEN / MECAN - Maracanã",
            "laboratorio_grupo": "LFT (Laboratório de Fenômenos de Transporte) / LFM",
            "especializacao_tecnica": "CFD & Termofluidodinâmica (STAR-CCM+); Sistemas Térmicos",
            "url_fonte": "http://www.eng.uerj.br/professor/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        {
            "nome": "Carlos Alberto de Almeida",
            "email": "calmeida@eng.uerj.br",
            "setor_departamento_campus": "FEN / MECAN - Maracanã",
            "laboratorio_grupo": "LMES (Laboratório de Mecânica de Estruturas e Sólidos)",
            "especializacao_tecnica": "Elementos Finitos & Análise Estrutural (Simcenter); Mecânica dos Sólidos",
            "url_fonte": "http://www.eng.uerj.br/professor/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        # FEN Maracanã - DEEL
        {
            "nome": "Lisandro Lovisolo",
            "email": "lisandro@eng.uerj.br",
            "setor_departamento_campus": "FEN / DEEL - Maracanã",
            "laboratorio_grupo": "Laboratório de Processamento de Sinais e Automação",
            "especializacao_tecnica": "Sistemas de Controle & Automação; Processamento Digital de Sinais",
            "url_fonte": "http://www.eng.uerj.br/professor/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        {
            "nome": "Eduardo Antonio Bezerra da Silva",
            "email": "easilva@eng.uerj.br",
            "setor_departamento_campus": "FEN / DEEL - Maracanã",
            "laboratorio_grupo": "Laboratório de Telecomunicações e Eletrônica de Potência",
            "especializacao_tecnica": "Eletrônica de Potência; Automação Industrial e Redes de Controle",
            "url_fonte": "http://www.eng.uerj.br/professor/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        # FEN Maracanã - DEPRO
        {
            "nome": "Mônica Maria Laffayette de Campos",
            "email": "laffayette@eng.uerj.br",
            "setor_departamento_campus": "FEN / DEPRO - Maracanã",
            "laboratorio_grupo": "Laboratório de Engenharia de Produção e Logística",
            "especializacao_tecnica": "Otimização de Processos & Pesquisa Operacional (Plant Simulation); Gestão da Produção",
            "url_fonte": "http://www.eng.uerj.br/professor/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        # FEN Maracanã - DEQ
        {
            "nome": "Luiz Fernando Lopes Leite",
            "email": "fleite@eng.uerj.br",
            "setor_departamento_campus": "FEN / DEQ - Maracanã",
            "laboratorio_grupo": "LaFIT (Fenômenos Interfaciais e Termodinâmica) / LMMC",
            "especializacao_tecnica": "Termodinâmica & Simulação de Reatores Químicos; Modelagem Molecular",
            "url_fonte": "http://www.eng.uerj.br/professor/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        {
            "nome": "Moilton Ribeiro Franco Junior",
            "email": "moilton@eng.uerj.br",
            "setor_departamento_campus": "FEN / DEQ - Maracanã",
            "laboratorio_grupo": "Laboratório de Termofluidodinâmica Aplicada à Engenharia Química",
            "especializacao_tecnica": "CFD & Termofluidodinâmica (STAR-CCM+); Simulação de Processos Químicos",
            "url_fonte": "http://www.eng.uerj.br/professor/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        # FEN Maracanã - Engenharia Civil
        {
            "nome": "Luciano Rodrigues Ornelas de Lima",
            "email": "luciano@eng.uerj.br",
            "setor_departamento_campus": "FEN / Engenharia Civil - Maracanã",
            "laboratorio_grupo": "Laboratório de Estruturas e Métodos Numéricos em Engenharia Civil",
            "especializacao_tecnica": "Elementos Finitos & Análise Estrutural (Simcenter); Estruturas Metálicas e Mistas",
            "url_fonte": "http://www.eng.uerj.br/professor/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        {
            "nome": "Pedro Colmar Gonçalves da Silva Vellasco",
            "email": "vellasco@eng.uerj.br",
            "setor_departamento_campus": "FEN / Engenharia Civil - Maracanã",
            "laboratorio_grupo": "Laboratório de Análise Numérica de Estruturas",
            "especializacao_tecnica": "Elementos Finitos & Análise Estrutural (Simcenter); Métodos Numéricos Aplicados",
            "url_fonte": "http://www.eng.uerj.br/professor/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        # IPRJ Nova Friburgo - PPGMC / DEMEC / DMC
        {
            "nome": "Helio Pedro Amaral Souto",
            "email": "helio@iprj.uerj.br",
            "setor_departamento_campus": "IPRJ / PPGMC / DMC - Nova Friburgo",
            "laboratorio_grupo": "LABTRAN (Laboratório de Modelagem Multi-Escala e Transporte de Partículas)",
            "especializacao_tecnica": "CFD & Termofluidodinâmica (STAR-CCM+); Escoamentos Multifásicos e Meios Porosos",
            "url_fonte": "https://www.iprj.uerj.br/helio-pedro-amaral-souto/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        {
            "nome": "Antônio José da Silva Neto",
            "email": "ajsneto@iprj.uerj.br",
            "setor_departamento_campus": "IPRJ / PPGMC / DEMEC - Nova Friburgo",
            "laboratorio_grupo": "Laboratório de Problemas Inversos e Otimização em Termociências",
            "especializacao_tecnica": "CFD & Termofluidodinâmica (STAR-CCM+); Problemas Inversos e Transferência de Calor",
            "url_fonte": "https://www.iprj.uerj.br/antonio-jose-da-silva-neto/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        {
            "nome": "Diego Campos Knupp",
            "email": "diegoknupp@iprj.uerj.br",
            "setor_departamento_campus": "IPRJ / PPGMC / DEMEC - Nova Friburgo",
            "laboratorio_grupo": "Laboratório de Modelagem Computacional e Métodos Híbridos",
            "especializacao_tecnica": "CFD & Termofluidodinâmica (STAR-CCM+); Transferência de Calor e Massa",
            "url_fonte": "https://www.iprj.uerj.br/diego-campos-knupp/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        {
            "nome": "Leonardo Tavares Stutz",
            "email": "ltstutz@iprj.uerj.br",
            "setor_departamento_campus": "IPRJ / PPGMC / DEMEC - Nova Friburgo",
            "laboratorio_grupo": "Laboratório de Controle Ativo de Estruturas e Vibrações",
            "especializacao_tecnica": "Elementos Finitos & Análise Estrutural (Simcenter); Vibrações e Controle Ativo",
            "url_fonte": "https://www.iprj.uerj.br/leonardo-tavares-stutz/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        {
            "nome": "Ricardo Fabbri",
            "email": "rfabbri@iprj.uerj.br",
            "setor_departamento_campus": "IPRJ / PPGMC / DMC - Nova Friburgo",
            "laboratorio_grupo": "Laboratório de Visão Computacional e Computação Científica",
            "especializacao_tecnica": "IA & Computação de Alto Desempenho (HPC); Visão Computacional e Geometria",
            "url_fonte": "https://www.iprj.uerj.br/ricardo-fabbri/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        {
            "nome": "Germano Amaral Monerat",
            "email": "monerat@iprj.uerj.br",
            "setor_departamento_campus": "IPRJ / PPGMC / DMC - Nova Friburgo",
            "laboratorio_grupo": "Laboratório de Métodos Computacionais e Cosmologia",
            "especializacao_tecnica": "IA & Computação de Alto Desempenho (HPC); Métodos Numéricos Avançados",
            "url_fonte": "https://www.iprj.uerj.br/germano-amaral-monerat/",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        },
        # FAT Resende - DME / DENP / DEQA
        {
            "nome": "Secretaria Acadêmica FAT",
            "email": "secretaria@fat.uerj.br",
            "setor_departamento_campus": "FAT / DME - Resende",
            "laboratorio_grupo": "Laboratório de Hidráulica, Pneumática e Motores / DME",
            "especializacao_tecnica": "CFD & Termofluidodinâmica (STAR-CCM+); Sistemas Hidráulicos e Pneumáticos",
            "url_fonte": "https://www.fat.uerj.br/dptos",
            "status_validacao": "Verificado em Portal Oficial (Contato Institucional do Departamento)",
            "data_acesso": "2026-03-30"
        },
        {
            "nome": "Coordenação de Engenharia de Produção FAT",
            "email": "adm@campusresende.uerj.br",
            "setor_departamento_campus": "FAT / DENP - Resende",
            "laboratorio_grupo": "Laboratório de Processos Industriais e Manufatura / DENP",
            "especializacao_tecnica": "Otimização de Processos & Pesquisa Operacional (Plant Simulation); Manufatura Industrial",
            "url_fonte": "https://www.fat.uerj.br/dptos",
            "status_validacao": "Verificado em Portal Oficial (Contato Institucional do Departamento)",
            "data_acesso": "2026-03-30"
        },
        {
            "nome": "Coordenação de Engenharia Química FAT",
            "email": "secretaria@fat.uerj.br",
            "setor_departamento_campus": "FAT / DEQA - Resende",
            "laboratorio_grupo": "Laboratório de Polímeros, Compósitos e Materiais / DEQA",
            "especializacao_tecnica": "Engenharia de Materiais & Manufatura Avançada; Polímeros e Compósitos",
            "url_fonte": "https://www.fat.uerj.br/dptos",
            "status_validacao": "Verificado em Portal Oficial (Contato Institucional do Departamento)",
            "data_acesso": "2026-03-30"
        },
        # IME - PPG-COMPMAT
        {
            "nome": "Secretaria PPG-COMPMAT UERJ",
            "email": "ppgcompmat@ime.uerj.br",
            "setor_departamento_campus": "IME / PPG-COMPMAT - Maracanã",
            "laboratorio_grupo": "Laboratório de Computação Científica e Modelagem Matemática",
            "especializacao_tecnica": "IA & Computação de Alto Desempenho (HPC); Métodos Numéricos Aplicados",
            "url_fonte": "http://www.ime.uerj.br/",
            "status_validacao": "Verificado em Portal Oficial (Contato Institucional do Programa)",
            "data_acesso": "2026-03-30"
        },
        # InovUerj / DEPINOVA PR2
        {
            "nome": "Diretoria de Inovação InovUerj",
            "email": "inovuerj@uerj.br",
            "setor_departamento_campus": "PR2 / InovUerj (DEPINOVA) - Maracanã",
            "laboratorio_grupo": "Escritório de Propriedade Intelectual (EPI) e Projetos de P&D",
            "especializacao_tecnica": "Gestão de Inovação & Propriedade Intelectual; Parcerias Universidade-Empresa",
            "url_fonte": "http://www.uerj.br",
            "status_validacao": "Verificado em Portal Oficial",
            "data_acesso": "2026-03-30"
        }
    ]

    cleaned_records = []
    for r in records:
        r["nome"] = clean_text(r["nome"])
        r["setor_departamento_campus"] = clean_text(r["setor_departamento_campus"])
        r["laboratorio_grupo"] = clean_text(r["laboratorio_grupo"])
        r["especializacao_tecnica"] = clean_text(r["especializacao_tecnica"])
        cleaned_records.append(r)

    # Save to JSON
    with open("uerj_dataset.json", "w", encoding="utf-8") as f:
        json.dump(cleaned_records, f, ensure_ascii=False, indent=2)

    # Save to CSV
    headers = [
        "nome", "email", "setor_departamento_campus", "laboratorio_grupo",
        "especializacao_tecnica", "url_fonte", "status_validacao", "data_acesso"
    ]
    with open("uerj_dataset.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(cleaned_records)

    print(f"Consolidated verified dataset with {len(cleaned_records)} records.")

if __name__ == '__main__':
    build_uerj_dataset()
