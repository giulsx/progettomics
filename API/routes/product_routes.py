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
# SENZA FILTRI
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
@product_bp.route("/activitiesandproducts", methods=["GET"])
def get_activities_and_fornitori_products_by_filters():
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
@product_bp.route("/activitiesandproducts", methods=["GET"])
def get_activities_and_fornitori_products_by_filters():
    systemmodel = request.args.get("systemmodel")
    tipologia_id = request.args.get("tipologiaid")  # ID della ISICSection
    fornitore_id = request.args.get("fornitoreid")  # ID dell'Utente fornitore

    # --- Filtri e dati aggiuntivi per le Attività ---
    # Iniziamo la query selezionando l'Activity e aggiungendo i campi che vogliamo
    activity_query = (
        db.session.query(
            Activity,
            IntermediateExchange.intermediatename.label("reference_product_name"),
            Unit.unitname.label("reference_product_unit")
        )
        .outerjoin(Activity_IntermediateExchange,
                   (Activity.activityid == Activity_IntermediateExchange.activityid) &
                   (Activity_IntermediateExchange.referenceproduct == True))
        .outerjoin(IntermediateExchange,
                   Activity_IntermediateExchange.intermediateexchangeid == IntermediateExchange.intermediateexchangeid)
        .outerjoin(Unit,
                   IntermediateExchange.unitid == Unit.unitid)
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
            .join(User_Activity, Activity.activityid == User_Activity.activityid)
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
        db.session.query(Product)
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

    fornitori_products = fornitori_products_query.all()
    product_schema = ProductSchema(many=True)
    fornitori_data = product_schema.dump(fornitori_products)

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
            coll_trasporto=data.get("coll_trasporto")
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
                prodottofornitore_id=fornitore_product.id
            )
            db.session.add(nuova_associazione)

        db.session.commit()
        return jsonify({"message": "Attività del prodotto fornitore duplicate con successo"}), 201

    else:
        return jsonify({"error": "Specificare almeno 'activityid' o 'prodottofornitore_id'"}), 400


# ELIMINAZIONE DI UN'ATTIVITà(normale)/PRODOTTO FORTNITORE ASSOCIATA A UN PRODOTTO
@product_bp.route("/product-activity", methods=["DELETE"])
def delete_product_activity():
    data = request.get_json()

    if not data or "productid" not in data:
        return jsonify({"error": "Campo 'productid' obbligatorio"}), 400

    productid = data["productid"]
    fase = data.get("fase")  # solo per attività normali
    activityid = data.get("activityid")
    prodottofornitore_id = data.get("prodottofornitore_id")

    if activityid:
        # Caso: eliminazione attività normale
        if not fase:
            return jsonify({"error": "Parametro 'fase' obbligatorio per attività normale"}), 400

        association = Product_Activity.query.filter_by(
            productid=productid,
            activityid=activityid,
            fase=fase
        ).first()

        if not association:
            return jsonify({"error": "Associazione attività non trovata"}), 404

        db.session.delete(association)
        db.session.commit()
        return jsonify({"message": "Attività rimossa dal prodotto"}), 200

    elif prodottofornitore_id:
        # Caso: eliminazione di tutte le attività da un prodotto fornitore
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

    else:
        return jsonify({"error": "Specificare 'activityid' oppure 'prodottofornitore_id'"}), 400

# RECUPERO DI TUTTE LE ATTIVITÀ E PRODOTTI (DEL FORNITORE) ASSOCIATI A UN PRODOTTO
# RECUPERO DI TUTTE LE ATTIVITÀ E PRODOTTI (DEL FORNITORE) ASSOCIATI A UN PRODOTTO
# CON DETTAGLI DEL PRODOTTO DI RIFERIMENTO PER LE ATTIVITÀ
@product_bp.route("/products/<uuid:productid>/activities/full", methods=["GET"])
def get_full_activities_for_product(productid):
    fase = request.args.get("fase")

    # Recupera le associazioni Product_Activity
    query = Product_Activity.query.filter_by(productid=productid)
    if fase:
        query = query.filter_by(fase=fase)

    associations = query.all()
    result = []

    for assoc in associations:
        if assoc.prodottofornitore_id:
            # È una riga derivata da un prodotto fornitore (logica invariata)
            prodotto_fornitore = Product.query.get(assoc.prodottofornitore_id)
            result.append({
                "prodottofornitore_id": str(assoc.prodottofornitore_id),
                "nome_prodotto_fornitore": prodotto_fornitore.productname if prodotto_fornitore else None, # Ho corretto in .productname
                "amount": str(assoc.amount),
                "fase_generale": assoc.fase,
                "nome_risorsa": assoc.nome_risorsa,
                "fase_produttiva": assoc.fase_produttiva,
                "distanza_fornitore": assoc.distanza_fornitore,
                "coll_trasporto": str(assoc.coll_trasporto) if assoc.coll_trasporto else None
            })
        else:
            # Attività normale - Recupera i dettagli del prodotto di riferimento
            activity_id = assoc.activityid

            # Iniziamo la query per l'attività con i dettagli del prodotto di riferimento
            activity_details_query = (
                db.session.query(
                    Activity,
                    IntermediateExchange.intermediatename.label("reference_product_name"),
                    Unit.unitname.label("reference_product_unit")
                )
                .filter(Activity.activityid == activity_id) # Filtra per l'activityid corrente
                .outerjoin(Activity_IntermediateExchange,
                           (Activity.activityid == Activity_IntermediateExchange.activityid) &
                           (Activity_IntermediateExchange.referenceproduct == True))
                .outerjoin(IntermediateExchange,
                           Activity_IntermediateExchange.intermediateexchangeid == IntermediateExchange.intermediateexchangeid)
                .outerjoin(Unit,
                           IntermediateExchange.unitid == Unit.unitid)
            )
            
            activity, ref_prod_name, ref_prod_unit = activity_details_query.first() # Prende il primo (e unico) risultato

            if activity:
                activity_data = ActivitySchema().dump(activity)
                # Aggiungi i dettagli del prodotto di riferimento
                activity_data["reference_product_name"] = ref_prod_name
                activity_data["reference_product_unit"] = ref_prod_unit
            else:
                # Se l'attività non viene trovata, gestisci il caso (potrebbe essere un errore o dati inconsistenti)
                activity_data = {} # O un messaggio di errore adeguato
            
            activity_data.update({
                "prodottofornitore_id": None,
                "amount": str(assoc.amount),
                "fase_generale": assoc.fase,
                "nome_risorsa": assoc.nome_risorsa,
                "fase_produttiva": assoc.fase_produttiva,
                "distanza_fornitore": assoc.distanza_fornitore,
                "coll_trasporto": str(assoc.coll_trasporto) if assoc.coll_trasporto else None
            })
            result.append(activity_data)

    return jsonify(result), 200