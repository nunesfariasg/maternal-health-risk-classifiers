"""Confere resultados reais, seleção e rastreabilidade, sem treinar novamente a grade."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.data import FEATURES, TARGET, load_data
from src.models import GRIDS, ORDER
from src.stats import compare

RESULTS = Path("results")


@pytest.fixture
def artifacts():
    return {
        name: pd.read_csv(RESULTS / f"{name}.csv")
        for name in ["accuracies", "summary", "best_params", "candidates", "splits", "predictions"]
    }


def test_all_40_scores_match_saved_test_predictions(artifacts):
    scores = artifacts["accuracies"].set_index("seed")
    predictions = artifacts["predictions"]
    assert scores.index.tolist() == list(range(10))
    assert len(predictions) == 40 * 113
    assert not predictions.duplicated(["seed", "classifier", "row_id"]).any()
    data, _ = load_data()
    for (seed, classifier), group in predictions.groupby(["seed", "classifier"]):
        assert len(group) == 113
        assert group.actual.tolist() == data.loc[group.row_id, TARGET].tolist()
        measured = (group.actual == group.predicted).mean()
        assert scores.loc[seed, classifier] == pytest.approx(measured)
        split = artifacts["splits"]
        test_ids = set(split.loc[(split.seed == seed) & (split.split == "test"), "row_id"])
        assert set(group.row_id) == test_ids


def test_saved_choices_use_only_maximum_validation_accuracy(artifacts):
    trials, choices = artifacts["candidates"], artifacts["best_params"]
    assert len(trials) == 520
    assert len(choices) == 40
    assert not choices.duplicated(["seed", "classifier"]).any()
    for _, selected in choices.iterrows():
        group = trials[(trials.seed == selected.seed) & (trials.classifier == selected.classifier)]
        best = group.loc[group.validation_accuracy.idxmax()]
        assert selected.validation_accuracy == best.validation_accuracy
        assert json.loads(selected.params) == json.loads(best.params)
    for _, candidate in trials[trials.classifier == "MLP"].iterrows():
        assert json.loads(candidate.n_iter) == json.loads(candidate.params)["model__max_iter"]


def test_all_partitions_are_complete_disjoint_and_stratified(artifacts):
    data, _ = load_data()
    assert not data.duplicated().any()
    split = artifacts["splits"]
    for seed in range(10):
        group = split[split.seed == seed]
        assert len(group) == 452 and group.row_id.nunique() == 452
        assert set(group.row_id) == set(data.index)
        for name, n in [("train", 226), ("validation", 113), ("test", 113)]:
            frame = data.loc[group[group.split == name].row_id]
            assert len(frame) == n
            deviation = (
                frame[TARGET].value_counts(normalize=True)
                - data[TARGET].value_counts(normalize=True)
            ).abs()
            assert deviation.max() <= 1 / n
        # Linhas completas nunca se repetem; vetores com rótulos conflitantes são auditados.
        assert set(data.columns) == set(FEATURES + [TARGET])


def test_summary_statistics_and_source_hashes_match(artifacts):
    summary, stats = compare(artifacts["accuracies"])
    saved = artifacts["summary"].set_index("classifier")
    np.testing.assert_allclose(summary.loc[ORDER], saved.loc[ORDER], rtol=1e-12)
    assert stats == json.loads((RESULTS / "statistics.json").read_text(encoding="utf-8"))
    meta = json.loads((RESULTS / "metadata.json").read_text(encoding="utf-8"))
    assert meta["grids"] == json.loads(json.dumps(GRIDS))
    for path, digest in meta["source_sha256"].items():
        assert hashlib.sha256(Path(path.replace("\\", "/")).read_bytes()).hexdigest() == digest
