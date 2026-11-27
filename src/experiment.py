"""Execução reproduzível: python -m src.experiment --output results."""

import argparse
import hashlib
import importlib.metadata
import json
import platform
import time
from datetime import UTC, datetime
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from threadpoolctl import threadpool_limits

from src.data import CLASSES, FEATURES, TARGET, load_data, split_data
from src.models import GRIDS, ORDER, make_model, select_model
from src.stats import compare


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def run(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    data, audit = load_data()
    save_json(output / "data_audit.json", audit)
    data[FEATURES].describe().to_csv(output / "feature_summary.csv")
    raw_scores, selected, candidates, assignments, predictions, split_audits = (
        [],
        [],
        [],
        [],
        [],
        [],
    )
    seed_reports = {}
    with threadpool_limits(limits=1):
        for seed in range(10):
            parts = split_data(data, seed)
            for split, frame in parts.items():
                for row_id in frame.index:
                    assignments.append({"seed": seed, "row_id": int(row_id), "split": split})
            overlaps = {}
            for a, b in combinations(parts, 2):
                aa = set(map(tuple, parts[a][FEATURES].to_numpy()))
                bb = set(map(tuple, parts[b][FEATURES].to_numpy()))
                overlaps[f"{a}_{b}"] = len(aa & bb)
                assert not set(parts[a].index) & set(parts[b].index)
            split_audits.append(
                {
                    "seed": seed,
                    "feature_vector_overlap": overlaps,
                    "class_counts": {
                        k: v[TARGET].value_counts().to_dict() for k, v in parts.items()
                    },
                }
            )
            train, validation, test = (parts[k] for k in ["train", "validation", "test"])
            row = {"repetition": seed + 1, "seed": seed}
            for name in ORDER:
                best, params, val_score, trials = select_model(
                    make_model(name, seed),
                    GRIDS[name],
                    train[FEATURES],
                    train[TARGET],
                    validation[FEATURES],
                    validation[TARGET],
                )
                # Única avaliação de teste, depois de encerrar a seleção.
                predicted = best.predict(test[FEATURES])
                row[name] = float(accuracy_score(test[TARGET], predicted))
                selected.append(
                    {
                        "seed": seed,
                        "classifier": name,
                        "params": json.dumps(params),
                        "validation_accuracy": val_score,
                        "test_accuracy": row[name],
                    }
                )
                for trial in trials:
                    candidates.append(
                        {
                            "seed": seed,
                            "classifier": name,
                            "params": json.dumps(trial["params"]),
                            "validation_accuracy": trial["validation_accuracy"],
                            "n_iter": json.dumps(trial["n_iter"]),
                            "warnings": json.dumps(trial["warnings"]),
                        }
                    )
                for row_id, actual, pred in zip(test.index, test[TARGET], predicted):
                    predictions.append(
                        {
                            "seed": seed,
                            "classifier": name,
                            "row_id": int(row_id),
                            "actual": actual,
                            "predicted": pred,
                        }
                    )
                seed_reports[f"{seed}_{name}"] = {
                    "classification_report": classification_report(
                        test[TARGET], predicted, labels=CLASSES, output_dict=True, zero_division=0
                    ),
                    "confusion_matrix": confusion_matrix(
                        test[TARGET], predicted, labels=CLASSES
                    ).tolist(),
                    "class_order": CLASSES,
                }
                print(
                    f"Semente {seed} | {name}: validação={val_score:.4f}, teste={row[name]:.4f}",
                    flush=True,
                )
            raw_scores.append(row)
            pd.DataFrame(raw_scores).to_csv(output / "accuracies.csv", index=False)
    scores = pd.DataFrame(raw_scores)
    summary, stats = compare(scores)
    summary.to_csv(output / "summary.csv", index_label="classifier")
    save_json(output / "statistics.json", stats)
    save_json(output / "split_audit.json", split_audits)
    save_json(output / "classification_reports.json", seed_reports)
    for filename, records in [
        ("best_params", selected),
        ("candidates", candidates),
        ("splits", assignments),
        ("predictions", predictions),
    ]:
        pd.DataFrame(records).to_csv(output / f"{filename}.csv", index=False)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.boxplot([scores[name] * 100 for name in ORDER], tick_labels=ORDER)
    for i, name in enumerate(ORDER, 1):
        ax.scatter([i] * 10, scores[name] * 100, s=18, alpha=0.7)
    ax.set(
        ylabel="Acurácia no teste (%)",
        xlabel="Classificador",
        title="Dez repetições estratificadas - base sem duplicatas exatas",
    )
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output / "accuracies.png", dpi=200)
    plt.close(fig)
    packages = ["numpy", "pandas", "scipy", "scikit-learn", "matplotlib", "threadpoolctl"]
    source_hashes = {
        str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path("src").glob("*.py"))
    }
    save_json(
        output / "metadata.json",
        {
            "created_utc": datetime.now(UTC).isoformat(),
            "elapsed_seconds": time.perf_counter() - started,
            "python": platform.python_version(),
            "platform": platform.platform(),
            "packages": {p: importlib.metadata.version(p) for p in packages},
            "source_sha256": source_hashes,
            "seeds": list(range(10)),
            "grids": GRIDS,
            "threads": 1,
            "refit_train_plus_validation": False,
            "tie_break": "Primeiro candidato da ParameterGrid com máxima acurácia na validação.",
        },
    )
    print(summary.to_string(), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="results")
    run(parser.parse_args().output)
