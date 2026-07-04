# MedAudit: A Reproducible Medical-Model Audit Agent

**Subtitle:** Turning prediction CSV files into deterministic evidence, safe interpretation, and a production-grade audit trail.

> **One-sentence summary:** MedAudit is a research-only agent workflow that validates medical-model prediction files, computes reproducible performance statistics with deterministic tools, and constrains interpretation through a portable, evaluated Agent Skill.

## Why I built this

Medical-imaging teams often have a fragile gap between exporting model predictions and deciding whether an experiment deserves further validation. Metrics may be copied through notebooks and spreadsheets, confidence intervals may be calculated inconsistently, and an LLM can make a plausible but unsupported clinical claim even when the underlying number is correct.

I wanted to build something narrower and more defensible than another medical chatbot. MedAudit treats the LLM as an orchestrator and interpreter, not as a calculator or clinician. Numerical evidence comes from deterministic code. The Agent Skill defines the workflow and safety boundary. Evaluation checks both the final result and the tool trajectory.

The intended users are medical-imaging researchers and ML engineers reviewing binary-classification experiments before any deployment decision. MedAudit is explicitly not a diagnostic device and does not recommend treatment, operating thresholds, or clinical deployment.

## What MedAudit does

MedAudit accepts a CSV with three required columns:

| Column | Meaning | Validation |
|---|---|---|
| `case_id` | De-identified record identifier | Non-empty and unique |
| `y_true` | Reference label | Binary, with both classes present |
| `y_score` | Model probability or score | Finite value from 0 to 1 |

The deterministic audit tool returns:

- row count and positive-class prevalence;
- ROC AUC using average ranks for tied scores;
- a Hanley-McNeil 95% confidence interval;
- sensitivity and specificity at a user-supplied threshold;
- structured validation errors for malformed or unsuitable inputs.

Uploaded data is processed in memory. Audit logs contain only an opaque audit ID, status, duration, row count, and threshold; filenames, case identifiers, CSV rows, and images are not logged.

## Architecture

```text
Researcher / ML engineer
          |
          v
Compatible agent host
          |
          | loads only when the request matches
          v
medaudit-model-audit Skill
  |-- workflow and safety instructions
  |-- metric definitions
  |-- report template
  |-- trigger-boundary evaluations
          |
          | calls; never invents metrics
          v
Deterministic audit tool / Cloud Run API
  |-- schema validation
  |-- ROC AUC and 95% CI
  |-- sensitivity and specificity
  |-- metadata-only structured logging
          |
          v
Evidence + qualitative, research-only interpretation
```

The project has two public demonstrations:

1. **Interactive AI Studio frontend prototype:** [MedAudit UI](https://remix-medaudit-770349538120.us-east1.run.app/)
2. **Production deterministic service:** [MedAudit statistics tool](https://medaudit-statistics-tool-770349538120.us-east1.run.app/)

The frontend demonstrates the researcher workflow. The second service is the independently tested numerical source of truth. They are presented separately rather than claiming an integration that does not yet exist.

## How the five course days shaped the project

### Day 1 - From prompt to deployed prototype

I used Google AI Studio to generate an interactive audit workstation and deployed it to Cloud Run. The first generated version exposed an important lesson: visual polish does not guarantee scientific correctness. It contained inconsistent AUC values and unsupported clinical language. I manually repaired the evidence display and restricted the prototype to research-use wording.

### Day 2 - Tools and interoperability

I moved numerical work out of model-generated text and into a deterministic Python tool. A `POST /api/audit` endpoint allows any compatible client or agent to submit a valid prediction CSV. This reduces integration debt and keeps one stable numerical contract across interfaces.

### Day 3 - Agent Skills and progressive disclosure

I packaged the workflow as `medaudit-model-audit`, a portable Skill containing:

- a concise `SKILL.md` with positive and negative trigger boundaries;
- a dependency-free audit script;
- metric definitions loaded only when needed;
- a research-report template;
- three positive and three negative routing examples.

The Skill instructs the agent to treat tool output as authoritative and forbids it from converting research statistics into diagnosis, clinical approval, or a disease-specific threshold recommendation.

### Day 4 - Quality, security, and observability

The evaluation suite checks both outcomes and trajectories. Six API cases cover valid inputs, tied scores, missing columns, duplicate identifiers, out-of-range scores, and single-class labels. Every case verifies that the request actually traversed the `audit_predictions` tool.

Additional tests scan user-facing Skill and report content for prohibited medical claims. A privacy test injects a sentinel patient identifier and filename, then verifies that neither appears in the log. Cloud Run emits queryable structured JSON logs without retaining uploaded content.

### Day 5 - Specification-driven productionization

The final release adds a written input, output, operational, and safety contract; semantic versioning; health and readiness endpoints; a 10 MiB request limit; browser security headers; and a non-root Docker image.

The Cloud Build pipeline performs four gated stages:

```text
evaluation + unit tests -> container build -> image push -> Cloud Run deploy
```

Release `1.0.0` was built by Cloud Build and deployed as Cloud Run revision `medaudit-statistics-tool-00005-w5b`, serving 100% of traffic. A GitHub Actions quality-gate template is also included for future repository hosting.

## Dataset and reproducibility

The demonstration uses the official MedMNIST v2 PneumoniaMNIST archive, a pediatric chest-X-ray classification dataset resized to 28 x 28 grayscale pixels. The archive is checked against the expected MD5 before use. A local NumPy logistic-regression baseline trains only on the official training split and exports predictions for the 624-record test split.

The current deterministic audit reports:

| Metric | Result |
|---|---:|
| Test records | 624 |
| Positive rate | 0.6250 |
| ROC AUC | 0.9260 |
| 95% CI | 0.9059-0.9461 |
| Sensitivity at 0.50 | 0.9795 |
| Specificity at 0.50 | 0.6752 |

These numbers are evidence that the software pipeline is reproducible on this dataset. They are not evidence of clinical validity. PneumoniaMNIST source: [Zenodo record 6496656](https://zenodo.org/records/6496656), CC BY 4.0.

## Evaluation results

| Quality gate | Result |
|---|---:|
| Day 4 API and trajectory cases | 6/6 passed |
| Full automated test suite | 6/6 passed |
| Prohibited medical phrases detected | 0 |
| Sentinel identifiers found in logs | 0 |
| Cloud Build production pipeline | Passed |
| Production health/readiness/version checks | Passed |

One subtle but important test uses tied prediction scores. A naive rank implementation can calculate the wrong AUC; MedAudit assigns average ranks and reproduces the expected value. This is the kind of quiet failure that motivates deterministic tools and golden evaluation cases.

## Safety and responsible-use decisions

MedAudit applies several deliberate constraints:

- numerical values are generated by code, not an LLM;
- uploaded data is not persisted by the application;
- logs exclude file content and direct record identifiers;
- the Skill separates evidence from qualitative interpretation;
- reports state the need for representative external validation;
- the system does not recommend a clinical threshold;
- no result is described as diagnostic, approved, or deployment-ready.

The service is publicly accessible for demonstration, so only de-identified or synthetic research data should be uploaded. Authentication, organization-specific retention controls, and formal threat modeling would be required before handling any sensitive institutional data.

## What I learned

The hardest part was not calculating AUC or deploying Flask. It was deciding where probabilistic behavior should stop. In a medical workflow, the agent can help select a procedure, call a tool, organize evidence, and explain limitations. It should not be allowed to manufacture the evidence or silently turn a research result into a clinical recommendation.

The course progression made that boundary concrete: prototype quickly, standardize the tool interface, encode the procedure as a Skill, evaluate the trajectory, and only then create a production release. The result is intentionally small, but every claimed capability has a corresponding artifact or test.

## Limitations and next steps

The current release evaluates binary prediction tables. It does not yet assess calibration, confidence-interval alternatives such as DeLong or bootstrap methods, subgroup fairness, distribution shift, image quality, or clinical endpoints. The public AI Studio UI and deterministic backend are separate deployments.

Next steps are to connect the UI to the production API, add calibration and subgroup modules, introduce authenticated project workspaces, and evaluate the Skill inside a supported agent host across multiple model families. Any move toward a clinical setting would require representative external validation, domain-expert review, security governance, and the appropriate regulatory process.

## Links

- Live frontend: https://remix-medaudit-770349538120.us-east1.run.app/
- Production statistics service: https://medaudit-statistics-tool-770349538120.us-east1.run.app/
- Source repository: https://github.com/Longer430/medaudit-pneumoniamnist
- Demo video (5 minutes or less): **[ADD PUBLIC YOUTUBE URL]**

---

**Track suggestion:** Agents for Good, with Freestyle as the alternative if the submission form uses broader categories.
