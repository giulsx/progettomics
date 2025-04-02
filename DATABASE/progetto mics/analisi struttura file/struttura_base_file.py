import json

# Funzione per estrarre la struttura delle chiavi
def recursive_extract_structure(data, indent_level=0):
    output = []
    indent = "    " * indent_level  # Indentazione per rappresentare i livelli di annidamento

    if isinstance(data, dict):
        for key in data.keys():
            output.append(f"{indent}- Key: '{key}'")
            # Estrai la struttura ricorsivamente
            output.extend(recursive_extract_structure(data[key], indent_level + 1))
    elif isinstance(data, list):
        # Mostriamo solo il primo elemento della lista e il numero totale di elementi
        if len(data) > 0:
            output.append(f"{indent}- List of {len(data)} items")
            # Estrai solo la struttura del primo elemento
            output.extend(recursive_extract_structure(data[0], indent_level + 1))

    return output

# Funzione principale per estrarre la struttura unica
def extract_structure(data):
    output = ["Base JSON Structure (No Duplicates):\n"]
    output.extend(recursive_extract_structure(data))
    return "\n".join(output)

def main():
    # Carica il file JSON
    with open("progetto mics/ecoinvent-3.10-cutoff-upr-15352.json", "r") as file:
        data = json.load(file)

    # Estrai la struttura unica delle chiavi
    extracted_structure = extract_structure(data)

    # Scrivi le informazioni estratte in un file di testo
    with open("progetto mics/analisi struttura file/struttura_base_UPR.txt", "w") as output_file:
        output_file.write(extracted_structure)

    print("Il file è stato creato con la struttura base del JSON.")

if __name__ == "__main__":
    main()
