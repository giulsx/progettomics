import unittest
import requests
import json
import uuid
import decimal # Importa il modulo decimal per confronti precisi

# URL di base della tua API Flask
# !!! IMPORTANTE: Assicurati che il tuo server Flask sia in ascolto su questa porta (e.g., 5000 o 8000)
# e che il tuo blueprint 'impact_bp' sia registrato sotto '/impact' nella tua app Flask principale.
BASE_URL = "http://127.0.0.1:8000/impact/calculate_product_impact" 

class TestImpactCalculationAPI(unittest.TestCase):

    # UUID di esempio per i test. 
    # Sostituiscili con UUID reali **esistenti nel tuo database** # per garantire che i test operino su dati significativi.
    # Se questi ID non esistono o non riflettono gli scenari, i test falliranno.
    VALID_PRODUCT_ID = "0ed88a45-b198-e482-a479-420ce96a004b"  # Esempio: productId con attività associate
    PRODUCT_ID_NO_ACTIVITIES = "" # Esempio: productId valido ma senza attività
    INVALID_PRODUCT_ID_FORMAT = "invalid-uuid-string" # Stringa che non è un UUID valido
    
    # Parametri di impatto di default usati dalla tua API
    DEFAULT_IMPACT_NAME = "global warming potential (GWP100)"
    DEFAULT_IMPACT_CATEGORY = "climate change"
    DEFAULT_IMPACT_METHOD = "EF v3.0"

    def test_01_missing_product_id(self):
        """
        Testa la gestione di una richiesta senza il parametro 'productId'.
        Ci aspettiamo uno stato 400 Bad Request.
        """
        print("\n--- Esecuzione test_01_missing_product_id ---")
        response = requests.get(BASE_URL)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Parametro 'productId' mancante.", response.json().get("error"))
        print(f"Risposta: {json.dumps(response.json(), indent=2)}")

    def test_02_invalid_product_id_format(self):
        """
        Testa la gestione di un 'productId' con formato non valido (non UUID).
        Ci aspettiamo uno stato 400 Bad Request.
        """
        print("\n--- Esecuzione test_02_invalid_product_id_format ---")
        params = {'productId': self.INVALID_PRODUCT_ID_FORMAT}
        response = requests.get(BASE_URL, params=params)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Formato 'productId' non valido.", response.json().get("error"))
        print(f"Risposta: {json.dumps(response.json(), indent=2)}")

    def test_03_valid_product_id_no_activities(self):
        """
        Testa un 'productId' valido ma che non ha attività associate nel database.
        Ci aspettiamo uno stato 404 Not Found e un messaggio appropriato, con impatto zero.
        """
        print("\n--- Esecuzione test_03_valid_product_id_no_activities ---")
        params = {'productId': self.PRODUCT_ID_NO_ACTIVITIES}
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertIn("Nessuna attività associata trovata", data.get("message"))
        # Modificato: si aspetta una stringa, e poi la converte in Decimal per il confronto numerico
        self.assertEqual(decimal.Decimal(data.get("total_impact")), decimal.Decimal('0.0'))
        self.assertEqual(data.get("impacts_by_fase"), {})
        print(f"Risposta: {json.dumps(data, indent=2)}")

    def test_04_successful_impact_calculation(self):
        """
        Testa un calcolo dell'impatto di successo per un prodotto esistente
        con i parametri di impatto di default.
        Ci aspettiamo uno stato 200 OK. L'impatto potrebbe essere '0.0' se il VALID_PRODUCT_ID
        non ha dati che generano impatto, ma la richiesta è comunque valida.
        """
        print("\n--- Esecuzione test_04_successful_impact_calculation ---")
        params = {
            'productId': self.VALID_PRODUCT_ID,
            'impactName': self.DEFAULT_IMPACT_NAME,
            'impactCategoryName': self.DEFAULT_IMPACT_CATEGORY,
            'impactMethodName': self.DEFAULT_IMPACT_METHOD
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_impact", data)
        self.assertIn("impacts_by_fase", data)
        # Modificato: ci aspettiamo una stringa, non un float.
        self.assertIsInstance(data["total_impact"], str) 
        self.assertIsInstance(data["impacts_by_fase"], dict)
        # Aggiungi asserzioni più specifiche se conosci i risultati attesi per VALID_PRODUCT_ID
        # Esempio: self.assertGreater(decimal.Decimal(data["total_impact"]), decimal.Decimal('0.0')) # Se ti aspetti un impatto positivo
        print(f"Risposta: {json.dumps(data, indent=2)}")

    def test_05_successful_impact_calculation_with_fase_filter(self):
        """
        Testa il calcolo dell'impatto con un filtro 'faseGenerale' specifico.
        Ci aspettiamo uno stato 200 OK e l'impatto solo per la fase specificata.
        !!! IMPORTANTE: Sostituisci 'materie prime' con una fase_generale esistente nel tuo DB
        per il VALID_PRODUCT_ID specificato.
        """
        print("\n--- Esecuzione test_05_successful_impact_calculation_with_fase_filter ---")
        FaseGeneraleDaFiltrare = "materie prime" # Esempio: Assicurati che esista nel tuo DB per VALID_PRODUCT_ID
        params = {
            'productId': self.VALID_PRODUCT_ID,
            'impactName': self.DEFAULT_IMPACT_NAME,
            'impactCategoryName': self.DEFAULT_IMPACT_CATEGORY,
            'impactMethodName': self.DEFAULT_IMPACT_METHOD,
            'filterFaseGenerale': FaseGeneraleDaFiltrare
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_impact", data)
        self.assertIn("impacts_by_fase", data)
        # Modificato: ci aspettiamo una stringa, non un float.
        self.assertIsInstance(data["total_impact"], str) 
        self.assertIsInstance(data["impacts_by_fase"], dict)
        self.assertEqual(len(data["impacts_by_fase"]), 1) # Ci aspettiamo solo una fase
        self.assertIn(FaseGeneraleDaFiltrare, data["impacts_by_fase"])
        # Esempio: self.assertGreater(decimal.Decimal(data["total_impact"]), decimal.Decimal('0.0')) # Se ti aspetti un impatto positivo per questa fase
        print(f"Risposta: {json.dumps(data, indent=2)}")

    def test_06_fase_filter_not_found(self):
        """
        Testa il calcolo dell'impatto con un filtro 'faseGenerale' che non esiste
        per il prodotto specificato.
        Ci aspettiamo uno stato 404 Not Found e impatto zero.
        """
        print("\n--- Esecuzione test_06_fase_filter_not_found ---")
        NonExistentFase = "FaseInesistente"
        params = {
            'productId': self.VALID_PRODUCT_ID,
            'impactName': self.DEFAULT_IMPACT_NAME,
            'impactCategoryName': self.DEFAULT_IMPACT_CATEGORY,
            'impactMethodName': self.DEFAULT_IMPACT_METHOD,
            'filterFaseGenerale': NonExistentFase
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertIn("Nessun impatto trovato per la fase", data.get("message"))
        # Modificato: si aspetta una stringa, e poi la converte in Decimal per il confronto numerico
        self.assertEqual(decimal.Decimal(data.get("total_impact")), decimal.Decimal('0.0'))
        self.assertEqual(data.get("impacts_by_fase"), {}) # Ci aspettiamo un dizionario vuoto
        print(f"Risposta: {json.dumps(data, indent=2)}")

    # Puoi aggiungere altri test per scenari specifici, ad esempio:
    # - Test con un productId che causa errori interni del server (es. dipendenze mancanti nel DB)
    # - Test con valori di impactName, impactCategoryName, impactMethodName non standard
    # - Test con un productId per il quale sono presenti solo scambi elementari o solo intermedi
    # - Test con prodotti che hanno 'prodottofornitore_id' per verificare la ricorsione

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)