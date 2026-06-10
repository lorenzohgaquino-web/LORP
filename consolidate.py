import json
import re

def consolidate():
    faculty = []
    with open('atrio_faculty_data.json', 'r') as f:
        faculty.extend(json.load(f))
    with open('generic_data_v2.json', 'r') as f:
        faculty.extend(json.load(f))

    labs = []
    with open('atrio_labs_data.json', 'r') as f:
        labs.extend(json.load(f))

    # Mapping of name -> record
    combined = {}

    # First, populate with faculty (they have emails)
    for r in faculty:
        name = r['Nome'].strip().upper()
        if not name: continue
        if name not in combined or (not combined[name].get('E-mail') and r.get('E-mail')):
            combined[name] = r

    # Then, add info from labs
    for r in labs:
        name = r['Nome'].strip().upper()
        if not name: continue
        if name in combined:
            # Update research area if current is empty
            if not combined[name].get('Área de Pesquisa') or combined[name]['Área de Pesquisa'] == "":
                combined[name]['Área de Pesquisa'] = r['Área de Pesquisa']
        else:
            # New researcher from lab, but we might not have their email yet
            combined[name] = r

    results = list(combined.values())
    print(f"Total consolidated: {len(results)}")

    with open('consolidated_data.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    consolidate()
