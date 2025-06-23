import requests

# URL del tuo server Flask
url = "http://127.0.0.1:5000/activities/00027245-d6be-527e-82d0-fcee42d50a9f"  # Cambia con l'endpoint corretto

# Fai la richiesta GET
response = requests.get(url)

# Stampa il risultato 
if response.status_code == 200:
    print(response.json())  # Stampa la risposta JSON
else:
    print(f"Errore: {response.status_code}")