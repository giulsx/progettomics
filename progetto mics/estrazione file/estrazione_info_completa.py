from ecoinvent_interface import EcoinventProcess, Settings, ProcessFileType
from pathlib import Path
import xmltodict
import json
import pandas as pd
import numpy as np 

# LOGIN
my_settings = Settings(username="precon13329", password="Dtm_2024")

# Set VERSIONE
ep = EcoinventProcess(my_settings)
ep.set_release(version="3.10", system_model="cutoff")

# Selezione processo
ep.select_process(dataset_id="15352")

# Download file LCIA e UPR
file_upr = ep.get_file(file_type=ProcessFileType.upr, directory=Path.cwd())
file_lcia = ep.get_file(file_type=ProcessFileType.lcia, directory=Path.cwd())

# CONVERSIONE XML-JSON

# Conversione file LCIA
with open(file_lcia, 'r', encoding='utf-8') as xml_file:
    xml_content = xml_file.read()

json_data_lcia = xmltodict.parse(xml_content)

with open('progetto mics/file_lcia.json', 'w', encoding='utf-8') as json_file:
     json.dump(json_data_lcia, json_file, indent=4)

# Conversione file UPR
with open(file_upr, 'r', encoding='utf-8') as xml_file:
    xml_content = xml_file.read()

json_data_upr = xmltodict.parse(xml_content)

with open('progetto mics/file_upr.json', 'w', encoding='utf-8') as json_file:
     json.dump(json_data_upr, json_file, indent=4)

# ESTRAZIONE INFORMAZIONI

# Funzione per estrarre i dati dal file UPR
def extract_from_upr(upr_data):
    data = upr_data
    
    # Estrarre Activity Next
    activity = data['ecoSpold']['childActivityDataset']['activityDescription']['activity']
    activity_id = activity['@id']
    activity_name = activity['activityName']['#text']
    
    # Estrarre Included Activities Start e End
    included_activities_start = activity['includedActivitiesStart']['#text'] if activity.get('includedActivitiesStart') and activity['includedActivitiesStart'].get('#text') else "null"
    included_activities_end = activity['includedActivitiesEnd']['#text'] if activity.get('includedActivitiesEnd') and activity['includedActivitiesEnd'].get('#text') else "null"
    
    # Estrarre Geografia
    geography = data['ecoSpold']['childActivityDataset']['activityDescription']['geography']['shortname']['#text']

    # Estrazione Classification 
    classification_value = None
    if isinstance(data['ecoSpold']['childActivityDataset']['activityDescription']['classification'], dict):
        classification_value = data['ecoSpold']['childActivityDataset']['activityDescription']['classification']['classificationValue']['#text']
    elif isinstance(data['ecoSpold']['childActivityDataset']['activityDescription']['classification'], list):
        classification_value = data['ecoSpold']['childActivityDataset']['activityDescription']['classification'][0]['classificationValue']['#text']
    
    # Estrarre Classification aggiuntive dal file Excel
    file_path = 'progetto mics/Database-Overview-for-ecoinvent-v3.10_29.04.24.xlsx'
    df = pd.read_excel(file_path, sheet_name='Cut-Off AO')
    filtered_row = df[df['Activity UUID'] == activity_id]
    
    special_activity_type = filtered_row['Special Activity Type'].values[0] if len(filtered_row['Special Activity Type'].values) > 0 else "null"
    sector = filtered_row['Sector'].values[0] if len(filtered_row['Sector'].values) > 0 else "null"
    isic_classification = filtered_row['ISIC Classification'].values[0] if len(filtered_row['ISIC Classification'].values) > 0 else "null"
    isic_section = filtered_row['ISIC Section'].values[0] if len(filtered_row['ISIC Section'].values) > 0 else "null"

    # Estrarre General Comment
    general_comments = []
    general_comment_texts = activity['generalComment']['text']
    if isinstance(general_comment_texts, dict):
        if '#text' in general_comment_texts:
            general_comments.append(general_comment_texts['#text'])
    elif isinstance(general_comment_texts, list):
        general_comments = [comment['#text'] for comment in general_comment_texts if '#text' in comment]

    # Estrarre Intermediate Exchanges e Reference Product completo
    intermediate_exchanges = []
    reference_product = None
    intermediate_exchange_data = data['ecoSpold']['childActivityDataset']['flowData']['intermediateExchange']

    if isinstance(intermediate_exchange_data, list) and intermediate_exchange_data:
        # Il primo elemento è il reference_product
        reference_product = {
            '@intermediateExchangeId': intermediate_exchange_data[0]['@intermediateExchangeId'],
            'name': intermediate_exchange_data[0]['name']['#text'],
            '@amount': intermediate_exchange_data[0]['@amount'],
            'unitName': intermediate_exchange_data[0]['unitName']['#text']
        }
        # Tutti gli altri elementi sono intermediate exchanges
        for exchange in intermediate_exchange_data[1:]:
            activity_id_product_id = f"{exchange.get('@activityLinkId', 'null')}_{exchange['@intermediateExchangeId']}"  # Creazione activityId_productId
            intermediate_exchanges.append({
                '@intermediateExchangeId': exchange['@intermediateExchangeId'],
                'name': exchange['name']['#text'],
                '@amount': exchange['@amount'],
                'unitName': exchange['unitName']['#text'],
                'activityId_productId': activity_id_product_id  # Aggiunto campo
            })
    elif isinstance(intermediate_exchange_data, dict):
        # Caso in cui esiste un solo intermediate exchange che è anche il reference product
        activity_id_product_id = f"{intermediate_exchange_data.get('@activityLinkId', 'null')}_{intermediate_exchange_data['@intermediateExchangeId']}"
        reference_product = {
            '@intermediateExchangeId': intermediate_exchange_data['@intermediateExchangeId'],
            'name': intermediate_exchange_data['name']['#text'],
            '@amount': intermediate_exchange_data['@amount'],
            'unitName': intermediate_exchange_data['unitName']['#text'],
            'activityId_productId': activity_id_product_id  # Aggiunto campo
        }

    # Estrarre Elementary Exchanges
    elementary_exchanges = []
    if 'elementaryExchange' in data['ecoSpold']['childActivityDataset']['flowData']:
        for exchange in data['ecoSpold']['childActivityDataset']['flowData']['elementaryExchange']:
            elementary_exchanges.append({
                '@elementaryExchangeId': exchange.get('@elementaryExchangeId', 'null'),
                'name': exchange['name']['#text'],
                '@amount': exchange['@amount'],
                'unitName': exchange['unitName']['#text'],
                '@subcompartmentId': exchange['compartment']['@subcompartmentId'] if 'compartment' in exchange else 'null',
                'compartment': exchange['compartment']['compartment']['#text'] if 'compartment' in exchange else 'null',
                'subcompartment': exchange['compartment']['subcompartment']['#text'] if 'compartment' in exchange else 'null'
            })

    return {
        'activityName': activity_name,
        '@id': activity_id,
        'includedActivitiesStart': included_activities_start,
        'includedActivitiesEnd': included_activities_end,
        'referenceProduct': reference_product,  # Contiene tutte le info del reference product
        'geography': geography,
        'specialActivityType': special_activity_type,
        #'classificationValue': classification_value,
        'sector': sector,
        'ISICClassification': isic_classification,
        'ISICSection': isic_section,
        'generalComment': general_comments,
        'intermediateExchange': intermediate_exchanges,
        'elementaryExchange': elementary_exchanges
    }


# Funzione per estrarre i dati dal file LCIA
def extract_from_lcia(lcia_data):
    data = lcia_data
    
    # Estrarre Impact Indicators
    impact_indicators = []
    for indicator in data['ecoSpold']['childActivityDataset']['flowData'].get('impactIndicator', []):
        impact_indicators.append({
            '@impactIndicatorId': indicator['@impactIndicatorId'],
            '@impactMethodId': indicator['@impactMethodId'],
            '@impactCategoryId': indicator['@impactCategoryId'],
            '@amount': indicator['@amount'],
            'impactMethodName': indicator['impactMethodName'],
            'impactCategoryName': indicator['impactCategoryName'],
            'name': indicator['name'],           
            'unitName': indicator['unitName'] if 'unitName' in indicator else 'null'
        })
    
    return impact_indicators

# Funzione per scrivere i risultati in un file JSON
def write_to_json(upr_data, lcia_data, output_file):
    combined_data = {**upr_data, 'impact_indicators': lcia_data}
    
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(combined_data, file, ensure_ascii=False, indent=2)

# Esempio di utilizzo delle funzioni
upr_data = json_data_upr
lcia_data = json_data_lcia
output_file = 'progetto mics/output.json'

# Estrarre i dati direttamente dai dizionari JSON
upr_extracted_data = extract_from_upr(upr_data)
lcia_extracted_data = extract_from_lcia(lcia_data)

# Scrivi i risultati in un file JSON
write_to_json(upr_extracted_data, lcia_extracted_data, output_file)

print(f"I dati estratti sono stati salvati in {output_file}")
