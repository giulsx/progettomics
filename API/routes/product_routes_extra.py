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
