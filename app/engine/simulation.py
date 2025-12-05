# app/engine/simulation.py
import itertools
import numpy as np
from typing import List, Tuple
from app.engine.degradation import tyre_degradation

# parámetros globales
MIN_STINT_LAPS = 5

def base_lap_time(circuit: str, driver: str, team: str):
    """
    Aquí cargas métricas históricas. Por ahora devuelve un valor de ejemplo (s).
    Reemplazar por lookup real usando loader.
    """
    # ejemplo hipótesis: 90 segundos de base
    return 90.0

def simulate_strategy(total_laps:int, pitstops:List[Tuple[int,str]], req):
    """
    Simula una estrategia dada: pitstops = list of (lap, tyre)
    Retorna tiempo total promedio (segundos).
    """
    base = base_lap_time(req.circuit, req.driver, req.team)
    pit_time = req.pit_time
    # construir stints
    stints = []
    sorted_pits = sorted(pitstops, key=lambda x: x[0])
    prev_lap = 1
    prev_tyre = None
    for lap, tyre in sorted_pits + [(total_laps+1, None)]:
        stint_len = lap - prev_lap
        if stint_len <= 0:
            return float('inf')  # estrategia inválida
        stints.append((stint_len, tyre if tyre else prev_tyre))
        prev_lap = lap
        prev_tyre = tyre
    # calcular tiempo
    total_time = 0.0
    for i, (stint_len, tyre) in enumerate(stints):
        tyre = tyre or "medium"
        extra_per_lap = tyre_degradation(tyre, stint_len)
        for delta in extra_per_lap:
            lap_time = base + delta
            total_time += lap_time
        if i < len(stints)-1:
            total_time += pit_time
    return total_time

def enumerate_strategies(total_laps:int, available_tyres:List[str], max_stops=3):
    """
    Genera estrategias válidas (hasta max_stops), retorna listas de pitstops (lap,tyre).
    Para ahorrar combinaciones: solo permite paradas entre lap 5 y lap total-5.
    """
    valid_laps = list(range(5, total_laps-4))
    strategies = []
    for stops in range(0, max_stops+1):
        if stops == 0:
            strategies.append([])
            continue
        # elegir paradas (combinaciones de vueltas)
        for laps in itertools.combinations(valid_laps, stops):
            # asignar compuestos (cartesian product)
            for tyres in itertools.product(available_tyres, repeat=stops):
                strategy = list(zip(laps, tyres))
                # validar stints min length
                laps_sorted = [0] + list(laps) + [total_laps]
                lengths = [laps_sorted[i+1]-laps_sorted[i] for i in range(len(laps_sorted)-1)]
                if all(l >= MIN_STINT_LAPS for l in lengths):
                    strategies.append(strategy)
    return strategies

def find_best_strategy(req) -> dict:
    total_laps = req.total_laps
    available = req.available_tyres
    strategies = enumerate_strategies(total_laps, available, max_stops=2)  # por defecto hasta 2 paradas, ajustar si quieres 3
    best = None
    best_time = float('inf')
    for strat in strategies:
        t = simulate_strategy(total_laps, strat, req)
        if t < best_time:
            best_time = t
            best = strat
    return {"best": best, "time_s": best_time}
