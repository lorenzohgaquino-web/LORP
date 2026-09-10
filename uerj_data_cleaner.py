import re
import ftfy

def clean_string(text: str) -> str:
    if not text:
        return ""

    # Fix ftfy
    try:
        text = ftfy.fix_text(text)
    except Exception:
        pass

    # Remove replacement characters
    text = text.replace("", "").replace("\uFFFD", "")

    # Strip titles/honorifics if present at beginning of name
    titles = [
        r"^Prof\.\s*Dr\.\s*", r"^Profa\.\s*Dra\.\s*", r"^Profª\.\s*Dra\.\s*", r"^Profº\.\s*Dr\.\s*",
        r"^Prof\.\s*", r"^Profa\.\s*", r"^Dr\.\s*", r"^Dra\.\s*", r"^Profª\s*", r"^Profº\s*"
    ]
    for t in titles:
        text = re.sub(t, "", text, flags=re.IGNORECASE)

    # Standardize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def sanitize_email(email: str) -> str:
    if not email:
        return ""
    email = email.strip().lower()
    email = re.sub(r"\s+", "", email)
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", email)
    if match:
        return match.group(0)
    return ""
