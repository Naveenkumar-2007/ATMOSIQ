TASKS = {
    "temperature": ("temperature_2m", "regression", [1, 3, 6, 12, 24, 48, 72]),
    "apparent_temperature": ("apparent_temperature", "regression", [1, 6, 24]),
    "humidity": ("relative_humidity_2m", "regression", [6, 12, 24]),
    "dew_point": ("dew_point_2m", "regression", [6, 24]),
    "pressure": ("pressure_msl", "regression", [6, 24]),
    "surface_pressure": ("surface_pressure", "regression", [24]),
    "cloud_cover": ("cloud_cover", "regression", [6, 12, 24]),
    "visibility": ("visibility", "regression", [6]),
    "precipitation_amount": ("precipitation", "regression", [1, 6, 24]),
    "rain_occurrence": ("precipitation", "binary", [1, 3, 6, 12, 24]),
    "precipitation_probability": ("precipitation_probability", "regression", [1, 6, 24]),
    "wind_speed": ("wind_speed_10m", "regression", [1, 6, 24, 48]),
    "wind_gusts": ("wind_gusts_10m", "regression", [1, 6, 24]),
    "wind_direction": ("wind_direction_10m", "direction_class", [1, 6, 24]),
    "weather_condition": ("weather_code", "condition_class", [1, 6, 24]),
}


def source_of(task):
    return TASKS[task][0]


def kind_of(task):
    return TASKS[task][1]


def horizons_of(task):
    return TASKS[task][2]


def is_classification(task):
    return kind_of(task) in ("binary", "direction_class", "condition_class")
