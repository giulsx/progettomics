import json

# Estrazione dei namespaces
def extract_namespaces(eco_spold):
    output = ["XML Namespaces:"]
    namespaces = eco_spold.get("@xmlns", "")
    xsi = eco_spold.get("@xmlns:xsi", "")
    schema_location = eco_spold.get("@xsi:schemaLocation", "")

    if namespaces:
        output.append(f"- xmlns: {namespaces}")
    if xsi:
        output.append(f"- xsi: {xsi}")
    if schema_location:
        output.append(f"- schemaLocation: {schema_location}")

    return "\n".join(output)

# Estrazione delle informazioni sull'attività
def extract_activity(activity_description):
    activity = activity_description.get("activity", {})
    output = ["Activity Description:"]
    output.append(f"- Special Activity Type: {activity.get('@specialActivityType', 'N/A')}")
    output.append(f"- Activity ID: {activity.get('@id', 'N/A')}")
    output.append(f"- Parent Activity ID: {activity.get('@parentActivityId', 'N/A')}")
    output.append(f"- Activity Name: {activity.get('activityName', {}).get('#text', 'N/A')}")
    output.append(f"- Included Activities Start: {activity.get('includedActivitiesStart', {}).get('#text', 'N/A')}")
    output.append(f"- Included Activities End: {activity.get('includedActivitiesEnd', {}).get('#text', 'N/A')}")

    # Commenti generali
    general_comment = activity.get("generalComment", {}).get("text", [])
    output.append("\nGeneral Comments:")
    output.extend([f"- {comment.get('#text', 'N/A')}" for comment in general_comment])

    return "\n".join(output)

# Estrazione della classificazione
def extract_classification(activity_description):
    classification = activity_description.get("classification", {})
    output = ["Classification:"]
    output.append(f"- Classification ID: {classification.get('@classificationId', 'N/A')}")
    output.append(f"- Classification System: {classification.get('classificationSystem', {}).get('#text', 'N/A')}")
    output.append(f"- Classification Value: {classification.get('classificationValue', {}).get('#text', 'N/A')}")

    return "\n".join(output)

# Estrazione della geografia
def extract_geography(activity_description):
    geography = activity_description.get("geography", {})
    output = ["Geography:"]
    output.append(f"- Geography ID: {geography.get('@geographyId', 'N/A')}")
    output.append(f"- Shortname: {geography.get('shortname', {}).get('#text', 'N/A')}")
    comment = geography.get("comment", {}).get("text", {}).get('#text', 'N/A')
    output.append(f"- Comment: {comment}")

    return "\n".join(output)

# Estrazione della tecnologia
def extract_technology(activity_description):
    technology = activity_description.get("technology", {})
    output = ["Technology:"]
    output.append(f"- Technology Level: {technology.get('@technologyLevel', 'N/A')}")
    tech_comment = technology.get("comment", {}).get("text", {}).get('#text', 'N/A')
    output.append(f"- Comment: {tech_comment}")

    return "\n".join(output)

# Estrazione del periodo temporale
def extract_time_period(activity_description):
    time_period = activity_description.get("timePeriod", {})
    output = ["Time Period:"]
    output.append(f"- Start Date: {time_period.get('@startDate', 'N/A')}")
    output.append(f"- End Date: {time_period.get('@endDate', 'N/A')}")
    output.append(f"- Data Valid for Entire Period: {time_period.get('@isDataValidForEntirePeriod', 'N/A')}")

    return "\n".join(output)

# Estrazione dello scenario macroeconomico
def extract_macro_economic_scenario(activity_description):
    macro_economic = activity_description.get("macroEconomicScenario", {})
    output = ["Macro-Economic Scenario:"]
    output.append(f"- Scenario ID: {macro_economic.get('@macroEconomicScenarioId', 'N/A')}")
    output.append(f"- Name: {macro_economic.get('name', {}).get('#text', 'N/A')}")

    return "\n".join(output)

# Estrazione delle proprietà del flusso
def extract_properties(properties):
    output = []
    for prop in properties:
        output.append(f"    - Property ID: {prop.get('@propertyId', 'N/A')}")
        output.append(f"      - Name: {prop.get('name', {}).get('#text', 'N/A')}")
        output.append(f"      - Amount: {prop.get('@amount', 'N/A')}")
        output.append(f"      - Unit ID: {prop.get('@unitId', 'N/A')}")
        output.append(f"      - Unit: {prop.get('unitName', {}).get('#text', 'N/A')}")
        comment = prop.get('comment', {}).get('#text', 'N/A')
        if comment != 'N/A':
            output.append(f"      - Comment: {comment}")
    return "\n".join(output)

# Estrazione delle incertezze
def extract_uncertainty(uncertainty):
    output = []
    if uncertainty:
        lognormal = uncertainty.get("lognormal", {})
        output.append(f"  - Lognormal Distribution:")
        output.append(f"    - Mean Value: {lognormal.get('@meanValue', 'N/A')}")
        output.append(f"    - Mu: {lognormal.get('@mu', 'N/A')}")
        output.append(f"    - Variance: {lognormal.get('@variance', 'N/A')}")
    return "\n".join(output)

# Estrazione dei dati di flusso intermedi
def extract_intermediate_exchange(intermediate_exchange):
    output = ["Intermediate Exchange Data:"]
    output.append(f"- Flow ID: {intermediate_exchange.get('@id', 'N/A')}")
    output.append(f"  - Name: {intermediate_exchange.get('name', {}).get('#text', 'N/A')}")
    output.append(f"  - Amount: {intermediate_exchange.get('@amount', 'N/A')}")
    output.append(f"  - Unit: {intermediate_exchange.get('unitName', {}).get('#text', 'N/A')}")
    output.append(f"  - Production Volume: {intermediate_exchange.get('@productionVolumeAmount', 'N/A')}")
    
    # Estrazione delle proprietà
    properties = intermediate_exchange.get("property", [])
    if properties:
        output.append(f"  - Properties:")
        output.append(extract_properties(properties))

    # Estrazione delle incertezze
    uncertainty = intermediate_exchange.get("uncertainty", {})
    if uncertainty:
        output.append(extract_uncertainty(uncertainty))

    return "\n".join(output)

# Estrazione dei parametri
def extract_parameters(parameters):
    output = ["Parameters:"]
    for param in parameters:
        output.append(f"    - Parameter ID: {param.get('@parameterId', 'N/A')}")
        output.append(f"       - Name: {param.get('name', {}).get('#text', 'N/A')}")
        output.append(f"       - Variable Name: {param.get('@variableName', 'N/A')}")
        output.append(f"       - Amount: {param.get('@amount', 'N/A')}")
        output.append(f"       - Unit ID: {param.get('@unitId', 'N/A')}")
        output.append(f"       - Unit: {param.get('unitName', {}).get('#text', 'N/A')}")
    return "\n".join(output)

# Estrazione degli impactIndicator
def extract_impact_indicators(impact_indicators):
    output = ["Impact Indicators:"]
    for indicator in impact_indicators:
        output.append(f"    - Impact Indicator ID: {indicator.get('@impactIndicatorId', 'N/A')}")
        output.append(f"      - Name: {indicator.get('name', 'N/A')}")
        output.append(f"      - Impact Method ID: {indicator.get('@impactMethodId', 'N/A')}")
        output.append(f"      - Impact Method: {indicator.get('impactMethodName', 'N/A')}")
        output.append(f"      - Impact Category ID: {indicator.get('@impactCategoryId', 'N/A')}")
        output.append(f"      - Impact Category: {indicator.get('impactCategoryName', 'N/A')}")
        output.append(f"      - Amount: {indicator.get('@amount', 'N/A')}")
        output.append(f"      - Unit: {indicator.get('unitName', 'N/A')}")
    return "\n".join(output)

# Funzione principale per l'estrazione delle informazioni
def extract_info(data):
    output = []

    eco_spold = data.get("ecoSpold", {})
    output.append(extract_namespaces(eco_spold))

    child_activity = eco_spold.get("childActivityDataset", {})
    if child_activity:
        activity_description = child_activity.get("activityDescription", {})
        output.append(extract_activity(activity_description))
        output.append(extract_classification(activity_description))
        output.append(extract_geography(activity_description))
        output.append(extract_technology(activity_description))
        output.append(extract_time_period(activity_description))
        output.append(extract_macro_economic_scenario(activity_description))

        # Estrazione dei flussi intermedi
        intermediate_exchange = child_activity.get("flowData", {}).get("intermediateExchange", {})
        output.append(extract_intermediate_exchange(intermediate_exchange))

        # Estrazione dei parametri
        parameters = child_activity.get("flowData", {}).get("parameter", [])
        if parameters:
            output.append(extract_parameters(parameters))

        # Estrazione degli impact indicator
        impact_indicators = child_activity.get("flowData", {}).get("impactIndicator", [])
        if impact_indicators:
            output.append(extract_impact_indicators(impact_indicators))

    return "\n".join(output)

def main():
    with open("progetto mics/ecoinvent-3.10-cutoff-lcia-15352.json", "r") as file:
        data = json.load(file)

    formatted_output = extract_info(data)

    with open("progetto mics/analisi struttura file/extracted_info_lcia.txt", "w") as output_file:
        output_file.write(formatted_output)

if __name__ == "__main__":
    main()
