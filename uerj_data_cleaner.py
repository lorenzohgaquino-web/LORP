import re

def sanitize_string(val):
    if not val:
        return ""

    # Strip non-printable / unicode replacement characters
    val = val.replace('\ufffd', '')
    val = val.replace('', '')

    val = re.sub(r'\s+', ' ', val).strip()
    return val

if __name__ == '__main__':
    print(sanitize_string("Afrânio Sérgio Pinho Dos Santos"))
