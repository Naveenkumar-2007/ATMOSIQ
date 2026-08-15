import numpy as np
from sklearn.ensemble import (
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge

from atmosiq.exception.exception import AtmosIQException
from atmosiq.utils.main_utils.utils import load_object, save_object


class ModelWrapper:
    def __init__(self, name, estimator, task, params):
        self.name = name
        self.estimator = estimator
        self.task = task
        self.params = params

    def fit(self, X, y):
        self.estimator.fit(X, y)
        return self

    def predict(self, X):
        return self.estimator.predict(X)

    def predict_proba(self, X):
        if hasattr(self.estimator, "predict_proba"):
            return self.estimator.predict_proba(X)[:, 1]
        raise AtmosIQException(f"{self.name} has no predict_proba")

    def save(self, path):
        save_object(path, {"name": self.name, "task": self.task, "params": self.params, "estimator": self.estimator})

    @staticmethod
    def load(path, trusted_hashes=None):
        blob = load_object(path, trusted_hashes)
        return ModelWrapper(blob["name"], blob["estimator"], blob["task"], blob["params"])

    def metadata(self):
        return {"name": self.name, "task": self.task, "params": self.params}


class PersistenceModel:
    def __init__(self, horizon):
        self.horizon = horizon
        self.name = "persistence"

    def fit(self, X, y):
        return self

    def predict(self, X):
        return np.asarray(X[:, 0], dtype=float)

    def predict_proba(self, X):
        return (np.asarray(X[:, 0], dtype=float) > 0.2).astype(float)

    def save(self, path):
        save_object(path, {"name": self.name, "horizon": self.horizon})

    @staticmethod
    def load(path, trusted_hashes=None):
        return PersistenceModel(load_object(path, trusted_hashes)["horizon"])

    def metadata(self):
        return {"name": self.name, "horizon": self.horizon}


class SeasonalNaiveModel:
    def __init__(self, season_hours=24, column_index=1):
        self.season_hours = season_hours
        self.column_index = column_index
        self.name = f"seasonal_naive_{season_hours}h"

    def fit(self, X, y):
        return self

    def predict(self, X):
        return np.asarray(X[:, self.column_index], dtype=float)

    def predict_proba(self, X):
        return (np.asarray(X[:, self.column_index], dtype=float) > 0.2).astype(float)

    def save(self, path):
        save_object(path, {"name": self.name, "season_hours": self.season_hours, "column_index": self.column_index})

    @staticmethod
    def load(path, trusted_hashes=None):
        blob = load_object(path, trusted_hashes)
        return SeasonalNaiveModel(blob["season_hours"], blob["column_index"])

    def metadata(self):
        return {"name": self.name}


class ClimatologyModel:
    def __init__(self):
        self.name = "climatology"
        self.lookup = {}
        self.fallback = 0.0

    def fit(self, X, y, hour=None, month=None):
        self.fallback = float(np.mean(y))
        if hour is not None and month is not None:
            for h, m, t in zip(hour, month, y):
                self.lookup.setdefault((int(h), int(m)), []).append(float(t))
            self.lookup = {k: float(np.mean(v)) for k, v in self.lookup.items()}
        return self

    def predict(self, X, hour=None, month=None):
        if hour is None:
            return np.full(len(X), self.fallback)
        return np.array([self.lookup.get((int(h), int(m)), self.fallback) for h, m in zip(hour, month)])

    def save(self, path):
        save_object(path, {"name": self.name, "lookup": self.lookup, "fallback": self.fallback})

    @staticmethod
    def load(path, trusted_hashes=None):
        blob = load_object(path, trusted_hashes)
        model = ClimatologyModel()
        model.lookup = {tuple(map(int, k.strip("()").split(", "))): v for k, v in blob["lookup"].items()} if blob["lookup"] else {}
        model.fallback = blob["fallback"]
        return model

    def metadata(self):
        return {"name": self.name}


def _catboost_reg(p):
    try:
        from catboost import CatBoostRegressor
        params = {k: v for k, v in p.items() if k not in ("iterations", "depth")}
        return CatBoostRegressor(thread_count=-1, iterations=p.get("iterations", 80), depth=p.get("depth", 6), verbose=False, **params)
    except ImportError:
        raise AtmosIQException("catboost not installed; run: pip install catboost")


def _catboost_clf(p):
    try:
        from catboost import CatBoostClassifier
        params = {k: v for k, v in p.items() if k not in ("iterations", "depth", "auto_class_weights", "scale_pos_weight", "class_weight")}
        return CatBoostClassifier(thread_count=-1, iterations=p.get("iterations", 80), depth=p.get("depth", 6), auto_class_weights=p.get("auto_class_weights", "Balanced"), verbose=False, **params)
    except ImportError:
        raise AtmosIQException("catboost not installed; run: pip install catboost")


class ModelFactory:
    REGRESSORS = {
        "linear_regression": lambda p: LinearRegression(),
        "ridge": lambda p: Ridge(**{k: v for k, v in p.items() if k not in ("scale_pos_weight", "class_weight")}),
        "random_forest": lambda p: RandomForestRegressor(n_jobs=-1, n_estimators=p.get("n_estimators", 40), max_depth=p.get("max_depth", 12), random_state=42, **{k: v for k, v in p.items() if k not in ("n_estimators", "max_depth", "scale_pos_weight", "class_weight")}),
        "extra_trees": lambda p: ExtraTreesRegressor(n_jobs=-1, n_estimators=p.get("n_estimators", 40), max_depth=p.get("max_depth", 12), random_state=42, **{k: v for k, v in p.items() if k not in ("n_estimators", "max_depth", "scale_pos_weight", "class_weight")}),
        "hist_gb": lambda p: HistGradientBoostingRegressor(**{k: v for k, v in p.items() if k not in ("scale_pos_weight", "class_weight")}),
        "xgboost": lambda p: __import__("xgboost", fromlist=["XGBRegressor"]).XGBRegressor(n_jobs=-1, n_estimators=p.get("n_estimators", 60), **{k: v for k, v in p.items() if k not in ("n_estimators", "scale_pos_weight", "class_weight")}),
        "lightgbm": lambda p: __import__("lightgbm", fromlist=["LGBMRegressor"]).LGBMRegressor(n_jobs=-1, n_estimators=p.get("n_estimators", 60), verbose=-1, **{k: v for k, v in p.items() if k not in ("n_estimators", "scale_pos_weight", "class_weight")}),
        "catboost": _catboost_reg,
    }
    CLASSIFIERS = {
        "logistic_regression": lambda p: LogisticRegression(max_iter=200, class_weight=p.get("class_weight", "balanced"), tol=1e-2, **{k: v for k, v in p.items() if k not in ("class_weight", "scale_pos_weight", "max_iter", "tol")}),
        "random_forest_clf": lambda p: RandomForestClassifier(n_jobs=-1, class_weight=p.get("class_weight", "balanced"), n_estimators=p.get("n_estimators", 40), max_depth=p.get("max_depth", 12), random_state=42, **{k: v for k, v in p.items() if k not in ("n_estimators", "max_depth", "class_weight", "scale_pos_weight")}),
        "extra_trees_clf": lambda p: ExtraTreesClassifier(n_jobs=-1, class_weight=p.get("class_weight", "balanced"), n_estimators=p.get("n_estimators", 40), max_depth=p.get("max_depth", 12), random_state=42, **{k: v for k, v in p.items() if k not in ("n_estimators", "max_depth", "class_weight", "scale_pos_weight")}),
        "hist_gb_clf": lambda p: HistGradientBoostingClassifier(class_weight=p.get("class_weight", "balanced"), **{k: v for k, v in p.items() if k not in ("class_weight", "scale_pos_weight")}),
        "xgboost_clf": lambda p: __import__("xgboost", fromlist=["XGBClassifier"]).XGBClassifier(n_jobs=-1, n_estimators=p.get("n_estimators", 60), scale_pos_weight=p.get("scale_pos_weight", 1.0), random_state=42, **{k: v for k, v in p.items() if k not in ("n_estimators", "scale_pos_weight", "class_weight")}),
        "lightgbm_clf": lambda p: __import__("lightgbm", fromlist=["LGBMClassifier"]).LGBMClassifier(n_jobs=-1, n_estimators=p.get("n_estimators", 60), scale_pos_weight=p.get("scale_pos_weight", 1.0), class_weight=p.get("class_weight"), verbose=-1, random_state=42, **{k: v for k, v in p.items() if k not in ("n_estimators", "scale_pos_weight", "class_weight")}),
        "catboost_clf": _catboost_clf,
    }

    @classmethod
    def create(cls, name, task, params=None):
        params = params or {}
        table = cls.CLASSIFIERS if task == "rain_occurrence" else cls.REGRESSORS
        if name not in table:
            raise AtmosIQException(f"Unknown model {name} for task {task}")
        return ModelWrapper(name, table[name](params), task, params)

    @classmethod
    def create_baseline(cls, name, horizon):
        if name == "persistence":
            return PersistenceModel(horizon)
        if name == "seasonal_naive_24h":
            return SeasonalNaiveModel(24)
        if name == "seasonal_naive_168h":
            return SeasonalNaiveModel(168)
        if name == "climatology":
            return ClimatologyModel()
        raise AtmosIQException(f"Unknown baseline {name}")
