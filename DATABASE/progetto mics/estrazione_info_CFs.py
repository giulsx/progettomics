import pandas as pd
import json

# Caricare il file Excel e il foglio CFs
file_path = 'progetto mics/LCIA Implementation 3.10.xlsx'
df = pd.read_excel(file_path, sheet_name='CFs')

# Selezionare le colonne di interesse
df_selected = df[['Method', 'Category', 'Indicator', 'Name', 'CF']]

# Rimuovere duplicati sulla combinazione "Method", "Indicator" e "Name"
df_unique = df_selected.drop_duplicates(subset=['Method', 'Indicator', 'Name'])

# Convertire il DataFrame in una lista di dizionari
cfs_list = df_unique.to_dict(orient='records')

# Salvare la lista in un file JSON
output_file = 'progetto mics/CFs.json'
with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(cfs_list, file, ensure_ascii=False, indent=2)

print(f"I dati sono stati salvati in {output_file} senza duplicati.")
