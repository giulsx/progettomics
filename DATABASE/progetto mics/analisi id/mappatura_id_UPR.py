import json 

def load_ids_from_file(file_path):
    ids = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Estrae solo il valore dell'ID dalla riga
                parts = line.split(",")
                if parts and len(parts) > 1:
                    id_value = parts[1].split(":")[1].strip()  # Estrae il valore dall'ID
                    ids.append(id_value)
    except Exception as e:
        print(f"Errore nel caricamento degli ID dal file: {e}")
    return ids

def find_id_texts_in_json(json_data, ids):
    results = {}

    # Funzione per cercare l'ID nel JSON e restituire i dettagli richiesti
    def search(json_data, id_value):
        if isinstance(json_data, dict):
            for key, value in json_data.items():
                if isinstance(value, (str, int)) and str(value) == str(id_value):
                    # Trova i dettagli richiesti se l'ID è trovato
                    if key == "@unitId":
                        # Se l'ID è un unitId, cerca il nome dell'unità
                        unit_name = json_data.get("unitName", {}).get("#text", "Unknown")
                        return {
                            "key": key,
                            "unit_name": unit_name,
                        }
                    elif key == "@sourceId":
                        # Se l'ID è un sourceId, cerca le info del source
                        source_year = json_data.get("@sourceYear", "Unknown Year")
                        source_first_author = json_data.get("@sourceFirstAuthor", "Unknown Author")

                        source_name = f"{source_first_author} ({source_year})"                        
                        return {
                            "key": key,
                            "unit_name": source_name,
                        }
                    elif key == "@classificationId":
                        # Se l'ID è un classificationId, cerca le info del classification
                        classification_system = json_data.get("classificationSystem", {}).get("#text", "Unknown")
                        classification_value = json_data.get("classificationValue", {}).get("#text", "Unknown")

                        classification_name = f"{classification_system} ({classification_value})"                        
                        return {
                            "key": key,
                            "unit_name": classification_name,
                        }
                    elif key == "@activityLinkId":
                        # Se l'ID è un activityLinkId, cerca le info del classification
                        activity_name = "Unknown"
                        return {
                            "key": key,
                            "unit_name": activity_name,
                        }
                    elif key == "@propertyId":
                        # Se l'ID è un propertyId, cerca le info del classification
                        property_name = json_data.get("name", {}).get("#text", "Unknown")
                        return {
                            "key": key,
                            "unit_name": property_name,
                        }
                
                    elif key == "@subcompartmentId":
                        # Se l'ID è un subcompartmentId, cerca il nome del compartment
                        subcompartment_name = json_data.get("subcompartment", {}).get("#text", "Unknown")
                        return {
                            "key": key,
                            "unit_name": subcompartment_name,
                        }
                    elif key == "@reviewerId":
                        # Se l'ID è un reviewerId, cerca il nome del reviewer
                        reviewer_name = json_data.get("@reviewerName", "Unknown")
                        return {
                            "key": key,
                            "unit_name": reviewer_name,
                        }
                    elif key == "@personId":
                        # Se l'ID è un personId, cerca il nome della persona
                        person_name = json_data.get("@personName", "Unknown")
                        return {
                            "key": key,
                            "unit_name": person_name,
                        }
                    return None  # Se non ci sono nomi associati
                elif isinstance(value, (dict, list)):
                    result = search(value, id_value)
                    if result:  # Se troviamo il risultato in una sotto-struttura
                        return result
        elif isinstance(json_data, list):
            for item in json_data:
                result = search(item, id_value)
                if result:  # Se troviamo il risultato in un oggetto della lista
                    return result
        return None  # Se non troviamo nulla

    for id_value in ids:
        result = search(json_data, id_value)
        if result:
            results[id_value] = result
        else:
            results[id_value] = "Not Found"  # Se non troviamo l'ID

    return results

# Carica il file JSON
json_file_path = "progetto mics/ecoinvent-3.10-cutoff-upr-15352.json"
try:
    with open(json_file_path, "r") as file:
        json_data = json.load(file)
except Exception as e:
    print(f"Errore nel caricamento del file JSON: {e}")
    json_data = {}

# Carica gli ID dal file di testo
id_file_path = "progetto mics/analisi id/output_id_counts_greater_than_one_UPR.txt"
ids_to_search = load_ids_from_file(id_file_path)

# Trova i testi associati agli ID nel JSON
id_texts = find_id_texts_in_json(json_data, ids_to_search)

# Scrivi i risultati in un file di output
output_file_path = "progetto mics/analisi id/output_id_texts_UPR.txt"
try:
    with open(output_file_path, "w") as output_file:
        for id_value, details in id_texts.items():
            if details != "Not Found":
                output_file.write(
                    f"ID: {id_value}, Key: {details['key']}, Value: {details['unit_name']}\n"
                )
            else:
                output_file.write(f"ID: {id_value}, Result: Not Found\n")
except Exception as e:
    print(f"Errore nel salvataggio del file di output: {e}")

print(f"Processo completato. Risultati salvati in '{output_file_path}'.")
