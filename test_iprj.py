import requests
from bs4 import BeautifulSoup
import urllib3, re, json

urllib3.disable_warnings()
session = requests.Session()
session.verify = False
session.headers.update({'User-Agent': 'Mozilla/5.0'})

url = "https://www.ppgmc.uerj.br/docentes"
r = session.get(url, timeout=15)
soup = BeautifulSoup(r.text, 'html.parser')

docentes = []

# Find all blocks with lattes links or email links
# Look at page structure
cards = soup.find_all('div')
for card in soup.find_all(['p', 'div']):
    # Check if card contains email link and lattes link
    mailto = card.find('a', href=re.compile(r'mailto:'))
    lattes = card.find('a', href=re.compile(r'lattes\.cnpq\.br'))
    if mailto and lattes:
        email = mailto['href'].replace('mailto:', '').strip()
        lattes_url = lattes['href']
        # Find name in card text
        text = card.get_text()
        # Clean text
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines:
            if '@' not in line and 'LATTES' not in line and 'Home' not in line and len(line) > 3:
                name = line
                docentes.append({'name': name, 'email': email, 'lattes': lattes_url})
                break

print(f"Extracted {len(docentes)} docentes from PPGMC")
for d in docentes:
    print(d)
