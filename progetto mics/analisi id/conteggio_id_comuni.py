import json
from collections import defaultdict

def extract_id_counts(json_data, id_counts=None):
    if id_counts is None:
        id_counts = defaultdict(int)

    if isinstance(json_data, dict):
        # Cerca l'ID in ogni chiave del dizionario
        for key, value in json_data.items():
            if "id" in key.lower() and isinstance(value, (str, int)):
                id_counts[(key, value)] += 1  # Incrementa il conteggio per la chiave e il valore
            # Ricorsione per oggetti annidati
            if isinstance(value, (dict, list)):
                extract_id_counts(value, id_counts)

    elif isinstance(json_data, list):
        for item in json_data:
            extract_id_counts(item, id_counts)

    return id_counts

def load_json_file(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Errore nel caricamento del file JSON {file_path}: {e}")
        return {}

# File JSON da analizzare in ordine specifico
file_paths = [
    "progetto mics/ecoinvent-3.10-cutoff-lci-15352.json",   # LCI in prima posizione
    "progetto mics/ecoinvent-3.10-cutoff-lcia-15352.json",  # LCIA in seconda posizione
    "progetto mics/ecoinvent-3.10-cutoff-upr-15352.json"    # UPR in terza posizione
]

# Estrai gli ID e i conteggi da ciascun file
id_counts_list = []
for file_path in file_paths:
    json_data = load_json_file(file_path)
    id_counts = extract_id_counts(json_data)
    id_counts_list.append(id_counts)

# Crea un dizionario per contare in quanti file appare ciascun ID
id_appearance_counts = defaultdict(int)

# Conta le apparizioni degli ID
for id_counts in id_counts_list:
    for key in id_counts.keys():
        id_appearance_counts[key] += 1

# Filtra solo gli ID che appaiono in almeno due file
common_ids = {key: count for key, count in id_appearance_counts.items() if count >= 2}

# Ordina gli ID comuni in base alla chiave
sorted_common_ids = sorted(common_ids.keys(), key=lambda x: x[0])  # Ordina per il primo elemento della chiave

# Stampa gli ID comuni e i loro conteggi, con 0 per i file in cui non compaiono
try:
    with open("progetto mics/analisi id/common_id_counts.txt", "w") as output_file:
        for key in sorted_common_ids:
            counts = [id_counts.get(key, 0) for id_counts in id_counts_list]  # Usa 0 se non trovato
            output_file.write(f"Key: {key[0]}, Value: {key[1]}, Counts (LCI, LCIA, UPR): {counts}\n")
except Exception as e:
    print(f"Errore nel salvataggio del file di output per ID comuni: {e}")
