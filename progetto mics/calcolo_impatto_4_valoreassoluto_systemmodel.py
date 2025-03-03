import psycopg2

# Configurazione del database
DB_CONFIG = {
    "dbname": "ecoinvent",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

# Parametri di input
activity_id = "9d05ca75-e018-5a21-8812-e02bd8a74da2"
impact_name = "global warming potential (GWP100)"
impact_category_name = "climate change"
impact_method_name = "EF v3.0"

def get_system_model(activity_id):
    """Recupera il system_model dalla tabella activity dato l'activity_id."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT systemmodel FROM activity WHERE id = %s
        """, (activity_id,))
        
        result = cursor.fetchone()
        return result[0] if result else None

    except Exception as e:
        print(f"Errore durante il recupero del system_model: {e}")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()

def calculate_impact():
    try:
        # Recupera il system_model
        system_model = get_system_model(activity_id)
        if not system_model:
            print("Errore: system_model non trovato per l'activity_id fornito.")
            return
        
        # Connessione al database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Passo 1: Recupera gli ID degli scambi elementari per l'attività specificata
        cursor.execute("""
            SELECT elementaryExchangeId
            FROM Activity_ElementaryExchange
            WHERE activityId = %s
        """, (activity_id,))
        elementary_exchange_ids = [str(row[0]) for row in cursor.fetchall()]

        # Passo 2: Recupera amount ed elementaryName dagli ID degli exchange
        total_impact_elementary = 0
        if elementary_exchange_ids:
            cursor.execute("""
                SELECT ee.amount, ee.elementaryName
                FROM ElementaryExchange ee
                WHERE ee.elementaryExchangeId = ANY(%s::uuid[])
            """, (elementary_exchange_ids,))
            exchanges = cursor.fetchall()

            # Calcola l'impatto sommando il prodotto di amount e CF
            for amount, elementary_name in exchanges:
                cursor.execute("""
                    SELECT cf.CF
                    FROM CFs cf
                    WHERE cf.elementaryName = %s
                      AND cf.impactName = %s
                      AND cf.impactCategoryName = %s
                      AND cf.impactMethodName = %s
                """, (elementary_name, impact_name, impact_category_name, impact_method_name))
                cf_result = cursor.fetchone()

                cf_value = cf_result[0] if cf_result else 0
                total_impact_elementary += abs(amount * cf_value)

        # Passo 3: Recupera gli ID degli intermediate exchange per l'attività specificata
        cursor.execute("""
            SELECT intermediateExchangeId
            FROM Activity_IntermediateExchange
            WHERE activityId = %s
        """, (activity_id,))
        intermediate_exchange_ids = [str(row[0]) for row in cursor.fetchall()]

        # Passo 4: Recupera amount ed activityId_productId dagli ID degli intermediate exchange
        total_impact_intermediate = 0
        if intermediate_exchange_ids:
            cursor.execute("""
                SELECT ie.amount, ie.activityId_productId
                FROM IntermediateExchange ie
                WHERE ie.intermediateExchangeId = ANY(%s::uuid[])
            """, (intermediate_exchange_ids,))
            intermediate_exchanges = cursor.fetchall()

            # Calcola l'impatto sommando il prodotto di amount e unitary impact
            for amount, activityId_productId in intermediate_exchanges:
                cursor.execute("""
                    SELECT ui.value
                    FROM UnitaryImpact ui
                    WHERE ui.activityId_productId = %s
                      AND ui.impactName = %s
                      AND ui.impactCategoryName = %s
                      AND ui.impactMethodName = %s
                      AND ui.systemModel = %s
                """, (activityId_productId, impact_name, impact_category_name, impact_method_name, system_model))
                unitary_impact_result = cursor.fetchone()

                unitary_impact_value = unitary_impact_result[0] if unitary_impact_result else 0
                total_impact_intermediate += abs(amount * unitary_impact_value)

        # Somma totale degli impatti
        total_impact = (total_impact_elementary + total_impact_intermediate)

        print(f"L'impatto degli scambi elementari calcolato è: {total_impact_elementary}")
        print(f"L'impatto degli scambi intermedi calcolato è: {total_impact_intermediate}")
        print(f"L'impatto totale calcolato è: {total_impact}")

    except Exception as e:
        print(f"Errore durante il calcolo dell'impatto: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    calculate_impact()
