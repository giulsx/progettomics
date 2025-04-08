-- Crea il database (questo comando va eseguito solo una volta da PgAdmin o dalla shell)
-- CREATE DATABASE database_ecoinvent;

-- Tabella: Product
CREATE TABLE Product (
    productId UUID PRIMARY KEY,
    productName TEXT NOT NULL
);


-- Tabella: ISICSection
CREATE TABLE ISICSection (
    ISICSection TEXT PRIMARY KEY,
    ISICClassification TEXT,
    Sector TEXT
);

-- Tabella: Utente
CREATE TABLE Utente (
    userId UUID PRIMARY KEY,
    userName TEXT UNIQUE,
    role TEXT
);

-- Tabella: Unit 
CREATE TABLE Unit (
    unitId UUID PRIMARY KEY,
    unitName TEXT UNIQUE
);

-- Tabella: Subcompartment
CREATE TABLE Subcompartment (
    subcompartmentId UUID PRIMARY KEY,
    subcompartment TEXT,
    compartment TEXT
);

-- Tabella: IntermediateExchange
CREATE TABLE IntermediateExchange (
    intermediateExchangeId UUID PRIMARY KEY,
    intermediateName TEXT NOT NULL,
    amount DECIMAL,
    modifiedIntermediate BOOLEAN NOT NULL,
    activityId_productId TEXT NOT NULL,
    unitId UUID NOT NULL,
    FOREIGN KEY (unitId) REFERENCES Unit(unitId),
    UNIQUE (activityId_productId) 
);

-- Tabella: ElementaryExchange
CREATE TABLE ElementaryExchange (
    elementaryExchangeId UUID PRIMARY KEY,
    elementaryName TEXT NOT NULL,
    amount DECIMAL,
    modifiedElementary BOOLEAN NOT NULL,
    subcompartmentId UUID,
    unitId UUID NOT NULL,
    FOREIGN KEY (subcompartmentId) REFERENCES Subcompartment(subcompartmentId),
    FOREIGN KEY (unitId) REFERENCES Unit(unitId)
);

-- Tabella: ImpactIndicator
CREATE TABLE ImpactIndicator (
    impactIndicatorId UUID PRIMARY KEY,
    impactName TEXT NOT NULL,
    amount DECIMAL,
    impactMethodName TEXT NOT NULL,
    impactCategoryName TEXT NOT NULL,
    unitName TEXT NOT NULL,
);

-- Tabella: Activity
CREATE TABLE Activity (
    id UUID PRIMARY KEY,
    activityName TEXT NOT NULL,
    includedActivitiesStart TEXT,
    includedActivitiesEnd TEXT,
    geography TEXT,
    specialActivityType TEXT,
    generalComment TEXT,
    modifiedActivity BOOLEAN NOT NULL,
    ISICSection TEXT,
    systemModel TEXT,
    FOREIGN KEY (ISICSection) REFERENCES ISICSection(ISICSection)
);

-- Tabella: CFs (Characterization Factors)
CREATE TABLE CFs (
    elementaryName TEXT NOT NULL,  
    impactMethodName TEXT NOT NULL,
    impactCategoryName TEXT NOT NULL,
    impactName TEXT NOT NULL,
    CF DECIMAL,
    unitName TEXT NOT NULL,
    PRIMARY KEY (elementaryName, impactMethodName, impactCategoryName, impactName)
    FOREIGN KEY (elementaryName) REFERENCES ElementaryExchange(elementaryName)
);

-- Tabella: UnitaryImpact
CREATE TABLE UnitaryImpact (
    activityId_productId TEXT NOT NULL,
    impactMethodName TEXT NOT NULL,
    impactCategoryName TEXT NOT NULL,
    impactName TEXT NOT NULL,
    value DECIMAL,
    unitName TEXT NOT NULL,
    PRIMARY KEY (activityId_productId, impactMethodName, impactCategoryName, impactName)
    FOREIGN KEY (activityId_productId) REFERENCES IntermediateExchange(activityId_productId)
);

-- Tabella di associazione tra Activity e ElementaryExchange
CREATE TABLE Activity_ElementaryExchange (
    activityId UUID,
    elementaryExchangeId UUID,
    PRIMARY KEY (activityId, elementaryExchangeId),
    FOREIGN KEY (activityId) REFERENCES Activity(id) ON DELETE CASCADE,
    FOREIGN KEY (elementaryExchangeId) REFERENCES ElementaryExchange(elementaryExchangeId) ON DELETE CASCADE
);

-- Tabella di associazione tra Activity e IntermediateExchange
CREATE TABLE Activity_IntermediateExchange (
    activityId UUID,
    intermediateExchangeId UUID,
    referenceProduct BOOLEAN NOT NULL,
    PRIMARY KEY (activityId, intermediateExchangeId),
    FOREIGN KEY (activityId) REFERENCES Activity(id) ON DELETE CASCADE,
    FOREIGN KEY (intermediateExchangeId) REFERENCES IntermediateExchange(intermediateExchangeId) ON DELETE CASCADE
);

-- Tabella di associazione tra Activity e impactIndicator
CREATE TABLE Activity_ImpactIndicator (
    activityId UUID,
    impactIndicatorId UUID,
    PRIMARY KEY (activityId, impactIndicatorId),
    FOREIGN KEY (activityId) REFERENCES Activity(id) ON DELETE CASCADE,
    FOREIGN KEY (impactIndicatorId) REFERENCES ImpactIndicator(impactIndicatorId) ON DELETE CASCADE
);

-- Tabella di associazione tra Product e Activity
CREATE TABLE Product_Activity (
    productId UUID NOT NULL,
    activityId UUID NOT NULL,
    amount DECIMAL,
    PRIMARY KEY (productId, activityId),
    FOREIGN KEY (productId) REFERENCES Product(productId) ON DELETE CASCADE,
    FOREIGN KEY (activityId) REFERENCES Activity(id) ON DELETE CASCADE
);

-- Tabella di associazione tra User e Activity
CREATE TABLE User_Activity (
    userid UUID NOT NULL,
    activityid UUID NOT NULL,
    PRIMARY KEY (userid, activityid),
    FOREIGN KEY (userid) REFERENCES utente(userid) ON DELETE CASCADE,
    FOREIGN KEY (activityid) REFERENCES Activity(id) ON DELETE CASCADE
);

-- Tabella di associazione tra User e Product
CREATE TABLE User_Product (
    userid UUID NOT NULL,
    productid UUID NOT NULL,
    PRIMARY KEY (userid, productid),
    FOREIGN KEY (userid) REFERENCES utente(userid) ON DELETE CASCADE,
    FOREIGN KEY (productid) REFERENCES Product(productid) ON DELETE CASCADE
);