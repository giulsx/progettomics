import pandas as pd
import json

# Caricare il file Excel
file_path = 'progetto mics/LCIA Implementation 3.10.xlsx'

# Caricare il foglio CFs
df_cfs = pd.read_excel(file_path, sheet_name='CFs')

# Selezionare le colonne di interesse dal foglio CFs
df_cfs_selected = df_cfs[['Method', 'Category', 'Indicator', 'Name', 'CF']]

# Rimuovere duplicati sulla combinazione "Method", "Indicator" e "Name"
df_cfs_unique = df_cfs_selected.drop_duplicates(subset=['Method', 'Indicator', 'Name'])

# Caricare il foglio Indicators
df_indicators = pd.read_excel(file_path, sheet_name='Indicators')

# Selezionare le colonne di interesse dal foglio Indicators
df_indicators_selected = df_indicators[['Method', 'Category', 'Indicator', 'Indicator Unit']]

# Unire i due DataFrame sulla base delle colonne "Method", "Category" e "Indicator"
df_merged = pd.merge(df_cfs_unique, df_indicators_selected, on=['Method', 'Category', 'Indicator'], how='left')

# Rimuovere duplicati nel DataFrame unito (nel caso in cui ci siano combinazioni duplicate)
df_merged_unique = df_merged.drop_duplicates(subset=['Method', 'Category', 'Indicator', 'Name'])

# Convertire il DataFrame unito e senza duplicati in una lista di dizionari
cfs_list = df_merged_unique.to_dict(orient='records')

# Salvare la lista in un file JSON
output_file = 'progetto mics/CFs_with_units_unique.json'
with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(cfs_list, file, ensure_ascii=False, indent=2)

print(f"I dati con le unità di misura senza duplicati sono stati salvati in {output_file}.")
