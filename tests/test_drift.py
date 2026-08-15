import numpy as np

from atmosiq.components.drift_monitor import compute_psi


def test_psi_detects_shift():
    rng = np.random.default_rng(0)
    reference = rng.normal(20, 2, 1000)
    shifted = rng.normal(30, 2, 1000)
    assert compute_psi(reference, shifted) > 0.25


def test_psi_stable_distribution():
    rng = np.random.default_rng(1)
    reference = rng.normal(20, 2, 1000)
    same = rng.normal(20, 2, 1000)
    assert compute_psi(reference, same) < 0.25
