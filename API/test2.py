import requests
import json

# URL della rotta POST del tuo backend Flask
url = "http://127.0.0.1:5000/products"  # Cambia con la tua rotta corretta

# Dati JSON da inviare
payload = {
    "productname": "Scarpa Sportiva",
    "systemmodel": "APOS",
    "intervallo": "2020-2025",
    "totale_produzione": 15000.75,
    "userid": "8c1e2f3a-4d5b-6789-90ab-cdef12345678"
}

# Fai la richiesta POST
response = requests.post(url, json=payload)

# Stampa il risultato
if response.status_code == 201:
    print("Prodotto creato con successo:")
    print(response.json())
else:
    print(f"Errore: {response.status_code}")
    print(response.text)
