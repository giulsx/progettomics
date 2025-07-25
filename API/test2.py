import requests
import json
import uuid

base_url = "http://localhost:8000" # Assicurati che questa URL e porta siano corrette

# --- Dati di Partenza (Valori ATTUALI nel tuo DB per la riga che vuoi modificare) ---
# Questi valori devono corrispondere ESATTAMENTE alla riga esistente nel tuo database.
# Copia/incolla questi UUID e gli altri valori direttamente dal tuo DB.
current_db_values = {
    "productid": "8ed88a45-b198-e482-a479-420ce96a004b",
    "activityid": "00027245-d6be-527e-82d0-fcee42d50a9f", # Assicurati che questo UUID sia corretto nel tuo DB
    "prodottofornitore_id": None, # O None se è NULL nel DB
    "amount": 530,            # Deve essere il valore ATTUALE nel DB (usa .0 per i float)
    "fase_generale": "materie prime",
    "nome_risorsa": None,       # Deve essere None se NULL nel DB
    "fase_produttiva": None,
    "distanza_fornitore": 130, # Deve essere None se NULL nel DB
    "coll_trasporto": "77d88a45-b198-e482-a479-420ce96a0049",
    "coll_trattamento": None,
    "q_annuale": None
}

# --- Dati di Aggiornamento (Nuovi valori che vuoi impostare) ---
# Contiene solo i campi che vuoi modificare e i loro NUOVI valori.
new_update_values = {
    "amount": 530,             # Il nuovo valore per 'amount'
    "distanza_fornitore": 130,
    "coll_trasporto" : "77d88a45-b198-e482-a479-420ce96a0049"  # Il nuovo valore per 'distanza_fornitore'
}

# --- Costruzione del Payload Finale ---
# Combina i criteri di ricerca (valori attuali) con i dati di aggiornamento (nuovi valori).
payload = {
    "search_criteria": current_db_values,
    "update_data": new_update_values
}

# --- Test di Validità Locale degli UUID in search_criteria ---
# Questo blocco verifica che gli UUID nella sezione 'search_criteria' siano validi
# PRIMA di inviare la richiesta HTTP. Questo ti aiuterà a catturare errori
# "badly formed hexadecimal UUID string" localmente, risparmiando tempo.
try:
    _ = uuid.UUID(payload["search_criteria"]["productid"])
    _ = uuid.UUID(payload["search_criteria"]["activityid"])
    if payload["search_criteria"]["prodottofornitore_id"] is not None:
        _ = uuid.UUID(payload["search_criteria"]["prodottofornitore_id"])
    print("Verifica locale: Tutti gli UUID in 'search_criteria' sono formattati correttamente.")
except ValueError as e:
    print(f"ERRORE CRITICO LOCALE: Uno degli UUID in 'search_criteria' non è formattato correttamente: {e}")
    print("Controlla attentamente gli UUID copiati dal tuo database per spazi extra o errori di battitura.")
    exit() # Interrompe l'esecuzione se c'è un errore di formato UUID locale

print("Invio richiesta PUT con il seguente payload:")
print(json.dumps(payload, indent=4))

try:
    response = requests.put(f"{base_url}/product-activity", json=payload)
    response.raise_for_status() # Genera un'eccezione per risposte 4xx/5xx
    print("\nStatus Code:", response.status_code)
    print("Response:", response.json())
except requests.exceptions.HTTPError as err:
    print(f"\nHTTP Error: {err}")
    # Stampa la risposta JSON dell'errore per maggiori dettagli dal server Flask
    if err.response:
        print("Response Error Details:", err.response.json())
except requests.exceptions.RequestException as err:
    print(f"\nRequest Error: {err}")