# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.models import RaceRequest, StrategyResponse, PitStop
from app.engine.simulation import find_best_strategy

app = FastAPI(title="F1 Pit Strategy API")

# 1. PRIMERO LOS ENDPOINTS (Python)
@app.post("/recommend", response_model=StrategyResponse)
def recommend(req: RaceRequest):
    result = find_best_strategy(req)
    best = result["best"]
    time_s = result["time_s"]
    
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
        details={
            "raw": str(best),
            "explanation": result.get("explanation", [])
        }
    )

# 2. AL FINAL LOS ESTÁTICOS
# Esto asegura que si la ruta no es /recommend, busque en la carpeta static
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
