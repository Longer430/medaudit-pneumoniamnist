# MedAudit Kaggle demo video script

Target length: 4 minutes 30 seconds. Maximum allowed: 5 minutes.

## 0:00-0:25 - Hook and problem

**Screen:** Kaggle cover image, then title slide.

**Narration:**

“Medical AI teams often have a fragile gap between exporting model predictions and deciding whether an experiment deserves further validation. Metrics move through notebooks and spreadsheets, while language models can produce confident but unsupported interpretations. MedAudit is a research-only audit agent that makes deterministic evidence the source of truth.”

## 0:25-0:55 - Why an agent

**Screen:** Architecture image.

**Narration:**

“This problem needs more than a calculator. A researcher expresses an audit goal, the agent selects the correct procedure, validates the input, calls a deterministic statistical tool, and organizes the evidence with explicit safety boundaries. The agent orchestrates the workflow, but it never invents the metrics and never acts as a clinician.”

## 0:55-1:35 - Architecture and course concepts

**Screen:** Slowly highlight each architecture box.

**Narration:**

“MedAudit demonstrates four course concepts. First, an Agent Skill uses progressive disclosure to load the audit workflow only when the request matches. Second, security features enforce schema checks, research-only language, upload limits, and metadata-only logs. Third, the application is deployable through a gated Cloud Build pipeline to Cloud Run. Fourth, I used an Antigravity-ready project structure with AGENTS.md, a local Skill, deterministic scripts, and evaluation commands that an agent can execute reproducibly.”

## 1:35-2:20 - Live demo

**Screen:** Open the production service. Show `/api/health`, then the web page. Upload or use the PneumoniaMNIST prediction CSV and run the audit.

**Narration:**

“The production service is public and reports version 1.0.0 as healthy and ready. The input contract requires case ID, true label, and model score. On the included 624-case PneumoniaMNIST test prediction file, the deterministic tool reports an ROC AUC of 0.9260 with a 95 percent confidence interval from 0.9059 to 0.9461. At threshold 0.5, sensitivity is 0.9795 and specificity is 0.6752. These are reproducible research results, not clinical validation.”

## 2:20-2:55 - Failure behavior

**Screen:** Run `python evals/run_evals.py`, or show terminal output. Highlight invalid-schema and single-class cases.

**Narration:**

“Reliable agents must fail safely. The evaluation suite covers valid data, tied prediction scores, missing columns, duplicate identifiers, out-of-range scores, and single-class labels. Every case also verifies the required audit tool trajectory. Invalid inputs are rejected instead of being patched or guessed.”

## 2:55-3:30 - Security and observability

**Screen:** Show `tests/test_evals.py`, then a Cloud Logging entry with only audit ID, duration, rows, and threshold.

**Narration:**

“A privacy test injects a sentinel patient identifier and filename, then proves that neither reaches the logs. Cloud Run stores structured metadata without CSV content. The project also scans user-facing Skill and report files for prohibited claims such as clinical approval or an unsupported disease threshold.”

## 3:30-4:05 - From Antigravity to production

**Screen:** In Antigravity, open the repository and show `AGENTS.md`, the Skill folder, and the test commands. Then show the successful GitHub Actions or Cloud Build run.

**Narration:**

“The repository is designed for agentic development in Antigravity. Project context lives in dot-Codex, behavioral rules live in AGENTS.md, and the reusable procedure lives in the Skill. The production pipeline runs evaluations and unit tests, builds a non-root container, pushes the image, and deploys a versioned Cloud Run revision.”

## 4:05-4:30 - Value, limitations, and close

**Screen:** Return to cover image with live demo and GitHub URLs.

**Narration:**

“MedAudit turns an informal model-review step into a traceable, reusable workflow for researchers and ML engineers. It does not diagnose patients, choose a clinical threshold, or establish deployment readiness. The next step is connecting the polished AI Studio interface directly to the production API and adding calibration, subgroup, and external-validation modules. The live service and complete source code are publicly available.”

## Recording checklist

- Keep the final video at or below 5:00.
- Record at 1080p with readable terminal text.
- Do not show API keys, billing pages, email, browser bookmarks, or private identifiers.
- Use only the included de-identified public dataset.
- Publish to YouTube as Public or Unlisted, then attach it to the Kaggle Media Gallery.
