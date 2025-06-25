###### per la modifica di attività
from flask import Blueprint, request, jsonify
from models import db, Activity, IntermediateExchange, ElementaryExchange, Activity_IntermediateExchange, Activity_ElementaryExchange
from utils.id_generatos import generate_activity_id, generate_intermediate_exchange_id, generate_elementary_exchange_id

activity_bp = Blueprint("activity", __name__)

@activity_bp.route("/activities/modify", methods=["POST"])
def modify_activity():
    data = request.get_json()

    # Dati base della nuova attività
    new_name = data.get("name")
    reference_product_name = data.get("reference_product_name")
    original_activity_id = data.get("original_activity_id")
    geography = data.get("geography")
    isicsection = data.get("isicsection")

    intermediate_exchanges = data.get("intermediate_exchanges", [])  # [{name, amount, action}]
    elementary_exchanges = data.get("elementary_exchanges", [])      # [{name, amount, action}]

    # Recupera attività originale
    original_activity = Activity.query.get(original_activity_id)
    if not original_activity:
        return jsonify({"error": "Attività originale non trovata"}), 404

    # Genera nuovo activityid
    new_activityid = generate_activity_id(new_name, reference_product_name)[0]

    # Crea nuova attività
    new_activity = Activity(
        id=new_activityid,
        activityname=new_name,
        geography=geography,
        isicsection=isicsection,
        systemmodel=original_activity.systemmodel,
        includedactivitiesstart=original_activity.includedactivitiesstart,
        includedactivitiesend=original_activity.includedactivitiesend,
        specialactivitytype=original_activity.specialactivitytype,
        generalcomment=original_activity.generalcomment,
        modifiedactivity=True
    )
    db.session.add(new_activity)

    # Reference product (intermediate exchange con amount=1)
    ref_intermediate_id = generate_intermediate_exchange_id(
        reference_product_name, 1, f"{new_name}_{reference_product_name}"
    )
    ref_intermediate = IntermediateExchange.query.get(ref_intermediate_id)

    if not ref_intermediate:
        ref_unitid = original_activity.intermediateexchanges[0].unitid if original_activity.intermediateexchanges else None
        ref_intermediate = IntermediateExchange(
            intermediateexchangeid=ref_intermediate_id,
            intermediatename=reference_product_name,
            amount=1,
            modifiedintermediate=True,
            unitid=ref_unitid
        )
        db.session.add(ref_intermediate)

    # Associazione reference product
    assoc_ref = Activity_IntermediateExchange(
        activityid=new_activityid,
        intermediateexchangeid=ref_intermediate_id,
        referenceproduct=True
    )
    db.session.add(assoc_ref)

    # Funzione per gestire exchanges
    def process_exchanges(exchange_list, is_intermediate=True):
        for exch in exchange_list:
            name = exch.get("name")
            amount = exch.get("amount")
            action = exch.get("action")

            if is_intermediate:
                id_exchange = generate_intermediate_exchange_id(name, amount, f"{new_name}_{name}")
                ExchangeModel = IntermediateExchange
                AssocModel = Activity_IntermediateExchange
                id_field = "intermediateexchangeid"
                modified_field = "modifiedintermediate"
                name_field = "intermediatename"
            else:
                id_exchange = generate_elementary_exchange_id(name, amount)
                ExchangeModel = ElementaryExchange
                AssocModel = Activity_ElementaryExchange
                id_field = "elementaryexchangeid"
                modified_field = "modifiedelementary"
                name_field = "elementaryname"

            if action == "remove":
                assoc = AssocModel.query.filter_by(
                    activityid=new_activityid,
                    **{id_field: id_exchange}
                ).first()
                if assoc:
                    db.session.delete(assoc)

            elif action in ("add", "modify"):
                existing_exch = ExchangeModel.query.get(id_exchange)
                if not existing_exch:
                    # Cerca un exchange con stesso nome per ricavare unitid
                    base_exch = ExchangeModel.query.filter_by(**{name_field: name}).first()
                    unitid = base_exch.unitid if base_exch else None

                    new_exch = ExchangeModel(
                        **{id_field: id_exchange},
                        **{modified_field: True},
                        amount=amount,
                        unitid=unitid,
                        intermediatename=name if is_intermediate else None,
                        elementaryname=name if not is_intermediate else None
                    )
                    db.session.add(new_exch)

                assoc = AssocModel.query.filter_by(
                    activityid=new_activityid,
                    **{id_field: id_exchange}
                ).first()

                if not assoc:
                    assoc = AssocModel(
                        activityid=new_activityid,
                        **{id_field: id_exchange},
                        referenceproduct=False
                    )
                    db.session.add(assoc)

    # Processa exchanges
    process_exchanges(intermediate_exchanges, is_intermediate=True)
    process_exchanges(elementary_exchanges, is_intermediate=False)

    db.session.commit()

    return jsonify({
        "message": "Attività modificata con successo",
        "new_activityid": str(new_activityid)
    }), 201
