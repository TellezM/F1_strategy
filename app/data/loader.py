import fastf1
fastf1.Cache.enable_cache("app/data/cache")

def load_race(year, circuit):
    session = fastf1.get_session(year, circuit, "R")
    session.load()
    return session