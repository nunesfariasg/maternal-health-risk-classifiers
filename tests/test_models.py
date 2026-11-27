import json

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from src.models import select_model


def test_selects_validation_winner_and_scaler_only_sees_training():
    x = pd.DataFrame({"a": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]})
    y = np.array([0, 0, 1, 1, 1, 1, 0, 0])
    xv = pd.DataFrame({"a": [100.0, 101.0]})
    yv = np.array([0, 0])
    model = Pipeline(
        [("scale", StandardScaler()), ("model", DecisionTreeClassifier(random_state=0))]
    )
    best, params, score, candidates = select_model(
        model, {"model__max_depth": [1, None]}, x, y, xv, yv
    )
    assert params == {"model__max_depth": None}
    assert score == 1.0
    assert len(candidates) == 2
    assert candidates[0]["validation_accuracy"] == 0.0
    np.testing.assert_allclose(best.named_steps["scale"].mean_, [3.5])
    assert best.named_steps["scale"].n_samples_seen_ == 8
    assert best.named_steps["model"].tree_.n_node_samples[0] == 8


def test_tie_uses_first_candidate():
    x = pd.DataFrame({"a": range(12)})
    y = [0] * 6 + [1] * 6
    model = Pipeline([("model", DecisionTreeClassifier(random_state=0))])
    _, params, _, _ = select_model(model, {"model__max_depth": [1, 2]}, x, y, x, y)
    assert params["model__max_depth"] == 1


def test_svm_candidate_metadata_can_be_written_as_json():
    x = pd.DataFrame({"a": range(12)})
    y = [0] * 6 + [1] * 6
    _, _, _, candidates = select_model(
        Pipeline([("model", SVC())]), {"model__C": [1.0]}, x, y, x, y
    )
    assert json.loads(json.dumps(candidates))[0]["n_iter"]
