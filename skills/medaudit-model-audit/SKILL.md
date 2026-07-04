---
name: medaudit-model-audit
description: Audit binary medical-model prediction CSV files with deterministic statistics and produce evidence-linked, research-use reports. Use when a user asks to inspect, validate, audit, compare, or summarize prediction data containing case_id, y_true, and y_score, including requests for ROC AUC, a 95% confidence interval, sensitivity, specificity, class balance, or threshold performance. Do not use for interpreting raw medical images, diagnosing patients, recommending treatment, or approving clinical deployment.
---

# MedAudit Model Audit

Run numerical checks with the bundled script. Treat its JSON output as the source of truth; never invent or overwrite metrics with model-generated values.

## Workflow

1. Confirm the input is a CSV with `case_id`, `y_true`, and `y_score`.
2. Run:

   ```bash
   python scripts/audit_predictions.py INPUT.csv --threshold 0.5
   ```

3. If the user requests a report, add `--report OUTPUT.md`. Use the generated report as the base and edit only explanatory prose.
4. Separate deterministic evidence from qualitative interpretation.
5. State that the result is for research workflow support, requires representative external validation, and is not diagnostic or clinical deployment approval.

## Interpretation rules

- Report AUC, its 95% CI, sensitivity, specificity, threshold, row count, and class balance exactly as returned.
- Describe threshold tradeoffs; do not prescribe a disease-specific operating threshold.
- Do not call a model safe, clinically validated, approved, or ready for deployment based on these metrics.
- Flag invalid schemas, duplicate identifiers, missing/non-finite values, out-of-range scores, and single-class labels instead of estimating around them.
- Read [references/metric-definitions.md](references/metric-definitions.md) when explaining formulas or limitations.
- Use [assets/audit-report-template.md](assets/audit-report-template.md) only through the bundled script so placeholders remain consistent.

## Verification

After changes to this skill, run:

```bash
python scripts/audit_predictions.py ../../data/processed/pneumoniamnist_test_predictions.csv
python -m unittest discover -s ../../tests -v
```

Check routing intent against `evals/cases.json`: positive cases should trigger this skill; negative cases should not.
