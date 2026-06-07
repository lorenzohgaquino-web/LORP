import json
import os

def merge_data():
    files = ['atrio_faculty_data.json', 'generic_data_v2.json', 'poli_data.json']
    all_records = []
    for f in files:
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8') as j:
                data = json.load(j)
                print(f"Loaded {len(data)} from {f}")
                all_records.extend(data)

    unique_names = {}
    for r in all_records:
        name = r['Nome'].strip().upper()
        if not name: continue
        if name not in unique_names:
            unique_names[name] = r
        else:
            # Prefer record with email
            if not unique_names[name].get('E-mail') and r.get('E-mail'):
                unique_records[name] = r

    print(f"Total records: {len(all_records)}")
    print(f"Unique names: {len(unique_names)}")

    with_email = [r for r in unique_names.values() if r.get('E-mail')]
    print(f"Unique records with email: {len(with_email)}")

    return unique_names

if __name__ == "__main__":
    merge_data()
