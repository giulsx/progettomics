import xmltodict
import json

# Leggi il file XML con codifica UTF-8
with open('ecoinvent-3.10-cutoff-lcia-15352.xml', 'r', encoding='utf-8') as xml_file:
    xml_content = xml_file.read()

# Converte l'XML in un dizionario
json_data = xmltodict.parse(xml_content)

# Converte il dizionario in JSON e lo salva in un file
with open('ecoinvent-3.10-cutoff-lcia-15352.json', 'w', encoding='utf-8') as json_file:
    json.dump(json_data, json_file, indent=4)

print("Conversione completata: file.json generato")



