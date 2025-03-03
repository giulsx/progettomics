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

# Carica il file JSON e usa la funzione per estrarre gli ID e i conteggi
try:
    with open("progetto mics/ecoinvent-3.10-cutoff-upr-15352.json", "r") as file:
        json_data = json.load(file)
except Exception as e:
    print(f"Errore nel caricamento del file JSON: {e}")
    json_data = {}

# Estrai i conteggi degli ID
id_counts = extract_id_counts(json_data)

# Salva le chiavi ID e i loro conteggi in un file di testo
try:
    with open("progetto mics/analisi id/output_id_counts_UPR.txt", "w") as output_file:
        for (key, value), count in id_counts.items():
            output_file.write(f"Key: {key}, Value: {value}, Count: {count}\n")
except Exception as e:
    print(f"Errore nel salvataggio del file di output: {e}")

# Salva solo gli ID con count maggiore di uno in un altro file
try:
    with open("progetto mics/analisi id/output_id_counts_greater_than_one_UPR.txt", "w") as output_file_greater:
        for (key, value), count in id_counts.items():
            if count > 1:
                output_file_greater.write(f"Key: {key}, Value: {value}, Count: {count}\n")
except Exception as e:
    print(f"Errore nel salvataggio del file di output per conteggio maggiore di uno: {e}")
