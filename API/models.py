import uuid
from database import db

# Tabella: Product
class Product(db.Model):
    __tablename__ = "product"
    productId = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    productName = db.Column(db.Text, nullable=False)

# Tabella: ISICSection
class ISICSection(db.Model):
    __tablename__ = "isicsection"
    ISICSection = db.Column(db.Text, primary_key=True)
    ISICClassification = db.Column(db.Text)
    Sector = db.Column(db.Text)

# Tabella: Unit
class Unit(db.Model):
    __tablename__ = "unit"
    unitId = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    unitName = db.Column(db.Text, unique=True)

# Tabella: Subcompartment
class Subcompartment(db.Model):
    __tablename__ = "subcompartment"
    subcompartmentId = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    subcompartment = db.Column(db.Text)
    compartment = db.Column(db.Text)

# Tabella: IntermediateExchange
class IntermediateExchange(db.Model):
    __tablename__ = "intermediateexchange"
    intermediateExchangeId = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    intermediateName = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric)
    modifiedIntermediate = db.Column(db.Boolean, nullable=False)
    activityId_productId = db.Column(db.Text, nullable=False, unique=True)
    unitId = db.Column(db.UUID, db.ForeignKey("unit.unitId"), nullable=False)

# Tabella: ElementaryExchange
class ElementaryExchange(db.Model):
    __tablename__ = "elementaryexchange"
    elementaryExchangeId = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    elementaryName = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric)
    modifiedElementary = db.Column(db.Boolean, nullable=False)
    subcompartmentId = db.Column(db.UUID, db.ForeignKey("subcompartment.subcompartmentId"))
    unitId = db.Column(db.UUID, db.ForeignKey("unit.unitId"), nullable=False)

# Tabella: ImpactIndicator
class ImpactIndicator(db.Model):
    __tablename__ = "impactindicator"
    impactIndicatorId = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    impactName = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric)
    impactMethodName = db.Column(db.Text, nullable=False)
    impactCategoryName = db.Column(db.Text, nullable=False)
    unitName = db.Column(db.Text, nullable=False)

# Tabella: Activity
class Activity(db.Model):
    __tablename__ = "activity"
    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    activityName = db.Column(db.Text, nullable=False)
    includedActivitiesStart = db.Column(db.Text)
    includedActivitiesEnd = db.Column(db.Text)
    geography = db.Column(db.Text)
    specialActivityType = db.Column(db.Text)
    generalComment = db.Column(db.Text)
    modifiedActivity = db.Column(db.Boolean, nullable=False)
    ISICSection = db.Column(db.Text, db.ForeignKey("isicsection.ISICSection"))
    systemModel = db.Column(db.Text)

# Tabella: CFs (Characterization Factors)
class CFs(db.Model):
    __tablename__ = "cfs"
    elementaryName = db.Column(db.Text, primary_key=True)
    impactMethodName = db.Column(db.Text, primary_key=True)
    impactCategoryName = db.Column(db.Text, primary_key=True)
    impactName = db.Column(db.Text, primary_key=True)
    CF = db.Column(db.Numeric)
    unitName = db.Column(db.Text)
    elementaryExchangeId = db.Column(db.Text, db.ForeignKey("elementaryexchange.elementaryName"))

# Tabella: UnitaryImpact
class UnitaryImpact(db.Model):
    __tablename__ = "unitaryimpact"
    activityId_productId = db.Column(db.Text, primary_key=True)
    impactMethodName = db.Column(db.Text, primary_key=True)
    impactCategoryName = db.Column(db.Text, primary_key=True)
    impactName = db.Column(db.Text, primary_key=True)
    value = db.Column(db.Numeric)
    unitName = db.Column(db.Text)
    intermediateExchangeId = db.Column(db.Text, db.ForeignKey("intermediateexchange.activityId_productId"))

# Tabella di associazione Activity - ElementaryExchange
class Activity_ElementaryExchange(db.Model):
    __tablename__ = "activity_elementaryexchange"
    activityId = db.Column(db.UUID, db.ForeignKey("activity.id"), primary_key=True)
    elementaryExchangeId = db.Column(db.UUID, db.ForeignKey("elementaryexchange.elementaryExchangeId"), primary_key=True)

# Tabella di associazione Activity - IntermediateExchange
class Activity_IntermediateExchange(db.Model):
    __tablename__ = "activity_intermediateexchange"
    activityId = db.Column(db.UUID, db.ForeignKey("activity.id"), primary_key=True)
    intermediateExchangeId = db.Column(db.UUID, db.ForeignKey("intermediateexchange.intermediateExchangeId"), primary_key=True)
    referenceProduct = db.Column(db.Boolean, nullable=False)

# Tabella di associazione Activity - ImpactIndicator
class Activity_ImpactIndicator(db.Model):
    __tablename__ = "activity_impactindicator"
    activityId = db.Column(db.UUID, db.ForeignKey("activity.id"), primary_key=True)
    impactIndicatorId = db.Column(db.UUID, db.ForeignKey("impactindicator.impactIndicatorId"), primary_key=True)

# Tabella di associazione Product - Activity
class Product_Activity(db.Model):
    __tablename__ = "product_activity"
    productId = db.Column(db.UUID, db.ForeignKey("product.productId"), primary_key=True)
    activityId = db.Column(db.UUID, db.ForeignKey("activity.id"), primary_key=True)
