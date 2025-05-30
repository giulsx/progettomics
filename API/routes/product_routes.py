# routes/product_routes.py

from flask import Blueprint, request, jsonify
from models import db, Product, User_Product, Activity, Product_Activity, ISICSection, User_Activity, Utente, Activity_IntermediateExchange, IntermediateExchange, Unit
from schemas import ActivitySchema, ISICSectionSchema
import uuid
import hashlib

product_bp = Blueprint("product_bp", __name__)

######## API PER LA CREAZIONE/SELEZIONE DI UN PRODOTTO #######

#INSERIMENTO DI UN PRODOTTO ALL'INTERNO DEL DB
@product_bp.route("/products", methods=["POST"])
def create_product():
    data = request.get_json()

    # Estrai i dati dal JSON
    productname = data["productname"]
    systemmodel = data["systemmodel"]
    intervallo = data["intervallo"]
    totale_produzione = data["totale_produzione"]
    userid = data["userid"]

    # Genera UUID basato su hash (deterministico)
    hash_input = f"{productname}{systemmodel}{userid}".encode("utf-8")
    hashed = hashlib.sha256(hash_input).hexdigest()
    productid = uuid.UUID(hashed[:32])  # Usa solo i primi 32 caratteri per un UUID valido

    # Crea il nuovo prodotto
    new_product = Product(
        productid=productid,
        productname=productname,
        systemmodel=systemmodel,
        intervallo=intervallo,
        totale_produzione=totale_produzione
    )
    db.session.add(new_product)

    # Aggiungi alla tabella di associazione
    association = User_Product(userid=userid, productid=productid)
    db.session.add(association)

    db.session.commit()

    return jsonify({"message": "Prodotto creato", "productid": str(productid)}), 201

#SUGGERIMENTO PRODOTTI GIà INSERITI (PER AUTOCOMPLETAMENTO)
@product_bp.route("/products/suggestions", methods=["GET"])
def suggest_products():
    userid = request.args.get("userid")
    query = request.args.get("query", "").lower()

    if not userid or not query:
        return jsonify({"error": "Missing userid or query"}), 400

    # Unisciti a User_Product per filtrare solo i prodotti dell'utente
    suggestions = (
        db.session.query(Product)
        .join(User_Product, Product.productid == User_Product.productid)
        .filter(User_Product.userid == userid)
        .filter(Product.productname.ilike(f"{query}%"))
        .all()
    )

    # Restituisci i dettagli dei prodotti trovati
    results = []
    for product in suggestions:
        results.append({
            "productid": str(product.productid),
            "productname": product.productname,
            "systemmodel": product.systemmodel,
            "intervallo": product.intervallo,
            "totale_produzione": product.totale_produzione
        })

    return jsonify(results), 200

######## API PER LA SEZIONE ESPLORA DATI#######

#RECUPERO DI TUTTE LE ISIC SECTION (per menù a tendina della tipologia)
@product_bp.route("/isicsections", methods=["GET"])
def get_isic_sections():
    isic_sections = ISICSection.query.all()
    schema = ISICSectionSchema(many=True)
    return jsonify(schema.dump(isic_sections))

#RECUPERO DELLE ATTIVITà FILTRATE PER ISIC SECTION SELEZIONATO E PER SYSTEMMODEL DEL PRODOTTO
@product_bp.route("/activities/filter", methods=["GET"])
def get_activities_by_isic_and_systemmodel():
    systemmodel = request.args.get("systemmodel")
    isicsection = request.args.get("isicsection")
    
    query = Activity.query
    if systemmodel:
        query = query.filter_by(systemmodel=systemmodel)
    if isicsection:
        query = query.filter_by(isicsection=isicsection)
    
    activities = query.all()
    schema = ActivitySchema(many=True)
    return jsonify(schema.dump(activities))

#OTTENIMENTO  GEOGRAPHY DELL'ATTIVITà SELEZIONATA 
@product_bp.route("/activities/<uuid:activity_id>", methods=["GET"])
def get_activity_details(activity_id):
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({"error": "Attività non trovata"}), 404
    schema = ActivitySchema()
    return jsonify(schema.dump(activity))

#OTTENIMENTO MEZZI DI TRASPORTO
@product_bp.route("/transport-activities", methods=["GET"])
def get_transport_activities():
    transport_activities = Activity.query.filter_by(isicsection="H - Transportation and storage").all()
    result = []
    for activity in transport_activities:
        result.append({
            "id": activity.id,
            "name": activity.name,
            "location": activity.location
        })
    return jsonify(result), 200

# OTTENIMENTO FORNITORE DI UN'ATTIVITÀ CREATA DA UN FORNITORE
@product_bp.route("/activities/<uuid:activity_id>/fornitore", methods=["GET"])
def get_activity_supplier(activity_id):
    # Verifica se l'attività esiste
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({"error": "Attività non trovata"}), 404

    # Trova gli ID degli utenti associati a questa attività
    user_activity_entries = User_Activity.query.filter_by(activityid=activity_id).all()
    user_ids = [ua.userid for ua in user_activity_entries]

    # Recupera il primo utente con ruolo 'fornitore'
    fornitore = (
        Utente.query.filter(Utente.userid.in_(user_ids), Utente.role.ilike("fornitore"))
        .first()
    )

    if fornitore:
        return jsonify({"fornitore": fornitore.username}), 200

    return jsonify({"fornitore": None}), 200

# OTTENIMENTO UNITA' DI MISURA DELL'ATTIVITÀ (PRODOTTO DI RIFERIMENTO)
@product_bp.route("/activities/<uuid:activity_id>/unita_misura", methods=["GET"])
def get_activity_unit(activity_id):
    # Cerca l'associazione con referenceproduct = True
    ref_assoc = Activity_IntermediateExchange.query.filter_by(
        activityid=activity_id, referenceproduct=True
    ).first()

    if not ref_assoc:
        return jsonify({"error": "Nessun prodotto di riferimento trovato per questa attività"}), 404

    # Recupera l'intermediate exchange
    intermediate = IntermediateExchange.query.get(ref_assoc.intermediateexchangeid)
    if not intermediate:
        return jsonify({"error": "IntermediateExchange non trovato"}), 404

    # Recupera l'unità di misura
    unit = Unit.query.get(intermediate.unitid)
    if not unit:
        return jsonify({"error": "Unità di misura non trovata"}), 404

    return jsonify({"unitname": unit.unitname}), 200

#INSERIMENTO ASSOCIAZIONE TRA PRODOTTO E ATTIVITà
#bisogna definire la quantità, fase_generale e fase_produttiva (es. materia prima, processo, ecc)
@product_bp.route("/product-activity", methods=["POST"])
def add_product_activity():
    data = request.json

    # Controllo dei campi obbligatori
    required_fields = ["productid", "activityid", "amount", "fase_generale", "fase_produttiva"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Campo obbligatorio mancante: {field}"}), 400

    # Verifica esistenza prodotto
    product = Product.query.get(data["productid"])
    if not product:
        return jsonify({"error": "Prodotto non trovato"}), 404

    # Verifica esistenza attività
    activity = Activity.query.get(data["activityid"])
    if not activity:
        return jsonify({"error": "Attività non trovata"}), 404

    # Crea nuova associazione
    new_association = Product_Activity(
        productid=data["productid"],
        activityid=data["activityid"],
        amount=data["amount"],
        fase_generale=data["fase_generale"],
        fase_produttiva=data["fase_produttiva"],
        distanza_fornitore=data.get("distanza_fornitore"),         # Opzionale
        id_mezzo_activity=data.get("id_mezzo_activity")            # Opzionale
    )

    # Salvataggio nel database
    db.session.add(new_association)
    db.session.commit()

    return jsonify({"message": "Associazione creata con successo"}), 201

#RIMOZIONE DI UN'ATTIVITà ASSOCIATA A UN PRODOTTO 
@product_bp.route("/products/<uuid:productid>/activities/<uuid:activityid>", methods=["DELETE"])
def remove_activity_from_product(productid, activityid):
    fase = request.args.get("fase")

    if not fase:
        return jsonify({"error": "Parametro 'fase' mancante"}), 400

    association = Product_Activity.query.filter_by(
        productid=productid,
        activityid=activityid,
        fase=fase
    ).first()

    if not association:
        return jsonify({"error": "Associazione non trovata"}), 404

    db.session.delete(association)
    db.session.commit()

    return jsonify({"message": "Attività rimossa dal prodotto"}), 200

#VISUALIZZAZIONE DI TUTTE LE ATTIVITà DI UNA FASE ASSOCIATE A UN PRODOTTO 
@product_bp.route("/products/<uuid:productid>/activities", methods=["GET"])
def get_activities_for_product_by_fase(productid):
    fase = request.args.get("fase")

    query = Product_Activity.query.filter_by(productid=productid)
    if fase:
        query = query.filter_by(fase=fase)

    associations = query.all()
    result = []

    for assoc in associations:
        activity = Activity.query.get(assoc.activityid)
        activity_data = ActivitySchema().dump(activity)
        activity_data.update({
            "amount": str(assoc.amount),
            "fase": assoc.fase
        })
        result.append(activity_data)

    return jsonify(result), 200

########API PER LA SEZIONE MODIFICA#######
