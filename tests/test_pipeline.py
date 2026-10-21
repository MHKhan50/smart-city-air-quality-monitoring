from __future__ import annotations

import base64
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "cloud_functions"))

import main as fn  # noqa: E402
from pipeline import core  # noqa: E402

GOOD = {"device_id": "edns-01", "site": "EDNS", "ts": 1641000000, "no_ugm3": 6.2, "no2_ugm3": 18.0}


class FakeDB:
    def __init__(self) -> None:
        self.docs: Dict[str, List[Any]] = {}

    def collection(self, name: str) -> "FakeDB":
        self._name = name
        return self

    def document(self, doc_id: str) -> "FakeDB":
        self._id = doc_id
        return self

    def set(self, doc: Dict[str, Any]) -> None:
        self.docs.setdefault(self._name, []).append((self._id, doc))

    def add(self, doc: Dict[str, Any]) -> None:
        self.docs.setdefault(self._name, []).append((None, doc))


def test_rows_skip_no_data_and_use_unix_timestamp() -> None:
    rows = [
        {"timestamp": 1641000000.0, "nitric_oxide": 6.2, "nitrogen_dioxide": 18.0},
        {"timestamp": 1641003600.0, "nitric_oxide": "No data", "nitrogen_dioxide": "No data"},
    ]
    out = list(core.rows_to_readings(rows))
    assert len(out) == 1 and out[0].ts == 1641000000 and out[0].to_message()["iso_time"].startswith("2022-01-01")


def test_validation_catches_bad_messages() -> None:
    assert core.validate(GOOD) == []
    bad = dict(GOOD, ts=True, no2_ugm3="12", device_id="")
    text = " | ".join(core.validate(bad))
    assert "ts" in text and "no2_ugm3" in text and "device_id" in text
    assert core.validate(dict(GOOD, no_ugm3=-1.0))


def test_cloud_function_and_core_rules_agree() -> None:
    cases = [GOOD, dict(GOOD, no2_ugm3=150.0), dict(GOOD, ts=0), dict(GOOD, no_ugm3=float("nan"))]
    for c in cases:
        assert fn.validate(c) == core.validate(c)
    for v in (10.0, 100.5, 250.0):
        assert fn.alert_level(v) == core.alert_level(v)


def test_handler_stores_alerts_and_rejects() -> None:
    db = FakeDB()
    assert fn.handle(GOOD, db) == "stored"
    assert fn.handle(dict(GOOD, ts=1641003600, no2_ugm3=210.0), db) == "alert"
    assert fn.handle({"raw": "not json"}, db) == "rejected"
    assert db.docs["telemetry"][0][0] == "edns-01-1641000000"
    assert db.docs["alerts"][0][1]["level"] == "limit"
    assert db.docs["rejected"]


def test_entry_point_decodes_pubsub_event(monkeypatch: Any) -> None:
    db = FakeDB()
    monkeypatch.setattr(fn, "_db", lambda: db)
    event = {"data": base64.b64encode(json.dumps(GOOD).encode())}
    assert fn.store_telemetry(event, None) == "stored"
    assert fn.store_telemetry({"data": base64.b64encode(b"{bad")}, None) == "rejected"
