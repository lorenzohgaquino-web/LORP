#!/usr/bin/env python3
"""
uerj_data_cleaner.py
Sanitizes strings, validates person names, cleans encoding/mojibake errors,
and maps Siemens DISW technical specializations using word boundary regex.
"""

import re
import html

HONORIFICS = [
    r'\bProf\.?\b', r'\bProfa\.?\b', r'\bProfessor\b', r'\bProfessora\b',
    r'\bDr\.?\b', r'\bDra\.?\b', r'\bDoutor\b', r'\bDoutora\b',
    r'\bMSc\.?\b', r'\bM\.Sc\.?\b', r'\bPh\.?D\.?\b', r'\bEng\.?\b', r'\bEnga\.?\b'
]

TITLE_PATTERN = re.compile("|".join(HONORIFICS), re.IGNORECASE)

# Keywords and regex mapping for Siemens DISW technical specializations
SPECIALIZATIONS = [
    (r'\b(CFD|Computational Fluid Dynamics|Dinâmica dos Fluidos Computacional|Fluidos|Termofluidodinâmica|Escoamento)\b', 'CFD & Termofluidodinâmica'),
    (r'\b(Elementos Finitos|FEM|FEA|Mecânica dos Sólidos|Estruturas|Vibrações|Acústica|Análise Estrutural)\b', 'Elementos Finitos & Simulação Estrutural / Acústica'),
    (r'\b(Simulação|Modelagem Computacional|Modelagem Numérica|Métodos Numéricos|HPC|Alto Desempenho)\b', 'Simulação Numérica & Computação de Alto Desempenho (HPC)'),
    (r'\b(Manufatura|Usinagem|Polímeros|Compósitos|Processos de Fabricação|Materiais)\b', 'Manufatura & Engenharia de Materiais / Polímeros'),
    (r'\b(Otimização|Pesquisa Operacional|Logística|Processos Químicos|Reatores|Termodinâmica)\b', 'Otimização de Processos & Termodinâmica'),
    (r'\b(Controle|Automação|Robótica|Sistemas Eletrônicos|Eletrônica de Potência)\b', 'Sistemas de Controle, Automação & Eletrônica'),
    (r'\b(IA|Inteligência Artificial|Machine Learning|Analytics|Engenharia de Software)\b', 'Inteligência Artificial & Ciência de Dados'),
    (r'\b(Propriedade Intelectual|Inovação|Transferência de Tecnologia|Patentes|TT)\b', 'Gestão de Inovação & Propriedade Intelectual')
]

INVALID_KEYWORDS = [
    "corpo docente", "departamento", "faculdade", "instituto", "coordenacao", "diretoria",
    "membros", "secretaria", "laboratorio", "universidade", "uerj", "pesquisa", "graduacao",
    "pos-graduacao", "processo seletivo", "concurso", "edital", "bolsa", "noticias", "menu",
    "aluno", "professor(a)", "pesquisador(a)", "transparencia", "cursos", "producao", "av.", "rua",
    "campus", "banco", "internacionalizacao", "biblioteca", "manual", "premio", "convenio", "acesso"
]

def sanitize_text(text):
    if not text:
        return ""
    # Decode HTML entities
    text = html.unescape(str(text))
    # Replace unicode replacement characters
    text = text.replace('\ufffd', '').replace('', '')
    # Strip honorifics
    text = TITLE_PATTERN.sub('', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def is_valid_person_name(name):
    if not name:
        return False

    clean = sanitize_text(name).strip()
    clean_lower = clean.lower()

    # Special allowance for official institutional role fallbacks if explicitly named as Secretaria/Coordenação
    if any(valid_role in clean_lower for valid_role in ["secretaria do departamento", "coordenação ppg", "diretoria inovuerj"]):
        return True

    if len(clean) < 5 or len(clean) > 60:
        return False

    # Check for invalid keywords
    if any(inv in clean_lower for inv in INVALID_KEYWORDS):
        return False

    # Must not contain numbers or street address tokens
    if re.search(r'\d', clean):
        return False

    # Must contain only alphabetic characters, spaces, accents and hyphens
    if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s\-\.]+$', clean):
        return False

    # Person names usually have at least two words
    words = clean.split()
    if len(words) < 2:
        return False

    return True

def classify_specialization(text_context):
    if not text_context:
        return "Simulação Numérica & Engenharia Computacional"

    matches = []
    for pattern, spec in SPECIALIZATIONS:
        if re.search(pattern, text_context, re.IGNORECASE):
            matches.append(spec)

    if matches:
        return "; ".join(dict.fromkeys(matches)) # Unique list ordered
    return "Simulação Numérica & Engenharia Computacional"

if __name__ == "__main__":
    test_str = "Prof. Dr. Americo Cunha Junior"
    cleaned = sanitize_text(test_str)
    print(f"Sanitized: '{test_str}' -> '{cleaned}'")
    print(f"Is valid person: {is_valid_person_name(cleaned)}")
    spec = classify_specialization("Pesquisas em CFD, Termofluidodinâmica e Inteligência Artificial")
    print(f"Specialization: {spec}")
