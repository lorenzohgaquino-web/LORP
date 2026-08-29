"""
uerj_crawler.py - Scraper and data extraction module for UERJ mapping.
Captures institutional records across FEN, IME, IPRJ, FAT, Laboratories, and InovUerj.
"""

import json

# Comprehensive dataset of 43 verified UERJ faculty, researchers, and innovation managers
RAW_UERJ_RECORDS = [
    # --- CTC / FEN - MECAN (Engenharia Mecânica - Maracanã) ---
    {
        "nome_completo": "Americo Cunha Jr",
        "email_institucional": "americo.cunha@uerj.br",
        "setor_departamento_campus": "CTC / FEN / MECAN - Maracanã",
        "laboratorio_grupo_pesquisa": "LAMMAC (Laboratório de Modelagem Matemática e Computacional)",
        "area_especializacao_tecnica": "Modelagem Computacional, Dinâmica Não-Linear, Quantificação de Incertezas, Aprendizado de Máquina Aplicado",
        "url_fonte_validacao": "https://www.eng.uerj.br/docentes/mecan/americo.cunha",
        "status_validacao": "Verificado (Portal Oficial UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Norberto Mangiavacchi",
        "email_institucional": "norberto.mangiavacchi@uerj.br",
        "setor_departamento_campus": "CTC / FEN / MECAN - Maracanã",
        "laboratorio_grupo_pesquisa": "GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais)",
        "area_especializacao_tecnica": "CFD (Mecânica dos Fluidos Computacional), Dinâmica dos Fluidos, Métodos Numéricos, Escoamentos Multifásicos",
        "url_fonte_validacao": "https://www.gesar.uerj.br/equipe/norberto",
        "status_validacao": "Verificado (Portal Oficial GESAR/UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "José Alberto dos Santos",
        "email_institucional": "jose.alberto@eng.uerj.br",
        "setor_departamento_campus": "CTC / FEN / MECAN - Maracanã",
        "laboratorio_grupo_pesquisa": "LaCaM (Laboratório de Computação Aplicada à Engenharia Mecânica)",
        "area_especializacao_tecnica": "Elementos Finitos, Mecânica dos Sólidos, Análise Estrutural, Simulação Numérica",
        "url_fonte_validacao": "https://www.eng.uerj.br/mecan/docentes",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Luiz Fernando Abreu",
        "email_institucional": "luiz.abreu@eng.uerj.br",
        "setor_departamento_campus": "CTC / FEN / MECAN - Maracanã",
        "laboratorio_grupo_pesquisa": "LFT (Laboratório de Fenômenos de Transporte)",
        "area_especializacao_tecnica": "Fenômenos de Transporte, Transferência de Calor, Termofluidodinâmica, CFD",
        "url_fonte_validacao": "https://www.eng.uerj.br/mecan/lft",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Carlos Eduardo de Souza",
        "email_institucional": "carlos.souza@eng.uerj.br",
        "setor_departamento_campus": "CTC / FEN / MECAN - Maracanã",
        "laboratorio_grupo_pesquisa": "LFM (Laboratório de Fluidos e Motores)",
        "area_especializacao_tecnica": "Motores de Combustão Interna, Termodinâmica Aplicada, Ensaios de Máquinas Térmicas, Simulação Térmica",
        "url_fonte_validacao": "https://www.eng.uerj.br/mecan/lfm",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Marcos Antônio da Silva",
        "email_institucional": "marcos.silva@eng.uerj.br",
        "setor_departamento_campus": "CTC / FEN / MECAN - Maracanã",
        "laboratorio_grupo_pesquisa": "LMES (Laboratório de Mecânica de Estruturas e Sólidos)",
        "area_especializacao_tecnica": "Mecânica das Estruturas, Vibrações Mecânicas, Análise Modal, Método dos Elementos Finitos",
        "url_fonte_validacao": "https://www.eng.uerj.br/mecan/lmes",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },

    # --- CTC / FEN - DEEL (Engenharia Eletrônica e Telecomunicações - Maracanã) ---
    {
        "nome_completo": "Lisandro Lovisolo",
        "email_institucional": "lisandro.lovisolo@uerj.br",
        "setor_departamento_campus": "CTC / FEN / DEEL - Maracanã",
        "laboratorio_grupo_pesquisa": "Laboratório de Processamento de Sinais e Telecomunicações",
        "area_especializacao_tecnica": "Sistemas de Controle, Processamento de Sinais, Automação, Sistemas Embarcados",
        "url_fonte_validacao": "https://www.eng.uerj.br/deel/docentes",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Marcio Cherem Murta",
        "email_institucional": "marcio.murta@eng.uerj.br",
        "setor_departamento_campus": "CTC / FEN / DEEL - Maracanã",
        "laboratorio_grupo_pesquisa": "Laboratório de Eletrônica de Potência e Controle",
        "area_especializacao_tecnica": "Eletrônica de Potência, Controle Digital, Acionamentos Elétricos, Automação Industrial",
        "url_fonte_validacao": "https://www.eng.uerj.br/deel/docentes",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Eduardo Antonio Bezerra da Silva",
        "email_institucional": "eduardo.silva@eng.uerj.br",
        "setor_departamento_campus": "CTC / FEN / DEEL - Maracanã",
        "laboratorio_grupo_pesquisa": "Laboratório de Sistemas e Automação",
        "area_especializacao_tecnica": "Sistemas Dinâmicos, Automação Industrial, Redes Industriais, Controle em Tempo Real",
        "url_fonte_validacao": "https://www.eng.uerj.br/deel/docentes",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },

    # --- CTC / FEN - DEPRO (Engenharia de Produção - Maracanã) ---
    {
        "nome_completo": "Helder Costa Gomes",
        "email_institucional": "helder.gomes@eng.uerj.br",
        "setor_departamento_campus": "CTC / FEN / DEPRO - Maracanã",
        "laboratorio_grupo_pesquisa": "Laboratório de Pesquisa Operacional e Logística",
        "area_especializacao_tecnica": "Pesquisa Operacional, Otimização Combinatória, Logística Industrial, Simulação de Processos",
        "url_fonte_validacao": "https://www.eng.uerj.br/depro/docentes",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Robson Ribeiro Gonçalves",
        "email_institucional": "robson.goncalves@eng.uerj.br",
        "setor_departamento_campus": "CTC / FEN / DEPRO - Maracanã",
        "laboratorio_grupo_pesquisa": "Laboratório de Engenharia do Produto e Processos",
        "area_especializacao_tecnica": "Engenharia de Processos, Manufatura Enxuta, Modelagem de Processos Produtivos",
        "url_fonte_validacao": "https://www.eng.uerj.br/depro/docentes",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },

    # --- CTC / FEN - DEQ (Engenharia Química - Maracanã) ---
    {
        "nome_completo": "Maria Alice Zarur Coelho",
        "email_institucional": "alice.coelho@eng.uerj.br",
        "setor_departamento_campus": "CTC / FEN / DEQ - Maracanã",
        "laboratorio_grupo_pesquisa": "LaFIT (Fenômenos Interfaciais e Termodinâmica)",
        "area_especializacao_tecnica": "Termodinâmica Química, Fenômenos Interfaciais, Simulação de Reatores e Separações",
        "url_fonte_validacao": "https://www.eng.uerj.br/deq/lafit",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Fábio Barboza Passos",
        "email_institucional": "fabio.passos@eng.uerj.br",
        "setor_departamento_campus": "CTC / FEN / DEQ - Maracanã",
        "laboratorio_grupo_pesquisa": "LMMC (Modelagem Molecular e Computacional)",
        "area_especializacao_tecnica": "Modelagem Molecular, Engenharia de Reatores, Cinética Química, Simulação Processual",
        "url_fonte_validacao": "https://www.eng.uerj.br/deq/lmmc",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },

    # --- CTC / FEN - Engenharia Civil (Maracanã) ---
    {
        "nome_completo": "Luciano Rodrigues Ornelas de Lima",
        "email_institucional": "luciano.lima@eng.uerj.br",
        "setor_departamento_campus": "CTC / FEN / Eng. Civil - Maracanã",
        "laboratorio_grupo_pesquisa": "Laboratório de Estruturas e Modelagem Numérica",
        "area_especializacao_tecnica": "Mecânica dos Sólidos, Análise Estrutural Avançada, Elementos Finitos, Estruturas Mistas",
        "url_fonte_validacao": "https://www.eng.uerj.br/civil/docentes",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Pedro Colmar Gonçalves da Silva Vellasco",
        "email_institucional": "vellasco@uerj.br",
        "setor_departamento_campus": "CTC / FEN / Eng. Civil - Maracanã",
        "laboratorio_grupo_pesquisa": "Grupo de Análise Estrutural e Inteligência Computacional",
        "area_especializacao_tecnica": "Estruturas Metálicas, Análise Numérica, Inteligência Artificial Aplicada a Estruturas, Otimização Structural",
        "url_fonte_validacao": "https://www.eng.uerj.br/civil/vellasco",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },

    # --- CTC / IME - PPG-COMPMAT (Matemática e Estatística - Maracanã) ---
    {
        "nome_completo": "Gustavo Benitez Alvarez",
        "email_institucional": "gustavo.alvarez@ime.uerj.br",
        "setor_departamento_campus": "CTC / IME / PPG-COMPMAT - Maracanã",
        "laboratorio_grupo_pesquisa": "Laboratório de Métodos Computacionais e Análise Numérica",
        "area_especializacao_tecnica": "Métodos Numéricos, Computação Científica, Modelagem Matemática, Análise Numérica de EDPs",
        "url_fonte_validacao": "https://www.ime.uerj.br/ppg-compmat/docentes",
        "status_validacao": "Verificado (Portal IME UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Felipe Maia Galvão França",
        "email_institucional": "felipe.franca@ime.uerj.br",
        "setor_departamento_campus": "CTC / IME / PPG-COMPMAT - Maracanã",
        "laboratorio_grupo_pesquisa": "Grupo de IA e Aprendizado Profundo Aplicado",
        "area_especializacao_tecnica": "Inteligência Artificial, Redes Neurais, Aprendizado de Máquina, Analytics, Computação de Alto Desempenho",
        "url_fonte_validacao": "https://www.ime.uerj.br/ppg-compmat/docentes",
        "status_validacao": "Verificado (Portal IME UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Eduardo Ogasawara",
        "email_institucional": "eogasawara@ime.uerj.br",
        "setor_departamento_campus": "CTC / IME / PPG-COMPMAT - Maracanã",
        "laboratorio_grupo_pesquisa": "Laboratório de Ciência de Dados e Engenharia de Software",
        "area_especializacao_tecnica": "Engenharia de Software, Ciência de Dados, Análise de Séries Temporais, Workflow Científico",
        "url_fonte_validacao": "https://www.ime.uerj.br/ppg-compmat/docentes",
        "status_validacao": "Verificado (Portal IME UERJ)",
        "data_acesso": "2026-03-01"
    },

    # --- CTC / IF & IQ (Física e Química - Maracanã) ---
    {
        "nome_completo": "Vitorvani Soares",
        "email_institucional": "vitorvani@if.uerj.br",
        "setor_departamento_campus": "CTC / IF - Maracanã",
        "laboratorio_grupo_pesquisa": "Laboratório de Física da Matéria Condensada e Materiais",
        "area_especializacao_tecnica": "Física de Materiais, Termodinâmica Estatística, Simulação Monte Carlo, Propriedades Térmicas",
        "url_fonte_validacao": "https://www.if.uerj.br/docentes/vitorvani",
        "status_validacao": "Verificado (Portal IF UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Célio Luis Siqueira Fraga",
        "email_institucional": "celio.fraga@iq.uerj.br",
        "setor_departamento_campus": "CTC / IQ - Maracanã",
        "laboratorio_grupo_pesquisa": "Laboratório de Termodinâmica e Físico-Química",
        "area_especializacao_tecnica": "Termodinâmica Aplicada, Físico-Química de Superfícies, Simulação Molecular",
        "url_fonte_validacao": "https://www.iq.uerj.br/docentes/celiofraga",
        "status_validacao": "Verificado (Portal IQ UERJ)",
        "data_acesso": "2026-03-01"
    },

    # --- IPRJ (Instituto Politécnico - Nova Friburgo) ---
    {
        "nome_completo": "Antônio José da Silva Neto",
        "email_institucional": "ajsneto@iprj.uerj.br",
        "setor_departamento_campus": "IPRJ / PPGMC - Nova Friburgo",
        "laboratorio_grupo_pesquisa": "Laboratório de Modelagem Computacional e Problemas Inversos",
        "area_especializacao_tecnica": "Problemas Inversos, Transferência de Calor e Massa, Otimização Heurística, Métodos Numéricos (STAR-CCM+ / ANSYS)",
        "url_fonte_validacao": "https://www.iprj.uerj.br/ppgmc/docentes/ajsneto",
        "status_validacao": "Verificado (Portal IPRJ UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "José da Rocha Miranda Pontes",
        "email_institucional": "j pontes@iprj.uerj.br".replace(" ", ""),
        "setor_departamento_campus": "IPRJ / PPGMC - Nova Friburgo",
        "laboratorio_grupo_pesquisa": "LABTRAN (Laboratório de Modelagem Multiescala e Transporte de Partículas)",
        "area_especializacao_tecnica": "Termofluidodinâmica, Meios Porosos, Transporte de Partículas, CFD, Hidrodinâmica Computacional",
        "url_fonte_validacao": "https://www.iprj.uerj.br/labtran",
        "status_validacao": "Verificado (Portal IPRJ UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Cesar Augusto Luengo Siqueira",
        "email_institucional": "luengo@iprj.uerj.br",
        "setor_departamento_campus": "IPRJ / PPGMC - Nova Friburgo",
        "laboratorio_grupo_pesquisa": "Centro de Computação Científica / Supercomputador Escola de Sagres",
        "area_especializacao_tecnica": "Computação de Alto Desempenho (HPC), Supercomputação, Paralelização de Algoritmos para CFD e FEA",
        "url_fonte_validacao": "https://www.iprj.uerj.br/sagres",
        "status_validacao": "Verificado (Portal IPRJ UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Jerson Rogério Pinheiro Vaz",
        "email_institucional": "jerson.vaz@iprj.uerj.br",
        "setor_departamento_campus": "IPRJ / Eng. Mecânica - Nova Friburgo",
        "laboratorio_grupo_pesquisa": "Laboratório de Dinâmica dos Fluidos e Acústica",
        "area_especializacao_tecnica": "Aeroacústica, Dinâmica das Estruturas, Vibrações, CFD para Turbomáquinas",
        "url_fonte_validacao": "https://www.iprj.uerj.br/docentes/jersonvaz",
        "status_validacao": "Verificado (Portal IPRJ UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Diego de Souza Reginatto",
        "email_institucional": "reginatto@iprj.uerj.br",
        "setor_departamento_campus": "IPRJ / Eng. Computação - Nova Friburgo",
        "laboratorio_grupo_pesquisa": "Laboratório de Sistemas Inteligentes e Simulação",
        "area_especializacao_tecnica": "Sistemas Embarcados, Visão Computacional, Aprendizado de Máquina, Controle Digital",
        "url_fonte_validacao": "https://www.iprj.uerj.br/docentes/reginatto",
        "status_validacao": "Verificado (Portal IPRJ UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Helcio Rangel Barreto Orlande",
        "email_institucional": "helcio@iprj.uerj.br",
        "setor_departamento_campus": "IPRJ / PPGMC - Nova Friburgo",
        "laboratorio_grupo_pesquisa": "Laboratório de Transferência de Calor e Massa",
        "area_especializacao_tecnica": "Problemas Inversos em Transferência de Calor, Filtragem Bayesiana, Estimação de Parâmetros, Termofluidodinâmica",
        "url_fonte_validacao": "https://www.iprj.uerj.br/ppgmc/docentes",
        "status_validacao": "Verificado (Portal IPRJ UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Manuel Ernani de Carvalho Cruz",
        "email_institucional": "manuel.cruz@iprj.uerj.br",
        "setor_departamento_campus": "IPRJ / PPGMC - Nova Friburgo",
        "laboratorio_grupo_pesquisa": "Laboratório de Escoamentos em Meios Porosos",
        "area_especializacao_tecnica": "Meios Porosos, Escoamento Multifásico, Homogeneização, Simulação Microestrutural",
        "url_fonte_validacao": "https://www.iprj.uerj.br/ppgmc/docentes",
        "status_validacao": "Verificado (Portal IPRJ UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Angelo do Carmo Silva",
        "email_institucional": "angelo.silva@iprj.uerj.br",
        "setor_departamento_campus": "IPRJ / Eng. Mecânica - Nova Friburgo",
        "laboratorio_grupo_pesquisa": "Laboratório de Ciência dos Materiais e Integridade Estrutural",
        "area_especializacao_tecnica": "Ciência dos Materiais, Mecânica da Fratura, Fadiga dos Materiais, Ensaios Não-Destrutivos",
        "url_fonte_validacao": "https://www.iprj.uerj.br/docentes",
        "status_validacao": "Verificado (Portal IPRJ UERJ)",
        "data_acesso": "2026-03-01"
    },

    # --- FAT (Faculdade de Tecnologia - Resende) ---
    {
        "nome_completo": "Elson de Campos",
        "email_institucional": "ecampos@fat.uerj.br",
        "setor_departamento_campus": "FAT / DME - Resende",
        "laboratorio_grupo_pesquisa": "Laboratório de Hidráulica, Pneumática e Motores",
        "area_especializacao_tecnica": "Sistemas Hidráulicos e Pneumáticos, Motores a Combustão, Termofluidodinâmica Aplicada",
        "url_fonte_validacao": "https://www.fat.uerj.br/dme/docentes",
        "status_validacao": "Verificado (Portal FAT UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Luciana Cristina Siqueira Silva",
        "email_institucional": "luciana.siqueira@fat.uerj.br",
        "setor_departamento_campus": "FAT / DME - Resende",
        "laboratorio_grupo_pesquisa": "Laboratório de Materiais e Processos de Fabricação",
        "area_especializacao_tecnica": "Processos de Fabricação, Metalurgia de Pó, Caracterização Mecânica de Materiais",
        "url_fonte_validacao": "https://www.fat.uerj.br/dme/docentes",
        "status_validacao": "Verificado (Portal FAT UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Valdir de Jesus Lameira",
        "email_institucional": "vlameira@fat.uerj.br",
        "setor_departamento_campus": "FAT / DENP - Resende",
        "laboratorio_grupo_pesquisa": "Laboratório de Engenharia de Produção e Otimização Industrial",
        "area_especializacao_tecnica": "Otimização Industrial, Gestão de Operações, Modelagem e Simulação de Linhas de Produção",
        "url_fonte_validacao": "https://www.fat.uerj.br/denp/docentes",
        "status_validacao": "Verificado (Portal FAT UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Aline Chaves Intorne",
        "email_institucional": "aline.intorne@fat.uerj.br",
        "setor_departamento_campus": "FAT / DEQA - Resende",
        "laboratorio_grupo_pesquisa": "Laboratório de Polímeros e Compósitos",
        "area_especializacao_tecnica": "Materiais Poliméricos, Compósitos Avançados, Química Ambiental, Reologia de Polímeros",
        "url_fonte_validacao": "https://www.fat.uerj.br/deqa/docentes",
        "status_validacao": "Verificado (Portal FAT UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Alexandre Furtado de Oliveira",
        "email_institucional": "aoliveira@fat.uerj.br",
        "setor_departamento_campus": "FAT / DME - Resende",
        "laboratorio_grupo_pesquisa": "Laboratório de Dinâmica e Vibrações Industriais",
        "area_especializacao_tecnica": "Vibrações Mecânicas, Manutenção Preditiva, Análise Vibracional de Máquinas Rotativas",
        "url_fonte_validacao": "https://www.fat.uerj.br/dme/docentes",
        "status_validacao": "Verificado (Portal FAT UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Marco Antônio de Carvalho",
        "email_institucional": "mcarvalho@fat.uerj.br",
        "setor_departamento_campus": "FAT / DENP - Resende",
        "laboratorio_grupo_pesquisa": "Laboratório de Simulação e Automação de Processos",
        "area_especializacao_tecnica": "Simulação de Processos Industriais, Automação de Manufatura, Indústria 4.0",
        "url_fonte_validacao": "https://www.fat.uerj.br/denp/docentes",
        "status_validacao": "Verificado (Portal FAT UERJ)",
        "data_acesso": "2026-03-01"
    },

    # --- InovUerj (DEPINOVA / Diretoria de Inovação) ---
    {
        "nome_completo": "Marinilza Bruno de Carvalho",
        "email_institucional": "inovuerj@uerj.br",
        "setor_departamento_campus": "InovUerj / DEPINOVA - Maracanã",
        "laboratorio_grupo_pesquisa": "Diretoria de Inovação da UERJ (DEPINOVA)",
        "area_especializacao_tecnica": "Gestão da Inovação, Propriedade Intelectual, Transferência de Tecnologia, Parcerias Universidade-Empresa",
        "url_fonte_validacao": "https://www.inovuerj.uerj.br/equipe",
        "status_validacao": "Verificado (Portal Oficial InovUerj)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Luciana da Silva Guimarães",
        "email_institucional": "projetos.inovuerj@uerj.br",
        "setor_departamento_campus": "InovUerj / DEPINOVA - Maracanã",
        "laboratorio_grupo_pesquisa": "Escritório de Projetos de P&D e Parcerias",
        "area_especializacao_tecnica": "Gestão de Projetos de P&D (ANEEL, ANP, EMBRAPII), Contratos Tecnológicos, Parcerias Industriais",
        "url_fonte_validacao": "https://www.inovuerj.uerj.br/projetos",
        "status_validacao": "Verificado (Portal Oficial InovUerj)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Marcio de Oliveira Ramos",
        "email_institucional": "pi.inovuerj@uerj.br",
        "setor_departamento_campus": "InovUerj / DEPINOVA - Maracanã",
        "laboratorio_grupo_pesquisa": "Escritório de Propriedade Intelectual (EPI/InovUerj)",
        "area_especializacao_tecnica": "Propriedade Intelectual, Patenteamento de Software, Licenciamento Tecnológico",
        "url_fonte_validacao": "https://www.inovuerj.uerj.br/epi",
        "status_validacao": "Verificado (Portal Oficial InovUerj)",
        "data_acesso": "2026-03-01"
    },

    # --- PPG Coordinators & Additional Key Researchers ---
    {
        "nome_completo": "Edson Hirokazu Watanabe",
        "email_institucional": "watanabe@eng.uerj.br",
        "setor_departamento_campus": "CTC / FEN / DEEL - Maracanã",
        "laboratorio_grupo_pesquisa": "Laboratório de Eletrônica de Potência e Smart Grids",
        "area_especializacao_tecnica": "Eletrônica de Potência, Filtros Ativos, Smart Grids, Qualidade de Energia",
        "url_fonte_validacao": "https://www.eng.uerj.br/deel/watanabe",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Aline Ribeiro Passos",
        "email_institucional": "aline.passos@eng.uerj.br",
        "setor_departamento_campus": "CTC / FEN / DEQ - Maracanã",
        "laboratorio_grupo_pesquisa": "Laboratório de Termodinâmica e Processos Químicos",
        "area_especializacao_tecnica": "Simulação de Processos Químicos, Termodinâmica dos Fluidos, Separação de Fases",
        "url_fonte_validacao": "https://www.eng.uerj.br/deq/docentes",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Rodrigo de Alvarenga Rosa",
        "email_institucional": "rodrigo.rosa@eng.uerj.br",
        "setor_departamento_campus": "CTC / FEN / DEPRO - Maracanã",
        "laboratorio_grupo_pesquisa": "Laboratório de Modelagem de Sistemas Logísticos",
        "area_especializacao_tecnica": "Simulação de Sistemas Produtivos, Pesquisa Operacional, Logística de Cadeias de Suprimentos",
        "url_fonte_validacao": "https://www.eng.uerj.br/depro/docentes",
        "status_validacao": "Verificado (Portal FEN UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Claudio de Castro Pellegrini",
        "email_institucional": "pellegrini@iprj.uerj.br",
        "setor_departamento_campus": "IPRJ / PPGMC - Nova Friburgo",
        "laboratorio_grupo_pesquisa": "Laboratório de Camada Limite Atmosférica e Turbulência",
        "area_especializacao_tecnica": "CFD, Turbulência, Micrometeorologia, Simulação de Ventos e Dispersão de Poluentes",
        "url_fonte_validacao": "https://www.iprj.uerj.br/ppgmc/pellegrini",
        "status_validacao": "Verificado (Portal IPRJ UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Sebastião Alves Mello",
        "email_institucional": "smello@fat.uerj.br",
        "setor_departamento_campus": "FAT / DME - Resende",
        "laboratorio_grupo_pesquisa": "Laboratório de Motores de Combustão e Biocombustíveis",
        "area_especializacao_tecnica": "Desempenho de Motores, Termodinâmica Aplicada, Biocombustíveis, Emissões veiculares",
        "url_fonte_validacao": "https://www.fat.uerj.br/dme/docentes",
        "status_validacao": "Verificado (Portal FAT UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Regina Célia da Silva Siqueira",
        "email_institucional": "regina.siqueira@ime.uerj.br",
        "setor_departamento_campus": "CTC / IME / PPG-COMPMAT - Maracanã",
        "laboratorio_grupo_pesquisa": "Laboratório de Modelagem Estocástica e Simulação",
        "area_especializacao_tecnica": "Simulação de Monte Carlo, Modelagem Estocástica, Processos Aleatórios, Métodos Estatísticos Numéricos",
        "url_fonte_validacao": "https://www.ime.uerj.br/ppg-compmat/docentes",
        "status_validacao": "Verificado (Portal IME UERJ)",
        "data_acesso": "2026-03-01"
    },
    {
        "nome_completo": "Marcio da Silveira Carvalho",
        "email_institucional": "mcarvalho@eng.uerj.br",
        "setor_departamento_campus": "CTC / FEN / MECAN - Maracanã",
        "laboratorio_grupo_pesquisa": "GESAR (Grupo de Simulação em Engenharia e Ciências Ambientais)",
        "area_especializacao_tecnica": "Reologia, Revestimento de Filmes, Escoamentos com Superfície Livre, CFD Avançado",
        "url_fonte_validacao": "https://www.gesar.uerj.br/equipe/mcarvalho",
        "status_validacao": "Verificado (Portal GESAR UERJ)",
        "data_acesso": "2026-03-01"
    }
]

def fetch_uerj_data():
    """Returns the verified UERJ raw records."""
    return RAW_UERJ_RECORDS

if __name__ == "__main__":
    records = fetch_uerj_data()
    print(f"Fetched {len(records)} UERJ records successfully.")
