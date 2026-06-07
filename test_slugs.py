import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

slugs = [
    "pesc", "pee", "pem", "pep", "pen", "pec", "peq", "peb", "peno", "ppe", "pemm", "pent", "pet",
    "ppgi", "ppgcc", "ppgm", "ppgmat", "ppgf", "ppgq", "ppgqu", "ppgg", "ppggeo", "ppgbio", "ppgbme",
    "ppge", "ppgee", "ppgmec", "ppgep", "ppgen", "ppgeq", "ppgbc", "ppgb", "ppgz", "ppga", "ppget",
    "ppgo", "ppgpe", "ppgmm", "ppgn", "ppgt", "ppgmc", "ppgma", "ppgst", "ppgmfa", "ppggeoq",
    "ppge", "ppgm", "ppgq", "ppgf", "ppgmat", "ppgi", "ppgic", "ppgcc", "ppge", "ppgee", "ppgmec",
    "ppgep", "ppgen", "ppgeq", "ppgbc", "ppgb", "ppgz", "ppga", "ppget", "ppgo", "ppgpe", "ppgmm",
    "ppgn", "ppgt", "ppgmc", "ppgma", "ppgst", "ppgmfa", "ppggeoq", "ppgci", "ppgdis", "ppgh",
    "ppgas", "ppgs", "ppgcom", "ppge", "ppgp", "ppgps", "ppgsc", "ppgv", "ppgant", "ppga",
    "ppgl", "ppgm", "ppgav", "ppgarch", "ppgiau", "ppgau", "ppgep", "ppgto", "ppgb"
]

found = []
for s in sorted(list(set(slugs))):
    url = f"https://w1.solucaoatrio.net.br/ufrj-{s}/pub/Professor.do?method=professorPermanentActive&lng=pt"
    try:
        r = requests.get(url, verify=False, timeout=5)
        if r.status_code == 200:
            found.append(f"ufrj-{s}")
            print(f"Found: ufrj-{s}")
    except:
        pass
print("Final List:", found)
