import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
units = ["ppgb", "ppg-biofisica", "ppg-bioprocessos", "ppg-biotecnologia", "ppg-biologia", "ppg-microbiologia", "ppg-nutricao", "ppg-farmacia", "ppg-medicina", "ppg-odontologia", "ppg-enfermagem", "ppg-fisioterapia", "ppg-educacao-fisica", "ppg-bioquimica", "ppg-genetica", "ppg-zoologia", "ppg-botanica", "ppg-ecologia"]
found = []
for s in units:
    slugs = [f"ufrj-{s}", f"ppg-{s}", f"pg-{s}"]
    for slug in slugs:
        url = f"https://w1.solucaoatrio.net.br/{slug}/pub/Professor.do?method=professorPermanentActive&lng=pt"
        try:
            r = requests.get(url, verify=False, timeout=1.5)
            if r.status_code == 200 and "Atrio" in r.text:
                found.append(slug)
                print(f"Found: {slug}")
        except: pass
