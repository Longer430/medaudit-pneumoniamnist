from io import BytesIO
import json
import logging
import os
from pathlib import Path
import sys
import time
import uuid

import numpy as np
from flask import Flask, jsonify, render_template, request, send_file
from PIL import Image


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from medaudit.pipeline import audit_predictions  # noqa: E402


DATASET = ROOT / "data" / "raw" / "pneumoniamnist.npz"
PREDICTIONS = ROOT / "data" / "processed" / "pneumoniamnist_test_predictions.csv"
VERSION = os.environ.get("APP_VERSION", (ROOT / "VERSION").read_text().strip())

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
logging.basicConfig(level=logging.INFO)
audit_logger = logging.getLogger("medaudit.audit")
audit_logger.handlers.clear()
audit_handler = logging.StreamHandler()
audit_handler.setFormatter(logging.Formatter("%(message)s"))
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)
audit_logger.propagate = False


def log_audit(event: str, **fields) -> None:
    """Emit metadata-only JSON logs; never include filenames, rows, or case IDs."""
    audit_logger.info(json.dumps({"event": event, **fields}, sort_keys=True))


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'"
    return response


@app.get("/")
def index():
    metrics = audit_predictions(PREDICTIONS)
    return render_template("index.html", metrics=metrics)


@app.get("/api/audit")
def audit_api():
    return jsonify(audit_predictions(PREDICTIONS))


@app.get("/healthz")
@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": VERSION}


@app.get("/readyz")
def readiness_check():
    ready = DATASET.is_file() and PREDICTIONS.is_file()
    return ({"status": "ready", "version": VERSION}, 200) if ready else ({"status": "not_ready"}, 503)


@app.get("/api/version")
def version_api():
    return {"service": "medaudit-statistics-tool", "version": VERSION}


@app.post("/api/audit")
def audit_uploaded_csv():
    audit_id = uuid.uuid4().hex
    started = time.monotonic()
    uploaded = request.files.get("file")
    if uploaded is None or not uploaded.filename:
        log_audit("audit_rejected", audit_id=audit_id, reason="missing_file")
        return {"error": "Upload a CSV file using the 'file' field"}, 400
    try:
        threshold = float(request.form.get("threshold", "0.5"))
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")
        metrics = audit_predictions(uploaded.stream, threshold)
        log_audit(
            "audit_completed",
            audit_id=audit_id,
            rows=metrics["rows"],
            threshold=threshold,
            duration_ms=round((time.monotonic() - started) * 1000, 2),
        )
        return jsonify(metrics)
    except (ValueError, TypeError) as error:
        log_audit("audit_rejected", audit_id=audit_id, reason="validation_error")
        return {"error": str(error)}, 400


@app.get("/sample/<int:index>.png")
def sample_image(index: int):
    data = np.load(DATASET)
    images = data["test_images"]
    if index < 0 or index >= len(images):
        return {"error": "sample index out of range"}, 404
    image = Image.fromarray(images[index]).resize((448, 448), Image.Resampling.NEAREST)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8080")), debug=False)
