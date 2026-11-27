import numpy as np
import pandas as pd
import pytest

from src.stats import compare


def test_six_pairs_and_bonferroni_and_sample_standard_deviation():
    scores = pd.DataFrame(
        {
            "KNN": np.linspace(0.50, 0.59, 10),
            "AD": np.linspace(0.80, 0.89, 10),
            "SVM": np.linspace(0.60, 0.69, 10),
            "MLP": np.linspace(0.70, 0.79, 10),
        }
    )
    summary, stats = compare(scores)
    assert len(stats["mann_whitney"]) == 6
    assert stats["kruskal_wallis"]["pvalue"] < 0.05
    assert summary.loc["KNN", "std"] == pytest.approx(0.03027650354)
    for pair in stats["mann_whitney"]:
        assert pair["p_bonferroni"] == pytest.approx(min(1, pair["pvalue"] * 6))
        assert pair["significant_bonferroni"]


def test_identical_scores_have_no_difference():
    _, stats = compare(pd.DataFrame({k: [0.5] * 10 for k in ["KNN", "SVM", "AD", "MLP"]}))
    assert stats["kruskal_wallis"]["pvalue"] == 1
    assert not any(p["significant_raw"] for p in stats["mann_whitney"])


@pytest.mark.parametrize("value", [np.nan, np.inf, 1.1])
def test_invalid_score_rejected(value):
    frame = pd.DataFrame({k: [0.5] * 10 for k in ["KNN", "SVM", "AD", "MLP"]})
    frame.loc[0, "KNN"] = value
    with pytest.raises(ValueError):
        compare(frame)
