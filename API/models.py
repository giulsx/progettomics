import uuid
from database import db

# Tabella: Product
class Product(db.Model):
    __tablename__ = "product"
    productid = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    productname = db.Column(db.Text, nullable=False)

# Tabella: ISICSection
class ISICSection(db.Model):
    __tablename__ = "isicsection"
    isicsection = db.Column(db.Text, primary_key=True)
    isicclassification = db.Column(db.Text)
    sector = db.Column(db.Text)

# Tabella: Unit
class Unit(db.Model):
    __tablename__ = "unit"
    unitid = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    unitname = db.Column(db.Text, unique=True)

# Tabella: Subcompartment
class Subcompartment(db.Model):
    __tablename__ = "subcompartment"
    subcompartmentid = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    subcompartment = db.Column(db.Text)
    compartment = db.Column(db.Text)

# Tabella: IntermediateExchange
class IntermediateExchange(db.Model):
    __tablename__ = "intermediateexchange"
    intermediateexchangeId = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    intermediatename = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric)
    modifiedIntermediate = db.Column(db.Boolean, nullable=False)
    activityid_productid = db.Column(db.Text, nullable=False, unique=True)
    unitid = db.Column(db.UUID, db.ForeignKey("unit.unitid"), nullable=False)

# Tabella: ElementaryExchange
class ElementaryExchange(db.Model):
    __tablename__ = "elementaryexchange"
    elementaryexchangeid = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    elementaryname = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric)
    modifiedelementary = db.Column(db.Boolean, nullable=False)
    subcompartmentid = db.Column(db.UUID, db.ForeignKey("subcompartment.subcompartmentid"))
    unitid = db.Column(db.UUID, db.ForeignKey("unit.unitid"), nullable=False)

# Tabella: ImpactIndicator
class ImpactIndicator(db.Model):
    __tablename__ = "impactindicator"
    impactindicatorId = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    impactname = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric)
    impactmethodName = db.Column(db.Text, nullable=False)
    impactcategoryName = db.Column(db.Text, nullable=False)
    unitname = db.Column(db.Text, nullable=False)

# Tabella: Activity
class Activity(db.Model):
    __tablename__ = "activity"
    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    activityname = db.Column(db.Text, nullable=False)
    includedactivitiesstart = db.Column(db.Text)
    includedactivitiesend = db.Column(db.Text)
    geography = db.Column(db.Text)
    specialactivitytype = db.Column(db.Text)
    generalcomment = db.Column(db.Text)
    modifiedactivity = db.Column(db.Boolean, nullable=False)
    isicsection = db.Column(db.Text, db.ForeignKey("isicsection.isicsection"))
    systemmodel = db.Column(db.Text)

# Tabella: CFs (Characterization Factors)
class CFs(db.Model):
    __tablename__ = "cfs"
    elementaryname = db.Column(db.Text, primary_key=True)
    impactmethodname = db.Column(db.Text, primary_key=True)
    impactCategoryName = db.Column(db.Text, primary_key=True)
    impactname = db.Column(db.Text, primary_key=True)
    cf = db.Column(db.Numeric)
    unit = db.Column(db.Text)
    elementaryexchangeid = db.Column(db.Text, db.ForeignKey("elementaryexchange.elementaryname"))

# Tabella: UnitaryImpact
class UnitaryImpact(db.Model):
    __tablename__ = "unitaryimpact"
    activityid_productid = db.Column(db.Text, primary_key=True)
    impactmethodname = db.Column(db.Text, primary_key=True)
    impactcategoryname = db.Column(db.Text, primary_key=True)
    impactname = db.Column(db.Text, primary_key=True)
    value = db.Column(db.Numeric)
    unit = db.Column(db.Text)
    intermediateexchangeid = db.Column(db.Text, db.ForeignKey("intermediateexchange.activityid_productid"))

# Tabella di associazione Activity - ElementaryExchange
class Activity_ElementaryExchange(db.Model):
    __tablename__ = "activity_elementaryexchange"
    activityid = db.Column(db.UUID, db.ForeignKey("activity.id"), primary_key=True)
    elementaryexchangeid = db.Column(db.UUID, db.ForeignKey("elementaryexchange.elementaryexchangeid"), primary_key=True)

# Tabella di associazione Activity - IntermediateExchange
class Activity_IntermediateExchange(db.Model):
    __tablename__ = "activity_intermediateexchange"
    activityid = db.Column(db.UUID, db.ForeignKey("activity.id"), primary_key=True)
    intermediateexchangeid = db.Column(db.UUID, db.ForeignKey("intermediateexchange.intermediateexchangeid"), primary_key=True)
    referenceproduct = db.Column(db.Boolean, nullable=False)

# Tabella di associazione Activity - ImpactIndicator
class Activity_ImpactIndicator(db.Model):
    __tablename__ = "activity_impactindicator"
    activityid = db.Column(db.UUID, db.ForeignKey("activity.id"), primary_key=True)
    impactindicatorid = db.Column(db.UUID, db.ForeignKey("impactindicator.impactindicatorid"), primary_key=True)

# Tabella di associazione Product - Activity
class Product_Activity(db.Model):
    __tablename__ = "product_activity"
    productid = db.Column(db.UUID, db.ForeignKey("product.productid"), primary_key=True)
    activityid = db.Column(db.UUID, db.ForeignKey("activity.id"), primary_key=True)
