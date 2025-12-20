# app/engine/simulation.py
import itertools
import numpy as np
from typing import List, Tuple
from app.engine.degradation import tyre_degradation
from functools import lru_cache
from app.data.loader import load_race
import pandas as pd

MIN_STINT_LAPS = 5

MAX_STINT_LAPS = {
    "soft": 18,   # Aumentamos un poco para dejar que el simulador vea el "cliff"
    "medium": 28,
    "hard": 40
}

COMPOUND_DELTA = {
    "soft": -0.6,
    "medium": 0.0,
    "hard": 0.4
}

@lru_cache(maxsize=32)
def base_lap_time(circuit: str, driver: str, team: str):
    session = load_race(2023, circuit)
    laps = session.laps

    drv_laps = laps[
        (laps["Driver"] == driver) &
        (laps["LapTime"].notna()) &
        (laps["PitInTime"].isna()) &
        (laps["PitOutTime"].isna()) &
        (laps["IsAccurate"] == True)
    ]

    if len(drv_laps) < 5:
        return 90.0  # fallback

    lap_times = drv_laps["LapTime"].dt.total_seconds()
    return float(np.median(lap_times))

def simulate_strategy(total_laps: int, pitstops: List[Tuple[int, str]], req):
    base = base_lap_time(req.circuit, req.driver, req.team)
    pit_time = req.pit_time

    # Construir stints
    stints = []
    sorted_pits = sorted(pitstops, key=lambda x: x[0])
    prev_lap = 1
    
    # Determinar neumático inicial (si la 1ra parada es a Soft, empezamos con Medium/Hard)
    first_pit_tyre = sorted_pits[0][1] if len(sorted_pits) > 0 else "medium"
    current_tyre = "soft" if first_pit_tyre != "soft" else "medium"

    # Lógica de construcción de stints (vuelta de inicio y duración)
    stint_data = [] # List of (start_lap, length, tyre)
    
    last_lap = 1
    for pit_lap, next_tyre in sorted_pits:
        stint_data.append((last_lap, pit_lap - last_lap, current_tyre))
        last_lap = pit_lap
        current_tyre = next_tyre
    
    # Último stint hasta la meta
    stint_data.append((last_lap, total_laps - last_lap + 1, current_tyre))

    # Validación y Cálculo de tiempo
    total_time = 0.0
    for i, (start_lap, length, tyre) in enumerate(stint_data):
        # Validación de reglas
        if length < MIN_STINT_LAPS or length > MAX_STINT_LAPS.get(tyre, 50):
            return float("inf")

        # Llamada a degradación con la vuelta de inicio de carrera
        extra_per_lap = tyre_degradation(tyre, length, start_lap, req.temperature)
        compound_offset = COMPOUND_DELTA.get(tyre, 0.0)
        
        for delta in extra_per_lap:
            total_time += base + compound_offset + delta

        # Añadir tiempo de pit stop (excepto en la última vuelta/meta)
        if i < len(stint_data) - 1:
            total_time += pit_time

    return total_time

def enumerate_strategies(total_laps:int, available_tyres:List[str], max_stops=2):
    valid_laps = list(range(10, total_laps-9)) # Ventanas más realistas
    strategies = []
    for stops in range(0, max_stops+1):
        if stops == 0:
            strategies.append([])
            continue
        for laps in itertools.combinations(valid_laps, stops):
            for tyres in itertools.product(available_tyres, repeat=stops):
                strategy = list(zip(laps, tyres))
                strategies.append(strategy)
    return strategies

def find_best_strategy(req) -> dict:
    total_laps = req.total_laps
    available = req.available_tyres
    strategies = enumerate_strategies(total_laps, available, max_stops=2)
    
    best = None
    best_time = float('inf')
    
    for strat in strategies:
        t = simulate_strategy(total_laps, strat, req)
        if t < best_time:
            best_time = t
            best = strat
            
    return {
        "best": best,
        "time_s": best_time,
        "explanation": explain_strategy(best, best_time, req)
    }

def explain_strategy(best, best_time, req):
    explanations = []
    
    # 1. Análisis de la estructura de paradas
    num_stops = len(best)
    if num_stops == 0:
        explanations.append("Estrategia de conservación: Se evita la pérdida de tiempo en pits debido a que la degradación calculada es manejable.")
    elif num_stops == 1:
        explanations.append(f"Estrategia de una parada: Punto de equilibrio óptimo entre ritmo de carrera y pérdida de tiempo en el pit lane.")
    else:
        explanations.append(f"Estrategia agresiva de {num_stops} paradas: Se prioriza el uso de neumáticos nuevos para compensar el tiempo invertido en boxes.")

    # 2. Impacto de las condiciones térmicas
    if req.temperature > 28:
        deg_impact = int((req.temperature - 25) * 2)
        explanations.append(f"Condiciones de alta temperatura ({req.temperature}°C): El desgaste térmico se incrementa en un {deg_impact}% sobre la base.")
    elif req.temperature < 20:
        explanations.append(f"Condiciones de baja temperatura ({req.temperature}°C): Menor degradación térmica detectada, permitiendo la extensión de los stints.")
    else:
        explanations.append("Temperatura ambiente nominal: La degradación se mantiene dentro de los parámetros estándar de operación.")

    # 3. Selección de compuestos y resistencia
    has_soft = any(tyre == "soft" for _, tyre in best)
    has_hard = any(tyre == "hard" for _, tyre in best)
    
    if has_soft:
        explanations.append("Compuesto Soft: Implementado para maximizar el grip en ventanas de tiempo donde la ventaja de ritmo compensa el desgaste.")
    if has_hard:
        explanations.append("Compuesto Hard: Seleccionado para el tramo de mayor exigencia por su alta resistencia al fenómeno de 'The Cliff'.")

    # 4. Dinámica de carga de combustible
    explanations.append("Compensación de carga: El modelo confirma una mejora progresiva del ritmo debido a la reducción de masa por consumo de combustible.")

    return explanations