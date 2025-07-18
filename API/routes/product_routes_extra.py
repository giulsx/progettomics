# routes/product_routes.py

from flask import Blueprint, request, jsonify
from models import db, Product, User_Product, Activity, Product_Activity, ISICSection, User_Activity, Utente, Activity_IntermediateExchange, IntermediateExchange, Unit
from schemas import ActivitySchema, ISICSectionSchema, ProductSchema, UtenteSchema
import uuid
import hashlib

product_bp = Blueprint("product_bp", __name__)


#OTTENIMENTO  GEOGRAPHY DELL'ATTIVITà SELEZIONATA 
@product_bp.route("/activities/<uuid:activity_id>", methods=["GET"])
def get_activity_details(activity_id):
    activity = Activity.query.get(activity_id)
    if not activity:
        return jsonify({"error": "Attività non trovata"}), 404
    schema = ActivitySchema()
    return jsonify(schema.dump(activity))

#OTTENIMENTO MEZZI DI TRASPORTO 
# probabilmmente non serve, sarà direttamente una lista di attività preselezionate

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

#RECUPERO DI TUTTE LE ATTIVITà DI UNA FASE ASSOCIATE A UN PRODOTTO 
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
            "fase_generale": assoc.fase
        })
        result.append(activity_data)

    return jsonify(result), 200

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
        coll_trasporto=data.get("coll_trasporto"),            # Opzionale
        coll_trattamento=data.get("coll_trattamento")  # Opzionale
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
            coll_trasporto=data.get("coll_trasporto"),
            coll_trattamento=data.get("coll_trattamento"),
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