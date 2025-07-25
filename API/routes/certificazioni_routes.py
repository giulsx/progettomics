# routes/certificazioni_routes.py

from flask import Blueprint, request, jsonify, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database import db
from models import Certificazione, Certificazione_Product, Certificazione_ImpactIndicator, Product # Importa il modello di associazione
from schemas import CertificazioneSchema, ProductSchema # Non abbiamo più bisogno di CertificazioneProductSchema qui per il load
import uuid

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