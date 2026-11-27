import numpy as np
import pandas as pd
import pytest

from src.data import FEATURES, prepare_data, split_data


def fixture_data():
    # IDs e atributos únicos permitem detectar perda ou repetição entre partições.
    frame = pd.DataFrame({name: np.arange(120) + i for i, name in enumerate(FEATURES)})
    frame["RiskLevel"] = ["low risk"] * 60 + ["mid risk"] * 40 + ["high risk"] * 20
    return frame


def test_split_is_stratified_disjoint_complete_and_reproducible():
    data, _ = prepare_data(fixture_data())
    parts = split_data(data, 7)
    assert [len(parts[k]) for k in ("train", "validation", "test")] == [60, 30, 30]
    ids = [set(part.index) for part in parts.values()]
    assert not ids[0] & ids[1] and not ids[0] & ids[2] and not ids[1] & ids[2]
    assert set.union(*ids) == set(data.index)
    for name, part in parts.items():
        assert part.index.tolist() == split_data(data, 7)[name].index.tolist()
        assert (
            part.RiskLevel.value_counts(normalize=True)
            - data.RiskLevel.value_counts(normalize=True)
        ).abs().max() < 0.001
    assert parts["train"].index.tolist() != split_data(data, 8)["train"].index.tolist()


def test_exact_duplicates_removed_but_conflicting_labels_reported():
    frame = fixture_data()
    conflict = frame.iloc[[0]].assign(RiskLevel="high risk")
    data, audit = prepare_data(pd.concat([frame, frame.iloc[[0]], conflict], ignore_index=True))
    assert len(data) == 121
    assert audit["exact_duplicates_removed"] == 1
    assert audit["conflicting_feature_groups"] == 1


@pytest.mark.parametrize("change", ["missing", "nonfinite", "label", "column"])
def test_invalid_data_rejected(change):
    frame = fixture_data()
    if change == "missing":
        frame.loc[0, "Age"] = np.nan
    elif change == "nonfinite":
        frame["Age"] = frame.Age.astype(float)
        frame.loc[0, "Age"] = np.inf
    elif change == "label":
        frame.loc[0, "RiskLevel"] = "unknown"
    else:
        frame = frame.drop(columns="BS")
    with pytest.raises(ValueError):
        prepare_data(frame)
