# Project context

- This is a portable extraction of the tested PneumoniaMNIST workflow from the
  parent `AI agent kaggle` workspace.
- The dataset is MedMNIST v2 PneumoniaMNIST, licensed CC BY 4.0.
- The source archive MD5 must be `28209eda62fecd6e6a2d98b1501bb15f`.
- Images and labels are real dataset records. Prediction scores are produced by
  the local NumPy logistic-regression baseline.
- Intended use: software testing, education, and research workflow evaluation.
- Prohibited framing: diagnosis, patient-care recommendations, clinical
  validation, or deployment approval.
- Day 2 implementation: deterministic CSV audit tool exposed through
  `POST /api/audit`. Numerical metrics are calculated in Python; any future
  agent layer may explain them but must not generate or overwrite them.
- Cloud Run service: `https://medaudit-statistics-tool-770349538120.us-east1.run.app`
- Production verification on 2026-07-03: built-in and uploaded PneumoniaMNIST
  CSV both returned AUC `0.9260` and 95% CI `0.9059-0.9461`.
- Day 3 implementation: portable skill at `skills/medaudit-model-audit/` with
  progressive-disclosure instructions, a dependency-free deterministic audit
  script, metric reference, report template, and six trigger-boundary evals.
- Day 4 implementation: `evals/run_evals.py` checks API outcomes and the required
  `audit_predictions` tool trajectory across six cases, scans user-facing skill
  and report content for prohibited medical claims, and verifies metadata-only
  audit logs do not retain filenames or case identifiers.
- Day 5 implementation: v1.0 specification and Capstone summary, liveness and
  readiness endpoints, semantic version endpoint, request-size and browser
  security controls, non-root Docker image, Cloud Build deployment pipeline,
  and GitHub Actions quality-gate template.
- Production release `1.0.0` completed through `cloudbuild.yaml` on 2026-07-03.
  Cloud Build `77f220d5-7f68-49ef-bff2-98ca0764e0f3` succeeded and Cloud Run
  revision `medaudit-statistics-tool-00005-w5b` serves 100% of traffic.
- Kaggle Capstone submission draft: `docs/KAGGLE_WRITEUP.md` (1,424 words).
  All technical claims were checked against the project; only the YouTube demo
  URL remains as an explicit submission placeholder.
- Public source repository target: `https://github.com/Longer430/medaudit-pneumoniamnist`.
- Kaggle card image: `docs/assets/kaggle-card-thumbnail.png` (1672 x 941).
- Kaggle submission requirements verified from the live Tracks and Awards page
  on 2026-07-04. Submission package: `docs/SUBMISSION_PACKAGE.md`; video script:
  `docs/VIDEO_SCRIPT.md`; media architecture image: `docs/assets/architecture.png`.
- Selected track: Agents for Good. Demonstrated course concepts: Agent Skills,
  Security Features, Deployability, and Antigravity (to be shown in the video).
- Generated Kaggle video: `docs/media/medaudit-kaggle-capstone.mp4`, English
  system narration, 3:12, 1600 x 900 H.264/AAC. Editable source deck:
  `docs/media/medaudit-capstone-video-deck.pptx`.
