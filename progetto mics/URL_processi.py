import pandas as pd
import json

# Percorso del file Excel e nome del foglio
file_path = 'progetto mics/Database-Overview-for-ecoinvent-v3.10_29.04.24.xlsx'
sheet_name = 'Cut-Off AO'

# Carica il foglio specificato e seleziona la colonna "ecoQuery URL"
df = pd.read_excel(file_path, sheet_name=sheet_name)
ecoquery_urls = df['ecoQuery URL'].dropna().tolist()  # Rimuove eventuali valori NaN e converte in lista

# Scrive la lista su un file JSON
output_file = 'progetto mics/ecoquery_urls.json'
with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(ecoquery_urls, file, ensure_ascii=False, indent=2)

print(f"I URL ecoQuery sono stati salvati in {output_file}")
