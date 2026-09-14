import re
import html

def repair_encoding(text: str) -> str:
    if not text:
        return ""
    # Unescape HTML entities
    text = html.unescape(text)

    # Common Mojibake replacements if ISO-8859-1 was double-decoded or misinterpreted
    replacements = {
        "": "",
        "Ã¡": "á", "Ã©": "é", "Ã­": "í", "Ã³": "ó", "Ãº": "ú",
        "Ã£": "ã", "Ãµ": "õ", "Ã¢": "â", "Ãª": "ê", "Ã´": "ô",
        "Ã§": "ç", "Ã": "Á", "Ã‰": "É", "ÃI": "Í", "Ã": "Ó",
        "Ãš": "Ú", "Ã": "Ã", "Ã•": "Õ", "Ã‚": "Â", "ÃŠ": "Ê",
        "Ã”": "Ô", "Ã‡": "Ç"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    # Clean control characters
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_name(name: str) -> str:
    if not name:
        return ""
    name = repair_encoding(name)

    # Remove degree / honorific / title prefixes and suffixes
    # Note: use word boundary checks e.g. \b(LATTES|S)\b to avoid cutting real names like Silva or Salles!
    title_patterns = [
        r'^\s*Prof\.?\s*(?:a\.?)?\s*',
        r'^\s*Professora?\s+',
        r'^\s*Dr\.?\s*(?:a\.?)?\s*',
        r'^\s*D\.Sc\.?\s*',
        r'^\s*Ph\.D\.?\s*',
        r'^\s*M\.Sc\.?\s*',
        r',\s*D\.Sc.*$',
        r',\s*Ph\.D.*$',
        r',\s*M\.Sc.*$',
        r',\s*Doctor.*$',
        r'\s*\(.*?\)\s*'
    ]
    for pattern in title_patterns:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)

    # Extra cleanup
    name = re.sub(r'^[k\d\s\-]+', '', name) # remove leading k-numbers or IDs if present
    name = re.sub(r'\s+', ' ', name).strip()
    return name.title()

def sanitize_email(email: str) -> str:
    if not email:
        return "não disponível publicamente"
    email = email.strip().lower()
    email = re.sub(r'^[^\w]+', '', email)
    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return email
    return "não disponível publicamente"

if __name__ == "__main__":
    sample = "Prof. Norberto Mangiavacchi , D.Sc. - COPPE/UFRJ"
    print("Original:", sample)
    print("Cleaned:", clean_name(sample))
