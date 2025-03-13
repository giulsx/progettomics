import os
import json
import psycopg2

# Configura la connessione al database
DB_CONFIG = {
    "dbname": "tuo_database",
    "user": "tuo_utente",
    "password": "tua_password",
    "host": "localhost",
    "port": "5432"
}

# Percorso della cartella contenente i file JSON
cartella = "output"  # Cambia con il percorso corretto
output_file = "id_non_presenti.txt"

id_list = []

# Connessione al database
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Scansiona tutti i file nella cartella
    for filename in os.listdir(cartella):
        if filename.endswith(".json"):
            file_path = os.path.join(cartella, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "@id" in data:  # Verifica se "@id" è presente nel file
                        id_ = data["@id"]

                        # Controlla se l'ID è presente nel database
                        cursor.execute("SELECT 1 FROM activity WHERE activityid = %s", (id_,))
                        result = cursor.fetchone()

                        if not result:  # Se l'ID non è presente
                            id_list.append(f"{filename}: {id_}")

            except Exception as e:
                print(f"Errore con il file {filename}: {e}")

    # Scrive gli ID mancanti e i file di origine in un file di testo
    with open(output_file, "w", encoding="utf-8") as out_f:
        for item in id_list:
            out_f.write(item + "\n")

    print(f"Verifica completata! {len(id_list)} ID non trovati nel database, salvati in {output_file}.")

except Exception as e:
    print(f"Errore di connessione al database: {e}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
