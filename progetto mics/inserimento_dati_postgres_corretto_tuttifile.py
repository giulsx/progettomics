import psycopg2
import json
import hashlib
import uuid
import os

# Configurazione della connessione al database PostgreSQL
DB_CONFIG = {
    "dbname": "ecoinvent",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

# Funzione per generare un elementaryExchangeId univoco
def generate_elementary_exchange_id(name, amount):
    hash_input = f"{name}-{amount}".encode('utf-8')
    hash_digest = hashlib.sha256(hash_input).hexdigest()
    return uuid.UUID(hash_digest[:32])

# Funzione per generare un intermediateExchangeId univoco
def generate_intermediate_exchange_id(name, amount):
    hash_input = f"{name}-{amount}".encode('utf-8')
    hash_digest = hashlib.sha256(hash_input).hexdigest()
    return uuid.UUID(hash_digest[:32])

# Funzione per generare un impactIndicatorId univoco
def generate_impact_indicator_id(impact_name, impact_category_name, impact_method_name, amount):
    hash_input = f"{impact_name}-{impact_category_name}-{impact_method_name}-{amount}".encode('utf-8')
    hash_digest = hashlib.sha256(hash_input).hexdigest()
    return uuid.UUID(hash_digest[:32])

# Funzione per verificare se un unitId esiste e, se non esiste, inserirlo
def check_and_insert_unit(cursor, unit_id, unit_name):
    cursor.execute("""
        SELECT COUNT(*) FROM Unit WHERE unitId = %s;
    """, (str(unit_id),))
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute("""
            INSERT INTO Unit (unitId, unitName) VALUES (%s, %s)
        """, (str(unit_id), unit_name))
        #print(f"UnitId {unit_id} e UnitName {unit_name} inseriti nella tabella Unit.")
    else:
        print(f"UnitId {unit_id} già esistente nella tabella Unit.")

# Funzione per verificare se un subcompartmentId esiste e, se non esiste, inserirlo
def check_and_insert_subcompartment(cursor, subcompartment_id, subcompartment, compartment):
    cursor.execute("""
        SELECT COUNT(*) FROM Subcompartment WHERE subcompartmentId = %s;
    """, (str(subcompartment_id),))
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute("""
            INSERT INTO Subcompartment (subcompartmentId, subcompartment, compartment) 
            VALUES (%s, %s, %s)
        """, (str(subcompartment_id), subcompartment, compartment))
        #print(f"SubcompartmentId {subcompartment_id} inserito nella tabella Subcompartment.")
    else:
        print(f"SubcompartmentId {subcompartment_id} già esistente nella tabella Subcompartment.")

import uuid

# Funzione per popolare la tabella ElementaryExchange 
def populate_elementary_exchange_table(cursor, activity_data):
    elementary_exchanges = activity_data.get("elementaryExchange", [])
    elementary_exchange_ids = []
    for exchange in elementary_exchanges:
        elementary_name = exchange.get("name", "")
        amount = exchange.get("@amount", "")
        unit_id = exchange.get("@unitId", "")
        unit_name = exchange.get("unitName", "")
        subcompartment_id = exchange.get("@subcompartmentId", "")
        subcompartment = exchange.get("subcompartment", "")
        compartment = exchange.get("compartment", "")       
        if elementary_name and amount and unit_id and unit_name and subcompartment_id:
            check_and_insert_unit(cursor, unit_id, unit_name)
            check_and_insert_subcompartment(cursor, subcompartment_id, subcompartment, compartment)          
            elementary_exchange_id = generate_elementary_exchange_id(elementary_name, amount)           
            cursor.execute(""" 
                SELECT COUNT(*) FROM ElementaryExchange 
                WHERE elementaryExchangeId = %s;
            """, (str(elementary_exchange_id),))
            count = cursor.fetchone()[0]           
            if count == 0:
                cursor.execute("""
                    INSERT INTO ElementaryExchange (
                        elementaryExchangeId, elementaryName, amount, modifiedElementary, 
                        subcompartmentId, unitId)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (str(elementary_exchange_id), elementary_name, amount, False, 
                      str(subcompartment_id), str(unit_id)))
                #print(f"ElementaryExchangeId {elementary_exchange_id} inserito con successo.")
                elementary_exchange_ids.append(str(elementary_exchange_id))
            else:
                #print(f"Elemento con name: {elementary_name} e amount: {amount} già esistente.")
                elementary_exchange_ids.append(str(elementary_exchange_id))
        else:
            print("Dati incompleti per l'inserimento in ElementaryExchange.")
    return elementary_exchange_ids

# Funzione per popolare la tabella IntermediateExchange e associare gli intermediateExchangeId all'attività
def populate_intermediate_exchange_table(cursor, activity_data, activity_id):
    intermediate_exchanges = activity_data.get("intermediateExchange", [])
    intermediate_exchange_ids = []

    # Inserisci il referenceProduct con riferimento a TRUE
    reference_product = activity_data.get("referenceProduct", {})
    if reference_product:
        intermediate_name = reference_product.get("name", "")
        amount = reference_product.get("@amount", "")
        unit_id = reference_product.get("@unitId", "")
        unit_name = reference_product.get("unitName", "")
        intermediate_exchange_id = generate_intermediate_exchange_id(intermediate_name, amount)
        intermediate_exchange = reference_product.get("@intermediateExchangeId", "")  # Usare quello dal file JSON
        activity_product_id = f"{activity_id}_{intermediate_exchange}"  # Creazione dell'activityId_productId

        check_and_insert_unit(cursor, unit_id, unit_name)

        if intermediate_name and amount and unit_id and unit_name and intermediate_exchange_id:
            cursor.execute(""" 
                SELECT COUNT(*) FROM IntermediateExchange 
                WHERE intermediateExchangeId = %s;
            """, (str(intermediate_exchange_id),))
            count = cursor.fetchone()[0]
            
            if count == 0:
                cursor.execute(""" 
                    INSERT INTO IntermediateExchange (
                        intermediateExchangeId, intermediateName, amount, modifiedIntermediate, 
                        activityId_productId, unitId)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (str(intermediate_exchange_id), intermediate_name, amount, False, 
                      str(activity_product_id), str(unit_id)))
                #print(f"ReferenceProduct {intermediate_exchange_id} inserito con successo.")
                intermediate_exchange_ids.append(str(intermediate_exchange_id))

            # Associare alla tabella di collegamento con referenceProduct = TRUE
            cursor.execute("""
                INSERT INTO Activity_IntermediateExchange (activityId, intermediateExchangeId, referenceProduct)
                VALUES (%s, %s, %s)
                ON CONFLICT (activityId, intermediateExchangeId) DO NOTHING;
            """, (str(activity_id), str(intermediate_exchange_id), True))
            #print(f"ReferenceProduct associato all'attività {activity_id}.")
    
    # Inserire gli altri intermediateExchange
    for exchange in intermediate_exchanges:
        intermediate_name = exchange.get("name", "")
        amount = exchange.get("@amount", "")
        unit_id = exchange.get("@unitId", "")
        unit_name = exchange.get("unitName", "")
        intermediate_exchange_id = generate_intermediate_exchange_id(intermediate_name, amount)
        activity_product_id = exchange.get("activityId_productId", "")

        if intermediate_name and amount and unit_id and unit_name and intermediate_exchange_id:
            check_and_insert_unit(cursor, unit_id, unit_name)
            
            cursor.execute(""" 
                SELECT COUNT(*) FROM IntermediateExchange 
                WHERE intermediateExchangeId = %s;
            """, (str(intermediate_exchange_id),))
            count = cursor.fetchone()[0]
            
            if count == 0:
                cursor.execute(""" 
                    INSERT INTO IntermediateExchange (
                        intermediateExchangeId, intermediateName, amount, modifiedIntermediate, 
                        activityId_productId, unitId)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (str(intermediate_exchange_id), intermediate_name, amount, False, 
                      str(activity_product_id), str(unit_id)))
                #print(f"IntermediateExchangeId {intermediate_exchange_id} inserito con successo.")
                intermediate_exchange_ids.append(str(intermediate_exchange_id))

                # Aggiungere nella tabella di associazione
                cursor.execute("""
                    INSERT INTO Activity_IntermediateExchange (activityId, intermediateExchangeId, referenceProduct)
                    VALUES (%s, %s, %s);
                """, (str(activity_id), str(intermediate_exchange_id), False))  # ReferenceProduct = FALSE
                #print(f"IntermediateExchange associato all'attività {activity_id}.")
            else:
                #print(f"Elemento con name: {intermediate_name} e amount: {amount} già esistente.")
                intermediate_exchange_ids.append(str(intermediate_exchange_id))
        else:
            print("Dati incompleti per l'inserimento in IntermediateExchange.")

    return intermediate_exchange_ids

# Funzione per inserire gli elementaryExchangeId nella tabella di associazione
def insert_elementary_exchange_to_activity_association(cursor, activity_id, elementary_exchange_ids):
    if not elementary_exchange_ids:
        print("Nessun elementaryExchangeId da associare.")
    else:
        for elementary_exchange_id in elementary_exchange_ids:
            # Verifica se l'associazione esiste già nella tabella Activity_ElementaryExchange
            cursor.execute("""
                SELECT COUNT(*) FROM Activity_ElementaryExchange 
                WHERE activityId = %s AND elementaryExchangeId = %s;
            """, (str(activity_id), str(elementary_exchange_id)))
            count = cursor.fetchone()[0]
            
            if count == 0:
                cursor.execute("""
                    INSERT INTO Activity_ElementaryExchange (activityId, elementaryExchangeId)
                    VALUES (%s, %s);
                """, (str(activity_id), str(elementary_exchange_id)))
                #print(f"Associato elementaryExchangeId {elementary_exchange_id} all'attività {activity_id}.")
            else:
                print(f"L'associazione tra ActivityId {activity_id} e ElementaryExchangeId {elementary_exchange_id} esiste già.")

# Funzione per inserire gli intermediateExchangeId nella tabella di associazione
def insert_intermediate_exchange_to_activity_association(cursor, activity_id, intermediate_exchange_ids):
    if not intermediate_exchange_ids:
        print("Nessun intermediateExchangeId da associare.")
    else:
        for intermediate_exchange_id in intermediate_exchange_ids:
            # Verifica se l'associazione esiste già nella tabella Activity_IntermediateExchange
            cursor.execute("""
                SELECT COUNT(*) FROM Activity_IntermediateExchange 
                WHERE activityId = %s AND intermediateExchangeId = %s;
            """, (str(activity_id), str(intermediate_exchange_id)))
            count = cursor.fetchone()[0]
            
            if count == 0:
                cursor.execute("""
                    INSERT INTO Activity_IntermediateExchange (activityId, intermediateExchangeId, referenceProduct)
                    VALUES (%s, %s, %s);
                """, (str(activity_id), str(intermediate_exchange_id), False))  # ReferenceProduct = FALSE
                #print(f"Associato intermediateExchangeId {intermediate_exchange_id} all'attività {activity_id}.")
            else:
                print(f"L'associazione tra ActivityId {activity_id} e IntermediateExchangeId {intermediate_exchange_id} esiste già.")

# Funzione per popolare la tabella ISICSection
def populate_isic_section_table(cursor, activity_data):
    isic_section = activity_data.get("ISICSection", "")
    isic_classification = activity_data.get("ISICClassification", "")
    sector = activity_data.get("sector", "")

    cursor.execute("""
        INSERT INTO ISICSection (ISICSection, ISICClassification, Sector)
        VALUES (%s, %s, %s)
        ON CONFLICT (ISICSection) DO NOTHING;
    """, (isic_section, isic_classification, sector))

# Funzione per popolare la tabella Activity
def populate_activity_table(cursor, activity_data):
    id_ = activity_data.get("@id", "")
    activity_name = activity_data.get("activityName", "")
    included_start = activity_data.get("includedActivitiesStart", "")
    included_end = activity_data.get("includedActivitiesEnd", "")
    geography = activity_data.get("geography", "")
    special_activity_type = activity_data.get("specialActivityType", "")
    general_comment = " ".join(activity_data.get("generalComment", []) or [])
    modified_activity = False
    isic_section = activity_data.get("ISICSection", "")
    system_model = activity_data.get("systemModel", "")
    
    cursor.execute("""
        INSERT INTO Activity (
            id,
            activityName,
            includedActivitiesStart,
            includedActivitiesEnd,
            geography,
            specialActivityType,
            generalComment,
            modifiedActivity,
            ISICSection,
            systemModel
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (id_, activity_name, included_start, included_end, geography, special_activity_type, general_comment, modified_activity, isic_section, system_model))

    #print(f"Attività con ID {id_} inserita con successo.")
    return id_


# Funzione per inserire gli impactIndicatorId nella tabella di associazione Activity_ImpactIndicator
def insert_impact_indicator_to_activity_association(cursor, activity_id, impact_indicator_ids):
    if not impact_indicator_ids:
        print("Nessun impactIndicatorId da associare.")
    else:
        for impact_indicator_id in impact_indicator_ids:
            # Verifica se l'associazione esiste già nella tabella Activity_ImpactIndicator
            cursor.execute("""
                SELECT COUNT(*) FROM Activity_ImpactIndicator 
                WHERE activityId = %s AND impactIndicatorId = %s;
            """, (str(activity_id), str(impact_indicator_id)))
            count = cursor.fetchone()[0]
            
            if count == 0:
                cursor.execute("""
                    INSERT INTO Activity_ImpactIndicator (activityId, impactIndicatorId)
                    VALUES (%s, %s);
                """, (str(activity_id), str(impact_indicator_id)))
                #print(f"Associato ImpactIndicatorId {impact_indicator_id} all'attività {activity_id}.")
            else:
                print(f"L'associazione tra ActivityId {activity_id} e ImpactIndicatorId {impact_indicator_id} esiste già.")

# Funzione per popolare la tabella ImpactIndicator
def populate_impact_indicator_table(cursor, json_data):
    impact_indicators = json_data.get("impact_indicators", [])
    impact_indicator_ids = []  # Lista per raccogliere gli ID degli indicatori di impatto
    for indicator in impact_indicators:
        impact_name = indicator.get("name", "")
        amount = indicator.get("@amount", None)
        impact_method_name = indicator.get("impactMethodName", "")
        impact_category_name = indicator.get("impactCategoryName", "")
        unit_name = indicator.get("unitName", "")

        if impact_name and impact_method_name and impact_category_name and unit_name and amount:
            # Genera l'impactIndicatorId
            impact_indicator_id = generate_impact_indicator_id(
                impact_name, impact_category_name, impact_method_name, amount
            )
            
            cursor.execute("""
                SELECT COUNT(*) FROM ImpactIndicator WHERE impactIndicatorId = %s;
            """, (str(impact_indicator_id),))
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute("""
                    INSERT INTO ImpactIndicator (
                        impactIndicatorId, impactName, amount, 
                        impactMethodName, impactCategoryName, unitName
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    str(impact_indicator_id), impact_name, amount,
                    impact_method_name, impact_category_name, unit_name
                ))
                #print(f"ImpactIndicatorId {impact_indicator_id} inserito con successo.")
            else:
                print(f"ImpactIndicatorId {impact_indicator_id} già esistente nella tabella ImpactIndicator.")
            
            impact_indicator_ids.append(impact_indicator_id)  # Aggiungi l'ID alla lista
        else:
            print("Dati incompleti per l'inserimento in ImpactIndicator.")   
    return impact_indicator_ids

def load_data_to_database_from_directory(directory_path, log_file_path):
    """
    Carica i dati da file JSON nel database PostgreSQL.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Connessione al database riuscita.")

        # Apri il file di log in modalità append
        with open(log_file_path, 'a') as log_file:
            # Itera sui file JSON nella cartella
            for filename in sorted(os.listdir(directory_path)):  # Ordina i file alfabeticamente
                if filename.endswith(".json"):  # Considera solo i file JSON
                    json_file_path = os.path.join(directory_path, filename)
                    
                    # Leggere i dati dal file JSON
                    with open(json_file_path, 'r', encoding='utf-8') as file:
                        json_data = json.load(file)

                    # Verifica che json_data sia un dizionario
                    if isinstance(json_data, dict):
                        print(f"Elaborazione del file: {filename}")

                        # Popolare le tabelle del database
                        populate_isic_section_table(cursor, json_data)
                        activity_id = populate_activity_table(cursor, json_data)
                        elementary_exchange_ids = populate_elementary_exchange_table(cursor, json_data)
                        insert_elementary_exchange_to_activity_association(cursor, activity_id, elementary_exchange_ids)
                        intermediate_exchange_ids = populate_intermediate_exchange_table(cursor, json_data, activity_id)
                        insert_intermediate_exchange_to_activity_association(cursor, activity_id, intermediate_exchange_ids)
                        impact_indicator_ids = populate_impact_indicator_table(cursor, json_data)
                        insert_impact_indicator_to_activity_association(cursor, activity_id, impact_indicator_ids)

                        # Conferma delle modifiche
                        conn.commit()

                        # Scrivi il file di log
                        log_file.write(f"{filename} caricato con successo.\n")

                    else:
                        print(f"Errore: Il file {filename} non è un oggetto JSON valido.")

    except (Exception, psycopg2.Error) as error:
        print("Errore durante il caricamento dei dati:", error)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Connessione al database chiusa.")

# Percorsi
directory_path = os.path.abspath("progetto mics/output copy")
log_file_path = os.path.abspath("progetto mics/caricamento_log.txt")

# Controlla se la directory esiste
if not os.path.isdir(directory_path):
    print(f"Errore: la directory '{directory_path}' non esiste.")
else:
    print(f"Avvio del caricamento dei file dalla directory: {directory_path}")
    load_data_to_database_from_directory(directory_path, log_file_path)
