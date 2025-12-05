# app/core/models.py
from pydantic import BaseModel
from typing import List, Optional

class RaceRequest(BaseModel):
    circuit: str
    temperature: float
    driver: str
    team: str
    available_tyres: List[str]  # e.g. ["soft", "medium", "hard"]
    total_laps: int
    pit_time: Optional[float] = 22.0  # segundos, configurable

class PitStop(BaseModel):
    lap: int
    tyre: str

class StrategyResponse(BaseModel):
    strategy: str
    pitstops: List[PitStop]
    estimated_time: str  # "1:29:42" o segundos
    expected_total_seconds: float
    details: Optional[dict] = None
