# routes/indicatori_routes.py

from flask import Blueprint, jsonify, request # <-- Aggiunta l'importazione di 'request'
import csv
import os

# Inizializza il Blueprint per le routes degli indicatori
indicatori_bp = Blueprint('indicatori', __name__)

# Percorso assoluto al file CSV
# Assicurati che questo percorso sia corretto rispetto alla tua struttura di progetto.
# 'current_dir' è la directory di questo file (routes/).
# 'PROJECT_ROOT' risale di un livello per arrivare alla radice del progetto (es. your_project/).
# 'INDICATORI_CSV_PATH' costruisce il percorso completo al file CSV.
current_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(current_dir, '..')
INDICATORI_CSV_PATH = os.path.join(PROJECT_ROOT, 'data', 'indicatori.csv')

@indicatori_bp.route('/indicatori_impatto', methods=['GET'])
def get_indicatori_impatto():
    """
    Recupera i dati degli indicatori di impatto dal file CSV e li restituisce.
    Supporta il filtraggio dinamico basato sui parametri di query (impactmethodname,
    impactcategoryname, impactindicatorname).
    """
    
    # Parametri di query opzionali per il filtraggio.
    # request.args.get() recupera i valori dai parametri URL (es. ?param=value).
    filter_method = request.args.get('impactmethodname')
    filter_category = request.args.get('impactcategoryname')
    filter_indicator = request.args.get('impactindicatorname')

    data = [] # Lista per immagazzinare i dati filtrati dal CSV
    try:
        # Apre il file CSV in modalità lettura con codifica UTF-8.
        # Usa csv.DictReader per leggere le righe come dizionari, dove le chiavi sono gli header.
        # Il delimitatore è specificato come ';'.
        with open(INDICATORI_CSV_PATH, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                # Applica i filtri: se un filtro è specificato e la riga non corrisponde,
                # salta questa riga e passa alla successiva.
                if filter_method and row.get('impactmethodname') != filter_method:
                    continue
                if filter_category and row.get('impactcategoryname') != filter_category:
                    continue
                if filter_indicator and row.get('impactindicatorname') != filter_indicator:
                    continue
                
                # Se la riga passa tutti i filtri (o se non ci sono filtri), aggiungila alla lista 'data'.
                data.append(row)
        
        # Restituisce i dati filtrati come risposta JSON con stato HTTP 200 (OK).
        return jsonify(data), 200

    except FileNotFoundError:
        # Gestisce l'errore se il file CSV non viene trovato nel percorso specificato.
        return jsonify({"message": f"File CSV non trovato a: {INDICATORI_CSV_PATH}"}), 500
    except Exception as e:
        # Cattura qualsiasi altro errore generico durante la lettura o l'elaborazione del CSV.
        return jsonify({"message": f"Errore durante la lettura del file CSV: {str(e)}"}), 500