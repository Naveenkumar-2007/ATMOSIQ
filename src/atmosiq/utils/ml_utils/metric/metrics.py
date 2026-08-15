import numpy as np
from sklearn import metrics as sk


def _a(y):
    return np.asarray(y, dtype=float)


def _p(y):
    return np.asarray(y, dtype=float)


def mae(y, p):
    return float(np.mean(np.abs(_a(y) - _p(p))))


def rmse(y, p):
    return float(np.sqrt(np.mean((_a(y) - _p(p)) ** 2)))


def r2(y, p):
    return float(sk.r2_score(_a(y), _p(p)))


def mase(y, p, seasonal=24):
    y = _a(y)
    p = _p(p)
    naive = np.mean(np.abs(y[seasonal:] - y[:-seasonal])) if len(y) > seasonal else np.mean(np.abs(np.diff(y)))
    return float(np.mean(np.abs(y - p)) / naive) if naive > 0 else float("inf")


def skill_score(y, p, baseline):
    denom = np.sum((_a(y) - _a(baseline)) ** 2)
    return float(1 - np.sum((_a(y) - _p(p)) ** 2) / denom) if denom > 0 else 0.0


def accuracy(y, p):
    return float(sk.accuracy_score(_a(y), _p(p)))


def macro_f1(y, p):
    return float(sk.f1_score(_a(y), _p(p), average="macro", zero_division=0))


def precision(y, p):
    return float(sk.precision_score(_a(y), _p(p), zero_division=0))


def recall(y, p):
    return float(sk.recall_score(_a(y), _p(p), zero_division=0))


def f1(y, p):
    return float(sk.f1_score(_a(y), _p(p), zero_division=0))


def roc_auc(y, proba):
    y = _a(y)
    return float(sk.roc_auc_score(y, _p(proba))) if len(np.unique(y)) > 1 else float("nan")


def pr_auc(y, proba):
    y = _a(y)
    if len(np.unique(y)) < 2:
        return float("nan")
    prec, rec, _ = sk.precision_recall_curve(y, _p(proba))
    return float(sk.auc(rec, prec))


def brier_score(y, proba):
    return float(np.mean((_a(y) - _p(proba)) ** 2))


def log_loss(y, proba):
    proba = np.clip(_p(proba), 1e-6, 1 - 1e-6)
    return float(sk.log_loss(_a(y), proba))


def pinball_loss(y, p, quantile):
    y, p = _a(y), _p(p)
    err = y - p
    return float(np.mean(np.where(err >= 0, quantile * err, (quantile - 1) * err)))


def coverage(y, lower, upper):
    return float(np.mean((_a(y) >= _a(lower)) & (_a(y) <= _a(upper))))


def interval_width(lower, upper):
    return float(np.mean(_a(upper) - _a(lower)))


def calibration_error(y, proba, bins=10):
    y, proba = _a(y), _p(proba)
    edges = np.linspace(0, 1, bins + 1)
    errors = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (proba >= lo) & (proba < hi + (1 if hi == 1 else 0))
        if mask.sum() > 0:
            errors.append(abs(y[mask].mean() - proba[mask].mean()))
    return float(np.mean(errors)) if errors else float("nan")
