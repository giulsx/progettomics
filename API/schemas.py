from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields
from models import *

ma = Marshmallow() 

# Schema: Product
class ProductSchema(Schema):
    productid = fields.UUID()
    productname = fields.Str()
    systemmodel = fields.Str()
    intervallo = fields.Str()
    totale_produzione = fields.Decimal()

# Schema : Utente
class UtenteSchema(Schema):
    userid = fields.UUID()
    username = fields.Str()
    role = fields.Str()

# Schema: ISICSection
class ISICSectionSchema(Schema):
    isicsection = fields.Str()
    isicclassification = fields.Str()
    sector = fields.Str()

# Schema: Unit
class UnitSchema(Schema):
    unitid = fields.UUID()
    unitname = fields.Str()

# Schema: Subcompartment
class SubcompartmentSchema(Schema):
    subcompartmentid = fields.UUID()
    subcompartment = fields.Str()
    compartment = fields.Str()

# Schema: IntermediateExchange
class IntermediateExchangeSchema(Schema):
    intermediateexchangeid = fields.UUID()
    intermediatename = fields.Str()
    amount = fields.Decimal()
    modifiedintermediate = fields.Bool()
    activityid_productid = fields.Str()
    unitid = fields.UUID()

# Schema: ElementaryExchange
class ElementaryExchangeSchema(Schema):
    elementaryexchangeid = fields.UUID()
    elementaryname = fields.Str()
    amount = fields.Decimal()
    modifiedelementary = fields.Bool()
    subcompartmentid = fields.UUID()
    unitid = fields.UUID()

# Schema: ImpactIndicator
class ImpactIndicatorSchema(Schema):
    impactindicatorid = fields.UUID()
    impactname = fields.Str()
    amount = fields.Decimal()
    impactmethodname = fields.Str()
    impactcategoryname = fields.Str()
    unitname = fields.Str()

# Schema: Activity
class ActivitySchema(Schema):
    id = fields.UUID()
    activityname = fields.Str()
    includedactivitiesstart = fields.Str()
    includedactivitiesend = fields.Str()
    geography = fields.Str()
    specialactivitytype = fields.Str()
    generalcomment = fields.Str()
    modifiedactivity = fields.Bool()
    isicsection = fields.Str()
    systemmodel = fields.Str()

# Schema: CFs (Characterization Factors)
class CFsSchema(Schema):
    elementaryname = fields.Str()
    impactmethodname = fields.Str()
    impactcategoryname = fields.Str()
    impactname = fields.Str()
    cf = fields.Decimal()
    unit = fields.Str()

# Schema: UnitaryImpact
class UnitaryImpactSchema(Schema):
    activityid_productid = fields.Str()
    impactmethodname = fields.Str()
    impactcategoryname = fields.Str()
    impactname = fields.Str()
    value = fields.Decimal()
    unit = fields.Str()

# Schema: Activity_ElementaryExchange
class ActivityElementaryExchangeSchema(Schema):
    activityid = fields.UUID()
    elementaryexchangeid = fields.UUID()

# Schema: Activity_IntermediateExchange
class ActivityIntermediateExchangeSchema(Schema):
    activityid = fields.UUID()
    intermediateexchangeid = fields.UUID()
    referenceproduct = fields.Bool()

# Schema: Activity_ImpactIndicator
class ActivityImpactIndicatorSchema(Schema):
    activityid = fields.UUID()
    impactindicatorid = fields.UUID()

# Schema: Product_Activity
class ProductActivitySchema(Schema):
    productid = fields.UUID()
    activityid = fields.UUID()
    amount = fields.Decimal()
    fase_generale = fields.Str()
    fase_produttiva = fields.Str()
    nome_fase = fields.Str()
    distanza_fornitore = fields.Decimal()
    id_mezzo_activity = fields.UUID()

# Schema: User_Product
class UserProductSchema(Schema):
    userid = fields.UUID()
    productid = fields.UUID()
    amount = fields.Decimal()
    fase = fields.Str()

# Schema: User_Activy
class UserActivitySchema(Schema):
    userid = fields.UUID()
    activityid = fields.UUID()
    
