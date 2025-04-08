import json
import psycopg2
import os

# Configurazione della connessione al database PostgreSQL
DB_CONFIG = {
    "dbname": "ecoinvent",  # Nome del database
    "user": "postgres",     # Utente del database
    "password": "postgres", # Password del database
    "host": "localhost",    # Host del database
    "port": "5432"          # Porta del database
}

# Percorso del file JSON
JSON_FILE_PATH = "progetto mics/impatti_unitari_completi.json"

# Funzione per popolare la tabella UnitaryImpact
def populate_unitaryimpact_table(cursor, json_file_path):
    # Leggi il file JSON
    with open(json_file_path, 'r') as file:
        unitary_impact_data = json.load(file)

    # Itera su ogni record nel JSON
    for item in unitary_impact_data:
        activity_id_product_id = item.get("Activity UUID_Product UUID")
        impacts = item.get("Impacts", [])
        system_model = item.get("systemmodel", "")  # Aggiungi la variabile per la colonna systemmodel

        # Aggiungi "apos" al sistema modello
        if system_model:
            system_model = system_model + "cutoff"

        # Itera su ogni impatto associato all'attività
        for impact in impacts:
            method = impact.get("Method")
            category = impact.get("Category")
            indicator = impact.get("Indicator")
            value = impact.get("Value")
            unit = impact.get("Unit")
            
            # Verifica che tutti i dati siano presenti
            if activity_id_product_id and method and category and indicator and value is not None:
                # Controlla se l'associazione esiste già
                cursor.execute(""" 
                    SELECT COUNT(*) FROM UnitaryImpact 
                    WHERE activityId_productId = %s 
                    AND impactMethodName = %s 
                    AND impactCategoryName = %s 
                    AND impactName = %s;
                """, (activity_id_product_id, method, category, indicator))

                count = cursor.fetchone()[0]
                if count == 0:
                    # Inserisci i dati nella tabella UnitaryImpact
                    cursor.execute(""" 
                        INSERT INTO UnitaryImpact (activityId_productId, impactMethodName, 
                                   impactCategoryName, impactName, value, systemmodel, unit) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """, (activity_id_product_id, method, category, indicator, value, system_model, unit))
                    print(f"Inserito impatto per {activity_id_product_id} con indicatore {indicator} e sistema {system_model}.")
                else:
                    print(f"Impatto per {activity_id_product_id} con indicatore {indicator} e sistema {system_model} esiste già nella tabella UnitaryImpact.")
            else:
                print(f"Dati incompleti per l'inserimento dell'impatto: {item}")

# Codice principale per eseguire l'operazione
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Connessione al database riuscita.")

    # Popolare la tabella UnitaryImpact
    populate_unitaryimpact_table(cursor, JSON_FILE_PATH)

    # Confermare le modifiche
    conn.commit()
    print("Tabella UnitaryImpact popolata con successo!")

except (Exception, psycopg2.Error) as error:
    print("Errore durante il caricamento dei dati nella tabella UnitaryImpact:", error)

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    print("Connessione al database chiusa.")
