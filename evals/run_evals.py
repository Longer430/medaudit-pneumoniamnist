#!/usr/bin/env python3
"""Run deterministic Day 4 API, trajectory, and safety-content evaluations."""

from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
import sys
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app as app_module  # noqa: E402


FORBIDDEN_PHRASES = (
    "approved for clinical use",
    "clinical trial approved",
    "recommended disease threshold",
    "94% agent confidence",
    "ready for clinical deployment",
)


def run() -> dict:
    cases = json.loads((ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
    results = []
    client = app_module.app.test_client()
    original_tool = app_module.audit_predictions

    for case in cases:
        trajectory = []

        def traced_tool(*args, **kwargs):
            trajectory.append("audit_predictions")
            return original_tool(*args, **kwargs)

        with patch.object(app_module, "audit_predictions", traced_tool):
            response = client.post(
                "/api/audit",
                data={"file": (BytesIO(case["csv"].encode()), "predictions.csv")},
                content_type="multipart/form-data",
            )
        payload = response.get_json()
        passed = response.status_code == case["expected_status"] and trajectory == case["expected_trajectory"]
        for key, value in case.get("expected", {}).items():
            passed = passed and abs(payload[key] - value) < 1e-12
        if "expected_error" in case:
            passed = passed and case["expected_error"] in payload.get("error", "")
        results.append({"case_id": case["case_id"], "passed": passed, "trajectory": trajectory})

    safety_files = [
        ROOT / "skills" / "medaudit-model-audit" / "SKILL.md",
        ROOT / "skills" / "medaudit-model-audit" / "assets" / "audit-report-template.md",
        ROOT / "templates" / "index.html",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in safety_files)
    unsafe = [phrase for phrase in FORBIDDEN_PHRASES if phrase in combined]
    return {
        "passed": all(item["passed"] for item in results) and not unsafe,
        "cases": results,
        "safety_content": {"passed": not unsafe, "forbidden_phrases_found": unsafe},
    }


if __name__ == "__main__":
    report = run()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
