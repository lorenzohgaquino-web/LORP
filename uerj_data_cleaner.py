#!/usr/bin/env python3
"""
uerj_data_cleaner.py - Utility functions for string sanitization, name validation,
encoding repairs, and Siemens DISW technical specialization classification.
"""

import re
import unicodedata

DISW_TAXONOMY = {
    "CFD & Termofluidodinâmica": [
        r"\bcfd\b", r"\btermofluido\w*", r"\bfluidodin[âa]mica\b", r"\bmec[âa]nica dos fluidos\b",
        r"\btransporte de massa\b", r"\bmeios porosos\b", r"\bescoamento\w*", r"\baerodin[âa]mica\b",
        r"\bturbul[êe]ncia\b", r"\bstar-ccm\b", r"\btransfer[êe]ncia de calor\b"
    ],
    "Elementos Finitos & Análise Estrutural": [
        r"\belementos finitos\b", r"\bfem\b", r"\bfea\b", r"\ban[áa]lise estrutural\b",
        r"\bmec[âa]nica dos s[óo]lidos\b", r"\belasticidade\b", r"\bplasticidade\b",
        r"\bvibra[çc][õo]es\b", r"\bac[úu]stica\b", r"\bfadiga\b", r"\bfratura\b"
    ],
    "Modelagem Computacional & HPC": [
        r"\bmodelagem computacional\b", r"\bm[ée]todos num[ée]ricos\b", r"\bhpc\b",
        r"\bcomputa[çc][ãa]o de alto desempenho\b", r"\bsimula[çc][ãa]o num[ée]rica\b",
        r"\balgoritmos\b", r"\botimiza[çc][ãa]o\b", r"\bsupercomputa[çc][ãa]o\b"
    ],
    "Sistemas de Controle & Automação": [
        r"\bcontrole\b", r"\bautoma[çc][ãa]o\b", r"\brob[óo]tica\b", r"\beletr[ôo]nica de pot[êe]ncia\b",
        r"\bsistemas embarcados\b", r"\bsinais\b", r"\barduino\b", r"\bplc\b"
    ],
    "Manufatura Aditiva & Materiais": [
        r"\bmanufatura\b", r"\bimpress[ãa]o 3d\b", r"\bpol[íi]meros\b", r"\bcomp[óo]sitos\b",
        r"\bcaracteriza[çc][ãa]o de materiais\b", r"\bcorros[ãa]o\b", r"\bmetalurgia\b", r"\bmetais\b"
    ],
    "Inovação & Transferência de Tecnologia": [
        r"\binova[çc][ãa]o\b", r"\bpropriedade intelectual\b", r"\bpatentes\b", r"\bincubadora\b",
        r"\btransfer[êe]ncia de tecnologia\b", r"\bparcerias\b", r"\bprojetos p&d\b"
    ]
}

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Fix common encoding issues
    try:
        text = text.encode('iso-8859-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    text = unicodedata.normalize('NFC', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_person_name(name: str) -> str:
    if not name:
        return ""
    name = clean_text(name)
    # Remove honorifics and titles
    prefixes = [r'^prof\.\s*dr[a]?\.\s*', r'^prof\.\s*', r'^dr[a]?\.\s*', r'^pesquisador[a]?\s*']
    for p in prefixes:
        name = re.sub(p, '', name, flags=re.IGNORECASE)
    return name.strip()

def classify_specialization(text: str) -> str:
    if not text:
        return "Modelagem Computacional & Engenharia Aplicada"
    matched_specs = []
    text_lower = text.lower()

    for spec, patterns in DISW_TAXONOMY.items():
        for p in patterns:
            if re.search(p, text_lower):
                matched_specs.append(spec)
                break

    if matched_specs:
        return " | ".join(matched_specs)
    return "Modelagem Computacional & Engenharia Aplicada"

def is_valid_person_name(name: str) -> bool:
    if not name or len(name) < 5:
        return False
    invalid_keywords = ['departamento', 'curso', 'graduação', 'pós-graduação', 'mencionado', 'pesquisa', 'laboratório', 'secretaria', 'direção']
    if any(k in name.lower() for k in invalid_keywords):
        return False
    return True
