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
JSON_FILE_PATH = "progetto mics/CFs_with_units_unique.json"

# Controlla se il file esiste
if not os.path.isfile(JSON_FILE_PATH):
    print(f"Errore: il file {JSON_FILE_PATH} non esiste.")
else:
    # Funzione per popolare la tabella CFs
    def populate_cfs_table(cursor, json_file_path):
        # Leggi il file JSON
        with open(json_file_path, 'r') as file:
            cfs_data = json.load(file)

        # Itera su ogni record nel JSON
        for item in cfs_data:
            method = item.get("Method")
            category = item.get("Category")
            indicator = item.get("Indicator")
            name = item.get("Name")
            cf = item.get("CF")
            unit = item.get("Indicator Unit")
            
            # Verifica che tutti i dati siano presenti
            if method and category and indicator and name and cf is not None:
                
                # Controlla se l'associazione esiste già
                cursor.execute("""
                    SELECT COUNT(*) FROM CFs 
                    WHERE elementaryName = %s 
                    AND impactMethodName = %s 
                    AND impactCategoryName = %s 
                    AND impactName = %s;
                """, (name, method, category, indicator))

                count = cursor.fetchone()[0]
                if count == 0:
                    # Inserisci i dati nella tabella CFs
                    cursor.execute("""
                        INSERT INTO CFs (elementaryName, impactMethodName, impactCategoryName, impactName, CF, unit)
                        VALUES (%s, %s, %s, %s, %s, %s);
                    """, (name, method, category, indicator, cf, unit))
                    print(f"Inserito CF per l'indicatore {indicator} nella tabella CFs.")
                else:
                    print(f"CF per l'indicatore {indicator} esiste già nella tabella CFs.")
            else:
                print(f"Dati incompleti per l'inserimento del CF: {item}")

    # Codice principale per eseguire l'operazione
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Connessione al database riuscita.")

        # Popolare la tabella CFs
        populate_cfs_table(cursor, JSON_FILE_PATH)

        # Confermare le modifiche
        conn.commit()
        print("Tabella CFs popolata con successo!")

    except (Exception, psycopg2.Error) as error:
        print("Errore durante il caricamento dei dati nella tabella CFs:", error)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Connessione al database chiusa.")
