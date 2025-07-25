import requests
import json
import uuid
import time # Utile per un piccolo ritardo se necessario tra il delete e il re-delete

# --- Configurazione API ---
BASE_URL = "http://localhost:8000"  # Assicurati che l'URL del tuo server Flask sia corretto
DELETE_ENDPOINT = f"{BASE_URL}/certificazione-impact-indicator" # Endpoint per eliminare l'associazione

# --- ID dell'Associazione Esistente da Eliminare ---
# *** IMPORTANTISSIMO: SOSTITUISCI QUESTI UUID CON VALORI REALI DAL TUO DATABASE ***
# Devi fornire l'ID di una Certificazione E un ImpactIndicator che SONO GIÀ ASSOCIATI.
CERTIFICAZIONE_ID_TO_DELETE = "4c3d7542-3f48-466b-8438-6bb6db62dac8" # <<< ID Certificazione ESISTENTE NELL'ASSOCIAZIONE
IMPACT_INDICATOR_ID_TO_DELETE = "524c2091-5506-4d28-b921-faf83946272a" # <<< ID ImpactIndicator ESISTENTE NELL'ASSOCIAZIONE


# --- Funzione helper per inviare richieste HTTP ---
def send_api_request(method, endpoint, payload=None, test_description=""):
    """Invia una richiesta HTTP e stampa la risposta."""
    print(f"\n--- Esecuzione Test: {test_description} ---")
    if payload:
        print("Payload inviato:")
        print(json.dumps(payload, indent=4))
    else:
        print("Nessun payload inviato.")

    try:
        response = requests.request(method, endpoint, json=payload)
        response.raise_for_status()  # Genera un'eccezione per codici di stato 4xx/5xx
        print(f"Status Code: {response.status_code}")
        # La DELETE non restituisce un corpo JSON se tutto va bene (200 OK o 204 No Content)
        if response.status_code not in [200, 204]:
            try:
                print("Risposta dal server:")
                print(json.dumps(response.json(), indent=4))
            except json.JSONDecodeError:
                print(f"Risposta non JSON: {response.text}")
        elif response.status_code == 200: # Se il tuo Flask restituisce 200 con un messaggio
            try:
                print("Risposta dal server:")
                print(json.dumps(response.json(), indent=4))
            except json.JSONDecodeError:
                print(f"Risposta non JSON: {response.text}")
        print(f"Test '{test_description}' completato con successo.")
        return response
    except requests.exceptions.HTTPError as http_err:
        print(f"ERRORE HTTP nel test '{test_description}': {http_err}")
        if http_err.response:
            try:
                print("Dettagli errore dal server:")
                print(json.dumps(http_err.response.json(), indent=4))
            except json.JSONDecodeError:
                print(f"Risposta di errore non JSON: {http_err.response.text}")
        print(f"Test '{test_description}' FALLITO.")
    except requests.exceptions.RequestException as req_err:
        print(f"ERRORE DI CONNESSIONE nel test '{test_description}': {req_err}")
        print(f"Assicurati che il tuo server Flask sia in esecuzione su {BASE_URL}.")
        print(f"Test '{test_description}' FALLITO.")
    except Exception as e:
        print(f"ERRORE IMPREVISTO nel test '{test_description}': {e}")
        print(f"Test '{test_description}' FALLITO.")
    return None

# --- Inizio del Test di Eliminazione Associazione ---

print("\n### Inizio del Test: Eliminazione di un'Associazione Certificazione-Indicatore (Fornita Esternamente) ###")

# FASE 1: Esegui l'operazione DELETE
print("\n--- FASE 1: Esecuzione dell'operazione DELETE ---")

delete_payload = {
    "certificazioneid": CERTIFICAZIONE_ID_TO_DELETE,
    "impactindicatorid": IMPACT_INDICATOR_ID_TO_DELETE
}

delete_response_obj = send_api_request("DELETE", DELETE_ENDPOINT, delete_payload, "Eliminazione Associazione")

# Verifica il risultato dell'operazione DELETE
if delete_response_obj and delete_response_obj.status_code == 200:
    print("\nVerifica dei risultati dell'eliminazione:")
    print("Associazione eliminata con successo!")
    print(f"Certificazione ID: {CERTIFICAZIONE_ID_TO_DELETE}, ImpactIndicator ID: {IMPACT_INDICATOR_ID_TO_DELETE}")
    print("Test di eliminazione completato con successo!")
else:
    print("\nTEST FALLITO: L'operazione DELETE non è riuscita come previsto.")

# FASE 2 (Opzionale ma consigliata): Tenta di eliminare la stessa associazione di nuovo
# Dovrebbe risultare in un 404, indicando che l'associazione non esiste più.
print("\n--- FASE 2: Tentativo di eliminare la stessa associazione (dovrebbe fallire con 404) ---")
print("Payload per tentativo di re-eliminazione:")
print(json.dumps(delete_payload, indent=4))

# Esegui la richiesta direttamente senza la funzione helper per catturare specificamente il 404
re_delete_response_obj = requests.delete(DELETE_ENDPOINT, json=delete_payload)

if re_delete_response_obj.status_code == 404:
    print(f"Status Code atteso (404 Not Found) ricevuto per il tentativo di re-eliminazione. L'associazione è stata correttamente rimossa.")
    try:
        print("Risposta dal server:")
        print(json.dumps(re_delete_response_obj.json(), indent=4))
    except json.JSONDecodeError:
        print(f"Risposta non JSON: {re_delete_response_obj.text}")
else:
    print(f"ATTENZIONE: Status Code inatteso ({re_delete_response_obj.status_code}) per il tentativo di re-eliminazione.")
    if re_delete_response_obj.content:
        print(f"Risposta: {re_delete_response_obj.text}")

print("\n### Fine del Test ###")