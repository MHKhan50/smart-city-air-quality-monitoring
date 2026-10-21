"""Run the whole pipeline on a laptop, with no cloud account.

edge replay -> the same message handler as the Cloud Function -> SQLite (in place of Firestore)
-> summary table and charts in local_demo/out/.
"""
from __future__ import annotations

import csv
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "cloud_functions"))
from edge.replay_sensor import DEFAULT_DATA, load_readings  # noqa: E402
from main import NO2_ELEVATED, NO2_HOURLY_LIMIT, handle  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
WHO_NO2_24H = 25.0  # WHO 2021 24-hour guideline, µg/m³


class SqliteCollection:
    def __init__(self, con: sqlite3.Connection, name: str) -> None:
        self.con, self.name = con, name
        con.execute(f"CREATE TABLE IF NOT EXISTS {name} (id TEXT PRIMARY KEY, doc TEXT)")

    def document(self, doc_id: str) -> "SqliteCollection":
        self._id = doc_id
        return self

    def set(self, doc: Dict[str, Any]) -> None:
        self.con.execute(f"INSERT OR REPLACE INTO {self.name} VALUES (?, ?)", (self._id, json.dumps(doc)))

    def add(self, doc: Dict[str, Any]) -> None:
        n = self.con.execute(f"SELECT COUNT(*) FROM {self.name}").fetchone()[0]
        self.con.execute(f"INSERT INTO {self.name} VALUES (?, ?)", (f"auto-{n + 1}", json.dumps(doc)))


class SqliteDB:
    """Minimal stand-in for the Firestore client methods the handler uses."""

    def __init__(self, path: Path) -> None:
        self.con = sqlite3.connect(path)

    def collection(self, name: str) -> SqliteCollection:
        return SqliteCollection(self.con, name)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    db_path = OUT / "telemetry.sqlite"
    if db_path.exists():
        db_path.unlink()
    db = SqliteDB(db_path)

    readings = load_readings(DEFAULT_DATA)
    counts: Dict[str, int] = {"stored": 0, "alert": 0, "rejected": 0}
    for r in readings:
        counts[handle(r.to_message(), db)] += 1
    # one deliberately broken message, to show the rejection path
    counts[handle({"device_id": "edns-01", "site": "EDNS", "ts": 0, "no_ugm3": "n/a", "no2_ugm3": 12.0}, db)] += 1
    db.con.commit()

    rows = [json.loads(d) for (d,) in db.con.execute("SELECT doc FROM telemetry")]
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["ts"], unit="s", utc=True)
    df = df.sort_values("time").set_index("time")
    daily = df["no2_ugm3"].resample("D").mean()

    summary = {
        "messages_in": len(readings) + 1,
        "stored": counts["stored"] + counts["alert"],
        "alerts": counts["alert"],
        "rejected": counts["rejected"],
        "first_reading_utc": str(df.index.min()),
        "last_reading_utc": str(df.index.max()),
        "no2_mean_ugm3": round(float(df["no2_ugm3"].mean()), 1),
        "no2_max_hourly_ugm3": round(float(df["no2_ugm3"].max()), 1),
        "hours_above_uk_hourly_objective_200": int((df["no2_ugm3"] > NO2_HOURLY_LIMIT).sum()),
        "hours_above_elevated_100": int((df["no2_ugm3"] > NO2_ELEVATED).sum()),
        "days_above_who_24h_25": int((daily > WHO_NO2_24H).sum()),
        "days_with_data": int(daily.notna().sum()),
    }
    with (OUT / "summary.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["metric", "value"])
        w.writerows(summary.items())

    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(df.index, df["no2_ugm3"], color="#9ec5f4", lw=0.8, label="Hourly NO2")
    ax.plot(daily.index, daily.values, color="#2a78d6", lw=2, label="Daily mean NO2")
    ax.axhline(WHO_NO2_24H, color="#0ca30c", ls="--", lw=1.5, label="WHO 24-hour guideline (25)")
    ax.axhline(NO2_ELEVATED, color="#eb6834", ls=":", lw=1.5, label="Alert level in this demo (100)")
    ax.set_ylabel("NO2 (µg/m³)")
    ax.set_title(f"Edinburgh Nicolson Street NO2, replayed through the pipeline", loc="left")
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "no2_timeseries.png", dpi=150, bbox_inches="tight")

    for k, v in summary.items():
        print(f"{k:38s} {v}")
    print(f"\nSaved {OUT.relative_to(ROOT)}/summary.csv, no2_timeseries.png and telemetry.sqlite")


if __name__ == "__main__":
    main()
