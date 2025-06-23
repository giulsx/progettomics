import uuid
import hashlib

def generate_deterministic_uuid(name: str, salt: str) -> str:
    """
    Genera uno UUID5 deterministico basato su nome e salt.
    """
    base = f"{name}_{salt}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, base))

def generate_activity_id(name: str, reference_product: str):
    """
    Genera UUID per attività basato su nome e prodotto di riferimento.
    """
    return generate_deterministic_uuid(name, reference_product),  # ritorna una tupla

def generate_intermediate_exchange_id(name: str, amount: float, salt: str):
    """
    Genera UUID per intermediate exchange in modo deterministico.
    """
    base = f"{name}_{amount}_{salt}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, base))

def generate_elementary_exchange_id(name: str, amount: float):
    """
    Genera UUID per elementary exchange (senza salt se non serve).
    """
    base = f"{name}_{amount}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, base))
