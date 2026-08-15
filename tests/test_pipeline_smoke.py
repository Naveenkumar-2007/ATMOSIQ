def test_config_loads(project_root):
    from atmosiq.entity.config_entity import AppConfig

    app = AppConfig()
    assert app.locations[0]["id"] == "kavali"
    assert app.horizons[0] == 1
    assert app.splits["train"] == 0.70
    assert app.raw["provider"]["name"] == "open_meteo"
