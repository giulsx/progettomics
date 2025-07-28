from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from database import db 
import uuid
import decimal 
import logging # Importa il modulo logging

# Assicurati che i modelli importati qui corrispondano ESATTAMENTE a quelli in models.py
from models import Product_Activity, Activity, ElementaryExchange, CFs, IntermediateExchange, UnitaryImpact, Product, Activity_ElementaryExchange, Activity_IntermediateExchange 


# Crea un Blueprint per le rotte relative al calcolo dell'impatto
impact_bp = Blueprint('impact', __name__)

# Configura il logger per questo modulo
# Assicurati di configurare logging.basicConfig() nella tua app Flask principale (es. app.py)
logger = logging.getLogger(__name__)

def get_system_model_sqla(activity_id: uuid.UUID) -> str | None:
    """
    Recupera il system_model dalla tabella 'activity' dato l'activity_id usando SQLAlchemy.
    """
    try:
        activity = Activity.query.get(activity_id)
        if activity:
            return activity.systemmodel
        logger.debug(f"System model non trovato per activity_id: {activity_id}")
        return None
    except SQLAlchemyError as e:
        logger.error(f"Errore SQLAlchemy durante il recupero del system_model per activity {activity_id}: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"Errore generico durante il recupero del system_model per activity {activity_id}: {e}", exc_info=True)
        return None

def calculate_activity_impact_sqla(
    activity_id: uuid.UUID,
    impact_name: str,
    impact_category_name: str,
    impact_method_name: str,
    amount: decimal.Decimal = decimal.Decimal('1.0') # Utilizzo Decimal come tipo predefinito
) -> decimal.Decimal: # Il valore di ritorno è Decimal
    """
    Calcola l'impatto di una singola attività usando SQLAlchemy.
    Accetta un parametro 'amount' per la moltiplicazione dell'impatto.
    """
    logger.debug(f"\nINIZIO calcolo impatto per Activity ID: {activity_id}")
    logger.debug(f"Parametri impatto: Name='{impact_name}', Category='{impact_category_name}', Method='{impact_method_name}'")
    logger.debug(f"Amount dell'attività (parametro input): {amount}")

    try:
        system_model = get_system_model_sqla(activity_id)
        logger.debug(f"System Model recuperato: {system_model}")
        if not system_model:
            logger.error(f"Errore: system_model non trovato per l'activity_id {activity_id}. Impatto calcolato come 0.")
            return decimal.Decimal('0.0')

        total_impact_elementary = decimal.Decimal('0.0')
        total_impact_intermediate = decimal.Decimal('0.0')

        # --- Calcolo impatto scambi elementari ---
        elementary_exchange_ids_rows = db.session.query(Activity_ElementaryExchange.elementaryexchangeid).filter(
            Activity_ElementaryExchange.activityid == activity_id
        ).all()
        elementary_exchange_ids = [row[0] for row in elementary_exchange_ids_rows]
        logger.debug(f"ID scambi elementari per {activity_id}: {elementary_exchange_ids}")

        if elementary_exchange_ids:
            elementary_exchanges = ElementaryExchange.query.filter(
                ElementaryExchange.elementaryexchangeid.in_(elementary_exchange_ids)
            ).all()
            logger.debug(f"Trovati {len(elementary_exchanges)} scambi elementari.")

            for ee in elementary_exchanges:
                logger.debug(f"Processing Elementary Exchange: ID={ee.elementaryexchangeid}, Name='{ee.elementaryname}', Amount={ee.amount}")
                
                cf = CFs.query.filter_by(
                    elementaryname=ee.elementaryname,
                    impactname=impact_name,
                    impactcategoryname=impact_category_name,
                    impactmethodname=impact_method_name      
                ).first()
                
                logger.debug(f"CF query for elementaryname='{ee.elementaryname}', impactcategoryname='{impact_category_name}', impactmethodname='{impact_method_name}': {'CF FOUND with value ' + str(cf.cf) if cf and cf.cf is not None else 'CF NOT FOUND'}")
                
                # Conversione sicura a Decimal
                cf_value = decimal.Decimal(str(cf.cf)) if cf and cf.cf is not None else decimal.Decimal('0.0')
                ee_amount_decimal = decimal.Decimal(str(ee.amount or '0.0')) 
                
                current_elementary_impact = ee_amount_decimal * cf_value
                logger.debug(f"Calc Elementary Impact: {ee_amount_decimal} (ee.amount) * {cf_value} (CF) = {current_elementary_impact}")
                total_impact_elementary += current_elementary_impact 
            logger.debug(f"Totale impatto scambi elementari per {activity_id}: {total_impact_elementary}")

        # --- Calcolo impatto scambi intermedi ---
        intermediate_exchange_ids_rows = db.session.query(Activity_IntermediateExchange.intermediateexchangeid).filter(
            Activity_IntermediateExchange.activityid == activity_id,
            Activity_IntermediateExchange.referenceproduct == False # Filtra i prodotti di riferimento
        ).all()
        intermediate_exchange_ids = [row[0] for row in intermediate_exchange_ids_rows]
        logger.debug(f"ID scambi intermedi per {activity_id}: {intermediate_exchange_ids}")

        if intermediate_exchange_ids:
            intermediate_exchanges = IntermediateExchange.query.filter(
                IntermediateExchange.intermediateexchangeid.in_(intermediate_exchange_ids)
            ).all()
            logger.debug(f"Trovati {len(intermediate_exchanges)} scambi intermedi.")

            for ie in intermediate_exchanges:
                logger.debug(f"Processing Intermediate Exchange: ID={ie.intermediateexchangeid}, Name='{ie.intermediatename}', ActivityProductID='{ie.activityid_productid}', Amount={ie.amount}")
                
                unitary_impact = UnitaryImpact.query.filter_by(
                    activityid_productid=ie.activityid_productid,
                    impactname=impact_name,
                    impactcategoryname=impact_category_name,
                    impactmethodname=impact_method_name,
                ).first()
                
                logger.debug(f"UnitaryImpact query for activityid_productid='{ie.activityid_productid}', impactcategoryname='{impact_category_name}', impactmethodname='{impact_method_name}': {'UNITARY IMPACT FOUND with value ' + str(unitary_impact.value) if unitary_impact and unitary_impact.value is not None else 'UNITARY IMPACT NOT FOUND'}")
                
                # Conversione sicura a Decimal
                unitary_impact_value = decimal.Decimal(str(unitary_impact.value)) if unitary_impact and unitary_impact.value is not None else decimal.Decimal('0.0')
                ie_amount_decimal = decimal.Decimal(str(ie.amount or '0.0')) 
                
                current_intermediate_impact = ie_amount_decimal * unitary_impact_value
                logger.debug(f"Calc Intermediate Impact: {ie_amount_decimal} (ie.amount) * {unitary_impact_value} (UI Value) = {current_intermediate_impact}")
                total_impact_intermediate += current_intermediate_impact 
            logger.debug(f"Totale impatto scambi intermedi per {activity_id}: {total_impact_intermediate}")

        final_activity_impact_unscaled = total_impact_elementary + total_impact_intermediate
        final_activity_impact = final_activity_impact_unscaled * amount
        logger.debug(f"Impatto totale attività {activity_id} (elementare + intermedio): {final_activity_impact_unscaled}")
        logger.debug(f"Impatto finale attività {activity_id} (moltiplicato per amount={amount}): {final_activity_impact}")
        return final_activity_impact

    except SQLAlchemyError as e:
        logger.error(f"ERRORE SQLAlchemy durante il calcolo dell'impatto per activity {activity_id}: {e}", exc_info=True)
        return decimal.Decimal('0.0')
    except Exception as e:
        logger.error(f"ERRORE Generico durante il calcolo dell'impatto per activity {activity_id}: {e}", exc_info=True)
        return decimal.Decimal('0.0')

def calculate_product_total_impact_sqla(
    product_id: uuid.UUID,
    impact_name: str,
    impact_category_name: str,
    impact_method_name: str,
    filter_fase_generale: str | None = None
) -> dict:
    logger.debug(f"\nINIZIO calcolo impatto totale per Product ID: {product_id}")
    try:
        product_activities = Product_Activity.query.filter_by(productid=product_id).all()
        logger.debug(f"Trovate {len(product_activities)} Product_Activity per {product_id}.")

        if not product_activities:
            logger.debug(f"Nessuna Product_Activity trovata per {product_id}. Ritorno 0.0.")
            return {
                "total_impact": decimal.Decimal('0.0'),
                "impacts_by_fase": {},
                "message": f"Nessuna attività associata trovata per il prodotto con ID {product_id}."
            }

        total_impact = decimal.Decimal('0.0')
        impacts_by_fase = {}

        for pa in product_activities:
            logger.debug(f"\nProcessing Product_Activity: productid={pa.productid}, activityid={pa.activityid}, prodottofornitore_id={pa.prodottofornitore_id}, fase_generale='{pa.fase_generale}', amount={pa.amount}, distanza_fornitore={pa.distanza_fornitore}")
            
            # Utilizzo di Decimal per amount e distanza_fornitore
            amount = decimal.Decimal(str(pa.amount)) if pa.amount is not None else decimal.Decimal('1.0')
            distanza_fornitore = decimal.Decimal(str(pa.distanza_fornitore)) if pa.distanza_fornitore is not None else decimal.Decimal('0.0')

            current_activity_impact = decimal.Decimal('0.0')

            if pa.prodottofornitore_id:
                logger.debug(f"Prodotto fornitore trovato: {pa.prodottofornitore_id}. Richiamo ricorsivo.")
                product_supplier_results = calculate_product_total_impact_sqla(
                    pa.prodottofornitore_id, impact_name, impact_category_name, impact_method_name
                )
                # Assicurati che total_impact del risultato ricorsivo sia un Decimal
                supplier_total_impact = decimal.Decimal(str(product_supplier_results.get('total_impact', '0.0')))
                current_activity_impact = supplier_total_impact * amount
                logger.debug(f"Impatto da prodotto fornitore ({pa.prodottofornitore_id}): {supplier_total_impact} * {amount} = {current_activity_impact}")
            else:
                if pa.activityid:
                    logger.debug(f"Calcolo impatto per attività principale: {pa.activityid}")
                    current_activity_impact = calculate_activity_impact_sqla(
                        pa.activityid, impact_name, impact_category_name, impact_method_name, amount
                    )
                else:
                    logger.debug(f"Nessun activityid né prodottofornitore_id per questa Product_Activity. Impatto attività = 0.")

            if pa.coll_trasporto and distanza_fornitore > decimal.Decimal('0.0'): # Confronto con Decimal
                logger.debug(f"Calcolo impatto trasporto: {pa.coll_trasporto} con distanza {distanza_fornitore}")
                transport_impact = calculate_activity_impact_sqla(
                    pa.coll_trasporto, impact_name, impact_category_name, impact_method_name, distanza_fornitore
                )
                current_activity_impact += transport_impact
                logger.debug(f"Impatto trasporto aggiunto. Totale parziale: {current_activity_impact}")
            
            if pa.coll_trattamento:
                logger.debug(f"Calcolo impatto trattamento: {pa.coll_trattamento}")
                treatment_impact = calculate_activity_impact_sqla(
                    pa.coll_trattamento, impact_name, impact_category_name, impact_method_name, amount
                )
                current_activity_impact += treatment_impact
                logger.debug(f"Impatto trattamento aggiunto. Totale parziale: {current_activity_impact}")
            
            total_impact += current_activity_impact
            logger.debug(f"Impatto cumulativo per Product {product_id}: {total_impact}")

            if pa.fase_generale not in impacts_by_fase:
                impacts_by_fase[pa.fase_generale] = decimal.Decimal('0.0')
            impacts_by_fase[pa.fase_generale] += current_activity_impact
            logger.debug(f"Impatto per fase '{pa.fase_generale}': {impacts_by_fase[pa.fase_generale]}")

        if filter_fase_generale:
            logger.debug(f"Filtro fase generale attivo: '{filter_fase_generale}'")
            if filter_fase_generale in impacts_by_fase:
                filtered_total_impact = impacts_by_fase[filter_fase_generale]
                return {
                    "total_impact": filtered_total_impact,
                    "impacts_by_fase": {filter_fase_generale: filtered_total_impact},
                    "message": f"Calcolo completato per la fase '{filter_fase_generale}' del prodotto {product_id}."
                }
            else:
                logger.debug(f"Fase '{filter_fase_generale}' non trovata tra gli impatti calcolati.")
                return {
                    "total_impact": decimal.Decimal('0.0'),
                    "impacts_by_fase": {},
                    "message": f"Nessun impatto trovato per la fase '{filter_fase_generale}' per il prodotto {product_id}."
                }
        
        logger.debug(f"Calcolo totale completato per Product ID {product_id}. Totale: {total_impact}, per fasi: {impacts_by_fase}")
        return {
            "total_impact": total_impact,
            "impacts_by_fase": impacts_by_fase,
            "message": f"Calcolo totale completato per il prodotto {product_id}."
        }

    except SQLAlchemyError as e:
        logger.error(f"ERRORE SQLAlchemy durante il calcolo dell'impatto totale per il prodotto {product_id}: {e}", exc_info=True)
        return {
            "total_impact": decimal.Decimal('0.0'),
            "impacts_by_fase": {},
            "message": f"Errore del database durante il calcolo dell'impatto per il prodotto {product_id}: {str(e)}"
        }
    except Exception as e:
        logger.error(f"ERRORE Generico durante il calcolo dell'impatto totale per il prodotto {product_id}: {e}", exc_info=True)
        return {
            "total_impact": decimal.Decimal('0.0'),
            "impacts_by_fase": {},
            "message": f"Errore interno del server durante il calcolo dell'impatto per il prodotto {product_id}: {str(e)}"
        }

# Funzione helper per convertire Decimal in stringhe per jsonify
def convert_decimals_to_str(obj):
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    if isinstance(obj, dict):
        return {k: convert_decimals_to_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimals_to_str(elem) for elem in obj]
    return obj

# --- Endpoint API ---
@impact_bp.route('/calculate_product_impact', methods=['GET'])
def get_product_impact():
    product_id_str = request.args.get('productId')
    impact_name = request.args.get('impactName', 'global warming potential (GWP100)')
    impact_category_name = request.args.get('impactCategoryName', 'climate change')
    impact_method_name = request.args.get('impactMethodName', 'EF v3.0')
    filter_fase_generale = request.args.get('filterFaseGenerale')

    logger.debug(f"Richiesta API ricevuta per Product ID: {product_id_str}, Categoria: '{impact_category_name}', Metodo: '{impact_method_name}'")

    if not product_id_str:
        logger.debug("'productId' mancante.")
        return jsonify({"error": "Parametro 'productId' mancante."}), 400
    
    try:
        product_id = uuid.UUID(product_id_str)
    except ValueError:
        logger.debug(f"Formato 'productId' non valido: {product_id_str}.")
        return jsonify({"error": "Formato 'productId' non valido. Deve essere un UUID valido."}), 400

    results = calculate_product_total_impact_sqla(
        product_id, 
        impact_name, 
        impact_category_name, 
        impact_method_name, 
        filter_fase_generale
    )
    
    json_results = convert_decimals_to_str(results)

    if "Errore del database" in results.get("message", "") or "Errore interno del server" in results.get("message", ""):
        logger.error(f"Ritorno 500: {results['message']}")
        return jsonify({"error": results["message"]}), 500
    elif results['total_impact'] == decimal.Decimal('0.0') and (
        "Nessuna attività associata trovata" in results.get("message", "") or 
        "Nessun impatto trovato per la fase" in results.get("message", "")
    ):
        logger.debug(f"Ritorno 404: {results['message']}")
        return jsonify(json_results), 404
    
    logger.debug(f"Ritorno 200 con impatto: {results['total_impact']}")
    return jsonify(json_results), 200