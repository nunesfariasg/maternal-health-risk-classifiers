"""Estatísticas descritivas e testes exigidos pelo enunciado."""

from itertools import combinations

import numpy as np
from scipy.stats import kruskal, mannwhitneyu

from src.models import ORDER


def compare(scores):
    values = scores[ORDER].to_numpy(dtype=float)
    if len(scores) != 10 or not np.isfinite(values).all() or ((values < 0) | (values > 1)).any():
        raise ValueError("Esperadas dez acurácias finitas entre zero e um por classificador.")
    summary = scores[ORDER].agg(["mean", "std", "median", "min", "max"]).T
    if np.unique(values).size == 1:
        h, p = 0.0, 1.0
    else:
        h, p = map(float, kruskal(*(scores[k] for k in ORDER)))
    pairs = []
    for a, b in combinations(ORDER, 2):
        u, pair_p = map(
            float, mannwhitneyu(scores[a], scores[b], alternative="two-sided", method="asymptotic")
        )
        corrected = min(1.0, pair_p * 6)
        pairs.append(
            {
                "a": a,
                "b": b,
                "statistic_u": u,
                "pvalue": pair_p,
                "p_bonferroni": corrected,
                "significant_raw": pair_p < 0.05,
                "significant_bonferroni": corrected < 0.05,
                "mean_difference_a_minus_b": float(summary.loc[a, "mean"] - summary.loc[b, "mean"]),
            }
        )
    return summary, {
        "alpha": 0.05,
        "kruskal_wallis": {"statistic_h": h, "pvalue": p},
        "mann_whitney": pairs,
        "caveat": "Partições compartilhadas e repetições sobrepostas: os escores não "
        "são independentes; inferência exploratória conforme o enunciado.",
    }
