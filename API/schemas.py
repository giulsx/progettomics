from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields
from models import *
import base64 # Importa base64

ma = Marshmallow() 

# Schema: Product
class ProductSchema(Schema):
    productid = fields.UUID()
    productname = fields.Str()
    systemmodel = fields.Str()
    intervallo = fields.Str()
    anni_uso = fields.Integer()
    pesoprodotto = fields.Decimal(allow_none=True)
    tipologiaprodotto = fields.Str(allow_none=True)
    totale_produzione = fields.Decimal()

# Schema : Utente
class UtenteSchema(Schema):
    userid = fields.Str() 
    username = fields.Str()
    role = fields.Str()
    password = fields.Str()
    tipologia_attore = fields.Str(allow_none=True)
    companyname = fields.Str(allow_none=True)  
    nation = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    municipality = fields.Str(allow_none=True)   


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
    nome_risorsa = fields.Str()
    distanza_fornitore = fields.Decimal()
    coll_trasporto = fields.UUID()
    coll_trattamento = fields.UUID()
    prodottofornitore_id = fields.UUID(allow_none=True)
    q_annuale = fields.Boolean()

# Schema: User_Product
class UserProductSchema(Schema):

    productid = fields.UUID()
    userid = fields.UUID()
    amount = fields.Decimal()
    fase = fields.Str()

# Schema: User_Activy
class UserActivitySchema(Schema):
    
    activityid = fields.UUID()
    userid = fields.UUID()

# schemas.py

from marshmallow import Schema, fields, validate
import base64
import uuid

# Schema: Certificazione_Product (questo schema non viene usato per il 'load' diretto in CertificazioneSchema,
# ma è necessario per definire la struttura dell'associazione quando la crei manualmente)
class CertificazioneProductSchema(Schema):
    productid = fields.UUID(required=True)
    certificazioneid = fields.UUID(dump_only=True)

# Schema: Certificazione_ImpactIndicator (invariato, non coinvolto nel problema attuale)
class CertificazioneImpactIndicatorSchema(Schema):
    certificazioneid = fields.UUID(dump_only=True)
    impactindicatorid = fields.UUID(required=True)

# Schema: Certificazione
class CertificazioneSchema(Schema):
    certificazioneid = fields.UUID(dump_only=True) # Sarà generato dal database
    nomecertificazione = fields.Str(required=True, validate=validate.Length(min=1))
    tipocertificazione = fields.Str(required=True, validate=validate.Length(min=1))
    entecertificatore = fields.Str(required=True, validate=validate.Length(min=1))
    anno = fields.Integer(required=True)
    certificazionepdf = fields.Method("get_pdf_base64", "load_pdf_base64", allow_none=True)
    userid = fields.UUID(allow_none=True)

    # *** AGGIUNGI/ASSICURATI CHE QUESTA RIGA SIA PRESENTE E CORRETTA ***
    # Questo campo dice a Marshmallow di aspettarsi un 'productid' nel JSON in ingresso.
    # 'load_only=True' significa che viene usato solo in fase di deserializzazione (input).
    # 'allow_none=True' lo rende opzionale; se vuoi sia obbligatorio, usa 'required=True'.
    productid = fields.UUID(load_only=True, allow_none=True) 

    # Metodo per serializzare i bytes del PDF in Base64 per l'output JSON
    def get_pdf_base64(self, obj):
        if obj.certificazionepdf is not None:
            return base64.b64encode(obj.certificazionepdf).decode('utf-8')
        return None

    # Metodo per deserializzare la stringa Base64 in bytes per il salvataggio nel DB
    def load_pdf_base64(self, value):
        if value is not None:
            try:
                return base64.b64decode(value)
            except Exception as e:
                raise ValueError(f"Dati PDF non validi (non è una stringa Base64): {e}")
        return None