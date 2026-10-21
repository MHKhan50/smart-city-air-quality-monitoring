"""Shared telemetry logic: parse sensor rows, validate messages, apply alert rules.

Used by the edge replay script, the local demo and (copied) by the Cloud Function,
so the same rules run on the device, locally and in the cloud.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Iterator, List, Optional

SITE_ID = "EDNS"
SITE_NAME = "Edinburgh Nicolson Street"

# Thresholds in µg/m³. UK hourly NO2 objective is 200 (not to be exceeded more than 18 times a year).
# The "elevated" level is a configurable early-warning level for this demo, not a legal limit.
NO2_HOURLY_LIMIT = 200.0
NO2_ELEVATED = 100.0
MAX_PLAUSIBLE = 2000.0


@dataclass(frozen=True)
class Reading:
    device_id: str
    site: str
    ts: int  # unix seconds, UTC
    no_ugm3: float
    no2_ugm3: float

    def to_message(self) -> Dict[str, Any]:
        msg = asdict(self)
        msg["iso_time"] = datetime.fromtimestamp(self.ts, tz=timezone.utc).isoformat()
        return msg


def _num(value: Any) -> Optional[float]:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def rows_to_readings(rows: Iterable[Dict[str, Any]], device_id: str = "edns-01") -> Iterator[Reading]:
    """Turn spreadsheet rows into readings. Rows with 'No data' or bad values are skipped.

    The unix 'timestamp' column is used as the time of record, because the sheet writes
    the last hour of each day as 00:00 on the same date.
    """
    for row in rows:
        ts, no, no2 = _num(row.get("timestamp")), _num(row.get("nitric_oxide")), _num(row.get("nitrogen_dioxide"))
        if ts is None or no is None or no2 is None:
            continue
        yield Reading(device_id=device_id, site=SITE_ID, ts=int(round(ts)), no_ugm3=no, no2_ugm3=no2)


def validate(msg: Dict[str, Any]) -> List[str]:
    """Return a list of problems with an incoming telemetry message (empty list = valid)."""
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
    """'limit' above the UK hourly objective, 'elevated' above the early-warning level, else None."""
    if no2 > NO2_HOURLY_LIMIT:
        return "limit"
    if no2 > NO2_ELEVATED:
        return "elevated"
    return None
