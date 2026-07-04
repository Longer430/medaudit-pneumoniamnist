#!/usr/bin/env python3
"""Deterministically audit a binary prediction CSV using only the standard library."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


REQUIRED_COLUMNS = {"case_id", "y_true", "y_score"}


def average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        rank = ((start + 1) + end) / 2.0
        for position in range(start, end):
            ranks[order[position]] = rank
        start = end
    return ranks


def load_rows(path: Path) -> tuple[list[int], list[float]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing columns: {sorted(missing)}")
        labels, scores, identifiers = [], [], set()
        for line, row in enumerate(reader, start=2):
            case_id = (row["case_id"] or "").strip()
            if not case_id or case_id in identifiers:
                raise ValueError(f"case_id must be non-empty and unique (line {line})")
            identifiers.add(case_id)
            try:
                label = int(row["y_true"])
                score = float(row["y_score"])
            except (TypeError, ValueError) as error:
                raise ValueError(f"Invalid numeric value on line {line}") from error
            if label not in (0, 1):
                raise ValueError(f"y_true must contain only 0 or 1 (line {line})")
            if not math.isfinite(score) or not 0.0 <= score <= 1.0:
                raise ValueError(f"y_score must be finite and between 0 and 1 (line {line})")
            labels.append(label)
            scores.append(score)
    if not labels:
        raise ValueError("CSV contains no prediction rows")
    if len(set(labels)) != 2:
        raise ValueError("y_true must contain both 0 and 1")
    return labels, scores


def calculate(labels: list[int], scores: list[float], threshold: float) -> dict[str, float | int]:
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")
    ranks = average_ranks(scores)
    n_pos = sum(labels)
    n_neg = len(labels) - n_pos
    auc = (sum(rank for rank, label in zip(ranks, labels) if label) - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    q1 = auc / (2 - auc)
    q2 = 2 * auc * auc / (1 + auc)
    variance = (auc * (1 - auc) + (n_pos - 1) * (q1 - auc * auc) + (n_neg - 1) * (q2 - auc * auc)) / (n_pos * n_neg)
    margin = 1.96 * math.sqrt(max(variance, 0.0))
    predicted = [score >= threshold for score in scores]
    true_positive = sum(pred and label == 1 for pred, label in zip(predicted, labels))
    true_negative = sum(not pred and label == 0 for pred, label in zip(predicted, labels))
    return {
        "rows": len(labels),
        "positive_rate": n_pos / len(labels),
        "auc": auc,
        "auc_ci_low": max(0.0, auc - margin),
        "auc_ci_high": min(1.0, auc + margin),
        "sensitivity": true_positive / n_pos,
        "specificity": true_negative / n_neg,
        "threshold": threshold,
    }


def write_report(metrics: dict[str, float | int], destination: Path) -> None:
    template = (Path(__file__).parents[1] / "assets" / "audit-report-template.md").read_text(encoding="utf-8")
    values = {key: f"{value:.4f}" if isinstance(value, float) else str(value) for key, value in metrics.items()}
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    destination.write_text(template, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    metrics = calculate(*load_rows(args.input), args.threshold)
    if args.report:
        write_report(metrics, args.report)
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
