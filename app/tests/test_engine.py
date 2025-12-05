from app.core.models import RaceRequest
from app.engine.simulation import find_best_strategy

def test_find_best_strategy_smoke():
    req = RaceRequest(
        circuit="monza",
        temperature=28.0,
        driver="Perez",
        team="Red Bull",
        available_tyres=["soft","medium","hard"],
        total_laps=53,
        pit_time=22.0
    )
    res = find_best_strategy(req)
    assert "best" in res
    assert "time_s" in res
    assert res["time_s"] > 0
