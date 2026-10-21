"""Cloud Function (Pub/Sub trigger): validate telemetry, store it in Firestore, record alerts.

Deploy from this folder:
  gcloud functions deploy store_telemetry --runtime python312 --trigger-topic telemetry \
      --entry-point store_telemetry --region europe-west2

Firestore collections:
  telemetry   one document per valid reading (id = <device_id>-<ts>, so replays do not duplicate)
  alerts      one document per reading above an alert level
  rejected    messages that failed validation, with the reasons
"""
from __future__ import annotations

import base64
import json
import math
from typing import Any, Dict, List, Optional

NO2_HOURLY_LIMIT = 200.0
NO2_ELEVATED = 100.0
MAX_PLAUSIBLE = 2000.0

_client = None


def _db():
    """Create the Firestore client on first use (keeps cold starts and tests light)."""
    global _client
    if _client is None:
        from google.cloud import firestore  # type: ignore

        _client = firestore.Client()
    return _client


def validate(msg: Dict[str, Any]) -> List[str]:
    problems: List[str] = []
    for key in ("device_id", "site"):
        if not isinstance(msg.get(key), str) or not msg.get(key):
            problems.append(f"missing or empty '{key}'")
    ts = msg.get("ts")
    if not isinstance(ts, int) or isinstance(ts, bool) or ts <= 0:
        problems.append("'ts' must be a positive integer (unix seconds)")
    for key in ("no_ugm3", "no2_ugm3"):
        val = msg.get(key)
        if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val):
            problems.append(f"'{key}' must be a number")
        elif not 0 <= val <= MAX_PLAUSIBLE:
            problems.append(f"'{key}' out of range 0-{MAX_PLAUSIBLE:g}")
    return problems


def alert_level(no2: float) -> Optional[str]:
    if no2 > NO2_HOURLY_LIMIT:
        return "limit"
    if no2 > NO2_ELEVATED:
        return "elevated"
    return None


def handle(msg: Dict[str, Any], db: Any) -> str:
    """Process one decoded message. Returns 'stored', 'alert' or 'rejected'."""
    problems = validate(msg)
    if problems:
        db.collection("rejected").add({"message": msg, "problems": problems})
        return "rejected"
    doc_id = f"{msg['device_id']}-{msg['ts']}"
    db.collection("telemetry").document(doc_id).set(msg)
    level = alert_level(float(msg["no2_ugm3"]))
    if level:
        db.collection("alerts").document(doc_id).set({**msg, "level": level})
        return "alert"
    return "stored"


def store_telemetry(event: Dict[str, Any], context: Any) -> str:
    """Entry point for a Pub/Sub-triggered (1st gen) Cloud Function."""
    raw = base64.b64decode(event.get("data", b"")).decode("utf-8")
    try:
        msg = json.loads(raw)
    except ValueError:
        msg = {"raw": raw}
    if not isinstance(msg, dict):
        msg = {"raw": raw}
    result = handle(msg, _db())
    print(json.dumps({"event_id": getattr(context, "event_id", None), "result": result}))
    return result
