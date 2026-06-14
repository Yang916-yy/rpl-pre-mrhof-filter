#!/usr/bin/env python3
"""Strip machine-local fields from a metric_runs.csv file."""

import argparse
import csv
from pathlib import Path


FIELDS = [
    "platform",
    "group",
    "scene",
    "scale",
    "seed",
    "test_ok",
    "metric_pdr",
    "metric_avg_delay_ms",
    "metric_recov_ms",
    "metric_gate_cmp",
    "metric_gate_sw",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()

    with args.input_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    missing = [field for field in FIELDS if field not in (rows[0] if rows else {})]
    if missing:
        raise SystemExit(f"missing fields in {args.input_csv}: {', '.join(missing)}")

    public_rows = [
        {field: row.get(field, "") for field in FIELDS}
        for row in rows
        if row.get("test_ok") == "1"
    ]
    public_rows.sort(
        key=lambda row: (
            row["group"],
            row["scene"],
            int(row["scale"]),
            int(row["seed"]),
        )
    )

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(public_rows)

    print(f"{args.output_csv}: {len(public_rows)} valid rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
