# AGENTS.md

## Project goal

Run a reproducible, research-only PneumoniaMNIST baseline and inspect its test
predictions through a small Flask application.

## Working rules

- Read `.Codex/project-context.md` before changing code.
- Keep the application local and deterministic; no external API is required.
- Never describe model output as clinical diagnosis or deployment approval.
- Preserve the official train/test split and do not train on test labels.
- Run `python -m unittest discover -s tests -v` after code changes.
- Run `python evals/run_evals.py` after changing audit behavior, safety text, or the MedAudit skill.
- Run `python scripts/build_predictions.py` when changing the model pipeline.

## Run commands

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build_predictions.py
python app.py
```

Open http://127.0.0.1:8080.
