import numpy as np

from atmosiq.utils.ml_utils.model.factory import ModelFactory


class QuantileEnsemble:
    def __init__(self, base="lightgbm", quantiles=(0.1, 0.5, 0.9)):
        self.base = base
        self.quantiles = quantiles
        self.models = []

    def fit(self, X, y):
        self.models = []
        for q in self.quantiles:
            if self.base == "lightgbm":
                params = {"objective": "quantile", "alpha": q}
            else:
                params = {"objective": "reg:quantileerror", "quantile_alpha": q}
            model = ModelFactory.create(self.base, "regression", params)
            model.fit(X, y)
            self.models.append(model)
        return self

    def predict_quantiles(self, X):
        return np.column_stack([m.predict(X) for m in self.models])
