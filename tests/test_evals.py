from io import BytesIO
import json
import logging
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app, audit_logger  # noqa: E402
from evals.run_evals import run  # noqa: E402


class AgentQualityTests(unittest.TestCase):
    def test_day4_evaluation_suite(self):
        report = run()
        self.assertTrue(report["passed"], report)
        self.assertEqual(len(report["cases"]), 6)

    def test_audit_log_contains_metadata_but_not_uploaded_content(self):
        client = app.test_client()
        sensitive_case_id = "PRIVATE-PATIENT-123"
        csv_data = f"case_id,y_true,y_score\n{sensitive_case_id},0,0.1\ncontrol,1,0.9\n".encode()
        with self.assertLogs(audit_logger, level=logging.INFO) as captured:
            response = client.post(
                "/api/audit",
                data={"file": (BytesIO(csv_data), "patient_predictions.csv")},
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 200)
        log_text = "\n".join(captured.output)
        self.assertNotIn(sensitive_case_id, log_text)
        self.assertNotIn("patient_predictions.csv", log_text)
        payload = json.loads(log_text[log_text.index("{"):])
        self.assertEqual(payload["event"], "audit_completed")
        self.assertEqual(payload["rows"], 2)


if __name__ == "__main__":
    unittest.main()
