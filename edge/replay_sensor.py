"""Edge device simulator: replays the recorded sensor sheet as live telemetry.

Sinks:
  stdout  print one JSON message per line (default, no cloud needed)
  pubsub  publish to a Google Cloud Pub/Sub topic (needs google-cloud-pubsub and credentials)

Examples:
  python edge/replay_sensor.py --limit 5
  python edge/replay_sensor.py --sink pubsub --project my-gcp-project --topic telemetry --speed 3600
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Iterator, List

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline.core import Reading, rows_to_readings  # noqa: E402

DEFAULT_DATA = ROOT / "data" / "edinburgh_sensor_data.xlsx"


def load_readings(path: Path) -> List[Reading]:
    if not path.exists():
        raise SystemExit(f"Data file not found: {path}")
    df = pd.read_excel(path) if path.suffix.lower() in (".xlsx", ".xls") else pd.read_csv(path)
    return list(rows_to_readings(df.to_dict("records")))


def replay(readings: List[Reading], speed: float) -> Iterator[Reading]:
    """Yield readings with real time gaps divided by `speed` (0 = as fast as possible)."""
    prev = None
    for r in readings:
        if speed > 0 and prev is not None:
            time.sleep(max(0.0, (r.ts - prev) / speed))
        prev = r.ts
        yield r


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--sink", choices=("stdout", "pubsub"), default="stdout")
    ap.add_argument("--project", help="GCP project id (pubsub sink)")
    ap.add_argument("--topic", default="telemetry", help="Pub/Sub topic name (pubsub sink)")
    ap.add_argument("--speed", type=float, default=0.0, help="time compression, e.g. 3600 = one hour per second")
    ap.add_argument("--limit", type=int, default=0, help="stop after N messages (0 = all)")
    args = ap.parse_args()

    readings = load_readings(args.data)
    if args.limit:
        readings = readings[: args.limit]

    publisher = topic_path = None
    if args.sink == "pubsub":
        if not args.project:
            raise SystemExit("--project is required for the pubsub sink")
        try:
            from google.cloud import pubsub_v1  # type: ignore
        except ImportError:
            raise SystemExit("Install the cloud extras first: pip install -r requirements-cloud.txt")
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(args.project, args.topic)

    sent = 0
    for r in replay(readings, args.speed):
        payload = json.dumps(r.to_message())
        if publisher is not None:
            publisher.publish(topic_path, payload.encode("utf-8"), device_id=r.device_id).result()
        else:
            print(payload)
        sent += 1
    print(f"sent {sent} messages", file=sys.stderr)


if __name__ == "__main__":
    main()
