import json

# Questo codice permette di modificare le informazioni contenute in un file JSON LCI
# degli intermediate exchange, elementary exchange e i parametri

# Funzione per modificare un campo specifico
def modify_field(prompt, current_value):
    response = input(f"{prompt} (valore corrente: {current_value}): ")
    return response if response else current_value

# Funzione per modificare gli elementary exchanges
def modify_elementary_exchanges(elementary_exchanges):
    while True:
        exchange_id = input("Inserisci l'ID dell'elementary exchange da modificare: ")
        for exchange in elementary_exchanges:
            if isinstance(exchange, dict) and exchange.get("@id") == exchange_id:
                print(f"Modifica l'elementary exchange con ID {exchange_id}:")
                exchange["@elementaryExchangeId"] = modify_field("Elementary Exchange ID", exchange.get("@elementaryExchangeId", "N/A"))
                exchange["name"]["#text"] = modify_field("Nome", exchange.get("name", {}).get("#text", "N/A"))
                exchange["@amount"] = modify_field("Quantità", exchange.get("@amount", "N/A"))
                exchange["@unitId"] = modify_field("Unit ID", exchange.get("@unitId", "N/A"))
                exchange["unitName"]["#text"] = modify_field("Unità", exchange.get("unitName", {}).get("#text", "N/A"))
                
                # Modifica del comparto e sottocomparto
                compartment = exchange.get("compartment", {}).get("compartment", {}).get('#text', 'N/A')
                exchange["compartment"]["compartment"]["#text"] = modify_field("Comparto", compartment)
                subcompartment = exchange.get("compartment", {}).get("subcompartment", {}).get('#text', 'N/A')
                exchange["compartment"]["subcompartment"]["#text"] = modify_field("Sottocomparto", subcompartment)
                
                print("Modifica completata.")
                break
        else:
            print("ID non trovato.")
        
        another = input("Vuoi modificare un altro elementary exchange? (s/n): ").lower()
        if another != 's':
            break

# Funzione per modificare gli intermediate exchanges
def modify_intermediate_exchanges(intermediate_exchange):
    while True:
        exchange_id = input("Inserisci l'ID dell'intermediate exchange da modificare: ")
        if intermediate_exchange.get("@id") == exchange_id:
            print(f"Modifica l'intermediate exchange con ID {exchange_id}:")
            intermediate_exchange["name"]["#text"] = modify_field("Nome", intermediate_exchange.get("name", {}).get("#text", "N/A"))
            intermediate_exchange["@amount"] = modify_field("Quantità", intermediate_exchange.get("@amount", "N/A"))
            intermediate_exchange["@unitId"] = modify_field("Unit ID", intermediate_exchange.get("@unitId", "N/A"))
            intermediate_exchange["@productionVolumeAmount"] = modify_field("Volume di produzione", intermediate_exchange.get("@productionVolumeAmount", "N/A"))
            print("Modifica completata.")
        else:
            print("ID non trovato.")
        
        another = input("Vuoi modificare un altro intermediate exchange? (s/n): ").lower()
        if another != 's':
            break

# Funzione per modificare i parametri
def modify_parameters(parameters):
    while True:
        param_id = input("Inserisci l'ID del parametro da modificare: ")
        for param in parameters:
            if isinstance(param, dict) and param.get("@parameterId") == param_id:
                print(f"Modifica il parametro con ID {param_id}:")
                param["name"]["#text"] = modify_field("Nome", param.get("name", {}).get("#text", "N/A"))
                param["@variableName"] = modify_field("Nome della variabile", param.get("@variableName", "N/A"))
                param["@amount"] = modify_field("Quantità", param.get("@amount", "N/A"))
                param["@unitId"] = modify_field("Unit ID", param.get("@unitId", "N/A"))
                param["unitName"]["#text"] = modify_field("Unità", param.get("unitName", {}).get("#text", "N/A"))
                print("Modifica completata.")
                break
        else:
            print("ID non trovato.")
        
        another = input("Vuoi modificare un altro parametro? (s/n): ").lower()
        if another != 's':
            break

# Funzione principale per l'interazione con l'utente e la modifica dei dati
def main():
    # Caricamento del file JSON
    with open("progetto mics/ecoinvent-3.10-cutoff-lci-15352.json", "r") as file:
        data = json.load(file)

    child_activity = data.get("ecoSpold", {}).get("childActivityDataset", {})
    flow_data = child_activity.get("flowData", {})

    # Richiesta di modifiche sugli elementary exchanges
    if flow_data.get("elementaryExchange", []):
        modify_elementary = input("Vuoi modificare gli elementary exchanges? (s/n): ").lower()
        if modify_elementary == 's':
            modify_elementary_exchanges(flow_data["elementaryExchange"])

    # Richiesta di modifiche sugli intermediate exchanges
    intermediate_exchange = flow_data.get("intermediateExchange", {})
    if intermediate_exchange:
        modify_intermediate = input("Vuoi modificare gli intermediate exchanges? (s/n): ").lower()
        if modify_intermediate == 's':
            modify_intermediate_exchanges(intermediate_exchange)

    # Richiesta di modifiche sui parametri
    if flow_data.get("parameter", []):
        modify_params = input("Vuoi modificare i parametri? (s/n): ").lower()
        if modify_params == 's':
            modify_parameters(flow_data["parameter"])

    # Salvataggio delle modifiche nel file JSON
    with open("ecoinvent-3.10-cutoff-lci-15352_modificato.json", "w") as output_file:
        json.dump(data, output_file, indent=4)
    print("Modifiche salvate con successo nel file JSON.")

import json

# Funzione per modificare un campo specifico
def modify_field(prompt, current_value):
    response = input(f"{prompt} (valore corrente: {current_value}): ")
    return response if response else current_value

# Funzione per modificare gli elementary exchanges
def modify_elementary_exchanges(elementary_exchanges):
    while True:
        exchange_id = input("Inserisci l'ID dell'elementary exchange da modificare: ")
        found = False
        for exchange in elementary_exchanges:
            if isinstance(exchange, dict) and exchange.get("@id") == exchange_id:
                found = True
                print(f"Modifica l'elementary exchange con ID {exchange_id}:")
                exchange["@elementaryExchangeId"] = modify_field("Elementary Exchange ID", exchange.get("@elementaryExchangeId", "N/A"))
                exchange["name"]["#text"] = modify_field("Nome", exchange.get("name", {}).get("#text", "N/A"))
                exchange["@amount"] = modify_field("Quantità", exchange.get("@amount", "N/A"))
                exchange["@unitId"] = modify_field("Unit ID", exchange.get("@unitId", "N/A"))
                exchange["unitName"]["#text"] = modify_field("Unità", exchange.get("unitName", {}).get("#text", "N/A"))
                
                compartment = exchange.get("compartment", {}).get("compartment", {}).get('#text', 'N/A')
                exchange["compartment"]["compartment"]["#text"] = modify_field("Comparto", compartment)
                subcompartment = exchange.get("compartment", {}).get("subcompartment", {}).get('#text', 'N/A')
                exchange["compartment"]["subcompartment"]["#text"] = modify_field("Sottocomparto", subcompartment)
                
                print("Modifica completata.")
                break
        if not found:
            print("ID non trovato.")
        
        another = input("Vuoi modificare un altro elementary exchange? (s/n): ").lower()
        if another != 's':
            break

# Funzione per modificare gli intermediate exchanges
def modify_intermediate_exchanges(intermediate_exchange):
    while True:
        exchange_id = input("Inserisci l'ID dell'intermediate exchange da modificare: ")
        if intermediate_exchange.get("@id") == exchange_id:
            print(f"Modifica l'intermediate exchange con ID {exchange_id}:")
            intermediate_exchange["name"]["#text"] = modify_field("Nome", intermediate_exchange.get("name", {}).get("#text", "N/A"))
            intermediate_exchange["@amount"] = modify_field("Quantità", intermediate_exchange.get("@amount", "N/A"))
            intermediate_exchange["@unitId"] = modify_field("Unit ID", intermediate_exchange.get("@unitId", "N/A"))
            intermediate_exchange["@productionVolumeAmount"] = modify_field("Volume di produzione", intermediate_exchange.get("@productionVolumeAmount", "N/A"))
            print("Modifica completata.")
        else:
            print("ID non trovato.")
        
        another = input("Vuoi modificare un altro intermediate exchange? (s/n): ").lower()
        if another != 's':
            break

# Funzione per modificare i parametri
def modify_parameters(parameters):
    while True:
        param_id = input("Inserisci l'ID del parametro da modificare: ")
        found = False
        for param in parameters:
            if isinstance(param, dict) and param.get("@parameterId") == param_id:
                found = True
                print(f"Modifica il parametro con ID {param_id}:")
                param["name"]["#text"] = modify_field("Nome", param.get("name", {}).get("#text", "N/A"))
                param["@variableName"] = modify_field("Nome della variabile", param.get("@variableName", "N/A"))
                param["@amount"] = modify_field("Quantità", param.get("@amount", "N/A"))
                param["@unitId"] = modify_field("Unit ID", param.get("@unitId", "N/A"))
                param["unitName"]["#text"] = modify_field("Unità", param.get("unitName", {}).get("#text", "N/A"))
                print("Modifica completata.")
                break
        if not found:
            print("ID non trovato.")
        
        another = input("Vuoi modificare un altro parametro? (s/n): ").lower()
        if another != 's':
            break

# Funzione principale per l'interazione con l'utente e la modifica dei dati
def main():
    # Caricamento del file JSON
    with open("ecoinvent-3.10-cutoff-lci-15352.json", "r") as file:
        data = json.load(file)

    child_activity = data.get("ecoSpold", {}).get("childActivityDataset", {})
    flow_data = child_activity.get("flowData", {})

    # Richiesta di modifiche sugli elementary exchanges
    if flow_data.get("elementaryExchange"):
        modify_elementary = input("Vuoi modificare gli elementary exchanges? (s/n): ").lower()
        if modify_elementary == 's':
            modify_elementary_exchanges(flow_data["elementaryExchange"])

    # Richiesta di modifiche sugli intermediate exchanges
    intermediate_exchange = flow_data.get("intermediateExchange", {})
    if intermediate_exchange:
        modify_intermediate = input("Vuoi modificare l'intermediate exchange (s/n): ").lower()
        if modify_intermediate == 's':
            modify_intermediate_exchanges(intermediate_exchange)

    # Richiesta di modifiche sui parametri
    if flow_data.get("parameter"):
        modify_params = input("Vuoi modificare i parametri? (s/n): ").lower()
        if modify_params == 's':
            modify_parameters(flow_data["parameter"])

    # Salvataggio delle modifiche nel file JSON
    with open("progetto mics/analisi struttura file/ecoinvent-3.10-cutoff-lci-15352_modificato.json", "w") as output_file:
        json.dump(data, output_file, indent=4)
    print("Modifiche salvate con successo nel file JSON.")

if __name__ == "__main__":
    main()
