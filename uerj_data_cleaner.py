import re
import html

# UI Junk and Non-Person Filters
INVALID_NAMES = {
    'PÁGINA PRINCIPAL', 'PAGINA PRINCIPAL', 'DOCENTES', 'LATTES', 'CURRICULO LATTES',
    'EQUIPE', 'CONTATO', 'RETORNA', 'HOME', 'NOTÍCIAS', 'SOBRE', 'PESQUISA', 'LABORATÓRIOS',
    'PUBLICAÇÕES', 'TESES E DISSERTAÇÕES', 'CURSOS', 'GRADUAÇÃO', 'PÓS-GRADUAÇÃO', 'ALUNO',
    'PROFESSOR', 'NOSSOS CURSOS', 'PRODUÇÃO ACADÊMICA', 'SOBRE A FEN', 'TRANSPARÊNCIA', 'LINKS ÚTEIS'
}

def clean_text(text):
    if not text:
        return ""
    text = html.unescape(text)
    # Remove unicode control/replacement characters and non-printable symbols
    text = re.sub(r'[\r\n\t]', ' ', text)
    text = re.sub(r'[^\w\s@._\-\(\)/,:;áàâãéèêíïóôõöúçÑñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇ]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def sanitize_name(name):
    if not name:
        return ""
    name = clean_text(name)

    # Remove honorifics/titles
    name = re.sub(r'^(Prof\.|Profa\.|Professora|Professor|Dr\.|Dra\.|Ph\.D\.|DSc\.|MSc\.|Eng\.)\s+', '', name, flags=re.IGNORECASE)
    # Remove trailing degrees or labels like ", DSc." or " - Coordinator"
    name = re.sub(r'[,–-].*$', '', name).strip()
    # Strip non-alphabetic leading characters
    name = re.sub(r'^[^\wáàâãéèêíïóôõöúçÑñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇ]+', '', name).strip()

    name_upper = name.upper()
    if name_upper in INVALID_NAMES or len(name) < 3:
        return ""
    if '@' in name or 'http' in name_upper or 'www.' in name_upper:
        return ""

    # Convert ALL CAPS names to Title Case for consistency
    if name.isupper():
        name = name.title()

    return name

def sanitize_email(email):
    if not email:
        return ""
    email = clean_text(email).lower()
    # Clean trailing corrupted chars like 'cv'
    email = re.sub(r'(uerj\.br|ufrj\.br|terra\.com\.br|puc-rio\.br|gmail\.com|crea-rj\.org\.br)(cv|html|php).*$', r'\1', email)
    # Match standard email pattern
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email)
    if match:
        clean_e = match.group(0).lower()
        if clean_e.endswith('cv'):
            clean_e = clean_e[:-2]
        return clean_e
    return ""

if __name__ == "__main__":
    print("Name test:", sanitize_name(" AANAMEN@IPRJ.UERJ.BR"))
    print("Name test 2:", sanitize_name("ROGERIO MARTINS SALDANHA DA GAMA"))
    print("Email test:", sanitize_email("ldmm@eng.uerj.brcv"))
