from atmosiq.providers.base import WeatherProvider as WeatherProvider
from atmosiq.providers.open_meteo import OpenMeteoProvider

_REGISTRY = {"open_meteo": OpenMeteoProvider}


def get_provider(name, settings=None):
    if name not in _REGISTRY:
        raise ValueError(f"Unknown weather provider: {name}. Known: {sorted(_REGISTRY)}")
    return _REGISTRY[name](settings or {})
