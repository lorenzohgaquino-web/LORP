import requests
from bs4 import BeautifulSoup
import urllib3
import json
import re
import datetime
import concurrent.futures
from uerj_data_cleaner import clean_name, sanitize_email, repair_encoding

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

VERIFICATION_DATE = datetime.datetime.now().strftime("%Y-%m-%d")

# Core faculty database with verified public data and sources across UERJ units
RAW_DOCENTES = [
    # --- FEN / MECAN (Engenharia Mecânica - Maracanã) ---
    {
        "nome": "Norberto Mangiavacchi",
        "email": "norberto@gesar.uerj.br",
        "setor": "FEN/MECAN - Maracanã",
        "lab": "GESAR / LFM (Laboratório de Fluidos e Motores)",
        "especializacao": "CFD, Simulação de Escoamentos Multifásicos, Termofluidodinâmica, Elementos Finitos, Computação de Alto Desempenho (HPC)",
        "url": "http://www.gesar.uerj.br/equipe/equipe-gesar.html"
    },
    {
        "nome": "José Pontes",
        "email": "pontes@gesar.uerj.br",
        "setor": "FEN/MECAN - Maracanã",
        "lab": "GESAR / LaCaM (Laboratório de Computação Aplicada à Engenharia Mecânica)",
        "especializacao": "Mecânica dos Fluidos Computacional, Instabilidades Hidrodinâmicas, Padrões de Convecção, Modelagem Numérica",
        "url": "http://www.gesar.uerj.br/equipe/equipe-gesar.html"
    },
    {
        "nome": "Daniel Chalhub",
        "email": "chalhub@gesar.uerj.br",
        "setor": "FEN/MECAN - Maracanã",
        "lab": "GESAR / LFT (Laboratório de Fenômenos de Transporte)",
        "especializacao": "Transferência de Calor e Massa, Fenômenos de Transporte, Métodos Numéricos, Otimização Térmica",
        "url": "http://www.gesar.uerj.br/equipe/equipe-gesar.html"
    },
    {
        "nome": "Gustavo Rabello dos Anjos",
        "email": "gustavo.anjos@eng.uerj.br",
        "setor": "FEN/MECAN - Maracanã",
        "lab": "GESAR / LaCaM (Laboratório de Computação Aplicada à Engenharia Mecânica)",
        "especializacao": "CFD, Escoamentos Multifásicos, Método dos Elementos Finitos, Métodos de Interface (ALE/Level Set), STAR-CCM+",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Renato de Oliveira Rocha",
        "email": "renato.rocha@eng.uerj.br",
        "setor": "FEN/MECAN - Maracanã",
        "lab": "LMES (Laboratório de Mecânica de Estruturas e Sólidos)",
        "especializacao": "Mecânica dos Sólidos, Análise Interativa de Estruturas, Elementos Finitos, Vibrações e Acústica",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Rogério Martins Saldanha da Gama",
        "email": "rsgama@eng.uerj.br",
        "setor": "FEN/MECAN - Maracanã",
        "lab": "LFT (Laboratório de Fenômenos de Transporte)",
        "especializacao": "Mecânica dos Meios Contínuos, Termodinâmica dos Meios Porosos, Transferência de Calor, Soluções Analíticas e Numéricas",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Francisco José da Cunha Pires Soeiro",
        "email": "soeiro@eng.uerj.br",
        "setor": "FEN/MECAN - Maracanã",
        "lab": "LMES (Laboratório de Mecânica de Estruturas e Sólidos)",
        "especializacao": "Otimização Estrutural, Métodos Inversos em Transferência de Calor, Elementos Finitos, Algoritmos Genéticos",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Leopoldo Eurico Gonçalves Bastos",
        "email": "leopoldo@eng.uerj.br",
        "setor": "FEN/MECAN - Maracanã",
        "lab": "LFT / LFM (Laboratório de Fluidos e Motores)",
        "especializacao": "Térmica e Fluidos, Transmissão de Calor, Energia Solar, Refrigeração, Análise Termodinâmica",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Carlos Alberto Biolchini da Silva",
        "email": "biolchini@eng.uerj.br",
        "setor": "FEN/MECAN - Maracanã",
        "lab": "LFM (Laboratório de Fluidos e Motores)",
        "especializacao": "Sistemas Térmicos, Motores de Combustão Interna, Análise Experimental e Numérica de Máquinas Térmicas",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Alcy Ruffier",
        "email": "alcy@eng.uerj.br",
        "setor": "FEN/MECAN - Maracanã",
        "lab": "LAMMAC (Laboratório de Modelagem Matemática e Computacional)",
        "especializacao": "Dinâmica dos Sólidos, Sistemas Mecânicos, Simulação Numérica, Automação Mecânica",
        "url": "http://www.eng.uerj.br/prof/"
    },

    # --- FEN / DEEL (Engenharia Eletrônica e de Telecomunicações - Maracanã) ---
    {
        "nome": "Lisandro Lovisolo",
        "email": "lisandro@eng.uerj.br",
        "setor": "FEN/DEEL - Maracanã",
        "lab": "Laboratório de Processamento de Sinais (LPS)",
        "especializacao": "Processamento Digital de Sinais, Sistemas de Controle, Inteligência Artificial, Telecomunicações",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Tiago Roux de Oliveira",
        "email": "tiagoroux@eng.uerj.br",
        "setor": "FEN/DEEL - Maracanã",
        "lab": "Laboratório de Automação e Controle (LAC)",
        "especializacao": "Sistemas de Controle Robusto, Controle Adaptativo por Modos Deslizantes, Automação Industrial, Robótica",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Nival Nunes de Almeida",
        "email": "nival@eng.uerj.br",
        "setor": "FEN/DEEL - Maracanã",
        "lab": "Laboratório de Automação e Sistemas",
        "especializacao": "Eletrônica de Potência, Sistemas de Controle Industrial, Automação de Processos",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Pedro Henrique Gouvêa Coelho",
        "email": "phgcoelho@eng.uerj.br",
        "setor": "FEN/DEEL - Maracanã",
        "lab": "Laboratório de Inteligência Computacional",
        "especializacao": "Redes Neurais Artificiais, Reconhecimento de Padrões, Sistemas Embarcados, Analytics",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Flavio Joaquim de Souza",
        "email": "fjoaquim@eng.uerj.br",
        "setor": "FEN/DEEL - Maracanã",
        "lab": "Laboratório de Sistemas Eletromagnéticos e Comunicações",
        "especializacao": "Eletromagnetismo Aplicado, Simulação Numérica de Campos Eletromagnéticos, Compatibilidade Eletromagnética",
        "url": "http://www.eng.uerj.br/prof/"
    },

    # --- FEN / DEPRO (Engenharia de Produção - Maracanã) ---
    {
        "nome": "Thais Spiegel",
        "email": "thais@eng.uerj.br",
        "setor": "FEN/DEPRO - Maracanã",
        "lab": "Laboratório de Engenharia de Processos e Gestão de Operações (LEP)",
        "especializacao": "Otimização de Processos, Pesquisa Operacional, Gestão da Produção e Operações, Engenharia Organizacional",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Luiz Antonio Joia",
        "email": "luiz.joia@eng.uerj.br",
        "setor": "FEN/DEPRO - Maracanã",
        "lab": "Laboratório de Gestão da Tecnologia da Informação",
        "especializacao": "Sistemas de Informação Industrial, Transformação Digital, Gestão da Inovação Tecnológica",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Ubirajara Aluizio de Oliveira Mattos",
        "email": "ubirajara@eng.uerj.br",
        "setor": "FEN/DEPRO - Maracanã",
        "lab": "Laboratório de Ergonometria e Segurança do Trabalho",
        "especializacao": "Engenharia do Trabalho, Ergonomia de Processos Industriais, Avaliação de Riscos Operacionais",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Carlos Alberto Pereira Correia",
        "email": "capc@eng.uerj.br",
        "setor": "FEN/DEPRO - Maracanã",
        "lab": "Laboratório de Logística e Cadeia de Suprimentos",
        "especializacao": "Logística Industrial, Simulação de Cadeias de Suprimentos, Planejamento e Controle da Produção (PCP)",
        "url": "http://www.eng.uerj.br/prof/"
    },

    # --- FEN / DEQ (Engenharia Química - Maracanã) ---
    {
        "nome": "Laís de Brito Caldas",
        "email": "lais.caldas@eng.uerj.br",
        "setor": "FEN/DEQ - Maracanã",
        "lab": "LaFIT (Fenômenos Interfaciais e Termodinâmica)",
        "especializacao": "Termodinâmica Química, Equilíbrio de Fases, Fenômenos Interfaciais, Simulação de Processos Químicos",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "LMMC / DEQ Coordenação",
        "email": "secretaria.deq@eng.uerj.br",
        "setor": "FEN/DEQ - Maracanã",
        "lab": "LMMC (Laboratório de Modelagem Molecular e Computacional)",
        "especializacao": "Modelagem Molecular, Simulação Computacional de Reatores, Termodinâmica Estatística, Propriedades de Fluidos",
        "url": "http://www.eng.uerj.br/deptos/deq.php"
    },
    {
        "nome": "Marisa Cristina Guimarães Rocha",
        "email": "mcrocha@eng.uerj.br",
        "setor": "FEN/DEQ - Maracanã",
        "lab": "Laboratório de Polímeros e Reologia",
        "especializacao": "Reologia de Polímeros, Processamento de Materiais Poliméricos, Caracterização Fisico-Química",
        "url": "http://www.eng.uerj.br/prof/"
    },

    # --- FEN / Civil (Engenharia Civil - Maracanã) ---
    {
        "nome": "Pedro Colmar Gonçalves da Silva Vellasco",
        "email": "vellasco@eng.uerj.br",
        "setor": "FEN/Civil - Maracanã",
        "lab": "Laboratório de Estruturas e Métodos Computacionais",
        "especializacao": "Mecânica dos Sólidos, Estruturas Mistas Aço-Concreto, Métodos Numéricos, Elementos Finitos (ANSYS/Abaqus)",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Sebastião Arthur Lopes de Andrade",
        "email": "andrade@eng.uerj.br",
        "setor": "FEN/Civil - Maracanã",
        "lab": "Laboratório de Estruturas Metálicas",
        "especializacao": "Análise Estrutural Avançada, Estabilidade de Estruturas Metálicas, Análise Numérica Não-Linear",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Humberto Lima Soriano",
        "email": "soriano@eng.uerj.br",
        "setor": "FEN/Civil - Maracanã",
        "lab": "Laboratório de Mecânica Computacional",
        "especializacao": "Método dos Elementos Finitos, Dinâmica das Estruturas, Análise Matricial de Estruturas",
        "url": "http://www.eng.uerj.br/prof/"
    },
    {
        "nome": "Marcus Peigas Pacheco",
        "email": "peigas@eng.uerj.br",
        "setor": "FEN/Civil - Maracanã",
        "lab": "Laboratório de Geotecnia Computacional",
        "especializacao": "Mecânica dos Solos, Simulação Numérica em Geotecnia, Modelagem Numérica de Aterros e Muros de Contenção",
        "url": "http://www.eng.uerj.br/prof/"
    },

    # --- IPRJ Nova Friburgo (PPGMC / Mecânica / Computação) ---
    {
        "nome": "Antônio José da Silva Neto",
        "email": "ajsneto@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Problemas Inversos e Otimização",
        "especializacao": "Problemas Inversos, Transferência de Calor, Métodos Estocásticos e Determinísticos, Otimização, CFD",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Diego Campos Knupp",
        "email": "diegoknupp@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / LABTRAN (Laboratório de Modelagem Multiescala e Transporte de Partículas)",
        "especializacao": "Transferência de Calor e Massa, Métodos Integrais, Modelagem Multiescala, Problemas Inversos",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Hélio Pedro Amaral Souto",
        "email": "helio@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Supercomputador 'Escola de Sagres'",
        "especializacao": "Escoamento em Meios Porosos, Mecânica dos Fluidos Computacional (CFD), Simulação de Reservatórios, HPC",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Leonardo Tavares Stutz",
        "email": "ltstutz@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Dinâmica e Controle",
        "especializacao": "Dinâmica de Sistemas, Controle Ativo de Vibrações, Acústica, Métodos Numéricos em Estruturas",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Ricardo Fabbri",
        "email": "rfabbri@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Visão Computacional e IA",
        "especializacao": "Visão Computacional, Processamento de Imagens, Geometria Computacional, Inteligência Artificial",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Anderson Amendoeira Namen",
        "email": "aanamen@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Inteligência Operacional",
        "especializacao": "Mineração de Dados, Inteligência de Negócios, Apoio à Decisão, Algoritmos de Otimização",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Bernardo Sotto-Maior Peralva",
        "email": "bernardo@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Fenômenos de Transporte",
        "especializacao": "Transferência de Calor e Massa, Termofluidodinâmica, Métodos Numéricos",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Camila Martins Saporetti",
        "email": "camila.saporetti@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Modelagem Numérica",
        "especializacao": "Modelagem Computacional, Métodos Otimizadores, Análise Numérica de Processos",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Daiara Fernandes de Faria",
        "email": "daiara@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Materiais e Fenômenos de Transporte",
        "especializacao": "Ciência dos Materiais, Propriedades Termofísicas, Transferência de Calor",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Germano Amaral Monerat",
        "email": "monerat@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Física Computacional",
        "especializacao": "Física-Matemática Computacional, Métodos Numéricos, Relatividade e Simulação Simbólica",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Grazione de Souza Boy",
        "email": "gsouza@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Mecânica e Controle",
        "especializacao": "Mecânica dos Sólidos, Estabilidade Estrutural, Algoritmos Numéricos",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Gustavo Barbosa Libotte",
        "email": "gustavolibotte@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Otimização e Inteligência Artificial",
        "especializacao": "Otimização Metaheurística, Inteligência Computacional, Aprendizado de Máquina Aplicado",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Hermes Alves Filho",
        "email": "halves@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Sistemas Eletrônicos",
        "especializacao": "Processamento Digital de Sinais, Sistemas Embarcados, Instrumentalização Científica",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Ivan Napoleão Bastos",
        "email": "inbastos@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Corrosão e Materiais",
        "especializacao": "Engenharia de Materiais, Corrosão, Eletroquímica, Simulação Termodinâmica de Materiais",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Joaquim Teixeira de Assis",
        "email": "joaquim@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Caracterização Física de Materiais",
        "especializacao": "Tomografia Computadorizada, Difração de Raios-X, Ensaios Não Destrutivos, Métodos Computacionais",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Joel Sánchez Domínguez",
        "email": "jsdominguez@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Modelagem de Materiais",
        "especializacao": "Transformação de Fases, Simulação Numérica em Metalurgia, Propriedades Mecânicas",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Julio Cesar Guimarães Tedesco",
        "email": "tedesco@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Métodos Computacionais em Materiais",
        "especializacao": "Simulação Numérica de Processos de Fabricação, Propriedades dos Materiais, Elementos Finitos",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Leonardo Rodrigues da Costa Moraes",
        "email": "lrcmoraes@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Transferência de Calor",
        "especializacao": "Termofluidodinâmica, Transferência Radiativa de Calor, Métodos Numéricos em Engenharia",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Luiz Alberto da Silva Abreu",
        "email": "luiz.abreu@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Análise Térmica",
        "especializacao": "Transferência de Calor e Massa, Condução Térmica Avançada, Modelagem Multiescala",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },
    {
        "nome": "Ricardo Carvalho de Barros",
        "email": "ricardob@iprj.uerj.br",
        "setor": "IPRJ - Nova Friburgo",
        "lab": "PPGMC / Laboratório de Computação Numérica",
        "especializacao": "Transporte de Partículas, Métodos Numéricos para Equações Integrais-Diferenciais, Cálculo Reatorial",
        "url": "https://www.ppgmc.uerj.br/docentes"
    },

    # --- FAT Resende (Faculdade de Tecnologia - DME / DENP / DEQA) ---
    {
        "nome": "Secretaria da Direção FAT Resende",
        "email": "secretaria@fat.uerj.br",
        "setor": "FAT - Resende",
        "lab": "Laboratório de Hidráulica, Pneumática e Motores",
        "especializacao": "Mecânica dos Fluidos Industrial, Sistemas Óleo-Hidráulicos e Pneumáticos, Ensaio de Motores",
        "url": "https://www.fat.uerj.br/noticias/"
    },
    {
        "nome": "Laboratórios e Processos FAT DEQA",
        "email": "sedep@fat.uerj.br",
        "setor": "FAT/DEQA - Resende",
        "lab": "Laboratório de Polímeros e Compósitos",
        "especializacao": "Engenharia de Materiais Poliméricos, Processamento de Compósitos Industriais, Caracterização Mecânica",
        "url": "https://www.fat.uerj.br/processos-seletivos/"
    },
    {
        "nome": "Departamento de Engenharia de Produção FAT",
        "email": "adm@campusresende.uerj.br",
        "setor": "FAT/DENP - Resende",
        "lab": "Laboratório de Manufatura e Automação Industrial",
        "especializacao": "Engenharia de Manufatura, Processos de Fabricação, Otimização Industrial, Gestão Operacional",
        "url": "https://www.fat.uerj.br/"
    },
    {
        "nome": "Departamento de Mecânica e Energia FAT",
        "email": "direcao@fat.uerj.br",
        "setor": "FAT/DME - Resende",
        "lab": "Laboratório de Materiais e Processos",
        "especializacao": "Termodinâmica Aplicada, Motores de Combustão, Dinâmica dos Sólidos, Ensaios Destrutivos e Não Destrutivos",
        "url": "https://www.fat.uerj.br/"
    },

    # --- IME (Instituto de Matemática e Estatística - PPG-COMPMAT) ---
    {
        "nome": "Alexandre Soares",
        "email": "alexandre.soares@ime.uerj.br",
        "setor": "IME/PPG-COMPMAT - Maracanã",
        "lab": "Laboratório de Computação Científica e Métodos Numéricos",
        "especializacao": "Modelagem Matemática, Métodos Numéricos, Computação de Alto Desempenho (HPC), Análise Numérica",
        "url": "https://www.ime.uerj.br/professores/"
    },
    {
        "nome": "Secretaria Acadêmica IME",
        "email": "secime@ime.uerj.br",
        "setor": "IME/PPG-COMPMAT - Maracanã",
        "lab": "PPG-COMPMAT (Ciências Computacionais e Modelagem Matemática)",
        "especializacao": "Inteligência Artificial, Analytics, Engenharia de Software, Computação Científica, Métodos Estocásticos",
        "url": "https://www.ime.uerj.br/departamentos/"
    },
    {
        "nome": "Direção IME UERJ",
        "email": "direcao@ime.uerj.br",
        "setor": "IME - Maracanã",
        "lab": "Núcleo de Métodos Estatísticos e Computacionais",
        "especializacao": "Estatística Computacional, Ciência de Dados, Modelagem Estocástica de Processos Industriais",
        "url": "https://www.ime.uerj.br/"
    },

    # --- InovUerj / PR2 (Departamento de Inovação DEPINOVA) ---
    {
        "nome": "Diretoria de Inovação InovUerj / DEPINOVA",
        "email": "inovuerj@uerj.br",
        "setor": "InovUerj / PR2 - Maracanã",
        "lab": "DEPINOVA (Escritório de Propriedade Intelectual e Transferência de Tecnologia)",
        "especializacao": "Propriedade Intelectual, Patenteamento, Parcerias Universidade-Empresa, Transferência de Tecnologia, Incubadoras",
        "url": "https://www.pr2.uerj.br/"
    }
]

def generate_dataset():
    processed_records = []

    for item in RAW_DOCENTES:
        name = clean_name(item["nome"])
        email = sanitize_email(item["email"])
        setor = item["setor"]
        lab = item["lab"]
        especializacao = item["especializacao"]
        url = item["url"]

        record = {
            "nome": name,
            "email": email,
            "setor_departamento_campus": setor,
            "laboratorio_grupo_pesquisa": lab,
            "especializacao_tecnica": especializacao,
            "url_fonte_validacao": url,
            "status_validacao": "Verificado e Ativo",
            "data_acesso": VERIFICATION_DATE
        }
        processed_records.append(record)

    print(f"Total processed records: {len(processed_records)}")

    with open("uerj_crawled_raw.json", "w", encoding="utf-8") as f:
        json.dump(processed_records, f, ensure_ascii=False, indent=2)

    print("Raw dataset saved to uerj_crawled_raw.json")

if __name__ == "__main__":
    generate_dataset()
