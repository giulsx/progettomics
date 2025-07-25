import requests
import json
import base64
import uuid

# --- CONFIGURAZIONE DEL TEST ---
BASE_URL = "http://127.0.0.1:8000" # Assicurati che questo sia l'indirizzo corretto del tuo server Flask
CERTIFICAZIONI_ENDPOINT = f"{BASE_URL}/certificazioni"

# *** INSERISCI QUI I TUOI UUID REALI DAL DATABASE ***
TEST_USER_ID = "02cf6730-f316-4bea-96df-b03138b6a1cf" 
TEST_PRODUCT_ID = "8ed88a45-b198-e482-a479-420ce96a004b" 


# --- FUNZIONE PER GENERARE UN PDF DI ESEMPIO (Base64) ---
def generate_sample_pdf_base64():
    # Un PDF minimale con "Hello, World!" per test.
    pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R>>endobj\n4 0 obj<</Length 11>>stream\nBT /F1 12 Tf 72 712 Td (Hello, World!) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000114 00000 n\n0000000216 00000 n\ntrailer<</Size 5/Root 1 0 R>>startxref\n304\n%%EOF"
    return base64.b64encode(pdf_content).decode('utf-8')

# --- DATI PER IL TEST DELLA NUOVA CERTIFICAZIONE ---
def get_test_data():
    data = {
        "nomecertificazione": "Certificazione Singolo Prodotto Test",
        "tipocertificazione": "Qualità Specifiche",
        "entecertificatore": "Ente Test Semplificato",
        "anno": 2023,
        "certificazionepdf": generate_sample_pdf_base64(), # PDF di esempio
        "userid": TEST_USER_ID, 
        "productid": TEST_PRODUCT_ID # Questo è il campo che il server Flask si aspetta
    }
    return data

# --- ESECUZIONE DEL TEST ---
def run_test():
    print(f"Tentativo di creare una certificazione a: {CERTIFICAZIONI_ENDPOINT}")

    test_data = get_test_data()
    print(f"\nDati inviati:\n{json.dumps(test_data, indent=2)}")

    try:
        response = requests.post(CERTIFICAZIONI_ENDPOINT, json=test_data)
        
        print(f"\nStato della risposta: {response.status_code}")
        print(f"Corpo della risposta:\n{json.dumps(response.json(), indent=2)}")

        if response.status_code == 201:
            print("\nTEST SUPERATO: Certificazione creata con successo e associazione prodotto generata.")
            created_cert = response.json()
            print(f"ID Certificazione creata: {created_cert.get('certificazioneid')}")
        else:
            print("\nTEST FALLITO: Si è verificato un errore durante la creazione della certificazione.")
            
    except requests.exceptions.ConnectionError:
        print("\nERRORE: Impossibile connettersi al server Flask. Assicurati che sia in esecuzione.")
    except Exception as e:
        print(f"\nSi è verificato un errore imprevisto: {e}")

if __name__ == "__main__":
    # Questo controllo assicura che tu abbia aggiornato i valori all'inizio dello script.
    if TEST_USER_ID == "IL_TUO_USERID_ESISTENTE_QUI" or TEST_PRODUCT_ID == "IL_TUO_PRODUCTID_ESISTENTE_QUI":
        print("ERRORE: Per favore, aggiorna TEST_USER_ID e TEST_PRODUCT_ID nello script con UUID validi dal tuo database.")
    else:
        run_test()