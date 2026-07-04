from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import BinaryIO

import numpy as np
import pandas as pd


EXPECTED_MD5 = "28209eda62fecd6e6a2d98b1501bb15f"


def verify_dataset(path: Path) -> None:
    digest = hashlib.md5(path.read_bytes()).hexdigest()
    if digest != EXPECTED_MD5:
        raise ValueError(f"Dataset MD5 mismatch: {digest}")


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -30, 30)))


def auc_score(labels: np.ndarray, scores: np.ndarray) -> float:
    ranks = pd.Series(scores).rank(method="average").to_numpy()
    positives = labels == 1
    n_pos = int(positives.sum())
    n_neg = len(labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        raise ValueError("y_true must contain both 0 and 1")
    return float((ranks[positives].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def auc_confidence_interval(auc: float, n_pos: int, n_neg: int) -> tuple[float, float]:
    """Return the Hanley-McNeil normal-approximation 95% CI for ROC AUC."""
    q1 = auc / (2.0 - auc)
    q2 = 2.0 * auc * auc / (1.0 + auc)
    variance = (
        auc * (1.0 - auc)
        + (n_pos - 1) * (q1 - auc * auc)
        + (n_neg - 1) * (q2 - auc * auc)
    ) / (n_pos * n_neg)
    margin = 1.96 * math.sqrt(max(variance, 0.0))
    return max(0.0, auc - margin), min(1.0, auc + margin)


def train_and_predict(dataset_path: Path) -> tuple[np.ndarray, np.ndarray]:
    verify_dataset(dataset_path)
    data = np.load(dataset_path)
    x_train = data["train_images"].reshape(len(data["train_images"]), -1).astype(float) / 255.0
    y_train = data["train_labels"].reshape(-1).astype(float)
    x_test = data["test_images"].reshape(len(data["test_images"]), -1).astype(float) / 255.0
    y_test = data["test_labels"].reshape(-1).astype(int)

    mean = x_train.mean(axis=0)
    scale = x_train.std(axis=0)
    scale[scale < 1e-6] = 1.0
    x_train = (x_train - mean) / scale
    x_test = (x_test - mean) / scale

    weights = np.zeros(x_train.shape[1])
    bias = 0.0
    learning_rate = 0.08
    l2 = 1e-3

    for _ in range(350):
        predictions = sigmoid(x_train @ weights + bias)
        error = predictions - y_train
        weights -= learning_rate * ((x_train.T @ error) / len(x_train) + l2 * weights)
        bias -= learning_rate * error.mean()

    return y_test, sigmoid(x_test @ weights + bias)


def export_predictions(dataset_path: Path, output_path: Path) -> dict[str, float | int]:
    labels, scores = train_and_predict(dataset_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "case_id": [f"PNEUMONIA-MNIST-TEST-{index:04d}" for index in range(len(labels))],
            "y_true": labels,
            "y_score": np.round(scores, 6),
        }
    ).to_csv(output_path, index=False)
    return audit_predictions(output_path)


def audit_prediction_frame(frame: pd.DataFrame, threshold: float = 0.5) -> dict[str, float | int]:
    required = {"case_id", "y_true", "y_score"}
    if not required.issubset(frame.columns):
        raise ValueError(f"Missing columns: {sorted(required - set(frame.columns))}")
    if frame["case_id"].duplicated().any():
        raise ValueError("case_id values must be unique")
    if not set(frame["y_true"].unique()).issubset({0, 1}):
        raise ValueError("y_true must contain only 0 or 1")
    if not frame["y_score"].between(0, 1).all():
        raise ValueError("y_score must be between 0 and 1")

    labels = frame["y_true"].to_numpy(dtype=int)
    scores = frame["y_score"].to_numpy(dtype=float)
    predicted = scores >= threshold
    positive = labels == 1
    negative = ~positive
    n_pos = int(positive.sum())
    n_neg = int(negative.sum())
    auc = auc_score(labels, scores)
    ci_low, ci_high = auc_confidence_interval(auc, n_pos, n_neg)
    sensitivity = float((predicted & positive).sum() / positive.sum())
    specificity = float((~predicted & negative).sum() / negative.sum())
    return {
        "rows": len(frame),
        "positive_rate": float(positive.mean()),
        "auc": auc,
        "auc_ci_low": ci_low,
        "auc_ci_high": ci_high,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "threshold": threshold,
    }


def audit_predictions(csv_source: Path | BinaryIO, threshold: float = 0.5) -> dict[str, float | int]:
    return audit_prediction_frame(pd.read_csv(csv_source), threshold)
