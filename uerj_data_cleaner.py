import sys
import os
import json
import csv
import re

def clean_text(text):
    if not text:
        return ""
    text = text.replace('\xa0', ' ').replace('\u200b', '')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def fix_mojibake(text):
    if not text:
        return ""
    replacements = {
        'Ã¢': 'â', 'Ã£': 'ã', 'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
        'Ã§': 'ç', 'ÃŠ': 'Ê', 'Ã': 'Á', 'Ã‰': 'É', 'ÃI': 'Í', 'ÃO': 'Ó', 'Ãš': 'Ú',
        'Ã‡': 'Ç', 'Ã´': 'ô', 'Ãª': 'ê', 'Ã ': 'à', 'Ãµ': 'õ', 'Ã‘': 'Ñ', 'Ã±': 'ñ',
        'â€“': '–', 'â€”': '—', 'â€™': "'", 'â€œ': '"', 'â€': '"'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def sanitize_name(name):
    name = fix_mojibake(name)
    name = re.sub(r'^(Prof\.?|Dr\.?|D\.Sc\.?|Dra\.?|Professor|Professora)\s+', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+(phd|d\.sc|dsc|m\.sc|msc|ph\.d\.?)$', '', name, flags=re.IGNORECASE)
    return clean_text(name)

def is_valid_person_name(name):
    if not name or len(name) < 5:
        return False
    invalid_keywords = ['home', 'login', 'secao', 'noticia', 'processo', 'edital', 'substituto', 'concurso', 'secretaria', 'atendimento']
    name_lower = name.lower()
    for kw in invalid_keywords:
        if kw in name_lower:
            return False
    words = name.split()
    return len(words) >= 2

def map_specialization(text, name=""):
    text_lower = (text + " " + name).lower()
    specs = []

    if re.search(r'\b(cfd|fluidodin[aâ]mica|fluidos?|escoamento|mdf|fvm|navier|lbm|boltzmann)\b', text_lower):
        specs.append("CFD / Simulação de Fluidos e Termofluidodinâmica")
    if re.search(r'\b(elementos finitos|fem|fea|mef|estruturas?|s[oó]lidos|elasticidade)\b', text_lower):
        specs.append("Métodos Numéricos / Elementos Finitos (FEA)")
    if re.search(r'\b(ac[uú]stica|vibra[çc][oõ]es?|ru[ií]do|din[aâ]mica das estruturas)\b', text_lower):
        specs.append("Vibrações, Acústica e Dinâmica Veicular")
    if re.search(r'\b(otimiza[çc][aã]o|pesquisa operacional|log[ií]stica|cadeia de suprimentos|processos)\b', text_lower):
        specs.append("Otimização Industrial e Pesquisa Operacional")
    if re.search(r'\b(intelig[eê]ncia artificial|ia|aprendizado de m[aá]quina|machine learning|redes neurais|deep learning|hpc|computa[çc][aã]o de alto desempenho)\b', text_lower):
        specs.append("Inteligência Artificial, Analytics e HPC")
    if re.search(r'\b(manufatura|usinagem|fabri|soldagem|pol[ií]meros|comp[oó]sitos|materiais)\b', text_lower):
        specs.append("Manufatura Avançada, Materiais e Polímeros")
    if re.search(r'\b(controle|automa[çc][aã]o|rob[oô]tica|servomecanismos|eletr[oô]nica de pot[eê]ncia)\b', text_lower):
        specs.append("Controle, Automação e Eletrônica de Potência")
    if re.search(r'\b(inova[çc][aã]o|propriedade intelectual|patentes|transfer[eê]ncia de tecnologia)\b', text_lower):
        specs.append("Gestão de Inovação, Propriedade Intelectual e Transferência Tecnológica")

    if not specs:
        specs.append("Simulação, Modelagem Computacional e Métodos Numéricos Aplicados")

    return " | ".join(specs)

if __name__ == "__main__":
    test_name = "Prof. Dr. Norberto Mangiavacchi, phD."
    print("Sanitized Name:", sanitize_name(test_name))
    print("Specialization:", map_specialization("Desenvolvimento de cfd e métodos de elementos finitos em escoamentos multipásicos"))
