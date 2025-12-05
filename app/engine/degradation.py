# app/engine/degradation.py
import numpy as np

# parámetros por compuesto (ejemplo)
COMPOUND_PARAMS = {
    "soft":  {"base_increase": 0.06, "wear_rate": 0.015},   # segundos por vuelta adicional
    "medium": {"base_increase": 0.03, "wear_rate": 0.009},
    "hard":  {"base_increase": 0.01, "wear_rate": 0.005},
}

def tyre_degradation(compound: str, stint_length: int):
    """
    Devuelve lista de delta-times por vuelta en el stint (relativo al base lap).
    Modelo simple: tiempo_extra(v) = base_increase + wear_rate * v^1.1
    """
    p = COMPOUND_PARAMS.get(compound, COMPOUND_PARAMS["medium"])
    v = np.arange(1, stint_length+1)
    extra = p["base_increase"] + p["wear_rate"] * (v ** 1.1)
    return extra.tolist()
