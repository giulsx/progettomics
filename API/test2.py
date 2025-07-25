# test_get_certificazioni_by_product.py
import requests
import json
import uuid

# --- CONFIGURAZIONE DEL TEST ---
BASE_URL = "http://127.0.0.1:8000" # Assicurati che corrisponda all'indirizzo del tuo server Flask
PRODUCTS_CERTIFICATIONS_ENDPOINT_PREFIX = f"{BASE_URL}/products"

# *** IMPORTANTE: INSERISCI QUI L'ID DI UN PRODOTTO ESISTENTE ***
# Scegli un ID di un prodotto che sai avere delle certificazioni associate.
TEST_PRODUCT_ID = "8ed88a45-b198-e482-a479-420ce96a004b" # Esempio, usa un ID reale dal tuo DB

def run_get_by_product_test():
    if TEST_PRODUCT_ID == "inserisci_qui_un_UUID_di_prodotto_esistente":
        print("ERRORE: Per favore, aggiorna TEST_PRODUCT_ID nello script con un UUID valido dal tuo database.")
        return

    get_url = f"{PRODUCTS_CERTIFICATIONS_ENDPOINT_PREFIX}/{TEST_PRODUCT_ID}/certificazioni"
    print(f"\nTentativo di recuperare le certificazioni per il Prodotto ID: {TEST_PRODUCT_ID}")
    print(f"URL della richiesta GET: {get_url}")

    try:
        # Esegue la richiesta GET all'API
        response = requests.get(get_url)
        
        print(f"\nStato della risposta: {response.status_code}")
        print(f"Corpo della risposta:\n{json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print(f"\nTEST SUPERATO: Recuperate {len(response.json())} certificazioni per il prodotto {TEST_PRODUCT_ID}.")
            # Puoi ispezionare 'response.json()' per vedere i dettagli delle certificazioni
        elif response.status_code == 404:
            print("\nTEST FALLITO: Prodotto non trovato. L'ID potrebbe essere sbagliato o non esiste.")
        else:
            print(f"\nTEST FALLITO: Si è verificato un errore durante il recupero delle certificazioni. Codice di stato: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\nERRORE: Impossibile connettersi al server Flask. Assicurati che il tuo server sia in esecuzione.")
    except Exception as e:
        print(f"\nSi è verificato un errore imprevisto durante il test: {e}")

if __name__ == "__main__":
    run_get_by_product_test()