# MedAudit v1.0 specification

## Objective

Audit binary medical-model prediction CSV files reproducibly and expose the results through a research-only web service.

## Input contract

CSV uploads must contain unique `case_id`, binary `y_true`, and finite `y_score` values in `[0, 1]`. The maximum request size is 10 MiB. Uploaded content is processed in memory and is not persisted.

## Output contract

`POST /api/audit` returns row count, positive rate, ROC AUC, Hanley-McNeil 95% CI, sensitivity, specificity, and threshold. Validation failures return HTTP 400. Oversized requests return HTTP 413.

## Operational contract

- `GET /api/health`: public process liveness and version (`/healthz` is also available locally).
- `GET /readyz`: required packaged data availability.
- `GET /api/version`: service name and semantic version.
- Every response includes baseline browser security headers.
- Audit logs contain an opaque audit ID, status, duration, row count, and threshold only. They must not contain filenames, CSV rows, case IDs, or images.

## Safety boundary

The service supports research workflow evaluation only. It must not diagnose patients, recommend treatment or disease-specific thresholds, claim clinical validation, or approve deployment.

## Release acceptance criteria

1. Dataset checksum and all unit tests pass.
2. All Day 4 evaluation cases pass with the expected tool trajectory.
3. Container runs as a non-root user and listens on `$PORT`.
4. Cloud Run health, readiness, and version endpoints return HTTP 200.
5. A production CSV audit matches local AUC and confidence interval.
6. Invalid single-class data returns HTTP 400.
