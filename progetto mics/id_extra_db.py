import psycopg2
from psycopg2 import sql

# Configurazione della connessione al database
DB_CONFIG = {
    "dbname": "nome_database",
    "user": "nome_utente",
    "password": "password",
    "host": "localhost",
    "port": "5432"
}

# Nome del file di input
input_file = "id_list.txt"
# Nome del file di output
output_file = "id_extra_db.txt"

# Leggere gli ID dal file
id_file_set = set()

with open(input_file, "r") as f:
    for line in f:
        if ": " in line:
            _, activity_id = line.strip().split(": ")
            id_file_set.add(activity_id)

# Connettersi al database e verificare la presenza degli ID
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Query per recuperare tutti gli ID dal database
    query = sql.SQL("SELECT id FROM activity")
    cur.execute(query)
    id_db_set = {str(row[0]) for row in cur.fetchall()}  # Convertire in set di stringhe

    # Chiudere la connessione
    cur.close()
    conn.close()

    # Identificare gli ID presenti nel database ma assenti nel file
    id_extra_db = id_db_set - id_file_set

    # Scrivere i risultati su file
    with open(output_file, "w") as f:
        for activity_id in id_extra_db:
            f.write(f"{activity_id}\n")

    print(f"Elaborazione completata. File generato: {output_file}")

except Exception as e:
    print(f"Errore durante l'accesso al database: {e}")
