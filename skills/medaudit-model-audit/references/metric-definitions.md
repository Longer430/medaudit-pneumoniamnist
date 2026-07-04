# Metric definitions and boundaries

- **ROC AUC:** Mann-Whitney rank statistic with average ranks for tied scores. It measures discrimination across thresholds, not calibration or clinical utility.
- **95% CI:** Hanley-McNeil normal approximation, clipped to `[0, 1]`. It reflects sampling uncertainty under its assumptions and is not a regulatory confidence statement.
- **Sensitivity:** `TP / positives` at the selected threshold.
- **Specificity:** `TN / negatives` at the selected threshold.
- **Positive rate:** Positive labels divided by all evaluated rows; it describes this dataset and may not represent the intended population.

Required input columns:

| Column | Constraint |
|---|---|
| `case_id` | Non-empty and unique |
| `y_true` | Binary integer, with both classes present |
| `y_score` | Finite number from 0 through 1 |

Report results as research evidence. External validation, calibration assessment, subgroup analysis, and endpoint-specific threshold selection remain separate work.
