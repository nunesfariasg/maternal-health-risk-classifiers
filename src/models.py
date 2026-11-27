"""Grades definidas antes do teste; seleção estritamente pela validação."""

import warnings

from sklearn.base import clone
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import accuracy_score
from sklearn.model_selection import ParameterGrid
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

GRIDS = {
    "KNN": {"model__n_neighbors": [3, 5, 7, 11], "model__weights": ["uniform", "distance"]},
    "AD": {"model__criterion": ["gini", "entropy"], "model__ccp_alpha": [0.0, 0.005, 0.02]},
    "SVM": {"model__C": [0.1, 1.0, 10.0], "model__kernel": ["poly", "rbf"]},
    "MLP": {
        "model__max_iter": [200, 500],
        "model__learning_rate_init": [0.001, 0.01],
        "model__hidden_layer_sizes": [(16,), (16, 8)],
        "model__activation": ["identity", "logistic", "tanh", "relu"],
    },
}
ORDER = ["KNN", "SVM", "AD", "MLP"]


def make_model(name, seed):
    estimators = {
        "KNN": KNeighborsClassifier(),
        "AD": DecisionTreeClassifier(random_state=seed),
        "SVM": SVC(gamma="scale", degree=3),
        # Executa o orçamento inteiro de épocas, sem validação interna ou parada antecipada.
        "MLP": MLPClassifier(
            random_state=seed,
            solver="adam",
            shuffle=True,
            early_stopping=False,
            tol=0.0,
            n_iter_no_change=501,
        ),
    }
    scale = "passthrough" if name == "AD" else StandardScaler()
    return Pipeline([("scale", scale), ("model", estimators[name])])


def select_model(estimator, grid, x_train, y_train, x_validation, y_validation):
    """Não recebe teste; retém o modelo ajustado no treino, sem refit em treino+validação."""
    best, best_params, best_score = None, None, -1.0
    candidates = []
    for params in ParameterGrid(grid):
        model = clone(estimator).set_params(**params)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", ConvergenceWarning)
            model.fit(x_train, y_train)
        score = float(accuracy_score(y_validation, model.predict(x_validation)))
        iterations = getattr(model.named_steps["model"], "n_iter_", None)
        if hasattr(iterations, "tolist"):
            iterations = iterations.tolist()
        candidates.append(
            {
                "params": params,
                "validation_accuracy": score,
                "n_iter": iterations,
                "warnings": [str(w.message) for w in caught],
            }
        )
        if score > best_score:
            best, best_params, best_score = model, params, score
    if best is None:
        raise ValueError("A grade precisa conter ao menos uma combinação.")
    return best, best_params, best_score, candidates
