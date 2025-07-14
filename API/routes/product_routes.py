# routes/product_routes.py

from flask import Blueprint, request, jsonify
from models import db, Product, User_Product, Activity, Product_Activity, ISICSection, User_Activity, Utente, Activity_IntermediateExchange, IntermediateExchange, Unit
from schemas import ActivitySchema, ISICSectionSchema, ProductSchema, UtenteSchema
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
    tipologiaprodotto = data["tipologiaprodotto"]
    anni_uso=data["anni_uso"]
    pesoprodotto=data["pesoprodotto"]
    
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
        totale_produzione=totale_produzione,
        tipologiaprodotto=tipologiaprodotto,
        anni_uso=anni_uso,
       pesoprodotto =pesoprodotto
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
            "totale_produzione": product.totale_produzione,
            "tipologiaprodotto": product.tipologiaprodotto,
            "pesoprodotto": product.pesoprodotto,
            "anni_uso": product.anni_uso
        })

    return jsonify(results), 200

######## API PER LA SEZIONE ESPLORA DATI#######

#RECUPERO DI TUTTE LE ISIC SECTION (per menù a tendina della tipologia)
@product_bp.route("/isicsections", methods=["GET"])
def get_isic_sections():
    isic_sections = ISICSection.query.all()
    schema = ISICSectionSchema(many=True)
    return jsonify(schema.dump(isic_sections))

#RECUPERO DI TUTTI I FORNITORI

@product_bp.route("/fornitori", methods=["GET"])
def get_all_fornitori():
    fornitori = Utente.query.filter_by(role="fornitore").all()
    schema = UtenteSchema(many=True)
    result = schema.dump(fornitori)
    return jsonify(result), 200


#RECUPERO DELLE ATTIVITà FILTRATE PER ISIC SECTION SELEZIONATO E PER SYSTEMMODEL DEL PRODOTTO
# !!! non ci sono i prodotti dei fornitori
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

#RECUPERO DI TUTTE LE ATTIVITà DEL DB e TUTTI I PRODOTTI DEI FORNITORE (FILTRATI PER SYSTEMMODEL)
@product_bp.route("/activitiesandproducts", methods=["GET"])
def get_activities_and_fornitori_products_by_systemmodel():
    systemmodel = request.args.get("systemmodel")

    # Recupero attività filtrate per systemmodel (se presente)
    query = Activity.query
    if systemmodel:
        query = query.filter_by(systemmodel=systemmodel)

    activities = query.all()
    activity_schema = ActivitySchema(many=True)
    activity_data = activity_schema.dump(activities)

    # Recupero prodotti associati a utenti 'fornitore' con lo stesso systemmodel
    fornitori_products_query = (
        db.session.query(Product)
        .join(User_Product, Product.id == User_Product.c.product_id)
        .join(Utente, User_Product.c.user_id == Utente.id)
        .filter(Utente.tipologia_attore == "fornitore")
    )
    if systemmodel:
        fornitori_products_query = fornitori_products_query.filter(Product.systemmodel == systemmodel)

    fornitori_products = fornitori_products_query.all()
    product_schema = ProductSchema(many=True)
    fornitori_data = product_schema.dump(fornitori_products)

    return jsonify({
        "activities": activity_data,
        "fornitori_products": fornitori_data
    })


#RECUPERO DI TUTTE LE ATTIVITà E PRODOTTI ASSOCIATI A UN FORNITORE
from flask import Blueprint, request, jsonify
from models import Utente, User_Activity, User_Product, Activity, Product
from schemas import ActivitySchema, ProductSchema
from database import db

bp = Blueprint('user_data', __name__)
activity_schema = ActivitySchema(many=True)
product_schema = ProductSchema(many=True)

@bp.route('/user/data', methods=['GET'])
def get_user_data():
    username = request.args.get('username')

    if not username:
        return jsonify({'error': 'Specificare almeno username'}), 400

    # Trova l'utente
    user = Utente.query.filter(
        (Utente.username == username)
    ).first()

    if not user:
        return jsonify({'error': 'Utente non trovato'}), 404

    # Recupera le attività associate
    activity_ids = db.session.query(User_Activity.activityid).filter_by(userid=user.userid).all()
    activity_ids = [a[0] for a in activity_ids]

    activities = Activity.query.filter(Activity.id.in_(activity_ids)).all()

    # Recupera i prodotti associati
    product_ids = db.session.query(User_Product.productid).filter_by(userid=user.userid).all()
    product_ids = [p[0] for p in product_ids]

    products = Product.query.filter(Product.productid.in_(product_ids)).all()

    return jsonify({
        'activities': activity_schema.dump(activities),
        'products': product_schema.dump(products)
    })

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
#bisogna definire la quantità, fase_generale e nome_risorsa (es. materia prima, processo, ecc)
@product_bp.route("/product-activity", methods=["POST"])
def add_product_activity():
    data = request.json

    # Controllo dei campi obbligatori
    required_fields = ["productid", "activityid", "amount", "fase_generale", "nome_risorsa"]
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
        productid=data["productid"], #obbligatorio
        activityid=data["activityid"], #obbligatorio
        amount=data["amount"], #obbligatorio
        fase_generale=data["fase_generale"], # obbligatorio
        nome_risorsa=data["nome_risorsa"], # obbligatorio
        fase_produttiva=data.get("fase_produttiva"), # Opzionale
        distanza_fornitore=data.get("distanza_fornitore"),         # Opzionale
        id_mezzo_activity=data.get("id_mezzo_activity")            # Opzionale
    )

    # Salvataggio nel database
    db.session.add(new_association)
    db.session.commit()

    return jsonify({"message": "Associazione creata con successo"}), 201

#INSERIMENTO DI UN PRODOTTO DEL FORNITORE ALL'INTERNO DI UN NUOVO PRODOTTO
@product_bp.route("/product/from-fornitore", methods=["POST"])
def create_product_with_fornitore_activities():
    data = request.json

    required_fields = [
        "new_product_id", 
        "fornitore_product_id",
        "amount",
        "fase_generale",
        "nome_risorsa"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Campo obbligatorio mancante: {field}"}), 400

    # Recupero prodotti
    new_product = Product.query.get(data["new_product_id"])
    if not new_product:
        return jsonify({"error": "Nuovo prodotto non trovato"}), 404

    fornitore_product = Product.query.get(data["fornitore_product_id"])
    if not fornitore_product:
        return jsonify({"error": "Prodotto del fornitore non trovato"}), 404

    # Recupera tutte le attività associate al prodotto del fornitore
    attività_fornitore = Product_Activity.query.filter_by(productid=fornitore_product.id).all()

    for associazione in attività_fornitore:

        nuova_associazione = Product_Activity(
            productid=new_product.id,
            activityid=associazione.activityid,
            amount=data["amount"],
            fase_generale=data["fase_generale"],
            nome_risorsa=data["nome_risorsa"],
            fase_produttiva=data.get("fase_produttiva"),
            distanza_fornitore=data.get("distanza_fornitore"),
            id_mezzo_activity=data.get("id_mezzo_activity"),
            prodottofornitore_id=fornitore_product.id  
        )
        db.session.add(nuova_associazione)

    db.session.commit()
    return jsonify({"message": "Attività del fornitore duplicate con valori personalizzati"}), 201


#RIMOZIONE DI UN'ATTIVITà (normale) ASSOCIATA A UN PRODOTTO 
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

#RIMOZIONE DI UN PRODOTTO FORNITORE ASSOCIATO A UN PRODOTTO
@product_bp.route("/products/<uuid:productid>/activities/from-fornitore/<uuid:prodottofornitore_id>", methods=["DELETE"])
def remove_activities_from_fornitore(productid, prodottofornitore_id):
    # Recupera tutte le associazioni da eliminare
    associazioni = Product_Activity.query.filter_by(
        productid=productid,
        prodottofornitore_id=prodottofornitore_id
    ).all()

    if not associazioni:
        return jsonify({"message": "Nessuna attività trovata per questo prodottofornitore_id"}), 404

    for assoc in associazioni:
        db.session.delete(assoc)

    db.session.commit()
    return jsonify({"message": f"{len(associazioni)} attività rimosse dal prodotto"}), 200

# RECUPERO DI TUTTE LE ATTIVITÀ E PRODOTTI (DEL FORNITORE) ASSOCIATI A UN PRODOTTO
@product_bp.route("/products/<uuid:productid>/activities/full", methods=["GET"])
def get_full_activities_for_product(productid):
    fase = request.args.get("fase")

    query = Product_Activity.query.filter_by(productid=productid)
    if fase:
        query = query.filter_by(fase=fase)

    associations = query.all()
    result = []

    for assoc in associations:
        if assoc.prodottofornitore_id:
            # È una riga derivata da un prodotto fornitore
            prodotto_fornitore = Product.query.get(assoc.prodottofornitore_id)
            result.append({
                "prodottofornitore_id": str(assoc.prodottofornitore_id),
                "nome_prodotto_fornitore": prodotto_fornitore.name if prodotto_fornitore else None,
                "amount": str(assoc.amount),
                "fase_generale": assoc.fase,
                "nome_risorsa": assoc.nome_risorsa,
                "fase_produttiva": assoc.fase_produttiva,
                "distanza_fornitore": assoc.distanza_fornitore,
                "id_mezzo_activity": str(assoc.id_mezzo_activity) if assoc.id_mezzo_activity else None
            })
        else:
            # Attività normale
            activity = Activity.query.get(assoc.activityid)
            activity_data = ActivitySchema().dump(activity)
            activity_data.update({
                "prodottofornitore_id": None,
                "amount": str(assoc.amount),
                "fase_generale": assoc.fase,
                "nome_risorsa": assoc.nome_risorsa,
                "fase_produttiva": assoc.fase_produttiva,
                "distanza_fornitore": assoc.distanza_fornitore,
                "id_mezzo_activity": str(assoc.id_mezzo_activity) if assoc.id_mezzo_activity else None
            })
            result.append(activity_data)

    return jsonify(result), 200
