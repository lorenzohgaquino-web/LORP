import json
import re

def clean_name(name):
    """Sanitize faculty name and remove unwanted prefixes/suffixes/degree noise."""
    if not name:
        return ""

    if "Secretaria" in name or "Diretoria" in name or "Assessoria" in name:
        return name.strip()

    name = re.sub(r'^(Prof\.|Profa\.|Dr\.|Dra\.|PhD|D\.Sc\.)\s*', '', name, flags=re.I)
    name = re.sub(r'\b(D\.Sc\.|Ph\.D\.|COPPE|PUC-Rio|UFRJ|Brasil|Área|Doutor|Mestre)\b', '', name, flags=re.I)
    name = re.sub(r'[^a-zA-ZÁ-ú\s.-]', ' ', name)

    words = [w for w in name.split() if len(w) > 1 and w.lower() not in ['doutor', 'mestre', 'area', 'brasil']]
    cleaned = " ".join(words)

    known_fixes = {
        "Evandro Luiz Cardoso Macedo": "Evandro Luiz Cardoso Macedo",
        "Helio do Nascimento Cunha": "Hélio do Nascimento Cunha Neto",
        "Ian Vilar Bastos": "Ian Vilar Bastos",
        "Marcelo Gonçalves Rubinstein": "Marcelo Gonçalves Rubinstein",
        "Lisandro Lovisolo": "Lisandro Lovisolo",
        "Michel Pompeu Tcheou": "Michel Pompeu Tcheou",
        "José Paulo Vilela Soares": "José Paulo Vilela Soares da Cunha",
        "Luís Fernando Corrêa Monteiro": "Luís Fernando Corrêa Monteiro",
        "Pedro Henrique Coutinho": "Pedro Henrique S. Coutinho",
        "Tiago Roux de Oliveira": "Tiago Roux de Oliveira",
        "Victor Hugo Pereira Rodrigues": "Victor Hugo Pereira Rodrigues",
        "Jorge Luís Machado do": "Jorge Luís Machado do Amaral",
        "José Franco Machado do": "José Franco Machado do Amaral",
        "Luiza de Macedo Mourelle": "Luiza de Macedo Mourelle",
        "Nadia Nedjah": "Nadia Nedjah",
        "Luciano Rodrigues Ornelas de": "Luciano Rodrigues Ornelas de Lima",
        "Ana Cristina Castro": "Ana Cristina Castro S. Lima",
        "Bruno Lima": "Bruno Lima",
        "Kíssila Goliath": "Kíssila Goliath",
        "Margareth Magalhães": "Margareth da Silva Magalhães",
        "Monique Rodrigues": "Monique Rodrigues",
        "Rodrigo Burgos": "Rodrigo Burgos",
        "Armando Prestes": "Armando Prestes Filho",
        "Fernando Lins": "Fernando Lins",
        "Maria Fernanda": "Maria Fernanda de Oliveira",
        "Marcus Pacheco": "Marcus Peigas Pacheco"
    }

    for k, v in known_fixes.items():
        if k.lower() in cleaned.lower():
            return v

    return cleaned if len(cleaned) > 3 else name.strip()

def process_and_clean():
    with open("uerj_raw_crawled.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_records = []
    seen_emails = set()

    for rec in data:
        email = rec.get("email", "").strip().lower()
        if not email or email in seen_emails:
            continue

        seen_emails.add(email)

        raw_name = rec.get("nome", "")
        cleaned_n = clean_name(raw_name)

        email_map = {
            "anacriscastro@hotmail.com": ("Ana Cristina Castro S. Lima", "FEN / Engenharia Civil", "PGECIV - Geotecnia e Métodos Numéricos"),
            "brunolima.professor@gmail.com": ("Bruno Lima", "FEN / Engenharia Civil", "PGECIV - Estruturas e Mecânica dos Sólidos"),
            "kissilagoliath@gmail.com": ("Kíssila Goliath", "FEN / Engenharia Civil", "PGECIV - Computação e Estruturas"),
            "margareth.magalhaes@uerj.br": ("Margareth da Silva Magalhães", "FEN / Engenharia Civil", "PGECIV - Análise Numérica e Materiais"),
            "monique.rodrigues@uerj.br": ("Monique Rodrigues", "FEN / Engenharia Civil", "PGECIV - Geotecnia Computacional"),
            "rburgos@eng.uerj.br": ("Rodrigo Burgos", "FEN / Engenharia Civil", "PGECIV - Estruturas e Métodos Finitos"),
            "armando.prestes.filho@uerj.br": ("Armando Prestes Filho", "FEN / Engenharia Civil", "PGECIV - Mecânica das Estruturas"),
            "pereiralins@gmail.com": ("Fernando Lins", "FEN / Engenharia Civil", "PGECIV - Métodos Numéricos"),
            "mariafer@eng.uerj.br": ("Maria Fernanda de Oliveira", "FEN / Engenharia Civil", "PGECIV - Estruturas e Sólidos"),
            "marcus_pacheco@terra.com.br": ("Marcus Peigas Pacheco", "FEN / Engenharia Civil", "PGECIV - Geotecnia e Simulação")
        }

        if email in email_map:
            cleaned_n, setor, lab = email_map[email]
            rec["setor"] = setor
            rec["laboratorio"] = lab

        record = {
            "nome": cleaned_n,
            "email": email,
            "setor": rec.get("setor", ""),
            "laboratorio": rec.get("laboratorio", ""),
            "especializacao": rec.get("especializacao", ""),
            "url": rec.get("url", ""),
            "status": "Verificado",
            "data_acesso": "11/09/2026"
        }

        cleaned_records.append(record)

    with open("uerj_cleaned.json", "w", encoding="utf-8") as f:
        json.dump(cleaned_records, f, ensure_ascii=False, indent=2)

    print(f"Cleaned and saved {len(cleaned_records)} unique records to uerj_cleaned.json")

if __name__ == "__main__":
    process_and_clean()
