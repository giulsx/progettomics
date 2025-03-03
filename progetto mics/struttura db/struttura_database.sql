CREATE DATABASE database_ecoinvent;
USE database_ecoinvent;

-- Tabella: Activity
CREATE TABLE Activity (
    id UUID PRIMARY KEY,
    activityName TEXT NOT NULL,
    includedActivitiesStart TEXT,
    includedActivitiesEnd TEXT,
    geography TEXT,
    specialActivityType TEXT,
    generalComment TEXT,
    modifiedActivity BOOLEAN,
    FOREIGN KEY ISICSection REFERENCES ISICSection(ISICSection),
    FOREIGN KEY intermediateExchangeId REFERENCES IntermediateExchange(intermediateExchangeId),
    FOREIGN KEY elementaryExchangeId REFERENCES elementatyExchange(elementaryExchangeId),
    FOREIGN KEY impactIndicatorId REFERENCES ImpactIndicator(impactIndicatorId),
);

-- Tabella: ISICSection
CREATE TABLE ISICSection (
    ISICSection TEXT PRIMARY KEY,
    ISICClassification TEXT,
    Sector TEXT
);
-- Tabella: IntermediateExchange
CREATE TABLE IntermediateExchange (
    intermediateExchangeId UUID PRIMARY KEY,
    intermediateName TEXT NOT NULL,
    amount DECIMAL,
    modifiedIntermediate BOOLEAN,
    activityId_productId NOT NULL, //combinazione UUID_UUID
    referenceProduct BOOLEAN,
    FOREIGN KEY unitId UUID NOT NULL REFERENCES Unit(unitId)
);

-- Tabella: ElementaryExchange
CREATE TABLE ElementaryExchange (
    elementaryExchangeId UUID PRIMARY KEY,
    elementaryName TEXT NOT NULL,
    amount DECIMAL,
    modifiedElementary BOOLEAN,
    FOREIGN KEY subcompartmentId REFERENCES Subcompartment(subcompartmentId),
    FOREIGN KEY unitId UUID NOT NULL REFERENCES Unit(unitId)
);

-- Tabella: Subcompartment
CREATE TABLE Subcompartment (
    subcompartmentId UUID PRIMARY KEY,
    subcompartment TEXT,
    compartment TEXT
);


-- Tabella: ImpactIndicator
CREATE TABLE ImpactIndicator (
    impactIndicatorId UUID PRIMARY KEY,
    impactName TEXT NOT NULL,
    unitName TEXT REFERENCES unit(unitName),
    amount DECIMAL,
    impactMethodName TEXT NOT NULL,
    impactCategoryName TEXT NOT NULL,
    FOREIGN KEY unitId UUID NOT NULL REFERENCES Unit(unitId)

);

-- Tabella: CFs (Characterization Factors)
CREATE TABLE CFs (
    elementaryName TEXT NOT NULL REFERENCES ElementaryExchange(elementaryName),
    impactMethodName TEXT NOT NULL,
    impactCategoryName TEXT NOT NULL,
    impactName TEXT NOT NULL,
    CF DECIMAL,
    PRIMARY KEY (elementaryName, impactMethodId, impactCategoryName, impactName)
);


-- Tabella: UnitaryImpact
CREATE TABLE UnitaryImpact (
    activityId_productId NOT NULL REFERENCES IntermediateExchange(activityId_productId),
    impactMethodName TEXT NOT NULL,
    impactCategoryName TEXT NOT NULL,
    impactName TEXT NOT NULL,
    value DECIMAL,
    PRIMARY KEY (activityId_productId, impactMethodName, impactCategoryName, impactName)
);

-- Tabella: Unit
CREATE TABLE Unit (
    unitId UUID PRIMARY KEY,
    unitName TEXT
);
