from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from database import db 
import uuid
import decimal 
import logging

# Assicurati che i modelli importati qui corrispondano ESATTAMENTE a quelli in models.py
from models import Product_Activity, Activity, ElementaryExchange, CFs, IntermediateExchange, UnitaryImpact, Product, Activity_ElementaryExchange, Activity_IntermediateExchange 


# Crea un Blueprint per le rotte relative al calcolo dell'impatto
impact_bp = Blueprint('impact', __name__)

# Configura il logger per questo modulo
logger = logging.getLogger(__name__)

# --- LEGENDA DEI FATTORI DI SCALA EOL (resta invariata) ---
EOL_SCALE_FACTORS = {
    "e9502c59-061a-55b7-b841-2fca78477a55": decimal.Decimal('1.0'),
    "28dfb649-5d63-5f8f-bf68-695772c18b82": decimal.Decimal('1.0'),
    "515c2227-b8e9-5b19-bc72-4f3141754d3c": decimal.Decimal('-0.8'),
    "13deb0b8-6d7c-52f9-a95d-147273527761": decimal.Decimal('-0.8'),
    "23bc1bea-e6d4-52d0-9194-58ef8fb8e6e2": decimal.Decimal('-0.8'),
}

def get_scale_factor_for_activity(activity_id: uuid.UUID) -> decimal.Decimal:
    """
    Recupera il fattore di scala specifico per la fase EOL per una data activity_id
    dalla leggenda predefinita.
    """
    activity_id_str = str(activity_id) # Converti UUID in stringa per la ricerca nel dizionario
    
    scale_factor = EOL_SCALE_FACTORS.get(activity_id_str)
    
    if scale_factor is None:
        logger.warning(f"Fattore di scala EOL non trovato per activity_id: {activity_id_str}. Restituendo il valore predefinito di 1.0.")
        return decimal.Decimal('1.0')
    
    logger.debug(f"Fattore di scala EOL trovato per activity_id {activity_id_str}: {scale_factor}")
    return scale_factor


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
    filter_fase_generale: str | None = None,
    is_supplier_product: bool = False
) -> dict:
    logger.debug(f"\nINIZIO calcolo impatto totale per Product ID: {product_id} (Is Supplier Product: {is_supplier_product})")
    try:
        # Recupera il prodotto per ottenere il totale_produzione, pesoprodotto e anni_uso
        product = Product.query.get(product_id)
        if not product:
            logger.error(f"Prodotto con ID {product_id} non trovato. Impossibile calcolare l'impatto.")
            return {
                "unitary_impact": decimal.Decimal('0.0'),
                "total_overall_impact": decimal.Decimal('0.0'), # Nuovo campo
                "impacts_by_fase": {},
                "message": f"Prodotto con ID {product_id} non trovato."
            }

        product_activities = Product_Activity.query.filter_by(productid=product_id).all()
        logger.debug(f"Trovate {len(product_activities)} Product_Activity per {product_id}.")

        if not product_activities:
            logger.debug(f"Nessuna Product_Activity trovata per {product_id}. Ritorno 0.0.")
            return {
                "unitary_impact": decimal.Decimal('0.0'),
                "total_overall_impact": decimal.Decimal('0.0'), # Nuovo campo
                "impacts_by_fase": {},
                "message": f"Nessuna attività associata trovata per il prodotto con ID {product_id}."
            }

        total_unitary_impact_sum = decimal.Decimal('0.0') # Questo sarà l'impatto unitario
        impacts_by_fase = {}

        # Recupera pesoprodotto e anni_uso del prodotto principale
        product_pesoprodotto = decimal.Decimal(str(product.pesoprodotto)) if product.pesoprodotto is not None else decimal.Decimal('1.0')
        product_anni_uso = decimal.Decimal(str(product.anni_uso)) if product.anni_uso is not None else decimal.Decimal('1.0') # Recupera anni_uso
        logger.debug(f"Peso prodotto principale ({product_id}): {product_pesoprodotto}")
        logger.debug(f"Anni uso prodotto principale ({product_id}): {product_anni_uso}")


        for pa in product_activities:
            logger.debug(f"\nProcessing Product_Activity: productid={pa.productid}, activityid={pa.activityid}, prodottofornitore_id={pa.prodottofornitore_id}, fase_generale='{pa.fase_generale}', amount={pa.amount}, distanza_fornitore={pa.distanza_fornitore}")
            
            amount = decimal.Decimal(str(pa.amount)) if pa.amount is not None else decimal.Decimal('1.0')
            distanza_fornitore = decimal.Decimal(str(pa.distanza_fornitore)) if pa.distanza_fornitore is not None else decimal.Decimal('0.0')

            current_activity_impact_contribution = decimal.Decimal('0.0') # Contributo di questa PA all'impatto unitario del prodotto padre

            if pa.prodottofornitore_id:
                logger.debug(f"Prodotto fornitore trovato: {pa.prodottofornitore_id}. Richiamo ricorsivo.")
                
                supplier_product_results = calculate_product_total_impact_sqla(
                    pa.prodottofornitore_id, impact_name, impact_category_name, impact_method_name,
                    is_supplier_product=True 
                )
                
                supplier_unitary_impact_val = decimal.Decimal(str(supplier_product_results.get('unitary_impact', '0.0')))
                
                current_activity_impact_contribution = supplier_unitary_impact_val * amount 
                logger.debug(f"Impatto da prodotto fornitore ({pa.prodottofornitore_id}): {supplier_unitary_impact_val} (Unitario Fornitore) * {amount} (PA Amount) = {current_activity_impact_contribution}")
            else: # Questa è un'attività diretta (non un prodotto fornitore)
                if pa.activityid:
                    # --- LOGICA SPECIFICA PER LA FASE EOL ---
                    if pa.fase_generale and pa.fase_generale.lower() == 'eol':
                        logger.debug(f"Calcolo impatto per attività EOL: {pa.activityid}")
                        
                        eol_scale_factor = get_scale_factor_for_activity(pa.activityid)
                        
                        eol_activity_base_impact = calculate_activity_impact_sqla(
                            pa.activityid, impact_name, impact_category_name, impact_method_name, decimal.Decimal('1.0') 
                        )
                        
                        current_activity_impact_contribution = amount * product_pesoprodotto * eol_scale_factor * eol_activity_base_impact
                        logger.debug(f"Formula EOL: {amount} (PA Amount) * {product_pesoprodotto} (Product Peso) * {eol_scale_factor} (EOL Scale Factor) * {eol_activity_base_impact} (EOL Activity Base Impact) = {current_activity_impact_contribution}")
                    
                    # --- NUOVA LOGICA SPECIFICA PER LA FASE USO ---
                    elif pa.fase_generale and pa.fase_generale.lower() == 'uso':
                        logger.debug(f"Calcolo impatto per attività USO: {pa.activityid}")
                        
                        # Impatto unitario dell'attività USO
                        uso_activity_base_impact = calculate_activity_impact_sqla(
                            pa.activityid, impact_name, impact_category_name, impact_method_name, decimal.Decimal('1.0')
                        )
                        
                        # Formula USO: amount (della Product_Activity) * anni_uso (del Product) * impatto base attività
                        current_activity_impact_contribution = amount * product_anni_uso * uso_activity_base_impact
                        logger.debug(f"Formula USO: {amount} (PA Amount) * {product_anni_uso} (Product Anni Uso) * {uso_activity_base_impact} (USO Activity Base Impact) = {current_activity_impact_contribution}")
                    
                    else: # Logica per attività non EOL e non USO
                        logger.debug(f"Calcolo impatto per attività principale (non EOL/USO): {pa.activityid}")
                        current_activity_impact_contribution = calculate_activity_impact_sqla(
                            pa.activityid, impact_name, impact_category_name, impact_method_name, amount
                        )
                else:
                    logger.debug(f"Nessun activityid né prodottofornitore_id per questa Product_Activity. Impatto attività = 0.")

            if pa.coll_trasporto and distanza_fornitore > decimal.Decimal('0.0'): # Confronto con Decimal
                logger.debug(f"Calcolo impatto trasporto: {pa.coll_trasporto} con distanza {distanza_fornitore}")
                transport_impact_unit = calculate_activity_impact_sqla(
                    pa.coll_trasporto, impact_name, impact_category_name, impact_method_name, distanza_fornitore
                )
                current_activity_impact_contribution += transport_impact_unit
                logger.debug(f"Impatto trasporto aggiunto. Totale parziale contributo: {current_activity_impact_contribution}")
            
            if pa.coll_trattamento:
                logger.debug(f"Calcolo impatto trattamento: {pa.coll_trattamento}")
                treatment_impact_unit = calculate_activity_impact_sqla(
                    pa.coll_trattamento, impact_name, impact_category_name, impact_method_name, amount
                )
                current_activity_impact_contribution += treatment_impact_unit
                logger.debug(f"Impatto trattamento aggiunto. Totale parziale contributo: {current_activity_impact_contribution}")
            
            total_unitary_impact_sum += current_activity_impact_contribution # Aggiorna l'impatto unitario totale
            logger.debug(f"Impatto unitario cumulativo per Product {product_id}: {total_unitary_impact_sum}")

            if pa.fase_generale not in impacts_by_fase:
                impacts_by_fase[pa.fase_generale] = decimal.Decimal('0.0')
            impacts_by_fase[pa.fase_generale] += current_activity_impact_contribution
            logger.debug(f"Impatto unitario per fase '{pa.fase_generale}': {impacts_by_fase[pa.fase_generale]}")

        # RECUPERA IL totale_produzione del prodotto principale (non dei fornitori nella ricorsione)
        total_produzione = decimal.Decimal(str(product.totale_produzione)) if product.totale_produzione is not None else decimal.Decimal('1.0')
        logger.debug(f"Totale produzione per Product ID {product_id}: {total_produzione}")

        # Calcola l'impatto totale complessivo del prodotto principale
        total_overall_impact = total_unitary_impact_sum * total_produzione
        logger.debug(f"Impatto totale complessivo per Product ID {product_id}: {total_unitary_impact_sum} (Unitario) * {total_produzione} (Produzione) = {total_overall_impact}")


        # Applicare il filtro fase generale al risultato finale se richiesto
        if filter_fase_generale:
            logger.debug(f"Filtro fase generale attivo: '{filter_fase_generale}'")
            if filter_fase_generale in impacts_by_fase:
                filtered_unitary_impact = impacts_by_fase[filter_fase_generale]
                # L'impatto complessivo filtrato deve usare il totale_produzione del prodotto principale
                filtered_overall_impact = filtered_unitary_impact * total_produzione
                return {
                    "unitary_impact": filtered_unitary_impact,
                    "total_overall_impact": filtered_overall_impact, # Nuovo campo filtrato
                    "impacts_by_fase": {filter_fase_generale: filtered_unitary_impact}, # La fase filtrata ha solo l'impatto unitario
                    "message": f"Calcolo completato per la fase '{filter_fase_generale}' del prodotto {product_id}."
                }
            else:
                logger.debug(f"Fase '{filter_fase_generale}' non trovata tra gli impatti calcolati.")
                return {
                    "unitary_impact": decimal.Decimal('0.0'),
                    "total_overall_impact": decimal.Decimal('0.0'), # Nuovo campo
                    "impacts_by_fase": {},
                    "message": f"Nessun impatto trovato per la fase '{filter_fase_generale}' per il prodotto {product_id}."
                }
        
        logger.debug(f"Calcolo totale completato per Product ID {product_id}. Unitario: {total_unitary_impact_sum}, Complessivo: {total_overall_impact}, per fasi: {impacts_by_fase}")
        return {
            "unitary_impact": total_unitary_impact_sum,
            "total_overall_impact": total_overall_impact, # Nuovo campo
            "impacts_by_fase": impacts_by_fase, # Contiene gli impatti unitari per fase
            "message": f"Calcolo totale completato per il prodotto {product_id}."
        }

    except SQLAlchemyError as e:
        logger.error(f"ERRORE SQLAlchemy durante il calcolo dell'impatto totale per il prodotto {product_id}: {e}", exc_info=True)
        return {
            "unitary_impact": decimal.Decimal('0.0'),
            "total_overall_impact": decimal.Decimal('0.0'), # Nuovo campo
            "impacts_by_fase": {},
            "message": f"Errore del database durante il calcolo dell'impatto per il prodotto {product_id}: {str(e)}"
        }
    except Exception as e:
        logger.error(f"ERRORE Generico durante il calcolo dell'impatto totale per il prodotto {product_id}: {e}", exc_info=True)
        return {
            "unitary_impact": decimal.Decimal('0.0'),
            "total_overall_impact": decimal.Decimal('0.0'), # Nuovo campo
            "impacts_by_fase": {},
            "message": f"Errore interno del server durante il calcolo dell'impatto per il prodotto {product_id}: {str(e)}"
        }

# Funzione helper per convertire Decimal in stringhe per jsonify (resta invariata)
def convert_decimals_to_str(obj):
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    if isinstance(obj, dict):
        return {k: convert_decimals_to_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimals_to_str(elem) for elem in obj]
    return obj

# --- Endpoint API (resta invariato, gestirà il nuovo output) ---
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
    elif results['unitary_impact'] == decimal.Decimal('0.0') and ( # Controlla unitary_impact
        "Nessuna attività associata trovata" in results.get("message", "") or 
        "Nessun impatto trovato per la fase" in results.get("message", "") or
        "Prodotto con ID" in results.get("message", "") and "non trovato" in results.get("message", "")
    ):
        logger.debug(f"Ritorno 404: {results['message']}")
        return jsonify(json_results), 404
    
    logger.debug(f"Ritorno 200 con impatto unitario: {results['unitary_impact']} e impatto complessivo: {results['total_overall_impact']}")
    return jsonify(json_results), 200