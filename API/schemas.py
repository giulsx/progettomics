from marshmallow import Schema, fields
from models import *

# Schema: Product
class ProductSchema(Schema):
    productId = fields.UUID()
    productName = fields.Str()

# Schema: ISICSection
class ISICSectionSchema(Schema):
    ISICSection = fields.Str()
    ISICClassification = fields.Str()
    Sector = fields.Str()

# Schema: Unit
class UnitSchema(Schema):
    unitId = fields.UUID()
    unitName = fields.Str()

# Schema: Subcompartment
class SubcompartmentSchema(Schema):
    subcompartmentId = fields.UUID()
    subcompartment = fields.Str()
    compartment = fields.Str()

# Schema: IntermediateExchange
class IntermediateExchangeSchema(Schema):
    intermediateExchangeId = fields.UUID()
    intermediateName = fields.Str()
    amount = fields.Decimal()
    modifiedIntermediate = fields.Bool()
    activityId_productId = fields.Str()
    unitId = fields.UUID()

# Schema: ElementaryExchange
class ElementaryExchangeSchema(Schema):
    elementaryExchangeId = fields.UUID()
    elementaryName = fields.Str()
    amount = fields.Decimal()
    modifiedElementary = fields.Bool()
    subcompartmentId = fields.UUID()
    unitId = fields.UUID()

# Schema: ImpactIndicator
class ImpactIndicatorSchema(Schema):
    impactIndicatorId = fields.UUID()
    impactName = fields.Str()
    amount = fields.Decimal()
    impactMethodName = fields.Str()
    impactCategoryName = fields.Str()
    unitName = fields.Str()

# Schema: Activity
class ActivitySchema(Schema):
    id = fields.UUID()
    activityName = fields.Str()
    includedActivitiesStart = fields.Str()
    includedActivitiesEnd = fields.Str()
    geography = fields.Str()
    specialActivityType = fields.Str()
    generalComment = fields.Str()
    modifiedActivity = fields.Bool()
    ISICSection = fields.Str()
    systemModel = fields.Str()

# Schema: CFs (Characterization Factors)
class CFsSchema(Schema):
    elementaryName = fields.Str()
    impactMethodName = fields.Str()
    impactCategoryName = fields.Str()
    impactName = fields.Str()
    CF = fields.Decimal()
    unitName = fields.Str()

# Schema: UnitaryImpact
class UnitaryImpactSchema(Schema):
    activityId_productId = fields.Str()
    impactMethodName = fields.Str()
    impactCategoryName = fields.Str()
    impactName = fields.Str()
    value = fields.Decimal()
    unitName = fields.Str()

# Schema: Activity_ElementaryExchange
class ActivityElementaryExchangeSchema(Schema):
    activityId = fields.UUID()
    elementaryExchangeId = fields.UUID()

# Schema: Activity_IntermediateExchange
class ActivityIntermediateExchangeSchema(Schema):
    activityId = fields.UUID()
    intermediateExchangeId = fields.UUID()
    referenceProduct = fields.Bool()

# Schema: Activity_ImpactIndicator
class ActivityImpactIndicatorSchema(Schema):
    activityId = fields.UUID()
    impactIndicatorId = fields.UUID()

# Schema: Product_Activity
class ProductActivitySchema(Schema):
    productId = fields.UUID()
    activityId = fields.UUID()
