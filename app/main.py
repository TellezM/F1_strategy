# app/main.py
from fastapi import FastAPI
from app.core.models import RaceRequest, StrategyResponse, PitStop
from app.engine.simulation import find_best_strategy
import math

app = FastAPI(title="F1 Pit Strategy API")

@app.post("/recommend", response_model=StrategyResponse)
def recommend(req: RaceRequest):
    result = find_best_strategy(req)
    best = result["best"]
    time_s = result["time_s"]
    # format estimated time hh:mm:ss
    h = int(time_s // 3600)
    m = int((time_s % 3600) // 60)
    s = int(time_s % 60)
    est = f"{h:d}:{m:02d}:{s:02d}"
    pitstops = [PitStop(lap=lap, tyre=tyre) for lap, tyre in best]
    strategy_text = f"{len(best)} paradas" if best else "0 paradas"
    return StrategyResponse(
        strategy=strategy_text,
        pitstops=pitstops,
        estimated_time=est,
        expected_total_seconds=time_s,
        details={"raw": str(best)}
    )
