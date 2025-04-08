import psycopg2

# Configurazione della connessione al database PostgreSQL
DB_CONFIG = {
    "dbname": "ecoinvent",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

# Nome del file contenente gli ID da eliminare
id_file = "id_ripetuti.txt"

# Leggere gli ID dal file e convertirli in una lista
with open(id_file, "r") as f:
    activity_ids = [line.strip() for line in f]

if not activity_ids:
    print("Nessun ID trovato nel file. Operazione interrotta.")
else:
    try:
        # Connessione al database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Query con CAST esplicito a UUID
        query = "DELETE FROM activity WHERE id = ANY(%s::uuid[]);"
        cursor.execute(query, (activity_ids,))

        # Confermare le modifiche
        conn.commit()
        print(f"Eliminati {cursor.rowcount} record dalla tabella activity.")

        # Chiudere la connessione
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Errore durante l'eliminazione dei record: {e}")