from flask import Blueprint, request, jsonify
from models import db, Product, Activity, ImpactIndicator, Product, ISICSection, Unit, Subcompartment, IntermediateExchange, ElementaryExchange, ImpactIndicator, Activity, CFs, UnitaryImpact, Activity_ElementaryExchange, Activity_IntermediateExchange, Activity_ImpactIndicator, Product_Activity  
from schemas import ProductSchema, ActivitySchema, ImpactIndicatorSchema, ProductSchema, ISICSectionSchema, UnitSchema, SubcompartmentSchema, IntermediateExchangeSchema, ElementaryExchangeSchema, ImpactIndicatorSchema, ActivitySchema, CFsSchema, UnitaryImpactSchema, ActivityElementaryExchangeSchema, ActivityIntermediateExchangeSchema, ActivityImpactIndicatorSchema, ProductActivitySchema


app_routes = Blueprint("app_routes", __name__)

# Serializzatori
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

activity_schema = ActivitySchema()
activities_schema = ActivitySchema(many=True)

impact_indicator_schema = ImpactIndicatorSchema()
impact_indicators_schema = ImpactIndicatorSchema(many=True)

# --------------------------------------------------------
# CRUD per Product
# --------------------------------------------------------

@app_routes.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify(products_schema.dump(products))

@app_routes.route("/products/<uuid:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product_schema.dump(product))

@app_routes.route("/products", methods=["POST"])
def create_product():
    data = request.json
    new_product = Product(productId=data["productId"], productName=data["productName"])
    db.session.add(new_product)
    db.session.commit()
    return jsonify(product_schema.dump(new_product)), 201

@app_routes.route("/products/<uuid:product_id>", methods=["PUT"])
def update_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    data = request.json
    product.productName = data.get("productName", product.productName)
    db.session.commit()
    return jsonify(product_schema.dump(product))

@app_routes.route("/products/<uuid:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"})

# --------------------------------------------------------
# CRUD per Activity
# --------------------------------------------------------

@app_routes.route("/activities", methods=["GET"])
def get_activities():
    activities = Activity.query.all()
    return jsonify(activities_schema.dump(activities))

@app_routes.route("/activities/<uuid:activity_id>", methods=["GET"])
def get_activity(activity_id):
    activity = Activity.query.get(activity_id)
    if activity is None:
        return jsonify({"error": "Activity not found"}), 404
    return jsonify(activity_schema.dump(activity))

@app_routes.route("/activities", methods=["POST"])
def create_activity():
    data = request.json
    new_activity = Activity(
        id=data["id"],
        activityName=data["activityName"],
        includedActivitiesStart=data.get("includedActivitiesStart"),
        includedActivitiesEnd=data.get("includedActivitiesEnd"),
        geography=data.get("geography"),
        specialActivityType=data.get("specialActivityType"),
        generalComment=data.get("generalComment"),
        modifiedActivity=data["modifiedActivity"],
        ISICSection=data.get("ISICSection"),
        systemModel=data.get("systemModel")
    )
    db.session.add(new_activity)
    db.session.commit()
    return jsonify(activity_schema.dump(new_activity)), 201

@app_routes.route("/activities/<uuid:activity_id>", methods=["PUT"])
def update_activity(activity_id):
    activity = Activity.query.get(activity_id)
    if activity is None:
        return jsonify({"error": "Activity not found"}), 404
    data = request.json
    activity.activityName = data.get("activityName", activity.activityName)
    activity.geography = data.get("geography", activity.geography)
    db.session.commit()
    return jsonify(activity_schema.dump(activity))

@app_routes.route("/activities/<uuid:activity_id>", methods=["DELETE"])
def delete_activity(activity_id):
    activity = Activity.query.get(activity_id)
    if activity is None:
        return jsonify({"error": "Activity not found"}), 404
    db.session.delete(activity)
    db.session.commit()
    return jsonify({"message": "Activity deleted successfully"})

# --------------------------------------------------------
# CRUD per ImpactIndicator
# --------------------------------------------------------

@app_routes.route("/impact_indicators", methods=["GET"])
def get_impact_indicators():
    impact_indicators = ImpactIndicator.query.all()
    return jsonify(impact_indicators_schema.dump(impact_indicators))

@app_routes.route("/impact_indicators/<uuid:impact_indicator_id>", methods=["GET"])
def get_impact_indicator(impact_indicator_id):
    impact_indicator = ImpactIndicator.query.get(impact_indicator_id)
    if impact_indicator is None:
        return jsonify({"error": "Impact Indicator not found"}), 404
    return jsonify(impact_indicator_schema.dump(impact_indicator))

@app_routes.route("/impact_indicators", methods=["POST"])
def create_impact_indicator():
    data = request.json
    new_impact_indicator = ImpactIndicator(
        impactIndicatorId=data["impactIndicatorId"],
        impactName=data["impactName"],
        amount=data["amount"],
        impactMethodName=data["impactMethodName"],
        impactCategoryName=data["impactCategoryName"],
        unitName=data["unitName"]
    )
    db.session.add(new_impact_indicator)
    db.session.commit()
    return jsonify(impact_indicator_schema.dump(new_impact_indicator)), 201

@app_routes.route("/impact_indicators/<uuid:impact_indicator_id>", methods=["DELETE"])
def delete_impact_indicator(impact_indicator_id):
    impact_indicator = ImpactIndicator.query.get(impact_indicator_id)
    if impact_indicator is None:
        return jsonify({"error": "Impact Indicator not found"}), 404
    db.session.delete(impact_indicator)
    db.session.commit()
    return jsonify({"message": "Impact Indicator deleted successfully"})

# --------------------------------------------------------
# CRUD per ISICSection
# --------------------------------------------------------
@app_routes.route("/isic_sections", methods=["GET"])
def get_isic_sections():
    sections = ISICSection.query.all()
    return jsonify(ISICSectionSchema(many=True).dump(sections))

@app_routes.route("/isic_sections", methods=["POST"])
def create_isic_section():
    data = request.json
    new_section = ISICSection(**data)
    db.session.add(new_section)
    db.session.commit()
    return jsonify(ISICSectionSchema().dump(new_section)), 201

# --------------------------------------------------------
# CRUD per Unit
# --------------------------------------------------------
@app_routes.route("/units", methods=["GET"])
def get_units():
    units = Unit.query.all()
    return jsonify(UnitSchema(many=True).dump(units))

@app_routes.route("/units", methods=["POST"])
def create_unit():
    data = request.json
    new_unit = Unit(**data)
    db.session.add(new_unit)
    db.session.commit()
    return jsonify(UnitSchema().dump(new_unit)), 201

# --------------------------------------------------------
# CRUD per Subcompartment
# --------------------------------------------------------
@app_routes.route("/subcompartments", methods=["GET"])
def get_subcompartments():
    subcompartments = Subcompartment.query.all()
    return jsonify(SubcompartmentSchema(many=True).dump(subcompartments))

@app_routes.route("/subcompartments", methods=["POST"])
def create_subcompartment():
    data = request.json
    new_subcompartment = Subcompartment(**data)
    db.session.add(new_subcompartment)
    db.session.commit()
    return jsonify(SubcompartmentSchema().dump(new_subcompartment)), 201

# --------------------------------------------------------
# CRUD per IntermediateExchange
# --------------------------------------------------------
@app_routes.route("/intermediate_exchanges", methods=["GET"])
def get_intermediate_exchanges():
    exchanges = IntermediateExchange.query.all()
    return jsonify(IntermediateExchangeSchema(many=True).dump(exchanges))

@app_routes.route("/intermediate_exchanges", methods=["POST"])
def create_intermediate_exchange():
    data = request.json
    new_exchange = IntermediateExchange(**data)
    db.session.add(new_exchange)
    db.session.commit()
    return jsonify(IntermediateExchangeSchema().dump(new_exchange)), 201

@app_routes.route("/intermediate_exchanges/<uuid:id>", methods=["GET"])
def get_intermediate_exchange(id):
    exchange = IntermediateExchange.query.get_or_404(id)
    return jsonify(IntermediateExchangeSchema().dump(exchange))

@app_routes.route("/intermediate_exchanges/<uuid:id>", methods=["PUT"])
def update_intermediate_exchange(id):
    data = request.json
    exchange = IntermediateExchange.query.get_or_404(id)
    for key, value in data.items():
        setattr(exchange, key, value)
    db.session.commit()
    return jsonify(IntermediateExchangeSchema().dump(exchange))

@app_routes.route("/intermediate_exchanges/<uuid:id>", methods=["DELETE"])
def delete_intermediate_exchange(id):
    exchange = IntermediateExchange.query.get_or_404(id)
    db.session.delete(exchange)
    db.session.commit()
    return '', 204

# --------------------------------------------------------
# CRUD per ElementaryExchange
# --------------------------------------------------------
@app_routes.route("/elementary_exchanges", methods=["GET"])
def get_elementary_exchanges():
    exchanges = ElementaryExchange.query.all()
    return jsonify(ElementaryExchangeSchema(many=True).dump(exchanges))

@app_routes.route("/elementary_exchanges", methods=["POST"])
def create_elementary_exchange():
    data = request.json
    new_exchange = ElementaryExchange(**data)
    db.session.add(new_exchange)
    db.session.commit()
    return jsonify(ElementaryExchangeSchema().dump(new_exchange)), 201

@app_routes.route("/elementary_exchanges/<uuid:id>", methods=["GET"])
def get_elementary_exchange(id):
    exchange = ElementaryExchange.query.get_or_404(id)
    return jsonify(ElementaryExchangeSchema().dump(exchange))

@app_routes.route("/elementary_exchanges/<uuid:id>", methods=["PUT"])
def update_elementary_exchange(id):
    data = request.json
    exchange = ElementaryExchange.query.get_or_404(id)
    for key, value in data.items():
        setattr(exchange, key, value)
    db.session.commit()
    return jsonify(ElementaryExchangeSchema().dump(exchange))

@app_routes.route("/elementary_exchanges/<uuid:id>", methods=["DELETE"])
def delete_elementary_exchange(id):
    exchange = ElementaryExchange.query.get_or_404(id)
    db.session.delete(exchange)
    db.session.commit()
    return '', 204

# --------------------------------------------------------
# CRUD per CFs (Characterization Factors)
# --------------------------------------------------------
@app_routes.route("/cfs", methods=["GET"])
def get_cfs():
    cfs = CFs.query.all()
    return jsonify(CFsSchema(many=True).dump(cfs))

@app_routes.route("/cfs", methods=["POST"])
def create_cfs():
    data = request.json
    new_cfs = CFs(**data)
    db.session.add(new_cfs)
    db.session.commit()
    return jsonify(CFsSchema().dump(new_cfs)), 201

# --------------------------------------------------------
# CRUD per UnitaryImpact
# --------------------------------------------------------
@app_routes.route("/unitary_impacts", methods=["GET"])
def get_unitary_impacts():
    impacts = UnitaryImpact.query.all()
    return jsonify(UnitaryImpactSchema(many=True).dump(impacts))

@app_routes.route("/unitary_impacts", methods=["POST"])
def create_unitary_impact():
    data = request.json
    new_impact = UnitaryImpact(**data)
    db.session.add(new_impact)
    db.session.commit()
    return jsonify(UnitaryImpactSchema().dump(new_impact)), 201

# --------------------------------------------------------
# CRUD per le tabelle di associazione
# --------------------------------------------------------

# GET e POST per Activity_ElementaryExchange
@app_routes.route("/activity_elementary_exchange", methods=["GET"])
def get_activity_elementary_exchange():
    data = Activity_ElementaryExchange.query.all()
    return jsonify(ActivityElementaryExchangeSchema(many=True).dump(data))

@app_routes.route("/activity_elementary_exchange", methods=["POST"])
def create_activity_elementary_exchange():
    data = request.json
    new_entry = Activity_ElementaryExchange(**data)
    db.session.add(new_entry)
    db.session.commit()
    return jsonify(ActivityElementaryExchangeSchema().dump(new_entry)), 201

# GET e POST per Activity_IntermediateExchange
@app_routes.route("/activity_intermediate_exchange", methods=["GET"])
def get_activity_intermediate_exchange():
    data = Activity_IntermediateExchange.query.all()
    return jsonify(ActivityIntermediateExchangeSchema(many=True).dump(data))

@app_routes.route("/activity_intermediate_exchange", methods=["POST"])
def create_activity_intermediate_exchange():
    data = request.json
    new_entry = Activity_IntermediateExchange(**data)
    db.session.add(new_entry)
    db.session.commit()
    return jsonify(ActivityIntermediateExchangeSchema().dump(new_entry)), 201

# GET e POST per Activity_ImpactIndicator
@app_routes.route("/activity_impact_indicator", methods=["GET"])
def get_activity_impact_indicator():
    data = Activity_ImpactIndicator.query.all()
    return jsonify(ActivityImpactIndicatorSchema(many=True).dump(data))

@app_routes.route("/activity_impact_indicator", methods=["POST"])
def create_activity_impact_indicator():
    data = request.json
    new_entry = Activity_ImpactIndicator(**data)
    db.session.add(new_entry)
    db.session.commit()
    return jsonify(ActivityImpactIndicatorSchema().dump(new_entry)), 201

# GET e POST per Product_Activity
@app_routes.route("/product_activity", methods=["GET"])
def get_product_activity():
    data = Product_Activity.query.all()
    return jsonify(ProductActivitySchema(many=True).dump(data))

@app_routes.route("/product_activity", methods=["POST"])
def create_product_activity():
    data = request.json
    new_entry = Product_Activity(**data)
    db.session.add(new_entry)
    db.session.commit()
    return jsonify(ProductActivitySchema().dump(new_entry)), 201
