import math

CONDITION_CLASSES = ["clear", "partly_cloudy", "cloudy", "fog", "rain", "heavy_rain", "snow", "thunderstorm"]
COMPASS_16 = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def weather_code_to_condition(code):
    if code is None:
        return "cloudy"
    try:
        if isinstance(code, float) and math.isnan(code):
            return "cloudy"
        code = int(code)
    except (TypeError, ValueError, OverflowError):
        return "cloudy"
    if code == 0:
        return "clear"
    if code <= 2:
        return "partly_cloudy"
    if code == 3:
        return "cloudy"
    if code in (45, 48):
        return "fog"
    if 51 <= code <= 57 or 61 <= code <= 65:
        return "rain"
    if 66 <= code <= 67 or 80 <= code <= 82:
        return "heavy_rain"
    if 71 <= code <= 77 or code in (85, 86):
        return "snow"
    if code >= 95:
        return "thunderstorm"
    return "cloudy"


def condition_index(code):
    if code is None:
        return float("nan")
    try:
        if isinstance(code, float) and math.isnan(code):
            return float("nan")
        return float(CONDITION_CLASSES.index(weather_code_to_condition(code)))
    except (TypeError, ValueError, OverflowError):
        return float("nan")


def compass_index(deg):
    if deg is None:
        return float("nan")
    try:
        if isinstance(deg, float) and math.isnan(deg):
            return float("nan")
        val = ((float(deg) % 360) / 22.5) + 0.5
        if math.isnan(val):
            return float("nan")
        return float(int(val) % 16)
    except (TypeError, ValueError, OverflowError):
        return float("nan")


def rain_intensity_category(mm, intensity):
    if mm is None or mm < 0.2:
        return "no_rain"
    if mm < intensity["light"]:
        return "light"
    if mm < intensity["moderate"]:
        return "moderate"
    if mm < intensity["heavy"]:
        return "heavy"
    return "very_heavy"
