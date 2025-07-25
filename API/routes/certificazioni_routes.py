# routes/certificazioni_routes.py

from flask import Blueprint, request, jsonify, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database import db
from models import Certificazione, Certificazione_Product, Certificazione_ImpactIndicator, Product, ImpactIndicator  # Importa il modello di associazione
from schemas import CertificazioneSchema, ProductSchema # Non abbiamo più bisogno di CertificazioneProductSchema qui per il load
import uuid
from sqlalchemy import exc

# Inizializza il Blueprint per le routes delle certificazioni
certificazioni_bp = Blueprint('certificazioni', __name__)

# Inizializza gli schemi Marshmallow
certificazione_schema = CertificazioneSchema()
certificazioni_schema = CertificazioneSchema(many=True)

#### CREAZIONE CERTIFICAZIONE NUOVA ####
@certificazioni_bp.route('/certificazioni', methods=['POST'])
def create_certificazione():
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"message": "Nessun dato JSON fornito nella richiesta"}), 400

        # Carica e valida i dati usando lo schema.
        validated_data = certificazione_schema.load(json_data)

        # Estrai i dati per la creazione della certificazione.
        nomecertificazione = validated_data.get('nomecertificazione')
        tipocertificazione = validated_data.get('tipocertificazione')
        entecertificatore = validated_data.get('entecertificatore')
        anno = validated_data.get('anno')
        certificazionepdf_bytes = validated_data.get('certificazionepdf')
        userid = validated_data.get('userid')

        # *** LA MODIFICA È QUI: USA 'productid' INVECE DI 'product_id_to_associate' ***
        product_id = validated_data.get('productid') # Estrai 'productid' come inviato dal client

        # Verifica che i campi obbligatori della certificazione siano presenti
        if not all([nomecertificazione, tipocertificazione, entecertificatore, anno is not None]):
            return jsonify({"message": "Campi obbligatori mancanti (nomecertificazione, tipocertificazione, entecertificatore, anno)"}), 400

        # Crea una nuova istanza di Certificazione
        new_certificazione = Certificazione(
            nomecertificazione=nomecertificazione,
            tipocertificazione=tipocertificazione,
            entecertificatore=entecertificatore,
            anno=anno,
            certificazionepdf=certificazionepdf_bytes,
            userid=userid
        )

        db.session.add(new_certificazione)
        # Usa flush() per ottenere l'ID della nuova certificazione prima del commit
        db.session.flush()

        # *** LOGICA DI ASSOCIAZIONE ***
        # Crea l'associazione nella tabella Certificazione_Product solo se product_id è stato fornito
        if product_id: # Ora questa condizione sarà vera se productid è stato inviato
            try:
                new_association = Certificazione_Product(
                    certificazioneid=new_certificazione.certificazioneid,
                    productid=product_id # Usa il product_id estratto
                )
                db.session.add(new_association)
            except IntegrityError as e:
                db.session.rollback()
                # Questo potrebbe accadere se il product_id fornito non esiste nel DB
                return jsonify({"message": f"Errore di integrità del database durante l'associazione prodotto (productid inesistente?): {str(e)}"}), 400
            except Exception as e:
                db.session.rollback()
                print(f"Attenzione: Impossibile associare il product ID {product_id} alla certificazione {new_certificazione.certificazioneid}. Errore: {e}")
                return jsonify({"message": f"Errore generico durante l'associazione prodotto: {str(e)}"}), 500

        db.session.commit()

        # Serializza e restituisci la nuova certificazione.
        # Il campo 'productid' non sarà incluso nella risposta perché è impostato su 'load_only' nello schema.
        return jsonify(certificazione_schema.dump(new_certificazione)), 201

    except ValueError as e: # Cattura errori di validazione da Marshmallow
        db.session.rollback()
        return jsonify({"message": f"Errore di validazione dei dati: {str(e)}"}), 400
    except IntegrityError as e:
        db.session.rollback()
        # Potrebbe indicare un userid non esistente o altri vincoli violati
        return jsonify({"message": f"Errore di integrità del database: {str(e)}"}), 400
    except SQLAlchemyError as e: # Cattura errori generici di SQLAlchemy
        db.session.rollback()
        return jsonify({"message": f"Errore del database: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Errore interno del server: {str(e)}"}), 500
    

#### ELIMINAZIONE CERTIFICAZIONE E ASSOCIAZIONI ####
@certificazioni_bp.route('/certificazioni/<uuid:certificazione_id>', methods=['DELETE'])
def delete_certificazione(certificazione_id):
    try:
        # 1. Trova la certificazione
        certificazione = Certificazione.query.get(certificazione_id)

        if not certificazione:
            return jsonify({"message": f"Certificazione con ID {certificazione_id} non trovata."}), 404

        # 2. Inizia una transazione per garantire l'integrità
        # (db.session.begin() è implicito con un try-except e db.session.commit()/rollback())

        # 3. Elimina tutte le associazioni Certificazione_Product per questa certificazione
        # Non è necessario un prodotto specifico, eliminiamo tutte le associazioni di quella certificazione
        Certificazione_Product.query.filter_by(certificazioneid=certificazione_id).delete()
        
        # 4. Elimina tutte le associazioni Certificazione_ImpactIndicator per questa certificazione
        Certificazione_ImpactIndicator.query.filter_by(certificazioneid=certificazione_id).delete()

        # 5. Elimina la riga della Certificazione stessa
        db.session.delete(certificazione)

        # 6. Conferma tutte le eliminazioni nel database
        db.session.commit()

        return jsonify({"message": f"Certificazione con ID {certificazione_id} e tutte le sue associazioni eliminate con successo."}), 200

    except SQLAlchemyError as e:
        db.session.rollback() # Annulla tutte le operazioni se c'è un errore
        return jsonify({"message": f"Errore del database durante l'eliminazione: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback() # Annulla tutte le operazioni per sicurezza
        return jsonify({"message": f"Errore interno del server: {str(e)}"}), 500
    

#### MODIFICA CERTIFICAZIONE ESISTENTE ####
@certificazioni_bp.route('/certificazioni/<uuid:certificazione_id>', methods=['PATCH'])
def update_certificazione(certificazione_id):
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"message": "Nessun dato JSON fornito nella richiesta."}), 400

        # Trova la certificazione esistente
        certificazione = Certificazione.query.get(certificazione_id)
        if not certificazione:
            return jsonify({"message": f"Certificazione con ID {certificazione_id} non trovata."}), 404

        # Carica e valida i dati in ingresso.
        # 'partial=True' è cruciale per le PATCH: Marshmallow ignorerà i campi mancanti nel JSON.
        validated_data = certificazione_schema.load(json_data, partial=True)

        # Applica gli aggiornamenti solo ai campi forniti nel JSON
        for key, value in validated_data.items():
            # Evita di aggiornare l'ID della certificazione
            if key == 'certificazioneid':
                continue
            # Aggiorna il campo corrispondente nel modello della certificazione
            setattr(certificazione, key, value)
        
        db.session.commit()

        # Restituisci la certificazione aggiornata
        return jsonify(certificazione_schema.dump(certificazione)), 200

    except ValueError as e: # Errori di validazione di Marshmallow
        db.session.rollback()
        return jsonify({"message": f"Errore di validazione dei dati: {str(e)}"}), 400
    except IntegrityError as e: # Errori di vincoli del DB (es. userid non esistente)
        db.session.rollback()
        return jsonify({"message": f"Errore di integrità del database: {str(e)}"}), 400
    except SQLAlchemyError as e: # Errori generici di SQLAlchemy
        db.session.rollback()
        return jsonify({"message": f"Errore del database: {str(e)}"}), 500
    except Exception as e: # Qualsiasi altro errore inatteso
        db.session.rollback()
        return jsonify({"message": f"Errore interno del server: {str(e)}"}), 500
    
#### RECUPERO CERTIFICAZIONI PER PRODOTTO ####
@certificazioni_bp.route('/products/<uuid:product_id>/certificazioni', methods=['GET'])
def get_certificazioni_by_product(product_id):
    try:
        # 1. Verifica se il prodotto esiste (opzionale ma consigliato per una migliore gestione degli errori)
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"message": f"Prodotto con ID {product_id} non trovato."}), 404

        # 2. Esegui la query per recuperare le certificazioni associate a quel product_id
        # Unisci Certificazione con Certificazione_Product sulla base di certificazioneid
        # e poi filtra per il productid desiderato.
        certificazioni = db.session.query(Certificazione) \
                             .join(Certificazione_Product, Certificazione.certificazioneid == Certificazione_Product.certificazioneid) \
                             .filter(Certificazione_Product.productid == product_id) \
                             .all()

        # 3. Serializza le certificazioni trovate
        # Usiamo certificazioni_schema (many=True) per serializzare una lista di oggetti
        result = certificazioni_schema.dump(certificazioni)

        return jsonify(result), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Errore del database durante il recupero delle certificazioni: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Errore interno del server: {str(e)}"}), 500
    

#### INSERIMENTO IMPACT INDICATOR IN CERTIFICAZIONE ####
@certificazioni_bp.route("/certificazione-impact-indicator", methods=["POST"])
def create_or_link_impact_indicator():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Nessun dato fornito per la creazione/collegamento dell'indicatore."}), 400

    # 1. Recupero e Validazione dei Dati di Input
    # Campi per l'ImpactIndicator
    method = data.get("method")
    category = data.get("category")
    impact_indicator_name = data.get("impactindicator") # Mappa a impactname
    amount_raw = data.get("amount")
    unit_name = data.get("unitname")

    # Campo per la Certificazione_ImpactIndicator
    certificazione_id_str = data.get("certificazioneid")

    # Validazione campi obbligatori per ImpactIndicator
    if not all([method, category, impact_indicator_name, unit_name]):
        return jsonify({"error": "I campi 'method', 'category', 'impactindicator' e 'unitname' sono obbligatori per l'indicatore."}), 400

    # Validazione campo obbligatorio per Certificazione_ImpactIndicator
    if not certificazione_id_str:
        return jsonify({"error": "Il campo 'certificazioneid' è obbligatorio per il collegamento."}), 400

    try:
        # Conversione dei tipi
        certificazione_id = uuid.UUID(certificazione_id_str)
        amount = float(amount_raw) if amount_raw is not None else None # Amount può essere None
    except ValueError as e:
        return jsonify({"error": f"Formato dati non valido: {e}. Controlla 'certificazioneid' (UUID) e 'amount' (numerico)."}), 400

    # 2. Controllo esistenza della Certificazione (Buona Pratica)
    # Anche se non esplicitamente richiesto, è buona pratica assicurarsi che la certificazione esista
    # prima di provare a collegare un indicatore ad essa.
    # Se la tua tabella Certificazione non ha un modello 'Certificazione', rimuovi o adatta questa parte.
    # certificazione_exists = db.session.query(Certificazione).filter_by(certificazioneid=certificazione_id).first()
    # if not certificazione_exists:
    #     return jsonify({"error": f"Certificazione con ID '{certificazione_id}' non trovata."}), 404


    # 3. Cerca un ImpactIndicator esistente
    existing_indicator = ImpactIndicator.query.filter_by(
        impactmethodname=method,
        impactcategoryname=category,
        impactname=impact_indicator_name,
        amount=amount,
        unitname=unit_name
    ).first()

    impact_indicator_id = None

    if existing_indicator:
        # Se l'indicatore esiste, usa il suo ID
        impact_indicator_id = existing_indicator.impactindicatorid
        message_indicator = "Indicatore di impatto esistente trovato e riutilizzato."
    else:
        # Se l'indicatore non esiste, creane uno nuovo
        new_indicator = ImpactIndicator(
            impactmethodname=method,
            impactcategoryname=category,
            impactname=impact_indicator_name,
            amount=amount,
            unitname=unit_name
        )
        db.session.add(new_indicator)
        try:
            db.session.flush() # Usa flush per ottenere l'ID generato prima del commit finale
            impact_indicator_id = new_indicator.impactindicatorid
            message_indicator = "Nuovo indicatore di impatto creato."
        except exc.IntegrityError as e:
            db.session.rollback()
            # Questo potrebbe accadere se c'è un'altra transazione che crea un indicatore identico
            # tra il controllo .first() e la creazione del nuovo.
            print(f"Errore di integrità durante la creazione dell'indicatore: {e}")
            return jsonify({"error": "Errore durante la creazione del nuovo indicatore di impatto. Potrebbe esserci un conflitto di dati."}), 500
        except Exception as e:
            db.session.rollback()
            print(f"Errore generico durante la creazione dell'indicatore: {e}")
            return jsonify({"error": f"Errore durante la creazione del nuovo indicatore di impatto: {str(e)}. Contattare l'amministratore."}), 500

    # 4. Crea o verifica l'associazione Certificazione_ImpactIndicator
    # Prima di creare, controlla se l'associazione esiste già per evitare duplicati sulla PK
    existing_association = Certificazione_ImpactIndicator.query.filter_by(
        certificazioneid=certificazione_id,
        impactindicatorid=impact_indicator_id
    ).first()

    if existing_association:
        message_association = "Associazione tra certificazione e indicatore già esistente."
        status_code = 200 # O 200 se consideri l'operazione idempotente e di successo
    else:
        new_association = Certificazione_ImpactIndicator(
            certificazioneid=certificazione_id,
            impactindicatorid=impact_indicator_id
        )
        db.session.add(new_association)
        message_association = "Nuova associazione creata con successo."
        status_code = 201 # Created

    # 5. Commit delle modifiche (sia per l'indicatore che per l'associazione)
    try:
        db.session.commit()
        return jsonify({
            "message": f"{message_indicator} {message_association}",
            "impactindicatorid": str(impact_indicator_id),
            "certificazioneId": str(certificazione_id)
        }), status_code
    except exc.IntegrityError as e:
        db.session.rollback()
        # Questo potrebbe accadere se la certificazioneid non esiste (se non hai il controllo sopra)
        # o altri vincoli di integrità.
        print(f"Errore di integrità durante il commit dell'associazione: {e}")
        return jsonify({"error": "Errore di integrità del database. Assicurati che 'certificazioneid' esista e che non ci siano duplicati inattesi."}), 409 # Conflict
    except Exception as e:
        db.session.rollback()
        print(f"Errore durante il commit finale: {e}")
        return jsonify({"error": f"Errore durante l'operazione: {str(e)}. Contattare l'amministratore."}), 500
    
#### MODIFICA ASSOCIAZIONE CERTIFICAZIONE-IMPACT INDICATOR ####
# Questa route permette di modificare un'associazione esistente tra una Certificazione e un ImpactIndicator.
# Può essere usata per cambiare l'indicatore associato o per aggiornare i dati dell'indicatore stesso.
@certificazioni_bp.route("/certificazione-impact-indicator", methods=["PUT"])
def update_cert_impact_indicator_association():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Nessun dato fornito per la modifica dell'associazione."}), 400

    # 1. Recupero e Validazione dei Dati:
    #   - search_criteria: per trovare l'associazione esistente da eliminare.
    #   - new_impact_indicator_data: per creare/trovare il nuovo ImpactIndicator.
    #   - certificazioneid_for_new_link: per collegare il nuovo indicatore (dovrebbe essere lo stesso del search_criteria).

    search_criteria_raw = data.get("search_criteria")
    new_impact_indicator_data_raw = data.get("new_impact_indicator_data")
    certificazione_id_for_new_link_str = data.get("certificazioneid") # L'ID della certificazione per la nuova associazione

    if not search_criteria_raw or not new_impact_indicator_data_raw or not certificazione_id_for_new_link_str:
        return jsonify({"error": "I campi 'search_criteria', 'new_impact_indicator_data' e 'certificazioneid' sono obbligatori."}), 400

    # Validazione e preparazione di certificazione_id per il nuovo link
    try:
        certificazione_id_for_new_link = uuid.UUID(certificazione_id_for_new_link_str)
    except ValueError as e:
        return jsonify({"error": f"Formato 'certificazioneid' per il nuovo collegamento non valido: {e}. Deve essere un UUID valido."}), 400

    # -- Processo di Eliminazione dell'Associazione Esistente --
    # Conversione e Validazione dei Criteri di Ricerca per l'eliminazione
    old_association_filters = {}
    try:
        old_cert_id_str = search_criteria_raw.get("certificazioneid")
        old_impact_id_str = search_criteria_raw.get("impactindicatorid")

        if not old_cert_id_str or not old_impact_id_str:
            return jsonify({"error": "Campi 'certificazioneid' e 'impactindicatorid' sono obbligatori in 'search_criteria' per l'eliminazione."}), 400

        old_association_filters["certificazioneid"] = uuid.UUID(old_cert_id_str)
        old_association_filters["impactindicatorid"] = uuid.UUID(old_impact_id_str)
    except ValueError as e:
        return jsonify({"error": f"Formato dati in 'search_criteria' non valido: {e}. Controlla gli UUID."}), 400

    # 2. Trova ed Elimina l'Associazione Esistente
    association_to_delete = Certificazione_ImpactIndicator.query.filter_by(**old_association_filters).first()

    if not association_to_delete:
        return jsonify({"error": "Associazione esistente non trovata con i criteri forniti. Nessuna modifica applicata."}), 404

    try:
        db.session.delete(association_to_delete)
        # Non facciamo il commit qui, lo faremo alla fine dopo la nuova associazione
        message_deletion = "Vecchia associazione marcata per l'eliminazione."
    except Exception as e:
        db.session.rollback() # Rollback se l'eliminazione fallisce
        print(f"Errore durante la marcatura per l'eliminazione della vecchia associazione: {e}")
        return jsonify({"error": f"Errore interno durante l'eliminazione della vecchia associazione: {str(e)}."}), 500

    # -- Processo di Inserimento/Collegamento del Nuovo ImpactIndicator --
    # Estrazione e validazione dei dati per il nuovo indicatore
    new_method = new_impact_indicator_data_raw.get("method")
    new_category = new_impact_indicator_data_raw.get("category")
    new_impact_indicator_name = new_impact_indicator_data_raw.get("impactindicator")
    new_amount_raw = new_impact_indicator_data_raw.get("amount")
    new_unit_name = new_impact_indicator_data_raw.get("unitname")

    if not all([new_method, new_category, new_impact_indicator_name, new_unit_name]):
        db.session.rollback() # Rollback anche l'eliminazione
        return jsonify({"error": "I campi 'method', 'category', 'impactindicator' e 'unitname' sono obbligatori in 'new_impact_indicator_data'."}), 400

    try:
        new_amount = float(new_amount_raw) if new_amount_raw is not None else None
    except ValueError as e:
        db.session.rollback() # Rollback anche l'eliminazione
        return jsonify({"error": f"Formato 'amount' in 'new_impact_indicator_data' non valido: {e}. Deve essere numerico."}), 400

    # 3. Cerca un ImpactIndicator esistente o creane uno nuovo
    existing_new_indicator = ImpactIndicator.query.filter_by(
        impactmethodname=new_method,
        impactcategoryname=new_category,
        impactname=new_impact_indicator_name,
        amount=new_amount,
        unitname=new_unit_name
    ).first()

    final_impact_indicator_id = None
    message_new_indicator = ""

    if existing_new_indicator:
        final_impact_indicator_id = existing_new_indicator.impactindicatorid
        message_new_indicator = "Nuovo indicatore di impatto (o corrispondente) trovato e riutilizzato."
    else:
        new_indicator_obj = ImpactIndicator(
            impactmethodname=new_method,
            impactcategoryname=new_category,
            impactname=new_impact_indicator_name,
            amount=new_amount,
            unitname=new_unit_name
        )
        db.session.add(new_indicator_obj)
        try:
            db.session.flush() # Per ottenere l'ID del nuovo indicatore prima del commit finale
            final_impact_indicator_id = new_indicator_obj.impactindicatorid
            message_new_indicator = "Nuovo indicatore di impatto creato."
        except exc.IntegrityError as e:
            db.session.rollback()
            print(f"Errore di integrità durante la creazione del nuovo indicatore: {e}")
            return jsonify({"error": "Errore durante la creazione del nuovo indicatore di impatto. Potrebbe esserci un conflitto di dati."}), 409
        except Exception as e:
            db.session.rollback()
            print(f"Errore generico durante la creazione del nuovo indicatore: {e}")
            return jsonify({"error": f"Errore durante la creazione del nuovo indicatore di impatto: {str(e)}."}), 500

    # 4. Crea la Nuova Associazione Certificazione_ImpactIndicator
    # Prima di creare, assicurati che la NUOVA associazione non esista già (caso in cui si sta "modificando"
    # con lo stesso indicatore, ma questo scenario è gestito dalla logica di eliminazione/re-creazione implicita qui).
    # Tuttavia, è buona pratica fare un controllo finale per evitare IntegrityError se il cliente invia dati che
    # risultano nella stessa associazione vecchia/nuova.
    
    # Questo controllo è cruciale: se l'ID del vecchio indicatore è lo stesso del nuovo, e si tenta di ricreare
    # senza un'effettiva eliminazione, la transazione fallirà. L'approccio attuale elimina e poi ricrea.
    # Non è necessario un controllo esplicito qui se l'obiettivo è sempre eliminare e ricreare.
    
    new_association = Certificazione_ImpactIndicator(
        certificazioneid=certificazione_id_for_new_link,
        impactindicatorid=final_impact_indicator_id
    )
    db.session.add(new_association)
    message_new_association = "Nuova associazione marcata per la creazione."

    # 5. Commit di tutte le modifiche (eliminazione e nuovo inserimento)
    try:
        db.session.commit()
        return jsonify({
            "message": f"{message_deletion} {message_new_indicator} {message_new_association}",
            "old_certificazioneid": str(old_association_filters["certificazioneid"]),
            "old_impactindicatorid": str(old_association_filters["impactindicatorid"]),
            "new_certificazioneid": str(certificazione_id_for_new_link),
            "new_impactindicatorid": str(final_impact_indicator_id)
        }), 200 # OK, operazione di modifica completata

    except exc.IntegrityError as e:
        db.session.rollback()
        print(f"Errore di integrità durante il commit finale dell'associazione: {e}")
        # Questo errore potrebbe indicare che certificazione_id_for_new_link non esiste nel DB
        # o un altro vincolo violato.
        return jsonify({"error": "Errore di integrità del database durante la creazione della nuova associazione. Verifica gli ID forniti."}), 409
    except Exception as e:
        db.session.rollback()
        print(f"Errore durante il commit finale: {e}")
        return jsonify({"error": f"Errore durante l'operazione di modifica: {str(e)}. Contattare l'amministratore."}), 500
    
    
@certificazioni_bp.route("/certificazione-impact-indicator", methods=["DELETE"])
def delete_cert_impact_indicator_association():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Nessun dato fornito per l'eliminazione dell'associazione."}), 400

    # 1. Recupero e Validazione dei Dati di Input
    certificazione_id_str = data.get("certificazioneid")
    impact_indicator_id_str = data.get("impactindicatorid")

    # Entrambi gli ID sono obbligatori per identificare univocamente l'associazione
    if not certificazione_id_str or not impact_indicator_id_str:
        return jsonify({"error": "I campi 'certificazioneid' e 'impactindicatorid' sono obbligatori per eliminare l'associazione."}), 400

    try:
        certificazione_id = uuid.UUID(certificazione_id_str)
        impact_indicator_id = uuid.UUID(impact_indicator_id_str)
    except ValueError as e:
        return jsonify({"error": f"Formato ID non valido: {e}. Controlla che 'certificazioneid' e 'impactindicatorid' siano UUID validi."}), 400

    # 2. Trova l'Associazione da Eliminare
    association_to_delete = Certificazione_ImpactIndicator.query.filter_by(
        certificazioneid=certificazione_id,
        impactindicatorid=impact_indicator_id
    ).first()

    if not association_to_delete:
        return jsonify({"error": "Associazione non trovata con gli ID forniti. Nessuna eliminazione effettuata."}), 404

    # 3. Elimina l'Associazione
    try:
        db.session.delete(association_to_delete)
        db.session.commit()
        return jsonify({"message": "Associazione eliminata con successo."}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Errore durante l'eliminazione dell'associazione Certificazione_ImpactIndicator: {e}")
        return jsonify({"error": f"Errore durante l'eliminazione dell'associazione: {str(e)}. Contattare l'amministratore."}), 500

