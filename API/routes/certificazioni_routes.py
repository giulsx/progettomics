# routes/certificazioni_routes.py

from flask import Blueprint, request, jsonify, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database import db
from models import Certificazione, Certificazione_Product # Importa il modello di associazione
from schemas import CertificazioneSchema # Non abbiamo più bisogno di CertificazioneProductSchema qui per il load
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