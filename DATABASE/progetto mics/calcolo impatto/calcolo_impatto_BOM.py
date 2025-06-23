import psycopg2
import pandas as pd
from decimal import Decimal

# Configurazione DB
DB_CONFIG = {
    "dbname": "ecoinvent",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

# Parametri impatto
impact_name = "global warming potential (GWP100)"
impact_category_name = "climate change"
impact_method_name = "EF v3.0"

impact_name = "global warming potential (GWP100)"
impact_category_name = "climate change"
impact_method_name = "CML v4.8 2016"

impact_name = "acidification"
impact_category_name = "acidification (incl. fate, average Europe total, A&B)"
impact_method_name = "CML v4.8 2016"

impact_name = "eutrophication (fate not incl.)"
impact_category_name = "eutrophication"
impact_method_name = "CML v4.8 2016"

impact_name = "tropospheric ozone concentration increase no LT"
impact_category_name = "photochemical oxidant formation: human health no LT"
impact_method_name = "EF v3.0"

impact_name = "abiotic depletion potential (ADP): elements (ultimate reserves)"
impact_category_name = "material resources: metals/minerals"
impact_method_name = "CML v4.8 2016"

impact_name = "energy resources: non-renewable"
impact_category_name = "abiotic depletion potential (ADP): fossil fuels"
impact_method_name = "CML v4.8 2016"

impact_name = "user deprivation potential (deprivation-weighted water consumption)"
impact_category_name = "water use"
impact_method_name = "EF v3.0"


# Carica file Excel
df = pd.read_excel("C:\\Users\\giuli\\OneDrive - Università Politecnica delle Marche\\provaBOM.xlsx")

def get_unitary_impact(activity_product_id, system_model):
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT value FROM UnitaryImpact
                WHERE activityId_productId = %s
                  AND impactName = %s
                  AND impactCategoryName = %s
                  AND impactMethodName = %s
                  AND systemModel = %s
            """, (activity_product_id, impact_name, impact_category_name, impact_method_name, system_model))
            result = cur.fetchone()
            return Decimal(result[0]) if result else Decimal(0)

def calculate_and_print_impacts(system_model):
    total_impact = Decimal(0)
    results = []

    for _, row in df.iterrows():
        name = row['Intermediate Exchange']
        activity_product_id = row['activityid_productid']
        amount_raw = row['amount']

        try:
            amount = Decimal(str(amount_raw).replace(",", ".")) if pd.notnull(amount_raw) else Decimal(0)
        except Exception as e:
            print(f"Errore nella conversione dell'amount '{amount_raw}' per '{name}': {e}")
            continue

        if pd.notnull(activity_product_id):
            unit_value = get_unitary_impact(activity_product_id, system_model)
            impact = amount * unit_value
            total_impact += impact

            results.append({
                "Exchange": name,
                "Activity_Product_ID": activity_product_id,
                "Amount": amount,
                "Unitary Impact": unit_value,
                "Impact": impact
            })

    # Stampa risultati per riga
    for r in results:
        print(f"{r['Exchange']}: amount={r['Amount']}, unitary_impact={r['Unitary Impact']}, IMPATTO={r['Impact']}")

    # Stampa impatto totale
    print(f"\nImpatto totale: {total_impact}")

# Esecuzione
calculate_and_print_impacts("cutoff")
