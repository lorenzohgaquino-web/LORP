import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = "https://w1.solucaoatrio.net.br/"
prefixes = ["ufrj-", "ppg-", "pg-", "ppg", "pg"]
# List of potential program names/acronyms at UFRJ
units = [
    "pesc", "pee", "pem", "pep", "pen", "pec", "peq", "peb", "peno", "ppe", "pemm", "pent", "pet",
    "ppgi", "ppgcc", "ppgm", "ppgmat", "ppgf", "ppgq", "ppgqu", "pgqu", "ppgg", "ppggeo", "ppgbio",
    "ppgbme", "ppge", "ppgee", "ppgmec", "ppgep", "ppgen", "ppgeq", "ppgbc", "ppgb", "ppgz", "ppga",
    "ppget", "ppgo", "ppgpe", "ppgmm", "ppgn", "ppgt", "ppgmc", "ppgma", "ppgst", "ppgmfa", "ppggeoq",
    "im", "if", "iq", "ic", "geo", "bio", "nut", "far", "med", "odo", "enf", "fis", "psi", "eco",
    "facc", "fnd", "ie", "ippur", "coppead", "irid", "eefd", "eean", "impg", "ices", "idt", "ig",
    "indc", "ipub", "ippmg", "cenabio", "hucff", "hesfa", "nupem", "ibccf", "ibqm", "nutes", "ippn",
    "me", "nubea", "needier", "ct", "poli", "eq", "ima", "nides", "macae", "caxias", "ccmn", "ccs",
    "ccje", "cfch", "cla", "forum", "bib", "sibi", "prefeitura", "etu", "eplam", "coppetec", "lattes",
    "atrio", "webmail", "pantheon", "minerva", "ale", "amb", "at", "biof", "biom", "biot", "bot", "cb",
    "cc", "cel", "cf", "cg", "ci", "cl", "cm", "cn", "co", "cp", "cs", "ct", "da", "de", "di", "dm",
    "dp", "dr", "ea", "ec", "ed", "ee", "ef", "eg", "el", "em", "en", "ep", "eq", "er", "es", "et",
    "ev", "fa", "fb", "fc", "fd", "fe", "ff", "fg", "fh", "fi", "fl", "fm", "fn", "fo", "fp", "fq",
    "fr", "fs", "ft", "fu", "fv", "ga", "gb", "gc", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm",
    "gn", "go", "gp", "gq", "gr", "gs", "gt", "gu", "gv", "ha", "hb", "hc", "hd", "he", "hf", "hg",
    "hh", "hi", "hj", "hk", "hl", "hm", "hn", "ho", "hp", "hq", "hr", "hs", "ht", "hu", "hv", "ia",
    "ib", "ic", "id", "ie", "if", "ig", "ih", "ii", "ij", "ik", "il", "im", "in", "io", "ip", "iq",
    "ir", "is", "it", "iu", "iv", "iw", "ix", "iy", "iz"
]

found = []
for p in prefixes:
    for u in units:
        slug = f"{p}{u}"
        url = f"{base_url}{slug}/pub/Professor.do?method=professorPermanentActive&lng=pt"
        try:
            r = requests.get(url, verify=False, timeout=1)
            if r.status_code == 200 and "Atrio" in r.text:
                found.append(slug)
                print(f"Found: {slug}")
        except:
            pass

print("Final List:", sorted(list(set(found))))
