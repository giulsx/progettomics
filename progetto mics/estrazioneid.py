import os
import json

# Percorso della cartella contenente i file JSON
cartella = "output"  # Cambia con il percorso corretto
output_file = "id_list.txt"

id_list = []

# Scansiona tutti i file nella cartella
for filename in os.listdir(cartella):
    if filename.endswith(".json"):
        file_path = os.path.join(cartella, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "@id" in data:  # Verifica se "@id" è presente nel file
                    id_list.append(f"{filename}: {data['@id']}")
        except Exception as e:
            print(f"Errore con il file {filename}: {e}")

# Scrive tutti gli ID e i relativi file di origine in un file di testo
with open(output_file, "w", encoding="utf-8") as out_f:
    for item in id_list:
        out_f.write(item + "\n")

print(f"Estrazione completata! {len(id_list)} ID salvati in {output_file}.")
