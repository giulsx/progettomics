import pandas as pd
import json

# Percorso del file Excel
file_path = 'progetto mics/APOS Cumulative LCIA v3.10.xlsx'

# Leggere manualmente le prime righe per estrarre Method, Category e Indicator
header_data = pd.read_excel(file_path, sheet_name='LCIA', nrows=3, header=None)

# Riga 1: Method, Riga 2: Category, Riga 3: Indicator
method_row = header_data.iloc[0, :]
category_row = header_data.iloc[1, :]
indicator_row = header_data.iloc[2, :]

# Leggere i dati delle attività a partire dalla quarta riga
data_start_row = 3
activity_data = pd.read_excel(file_path, sheet_name='LCIA', header=data_start_row)

# Identificare le colonne numeriche (dati degli impatti)
impact_columns = activity_data.columns[6:]  # Colonne dalla settima in poi (kg SO2-Eq, ecc.)

# Creare un DataFrame con le informazioni sugli impatti
impact_info = pd.DataFrame({
    'Method': method_row[6:],      # Metodi corrispondenti
    'Category': category_row[6:],  # Categorie corrispondenti
    'Indicator': indicator_row[6:],  # Indicatori corrispondenti
    'Column': impact_columns        # Colonne dei dati numerici
})

# Prepara i dati finali combinando le informazioni sugli impatti
df_selected = activity_data.iloc[:, :6].copy()  # Copia solo le prime 6 colonne (UUID, Name, Geography, ecc.)

# Creare una colonna con gli impatti dettagliati
df_selected['Impacts'] = activity_data[impact_columns].apply(
    lambda row: [
        {
            'Method': impact_info.iloc[i]['Method'],
            'Category': impact_info.iloc[i]['Category'],
            'Indicator': impact_info.iloc[i]['Indicator'],
            'Unit': impact_info.iloc[i]['Column'],  # Nome della colonna come unità (es. "kg CO2-Eq")
            'Value': row.iloc[i]  # Usare row.iloc[i] invece di row[i] per evitare FutureWarning
        } for i in range(len(impact_columns))
    ], axis=1
)

# Convertire il risultato finale in una lista di dizionari
df_selected_dict = df_selected.to_dict(orient='records')

# Salvare il risultato in un file JSON
output_file = 'progetto mics/impatti_unitari_completi_APOS.json'
with open(output_file, 'w', encoding='utf-8') as file:
    json.dump(df_selected_dict, file, ensure_ascii=False, indent=2)

print(f"I dati sono stati salvati in {output_file}")
