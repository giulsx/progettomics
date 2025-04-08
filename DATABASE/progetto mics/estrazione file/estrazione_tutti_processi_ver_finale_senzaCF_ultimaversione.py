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
system_model="cutoff"

# Leggi la lista di URL dal file JSON
with open('progetto mics/ecoquery_urls.json', 'r', encoding='utf-8') as file:
    urls = json.load(file)

# Crea la cartella di output
output_dir = Path('progetto mics/output')
output_dir.mkdir(parents=True, exist_ok=True)

# Crea il file di log per tracciare le URL utilizzate
log_file_path = output_dir / "processed_urls_log.txt"
with open(log_file_path, 'w', encoding='utf-8') as log_file:
    log_file.write("Log di URL processati:\n")

# Funzione per estrarre i dati dal file UPR
def extract_from_upr(upr_data):
    data = upr_data
    # Controlla se esiste 'childActivityDataset' o 'activityDataset'
    activity_dataset = data['ecoSpold'].get('childActivityDataset', data['ecoSpold'].get('activityDataset', None))
    
    if activity_dataset is None:
        raise KeyError("Né 'childActivityDataset' né 'activityDataset' trovati nei dati forniti.")
    
    activity = activity_dataset['activityDescription']['activity']
    activity_id = activity['@id']
    activity_name = activity['activityName']['#text']

    included_activities_start = activity['includedActivitiesStart']['#text'] if activity.get('includedActivitiesStart') and activity['includedActivitiesStart'].get('#text') else "null"
    included_activities_end = activity['includedActivitiesEnd']['#text'] if activity.get('includedActivitiesEnd') and activity['includedActivitiesEnd'].get('#text') else "null"
    geography = activity_dataset['activityDescription']['geography']['shortname']['#text']

    file_path = 'progetto mics/Database-Overview-for-ecoinvent-v3.10_29.04.24.xlsx'
    sheet_name = "Cut-Off AO" if system_model.lower() == "cutoff" else "APOS AO"
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    filtered_row = df[df['Activity UUID'] == activity_id]
    special_activity_type = filtered_row['Special Activity Type'].values[0] if len(filtered_row['Special Activity Type'].values) > 0 else "null"
    sector = filtered_row['Sector'].values[0] if len(filtered_row['Sector'].values) > 0 else "null"
    isic_classification = filtered_row['ISIC Classification'].values[0] if len(filtered_row['ISIC Classification'].values) > 0 else "null"
    isic_section = filtered_row['ISIC Section'].values[0] if len(filtered_row['ISIC Section'].values) > 0 else "null"

# Estrarre Commenti Generali
    general_comments = []

# Controlla se 'generalComment' esiste e se contiene effettivamente un oggetto valido
    if 'generalComment' in activity and isinstance(activity['generalComment'], dict):
        general_comment_texts = activity['generalComment'].get('text', None)
    
    # Se 'text' esiste e contiene dati validi
        if general_comment_texts is not None:
        # Se 'text' è un dizionario e contiene '#text'
            if isinstance(general_comment_texts, dict) and '#text' in general_comment_texts:
                general_comments.append(general_comment_texts['#text'])
        # Se 'text' è una lista, estrai tutti i commenti
            elif isinstance(general_comment_texts, list):
                general_comments = [comment['#text'] for comment in general_comment_texts if isinstance(comment, dict) and '#text' in comment]
    else:
    # Se 'generalComment' non esiste o non contiene un oggetto valido, restituisci None o una lista vuota
        general_comments = None


    # Estrarre Intermediate Exchanges con @unitId e activityId_productId
    intermediate_exchanges = []
    reference_product = None
    intermediate_exchange_data = activity_dataset['flowData']['intermediateExchange']
    if isinstance(intermediate_exchange_data, list) and intermediate_exchange_data:
        reference_product = {
            '@intermediateExchangeId': intermediate_exchange_data[0]['@intermediateExchangeId'],
            'name': intermediate_exchange_data[0]['name']['#text'],
            '@amount': intermediate_exchange_data[0]['@amount'],
            'unitName': intermediate_exchange_data[0]['unitName']['#text'],
            '@unitId': intermediate_exchange_data[0].get('@unitId', 'null')  
        }
        for exchange in intermediate_exchange_data[1:]:
            activity_id_product_id = f"{exchange.get('@activityLinkId', 'null')}_{exchange['@intermediateExchangeId']}"
            intermediate_exchanges.append({
                '@intermediateExchangeId': exchange['@intermediateExchangeId'],
                'name': exchange['name']['#text'],
                '@amount': exchange['@amount'],
                'unitName': exchange['unitName']['#text'],
                '@unitId': exchange.get('@unitId', 'null'),
                'activityId_productId': activity_id_product_id
            })
    elif isinstance(intermediate_exchange_data, dict):
        activity_id_product_id = f"{intermediate_exchange_data.get('@activityLinkId', 'null')}_{intermediate_exchange_data['@intermediateExchangeId']}"
        reference_product = {
            '@intermediateExchangeId': intermediate_exchange_data['@intermediateExchangeId'],
            'name': intermediate_exchange_data['name']['#text'],
            '@amount': intermediate_exchange_data['@amount'],
            'unitName': intermediate_exchange_data['unitName']['#text'],
            '@unitId': intermediate_exchange_data.get('@unitId', 'null'),
            'activityId_productId': activity_id_product_id
        }

    # Estrarre Elementary Exchanges 
    elementary_exchanges = []
    elementary_exchange_data = activity_dataset['flowData'].get('elementaryExchange', [])
    if isinstance(elementary_exchange_data, dict):
        elementary_exchange_data = [elementary_exchange_data]
    for exchange in elementary_exchange_data:
        exchange_name = exchange['name']['#text'] if isinstance(exchange['name'], dict) else exchange['name']
        unit_name = exchange['unitName']['#text'] if isinstance(exchange['unitName'], dict) else exchange['unitName']
        elementary_exchanges.append({
            '@elementaryExchangeId': exchange.get('@elementaryExchangeId', 'null'),
            'name': exchange_name,
            '@amount': exchange.get('@amount', 'null'),
            'unitName': unit_name,
            '@unitId': exchange.get('@unitId', 'null'),
            '@subcompartmentId': exchange.get('compartment', {}).get('@subcompartmentId', 'null') if 'compartment' in exchange else 'null',
            'compartment': exchange.get('compartment', {}).get('compartment', {}).get('#text', 'null') if 'compartment' in exchange and isinstance(exchange['compartment'], dict) else 'null',
            'subcompartment': exchange.get('compartment', {}).get('subcompartment', {}).get('#text', 'null') if 'compartment' in exchange and isinstance(exchange['compartment'], dict) else 'null',
        })

    return {
        'systemModel': system_model,
        'activityName': activity_name,
        '@id': activity_id,
        'includedActivitiesStart': included_activities_start,
        'includedActivitiesEnd': included_activities_end,
        'referenceProduct': reference_product,
        'geography': geography,
        'specialActivityType': special_activity_type,
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
    impact_indicators = []

    # Controlla prima 'childActivityDataset', se non esiste usa 'activityDataset'
    dataset = data['ecoSpold'].get('childActivityDataset', data['ecoSpold'].get('activityDataset', {}))

    for indicator in dataset.get('flowData', {}).get('impactIndicator', []):
        impact_indicators.append({
            '@impactIndicatorId': indicator.get('@impactIndicatorId', 'null'),
            # '@impactMethodId': indicator.get('@impactMethodId', 'null'),
            # '@impactCategoryId': indicator.get('@impactCategoryId', 'null'),
            '@amount': indicator.get('@amount', 'null'),
            'impactMethodName': indicator.get('impactMethodName', 'null'),
            'impactCategoryName': indicator.get('impactCategoryName', 'null'),
            'name': indicator.get('name', 'null'),
            'unitName': indicator.get('unitName', 'null')
        })

    return impact_indicators

# Funzione per scrivere i risultati in un file JSON
def write_to_json(upr_data, lcia_data, output_file):
    upr_extracted_data = extract_from_upr(upr_data)
    lcia_extracted_data = extract_from_lcia(lcia_data)
    combined_data = {**upr_extracted_data, 'impact_indicators': lcia_extracted_data}
    
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(combined_data, file, ensure_ascii=False, indent=2)

# Itera su ogni URL per estrarre il numero del dataset e processare i dati
for url in urls:
    # Estrai l'ID del dataset dall'URL
    dataset_id = url.split('/dataset/')[1].split('/')[0]
    
    # Seleziona il processo con l'ID estratto
    ep.select_process(dataset_id=dataset_id)

    # Scarica i file LCIA e UPR
    file_upr = ep.get_file(file_type=ProcessFileType.upr, directory=Path.cwd())
    file_lcia = ep.get_file(file_type=ProcessFileType.lcia, directory=Path.cwd())

    # Converti i file XML in JSON
    with open(file_upr, 'r', encoding='utf-8') as xml_file:
        json_data_upr = xmltodict.parse(xml_file.read())
    
    with open(file_lcia, 'r', encoding='utf-8') as xml_file:
        json_data_lcia = xmltodict.parse(xml_file.read())

    # Definisci il nome del file di output
    output_file = output_dir / f"output_{dataset_id}.json"

    # Scrivi i dati estratti nel file JSON
    write_to_json(json_data_upr, json_data_lcia, output_file)

    # Scrivi l'URL nel file di log
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"{url}\n")

    print(f"Dati estratti per il dataset {dataset_id} e salvati in {output_file}. URL registrato in {log_file_path}")
