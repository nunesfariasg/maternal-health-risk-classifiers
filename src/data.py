"""Leitura, auditoria e partições estratificadas, preservando IDs das linhas originais."""

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

FEATURES = ["Age", "SystolicBP", "DiastolicBP", "BS", "BodyTemp", "HeartRate"]
TARGET = "RiskLevel"
CLASSES = ["low risk", "mid risk", "high risk"]
DATA_PATH = Path("data/Maternal Health Risk Data Set.csv")
EXPECTED_SHA256 = "a1f7025719f84715096e0d1f95ae2e56b57809b9b15449e1836c96a7d976ae9b"


def prepare_data(frame):
    """Remove apenas duplicatas completas; não inventa correções para extremos ou rótulos."""
    if set(frame.columns) != set(FEATURES + [TARGET]):
        raise ValueError("Colunas diferentes do esquema esperado da base UCI.")
    frame = frame[FEATURES + [TARGET]].copy()
    if frame.isna().any().any():
        raise ValueError("A base contém valores ausentes; revisar antes do experimento.")
    if not all(pd.api.types.is_numeric_dtype(frame[c]) for c in FEATURES):
        raise ValueError("Os seis atributos devem ser numéricos.")
    if not np.isfinite(frame[FEATURES].to_numpy()).all():
        raise ValueError("Atributos não finitos encontrados.")
    if set(frame[TARGET].unique()) != set(CLASSES):
        raise ValueError("Classes diferentes das três classes esperadas.")
    data = frame.drop_duplicates().copy()
    q1, q3 = frame[FEATURES].quantile(0.25), frame[FEATURES].quantile(0.75)
    iqr = q3 - q1
    extremes = (frame[FEATURES] < q1 - 1.5 * iqr) | (frame[FEATURES] > q3 + 1.5 * iqr)
    conflicts = data.groupby(FEATURES)[TARGET].nunique()
    audit = {
        "raw_rows": len(frame),
        "rows_used": len(data),
        "exact_duplicates_removed": int(frame.duplicated().sum()),
        "conflicting_feature_groups": int((conflicts > 1).sum()),
        "missing_values": int(frame.isna().sum().sum()),
        "raw_class_counts": frame[TARGET].value_counts().to_dict(),
        "used_class_counts": data[TARGET].value_counts().to_dict(),
        "raw_describe": frame[FEATURES].describe().to_dict(),
        "used_describe": data[FEATURES].describe().to_dict(),
        "raw_iqr_outlier_counts": extremes.sum().to_dict(),
        "policy": "Remover duplicatas exatas; manter extremos e rótulos conflitantes sem correção.",
    }
    return data, audit


def load_data(path=DATA_PATH):
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("SHA-256 diferente do CSV oficial utilizado; revisar a origem dos dados.")
    data, audit = prepare_data(pd.read_csv(path))
    audit["sha256"] = digest
    return data, audit


def split_data(data, seed):
    """Embaralha antes da divisão e novamente o treino antes de cada ajuste."""
    shuffled = data.sample(frac=1, random_state=seed)
    train, rest = train_test_split(
        shuffled, train_size=0.5, stratify=shuffled[TARGET], shuffle=True, random_state=seed
    )
    validation, test = train_test_split(
        rest, test_size=0.5, stratify=rest[TARGET], shuffle=True, random_state=seed + 1000
    )
    return {
        "train": train.sample(frac=1, random_state=seed + 2000),
        "validation": validation,
        "test": test,
    }
