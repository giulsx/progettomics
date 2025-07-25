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

#AGGIORNAMENTO DI UN PRODOTTO
# MODIFICA DI UN PRODOTTO ESISTENTE NEL DB
@product_bp.route("/products/<uuid:productid>", methods=["PUT"])
def update_product(productid):
    data = request.get_json()

    # Cerca il prodotto per ID
    product = Product.query.get(productid)

    if not product:
        return jsonify({"error": "Prodotto non trovato"}), 404

    # Aggiorna solo i campi forniti nel JSON
    if "productname" in data:
        product.productname = data["productname"]
    if "systemmodel" in data:
        product.systemmodel = data["systemmodel"]
    if "intervallo" in data:
        product.intervallo = data["intervallo"]
    if "totale_produzione" in data:
        product.totale_produzione = data["totale_produzione"]
    if "tipologiaprodotto" in data:
        product.tipologiaprodotto = data["tipologiaprodotto"]
    if "anni_uso" in data:
        product.anni_uso = data["anni_uso"]
    if "pesoprodotto" in data:
        product.pesoprodotto = data["pesoprodotto"]

    try:
        db.session.commit()
        return jsonify({"message": f"Prodotto {productid} aggiornato con successo"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Errore durante l'aggiornamento del prodotto: {str(e)}"}), 500

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

#RECUPERO DEI 4 TRASPORTI
@product_bp.route("/mezzi-trasporto", methods=["GET"])
def get_mezzi_trasporto():
    mezzi = {
        "Nave": "986ee593-2dc9-526f-99e0-dbaafe0e91ab",
        "Aereo": "cfa30dd4-e6cf-584f-a083-4225169a8f49",
        "Treno": "3a6c3dff-4a80-55f1-8042-43ea1982b685",
        "Camion": "404e4cd3-7e0e-548a-b5da-caa303df3a0a"
    }
    return jsonify(mezzi)

#RECUPERO ATTIVITà PER L'EoL
@product_bp.route("/EoL", methods=["GET"])
def get_eol():
    eol = {
        "Discarica": "e9502c59-061a-55b7-b841-2fca78477a55",
        "Incenerimento": "28dfb649-5d63-5f8f-bf68-695772c18b82",
        "Riciclo tessuto sintetico": "515c2227-b8e9-5b19-bc72-4f3141754d3c",
        "Riciclo tessuto naturale": "13deb0b8-6d7c-52f9-a95d-147273527761",
        "Riciclo materiali plastici": "23bc1bea-e6d4-52d0-9194-58ef8fb8e6e2"
    }
    return jsonify(eol)


#RECUPERO DI TUTTE LE ATTIVITà DEL DB e TUTTI I PRODOTTI DEI FORNITORE (FILTRATI PER SYSTEMMODEL)
# SENZA FILTRI (API che stiamo usando attualmente)
@product_bp.route("/activitiesandproductsnofiltri", methods=["GET"])
def get_activities_and_fornitori_products_by_systemmodel1():
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
        .join(User_Product, Product.productid == User_Product.productid)
        .join(Utente, User_Product.userid == Utente.userid)
        .filter(Utente.role == "fornitore")
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

# RECUPERO DI TUTTE LE ATTIVITà DEL DB e TUTTI I PRODOTTI DEI FORNITORE (FILTRATI PER SYSTEMMODEL)
# SENZA FILTRI ma con dettagli come unità di misura e nome del prodotto di riferimento
@product_bp.route("/activitiesandproductsnofiltridetails", methods=["GET"])
def get_activities_and_fornitori_products_by_systemmodel_details():
    systemmodel = request.args.get("systemmodel")

    # Recupero attività con dettagli aggiuntivi (reference_product_name, reference_product_unit)
    activity_query = (
        db.session.query(
            Activity,
            IntermediateExchange.intermediatename.label("reference_product_name"),
            Unit.unitname.label("reference_product_unit")
        )
        .outerjoin(Activity_IntermediateExchange,
                   (Activity.id == Activity_IntermediateExchange.activityid) &
                   (Activity_IntermediateExchange.referenceproduct == True))
        .outerjoin(IntermediateExchange,
                   Activity_IntermediateExchange.intermediateexchangeid == IntermediateExchange.intermediateexchangeid)
        .outerjoin(Unit,
                   IntermediateExchange.unitid == Unit.unitid)
    )

    if systemmodel:
        activity_query = activity_query.filter(Activity.systemmodel == systemmodel)

    activities_with_details = activity_query.all()
    
    activity_data = []
    for activity, ref_prod_name, ref_prod_unit in activities_with_details:
        activity_dict = ActivitySchema().dump(activity) # Serializza l'oggetto Activity
        activity_dict["reference_product_name"] = ref_prod_name
        activity_dict["reference_product_unit"] = ref_prod_unit
        activity_data.append(activity_dict)

    # Recupero prodotti associati a utenti 'fornitore' con lo stesso systemmodel
    fornitori_products_query = (
        db.session.query(Product)
        .join(User_Product, Product.productid == User_Product.productid)
        .join(Utente, User_Product.userid == Utente.userid)
        .filter(Utente.role == "fornitore")
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

#RECUPERO DI TUTTE LE ATTIVITà DEL DB e TUTTI I PRODOTTI DEI FORNITORE (FILTRATI PER SYSTEMMODEL)
# CON FILTRI

# RECUPERO DI TUTTE LE ATTIVITà DAL DB E TUTTI I PRODOTTI DEI FORNITORI
# FILTRATI PER SYSTEMMODEL, TIPOLOGIA (ISICSection) E FORNITORE
@product_bp.route("/activitiesandproductsfiltri", methods=["GET"])
def get_activities_and_fornitori_products_by_filters2():
    systemmodel = request.args.get("systemmodel")
    tipologia = request.args.get("tipologia")  # ID della ISICSection
    fornitore_id = request.args.get("fornitoreid")  # ID dell'Utente fornitore

    # --- Filtri per le Attività ---
    activity_query = Activity.query

    if systemmodel:
        activity_query = activity_query.filter_by(systemmodel=systemmodel)
    
    if tipologia:
        # Assumendo che la tabella Activity abbia un campo isicsection_id o simile
        # Altrimenti, devi fare un join con ISICSection se la relazione è indiretta
        activity_query = activity_query.filter_by(isicsection=tipologia) 
    
    if fornitore_id:
        # Se le attività sono associate a fornitori tramite User_Activity (o simile)
        # Dovrai fare un join con User_Activity e Utente
        # Questa parte è un'ipotesi, adatta al tuo modello dati reale per Activity-Utente
        activity_query = (
            activity_query
            .join(User_Activity, Activity.id == User_Activity.activityid)
            .filter(User_Activity.userid == fornitore_id)
        )

    activities = activity_query.all()
    activity_schema = ActivitySchema(many=True)
    activity_data = activity_schema.dump(activities)

    # --- Filtri per i Prodotti dei Fornitori ---
    fornitori_products_query = (
        db.session.query(Product)
        .join(User_Product, Product.productid == User_Product.productid)
        .join(Utente, User_Product.userid == Utente.userid)
        .filter(Utente.role == "fornitore")
    )
    
    if systemmodel:
        fornitori_products_query = fornitori_products_query.filter(Product.systemmodel == systemmodel)

    if tipologia:
        # Assumendo che la tabella Product abbia un campo isicsection_id o simile
        # Altrimenti, devi fare un join con ISICSection se la relazione è indiretta
        fornitori_products_query = fornitori_products_query.filter(Product.tipologiaprodotto == tipologia) # Usiamo tipologiaprodotto se è l'ISIC ID
    
    if fornitore_id:
        fornitori_products_query = fornitori_products_query.filter(Utente.userid == fornitore_id)

    fornitori_products = fornitori_products_query.all()
    product_schema = ProductSchema(many=True)
    fornitori_data = product_schema.dump(fornitori_products)

    return jsonify({
        "activities": activity_data,
        "fornitori_products": fornitori_data
    })

# RECUPERO DI TUTTE LE ATTIVITà DAL DB E TUTTI I PRODOTTI DEI FORNITORI
# FILTRATI PER SYSTEMMODEL, TIPOLOGIA (ISICSection) E FORNITORE,
# CON DETTAGLI DEL PRODOTTO DI RIFERIMENTO PER LE ATTIVITÀ
@product_bp.route("/activitiesandproductswithdetails", methods=["GET"])
def get_activities_and_fornitori_products_by_filters():
    systemmodel = request.args.get("systemmodel")
    tipologia_id = request.args.get("tipologiaid") # ID della ISICSection
    fornitore_id = request.args.get("fornitoreid") # ID dell'Utente fornitore
 
    # --- Filtri e dati aggiuntivi per le Attività ---
    # Iniziamo la query selezionando l'Activity e aggiungendo i campi che vogliamo
    activity_query = (
        db.session.query(
            Activity,
            IntermediateExchange.intermediatename.label("reference_product_name"),
            Unit.unitname.label("reference_product_unit")
        )
        .outerjoin(Activity_IntermediateExchange, (Activity.id == Activity_IntermediateExchange.activityid) & (Activity_IntermediateExchange.referenceproduct == True))
        .outerjoin(IntermediateExchange, Activity_IntermediateExchange.intermediateexchangeid == IntermediateExchange.intermediateexchangeid)
        .outerjoin(Unit, IntermediateExchange.unitid == Unit.unitid)
    )
    if systemmodel:
        activity_query = activity_query.filter(Activity.systemmodel == systemmodel)
    if tipologia_id:
        # Assumendo che la tabella Activity abbia un campo isicsection_id o simile
        activity_query = activity_query.filter(Activity.isicsection_id == tipologia_id)
    if fornitore_id:
        # Se le attività sono associate a fornitori tramite User_Activity (o simile)
        activity_query = (
            activity_query
            .join(User_Activity, Activity.id == User_Activity.activityid)
            .filter(User_Activity.userid == fornitore_id)
        )
    activities_with_details = activity_query.all()
    activity_data = []
    for activity, ref_prod_name, ref_prod_unit in activities_with_details:
        activity_dict = ActivitySchema().dump(activity) # Serializza l'oggetto Activity
        activity_dict["reference_product_name"] = ref_prod_name
        activity_dict["reference_product_unit"] = ref_prod_unit
        activity_data.append(activity_dict)
 
    # --- Filtri per i Prodotti dei Fornitori (logica invariata) ---
    fornitori_products_query = (
        db.session.query(Product, Utente.userid) # Aggiungi Utente.userid qui
        .join(User_Product, Product.productid == User_Product.productid)
        .join(Utente, User_Product.userid == Utente.userid)
        .filter(Utente.role == "fornitore")
    )
   
    if systemmodel:
        fornitori_products_query = fornitori_products_query.filter(Product.systemmodel == systemmodel)
 
    if tipologia_id:
        fornitori_products_query = fornitori_products_query.filter(Product.tipologiaprodotto == tipologia_id)
   
    if fornitore_id:
        fornitori_products_query = fornitori_products_query.filter(Utente.userid == fornitore_id)
 
    fornitori_products_with_userid = fornitori_products_query.all() # Ora contiene tuple (Product, userid)
   
    fornitori_data = []
    for product, user_id in fornitori_products_with_userid:
        product_dict = ProductSchema().dump(product)
        product_dict["fornitoreid"] = str(user_id) # Aggiungi fornitoreid
        fornitori_data.append(product_dict)
 
    return jsonify({
        "activities": activity_data,
        "fornitori_products": fornitori_data
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


# INSERIMENTO ASSOCIAZIONE PORDOTTOFORNTITORE/ATTIVIà a UN NUOVO PRODOTTO
@product_bp.route("/product-activity", methods=["POST"])
def add_product_or_fornitore_activity():
    data = request.json

    # Controllo campo base
    if "productid" not in data:
        return jsonify({"error": "Campo obbligatorio mancante: productid"}), 400

    # Verifica esistenza prodotto base
    product = Product.query.get(data["productid"])
    if not product:
        return jsonify({"error": "Prodotto non trovato"}), 404

    # Caso A: attività normale
    if "activityid" in data:
        required_fields = ["activityid", "amount", "fase_generale", "nome_risorsa"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obbligatorio mancante: {field}"}), 400

        # Verifica attività
        activity = Activity.query.get(data["activityid"])
        if not activity:
            return jsonify({"error": "Attività non trovata"}), 404

        new_association = Product_Activity(
            productid=data["productid"],
            activityid=data["activityid"],
            amount=data["amount"],
            fase_generale=data["fase_generale"],
            nome_risorsa=data["nome_risorsa"],
            fase_produttiva=data.get("fase_produttiva"),
            distanza_fornitore=data.get("distanza_fornitore"),
            coll_trasporto=data.get("coll_trasporto"),
            coll_trattamento=data.get("coll_trattamento"),
            q_annuale=data.get("q_annuale")
        )

        db.session.add(new_association)
        db.session.commit()
        return jsonify({"message": "Attività associata al prodotto con successo"}), 201

    # Caso B: prodotto fornitore (con attività da copiare)
    elif "prodottofornitore_id" in data:
        required_fields = ["prodottofornitore_id", "amount", "fase_generale", "nome_risorsa"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obbligatorio mancante: {field}"}), 400

        fornitore_product = Product.query.get(data["prodottofornitore_id"])
        if not fornitore_product:
            return jsonify({"error": "Prodotto fornitore non trovato"}), 404

        attività_fornitore = Product_Activity.query.filter_by(productid=fornitore_product.productid).all()

        for associazione in attività_fornitore:
            nuova_associazione = Product_Activity(
                productid=data["productid"],
                activityid=associazione.activityid,
                amount=data["amount"],
                fase_generale=data["fase_generale"],
                nome_risorsa=data["nome_risorsa"],
                fase_produttiva=data.get("fase_produttiva"),
                distanza_fornitore=data.get("distanza_fornitore"),
                coll_trasporto=data.get("coll_trasporto"),
                coll_trattamento=data.get("coll_trattamento"),
                q_annuale=data.get("q_annuale"),  # Aggiunto q_annuale con default False
                prodottofornitore_id=fornitore_product.id
            )
            db.session.add(nuova_associazione)

        db.session.commit()
        return jsonify({"message": "Attività del prodotto fornitore duplicate con successo"}), 201

    else:
        return jsonify({"error": "Specificare almeno 'activityid' o 'prodottofornitore_id'"}), 400


## API per l'Aggiornamento delle Associazioni Prodotto-Attività
# Modifica un'associazione identificata dai "search_criteria"
# e aggiorna i campi specificati in "update_data".

@product_bp.route("/product-activity", methods=["PUT"])
def update_product_activity_corrected():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Nessun dato fornito per l'aggiornamento."}), 400

    search_criteria_raw = data.get("search_criteria")
    update_data_raw = data.get("update_data")

    if not search_criteria_raw:
        return jsonify({"error": "Campo 'search_criteria' mancante o vuoto."}), 400

    search_filters = {}
    try:
        productid_str = search_criteria_raw.get("productid")
        activityid_str = search_criteria_raw.get("activityid")

        if not productid_str or not activityid_str:
            return jsonify({"error": "Campi 'productid' e 'activityid' sono obbligatori in 'search_criteria'."}), 400

        search_filters["productid"] = uuid.UUID(productid_str)
        search_filters["activityid"] = uuid.UUID(activityid_str)

        prodottofornitore_id_str = search_criteria_raw.get("prodottofornitore_id")
        search_filters["prodottofornitore_id"] = uuid.UUID(prodottofornitore_id_str) if prodottofornitore_id_str else None

        amount_val = search_criteria_raw.get("amount")
        search_filters["amount"] = float(amount_val) if amount_val is not None else None
        
        distanza_fornitore_val = search_criteria_raw.get("distanza_fornitore")
        search_filters["distanza_fornitore"] = float(distanza_fornitore_val) if distanza_fornitore_val is not None else None
        
        q_annuale_val = search_criteria_raw.get("q_annuale")
        search_filters["q_annuale"] = float(q_annuale_val) if q_annuale_val is not None else None
        
        search_filters["fase_generale"] = search_criteria_raw.get("fase_generale")
        search_filters["nome_risorsa"] = search_criteria_raw.get("nome_risorsa")
        search_filters["fase_produttiva"] = search_criteria_raw.get("fase_produttiva")
        search_filters["coll_trasporto"] = search_criteria_raw.get("coll_trasporto")
        search_filters["coll_trattamento"] = search_criteria_raw.get("coll_trattamento")

    except (ValueError, TypeError, AttributeError) as e:
        return jsonify({"error": f"Formato dati in 'search_criteria' non valido: {e}. Controlla UUID e valori numerici."}), 400

    association_to_update = Product_Activity.query.filter_by(**search_filters).first()

    if not association_to_update:
        return jsonify({"error": "Associazione non trovata con i criteri di ricerca forniti. Verifica che tutti i valori (inclusi quelli nulli) corrispondano esattamente alla riga esistente."}), 404

    if not update_data_raw:
        return jsonify({"message": "Associazione trovata ma nessun dato di aggiornamento fornito. Nessuna modifica applicata."}), 200

    updatable_fields = [
        ("amount", float),
        ("fase_generale", str),
        ("nome_risorsa", str),
        ("fase_produttiva", str),
        ("distanza_fornitore", float),
        ("coll_trasporto", str),
        ("coll_trattamento", str),
        ("q_annuale", float)
    ]

    try:
        for field_name, field_type in updatable_fields:
            if field_name in update_data_raw:
                value = update_data_raw.get(field_name)
                if value is not None:
                    setattr(association_to_update, field_name, field_type(value))
                else:
                    setattr(association_to_update, field_name, None)
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Formato dati in 'update_data' non valido: {e}. Controlla i tipi per i campi aggiornati."}), 400

    try:
        db.session.commit()
        return jsonify({"message": "Associazione aggiornata con successo."}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Errore durante l'aggiornamento Product_Activity: {e}")
        return jsonify({"error": f"Errore durante l'aggiornamento: {str(e)}. Contattare l'amministratore."}), 500
    
# ELIMINAZIONE DI UN'ATTIVITÀ/PRODOTTO FORNITORE ASSOCIATA A UN PRODOTTO
@product_bp.route("/product-activity", methods=["DELETE"])
def delete_product_activity_fully_qualified():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Nessun dato fornito per l'eliminazione."}), 400

    # 1. Recupero e Conversione di TUTTI i Parametri per l'Identificazione
    try:
        productid_str = data.get("productid")
        activityid_str = data.get("activityid") # Ora obbligatorio e sempre valorizzato per la ricerca
        prodottofornitore_id_str = data.get("prodottofornitore_id") # Opzionale, può essere null/None

        # Questi campi ora servono per identificare la riga univoca
        amount_val = data.get("amount")
        fase_generale = data.get("fase_generale")
        nome_risorsa = data.get("nome_risorsa")
        fase_produttiva = data.get("fase_produttiva")
        distanza_fornitore = data.get("distanza_fornitore")
        coll_trasporto = data.get("coll_trasporto")
        coll_trattamento = data.get("coll_trattamento")
        q_annuale = data.get("q_annuale")

        # Conversione in tipi Python appropriati
        productid = uuid.UUID(productid_str) if productid_str else None
        activityid = uuid.UUID(activityid_str) if activityid_str else None
        prodottofornitore_id = uuid.UUID(prodottofornitore_id_str) if prodottofornitore_id_str else None
        
        amount = float(amount_val) if amount_val is not None else None
        # Esegui conversioni simili per gli altri campi se i loro tipi di DB non sono stringhe
        # es: distanza_fornitore = float(distanza_fornitore) if distanza_fornitore is not None else None

    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Formato dati inviati non valido: {e}. Controlla UUID e valori numerici."}), 400

    # 2. Validazione dei Campi Obbligatori per l'Identificazione
    # Ora productid e activityid sono entrambi considerati sempre obbligatori per trovare una riga
    if not productid or not activityid:
        return jsonify({"error": "Campi 'productid' e 'activityid' sono obbligatori per identificare l'associazione."}), 400

    # 3. Costruzione del Dizionario di Filtri Completo
    # Tutti i campi forniti, inclusi quelli che potrebbero essere None/NULL, sono usati per identificare la riga.
    filters = {
        "productid": productid,
        "activityid": activityid,
        "amount": amount,
        "fase_generale": fase_generale,
        "nome_risorsa": nome_risorsa,
        "fase_produttiva": fase_produttiva,
        "distanza_fornitore": distanza_fornitore,
        "coll_trasporto": coll_trasporto,
        "coll_trattamento": coll_trattamento,
        "q_annuale": q_annuale
    }

    # Gestisci il prodottofornitore_id in base alla sua presenza nel JSON:
    # Se presente, lo userà per filtrare. Se non presente (o null nel JSON), cercherà NULL nel DB.
    if prodottofornitore_id:
        filters["prodottofornitore_id"] = prodottofornitore_id
    else:
        filters["prodottofornitore_id"] = None # Cerca esplicitamente NULL nel DB

    # 4. Esecuzione della Query e Gestione dell'Eliminazione
    # Trova la riga SOLO se tutti i parametri forniti (e i loro stati NULL) corrispondono ESATTAMENTE
    association_to_delete = Product_Activity.query.filter_by(**filters).first()

    if not association_to_delete:
        return jsonify({"error": "Associazione non trovata con i parametri forniti. Verifica che tutti i valori (inclusi quelli nulli) corrispondano esattamente alla riga da eliminare."}), 404

    try:
        db.session.delete(association_to_delete)
        db.session.commit()
        return jsonify({"message": "Associazione rimossa con successo."}), 200
    except Exception as e:
        db.session.rollback()
        # Log dell'errore per debugging
        print(f"Errore durante l'eliminazione Product_Activity: {e}")
        return jsonify({"error": f"Errore durante l'eliminazione: {str(e)}. Contattare l'amministratore."}), 500
    
# RECUPERO DI TUTTI I PRODOTTI-ATTIVITÀ ASSOCIATI A UN PRODOTTO
# RECUPERO DI TUTTE LE ATTIVITÀ E PRODOTTI (DEL FORNITORE) ASSOCIATI A UN PRODOTTO
# CON DETTAGLI DEL PRODOTTO DI RIFERIMENTO PER LE ATTIVITÀ
@product_bp.route("/products/<uuid:productid>/activities/full", methods=["GET"])
def get_full_activities_for_product2(productid):
    fase_generale = request.args.get("fase_generale")

    # Recupera le informazioni del PRODOTTO PRINCIPALE (quello specificato nell'URL)
    main_product = Product.query.get(productid)
    main_product_info = {
        "main_product_id": str(main_product.productid),
        "main_product_name": main_product.productname,
        # Potresti voler recuperare anche l'unità del prodotto principale
        # Se Product ha un unitid, puoi fare un join o un'altra query
        "main_product_unit": main_product.unit.unitname if main_product and hasattr(main_product, 'unit') else None
    } if main_product else {}

    # Recupera le associazioni Product_Activity
    query = Product_Activity.query.filter_by(productid=productid)
    if fase_generale:
        query = query.filter_by(fase_generale=fase_generale)

    associations = query.all()
    result = []

    for assoc in associations:
        # Inizializza un dizionario per i dati dell'associazione corrente
        current_assoc_data = {
            "amount": str(assoc.amount),
            "fase_generale": assoc.fase_generale,
            "nome_risorsa": assoc.nome_risorsa,
            "fase_produttiva": assoc.fase_produttiva,
            "distanza_fornitore": assoc.distanza_fornitore,
            "coll_trasporto": str(assoc.coll_trasporto) if assoc.coll_trasporto else None,
            "coll_trattamento": str(assoc.coll_trattamento) if assoc.coll_trattamento else None,
            "q_annuale": assoc.q_annuale
        }

        if assoc.prodottofornitore_id:
            # È una riga derivata da un prodotto fornitore
            prodotto_fornitore = Product.query.get(assoc.prodottofornitore_id)
            current_assoc_data.update({
                "type": "supplier_product", # Aggiungi un tipo per distinguere
                "linked_id": str(assoc.prodottofornitore_id),
                "linked_name": prodotto_fornitore.productname if prodotto_fornitore else None,
                "linked_unit": prodotto_fornitore.unit.unitname if prodotto_fornitore and hasattr(prodotto_fornitore, 'unit') else None,
                # Imposta a None i campi specifici dell'attività per chiarezza
                "activity_details": None
            })
        else:
            # Attività normale - Recupera i dettagli dell'attività e del prodotto di riferimento
            activity_id = assoc.activityid

            activity_details_query = (
                db.session.query(
                    Activity,
                    IntermediateExchange.intermediatename.label("reference_product_name"),
                    Unit.unitname.label("reference_product_unit")
                )
                .filter(Activity.id == activity_id)
                .outerjoin(Activity_IntermediateExchange,
                           (Activity.id == Activity_IntermediateExchange.activityid) &
                           (Activity_IntermediateExchange.referenceproduct == True))
                .outerjoin(IntermediateExchange,
                           Activity_IntermediateExchange.intermediateexchangeid == IntermediateExchange.intermediateexchangeid)
                .outerjoin(Unit,
                           IntermediateExchange.unitid == Unit.unitid)
            )

            activity, ref_prod_name, ref_prod_unit = activity_details_query.first()

            if activity:
                # Usa ActivitySchema per serializzare i dati dell'attività
                activity_data = ActivitySchema().dump(activity)
                activity_data["reference_product_name"] = ref_prod_name
                activity_data["reference_product_unit"] = ref_prod_unit
            else:
                activity_data = {}
            
            current_assoc_data.update({
                "type": "activity", # Aggiungi un tipo per distinguere
                "linked_id": str(assoc.activityid), # L'ID collegato qui è l'ID dell'attività
                "linked_name": activity_data.get("activityname"), # Nome dell'attività
                "linked_unit": activity_data.get("reference_product_unit"), # L'unità del prodotto di riferimento dell'attività
                "activity_details": activity_data # Includi tutti i dettagli dell'attività qui
            })

        # Aggiungi le informazioni del prodotto principale a ogni elemento del risultato
        current_assoc_data.update(main_product_info)
        result.append(current_assoc_data)

    return jsonify(result), 200