from pathlib import Path
import sys
import unittest

import pandas as pd
from io import BytesIO


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from app import app  # noqa: E402
from medaudit.pipeline import EXPECTED_MD5, audit_predictions, verify_dataset  # noqa: E402


class PipelineTests(unittest.TestCase):
    dataset = ROOT / "data" / "raw" / "pneumoniamnist.npz"
    predictions = ROOT / "data" / "processed" / "pneumoniamnist_test_predictions.csv"

    def test_dataset_checksum(self):
        self.assertEqual(EXPECTED_MD5, "28209eda62fecd6e6a2d98b1501bb15f")
        verify_dataset(self.dataset)

    def test_prediction_schema_and_metrics(self):
        frame = pd.read_csv(self.predictions)
        self.assertEqual(list(frame.columns), ["case_id", "y_true", "y_score"])
        metrics = audit_predictions(self.predictions)
        self.assertEqual(metrics["rows"], 624)
        self.assertGreater(metrics["auc"], 0.90)
        self.assertLess(metrics["auc"], 0.95)
        self.assertLess(metrics["auc_ci_low"], metrics["auc"])
        self.assertGreater(metrics["auc_ci_high"], metrics["auc"])

    def test_auc_uses_average_ranks_for_tied_scores(self):
        data = BytesIO(b"case_id,y_true,y_score\na,0,0.5\nb,1,0.5\nc,0,0.1\nd,1,0.9\n")
        metrics = audit_predictions(data)
        self.assertAlmostEqual(metrics["auc"], 0.875)

    def test_web_routes(self):
        client = app.test_client()
        home = client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertEqual(home.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(home.headers["X-Frame-Options"], "DENY")
        self.assertEqual(client.get("/healthz").get_json()["version"], "1.0.0")
        self.assertEqual(client.get("/api/health").status_code, 200)
        self.assertEqual(client.get("/readyz").status_code, 200)
        self.assertEqual(client.get("/api/version").get_json()["service"], "medaudit-statistics-tool")
        response = client.get("/api/audit")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["rows"], 624)
        upload = client.post(
            "/api/audit",
            data={"file": (BytesIO(b"case_id,y_true,y_score\na,0,0.1\nb,1,0.9\n"), "audit.csv")},
            content_type="multipart/form-data",
        )
        self.assertEqual(upload.status_code, 200)
        self.assertEqual(upload.get_json()["auc"], 1.0)
        image = client.get("/sample/0.png")
        self.assertEqual(image.status_code, 200)
        self.assertEqual(image.mimetype, "image/png")


if __name__ == "__main__":
    unittest.main()
