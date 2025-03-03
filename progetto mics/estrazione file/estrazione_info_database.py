import json

# Funzione per estrarre i dati dal file UPR
def extract_from_upr(upr_file):
    with open(upr_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Estrarre Activity Next
    activity = data['ecoSpold']['childActivityDataset']['activityDescription']['activity']
    activity_name = activity['activityName']['#text']
    
    # Estrarre Included Activities Start e End
    included_activities_start = activity['includedActivitiesStart']['#text']
    included_activities_end = activity['includedActivitiesEnd']['#text']
    
    # Estrarre General Comment
    general_comments = [comment['#text'] for comment in activity['generalComment']['text']]
    
    # Estrarre Intermediate Exchanges
    intermediate_exchanges = []
    for exchange in data['ecoSpold']['childActivityDataset']['flowData']['intermediateExchange']:
        intermediate_exchanges.append({
            '@intermediateExchangeId': exchange['@intermediateExchangeId'],
            'name': exchange['name']['#text'],
            '@amount': exchange['@amount'],
            'unitName': exchange['unitName']['#text']
        })
    
    # Estrarre Elementary Exchanges
    elementary_exchanges = []
    if 'elementaryExchange' in data['ecoSpold']['childActivityDataset']['flowData']:
        for exchange in data['ecoSpold']['childActivityDataset']['flowData']['elementaryExchange']:
            elementary_exchanges.append({
                '@elementaryExchangeId': exchange.get('@elementaryExchangeId', 'N/A'),
                'name': exchange['name']['#text'],
                '@amount': exchange['@amount'],
                'unitName': exchange['unitName']['#text'],
                '@subcompartmentId': exchange['compartment']['@subcompartmentId'] if 'compartment' in exchange else 'N/A',
                'compartment': exchange['compartment']['compartment']['#text'] if 'compartment' in exchange else 'N/A',
                'subcompartment': exchange['compartment']['subcompartment']['#text'] if 'compartment' in exchange else 'N/A'
            })
    
    return {
        'activityName': activity_name,
        'includedActivitiesStart': included_activities_start,
        'includedActivitiesEnd': included_activities_end,
        'generalComment': general_comments,
        'intermediateExchange': intermediate_exchanges,
        'elementaryExchange': elementary_exchanges
    }

# Funzione per estrarre i dati dal file LCIA
def extract_from_lcia(lcia_file):
    with open(lcia_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
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
            'unitName': indicator['unitName'] if 'unitName' in indicator else 'N/A'
        })
    
    return impact_indicators

# Funzione per scrivere i risultati in un file JSON (senza le chiavi 'upr_data' e 'lcia_data')
def write_to_json(upr_data, lcia_data, output_file):
    combined_data = {**upr_data, 'impact_indicators': lcia_data}
    
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(combined_data, file, ensure_ascii=False, indent=2)

# Esempio di utilizzo delle funzioni
upr_file = 'progetto mics/ecoinvent-3.10-cutoff-upr-15352.json'
lcia_file = 'progetto mics/ecoinvent-3.10-cutoff-lcia-15352.json'
output_file = 'progetto mics/output.json'

upr_data = extract_from_upr(upr_file)
lcia_data = extract_from_lcia(lcia_file)

# Scrivi i risultati in un file JSON
write_to_json(upr_data, lcia_data, output_file)

print(f"I dati estratti sono stati salvati in {output_file}")
