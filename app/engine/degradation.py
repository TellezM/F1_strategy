# app/engine/degradation.py
import numpy as np

# Parámetros por compuesto
# Agregamos "limit": vuelta donde el neumático pierde el agarre drásticamente
COMPOUND_PARAMS = {
    "soft":   {"base_increase": 0.06, "wear_rate": 0.015, "limit": 15},
    "medium": {"base_increase": 0.03, "wear_rate": 0.009, "limit": 25},
    "hard":   {"base_increase": 0.01, "wear_rate": 0.005, "limit": 35},
}

def tyre_degradation(compound: str, stint_length: int, start_lap: int, temperature: float = 25.0):
    """
    Devuelve lista de delta-times por vuelta considerando:
    1. Degradación base + temperatura.
    2. El Acantilado (The Cliff): Caída de rendimiento tras superar el límite.
    3. Efecto Combustible: Mejora de tiempo por pérdida de peso.
    """
    p = COMPOUND_PARAMS.get(compound.lower(), COMPOUND_PARAMS["medium"])

    temp_factor = 1 + 0.02 * (temperature - 25)
    temp_factor = max(0.8, min(temp_factor, 1.4))

    delta_times = []
    
    for i in range(1, stint_length + 1):
        # Vuelta absoluta en la carrera (para el combustible)
        current_absolute_lap = start_lap + i - 1
        
        # --- MEJORA 1: EL ACANTILADO (THE CLIFF) ---
        cliff_penalty = 0
        if i > p["limit"]:
            # Penalización exponencial tras pasar el límite de vida útil
            cliff_penalty = (i - p["limit"]) * 1.2 

        # --- MEJORA 2: EFECTO COMBUSTIBLE ---
        # El coche es ~0.04s más rápido cada vuelta que pasa por peso
        fuel_benefit = current_absolute_lap * 0.04
        
        # Cálculo de degradación base
        base_deg = (p["base_increase"] + p["wear_rate"] * (i ** 1.1)) * temp_factor
        
        # Resultado final para esa vuelta
        total_delta = base_deg + cliff_penalty - fuel_benefit
        delta_times.append(total_delta)

    return delta_times

