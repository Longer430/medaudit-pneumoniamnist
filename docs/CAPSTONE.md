# MedAudit: Medical Model Prediction Audit Agent

## Problem

Medical-imaging researchers need a reproducible checkpoint between model prediction export and interpretation. Spreadsheet calculations and LLM-generated metrics are difficult to audit and can introduce unsupported clinical claims.

## Solution

MedAudit validates a prediction CSV, computes deterministic statistical evidence, and provides a portable Agent Skill that constrains subsequent interpretation to research-use language.

## Course architecture

- Day 1: AI Studio frontend and Cloud Run prototype.
- Day 2: deterministic statistics tool and upload API.
- Day 3: portable `medaudit-model-audit` Skill with progressive disclosure.
- Day 4: outcome, trajectory, safety-content, and privacy-log evaluations.
- Day 5: versioned specification, health/readiness endpoints, container, CI/CD templates, Cloud Run release, and production verification.

## Evidence

The included PneumoniaMNIST baseline contains 624 test predictions. The current audit reports ROC AUC 0.9260 with a 95% CI of 0.9059-0.9461. These results describe this research dataset only.

## Production service

https://medaudit-statistics-tool-770349538120.us-east1.run.app

## Limitations

This is not a diagnostic system. It does not evaluate calibration, distribution shift, image quality, clinical endpoints, or representative external validation. It does not currently run an LLM; the Skill is consumed by a compatible agent host.
