import psycopg2
from psycopg2 import sql
from collections import defaultdict

# Configurazione della connessione al database
DB_CONFIG = {
    "dbname": "ecoinvent",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

# Nome del file di input
input_file = "file_id_ripetuti.txt"
# Nome del file di output
output_file = "id_non_presenti.txt"

# Dizionario per memorizzare ID e file associati
id_to_files = defaultdict(list)

# Leggere il file e popolare il dizionario
with open(input_file, "r") as f:
    for line in f:
        if ": " in line:
            filename, activity_id = line.strip().split(": ")
            id_to_files[activity_id].append(filename)

# Creare un set di ID unici da verificare
id_list = set(id_to_files.keys())

# Connettersi al database e verificare la presenza degli ID
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Query per recuperare gli ID presenti nel database
    query = sql.SQL("SELECT id FROM activity WHERE id = ANY(%s::uuid[])")
    cur.execute(query, (list(id_list),))
    ids_presenti = {row[0] for row in cur.fetchall()}  # Convertire in set

    # Chiudere la connessione
    cur.close()
    conn.close()

    # Identificare gli ID non presenti
    id_non_presenti = id_list - ids_presenti

    # Scrivere i risultati su file
    with open(output_file, "w") as f:
        for activity_id in id_non_presenti:
            for filename in id_to_files[activity_id]:
                f.write(f"{filename}: {activity_id}\n")

    print(f"Elaborazione completata. File generato: {output_file}")

except Exception as e:
    print(f"Errore durante l'accesso al database: {e}")
