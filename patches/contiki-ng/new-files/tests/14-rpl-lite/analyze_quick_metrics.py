#!/usr/bin/env python3
import csv
import os
import re
from collections import defaultdict
from pathlib import Path

BASE = Path(os.environ.get("PAPER_TEST_DIR", str(Path(__file__).resolve().parent)))
QUICK = BASE / "quick-results" / "quick_compare_results.csv"
RUN_OUT = BASE / "quick-results" / "quick_metrics_runs.csv"
SUM_OUT = BASE / "quick-results" / "quick_metrics_summary.csv"
CMP_OUT = BASE / "quick-results" / "quick_metrics_compare.csv"

PAT_RUNTIME = re.compile(
    r"Simulation\.java:450\].*Runtime: ([0-9]+) ms\. Simulated time: ([0-9]+) ms\. Speedup: ([0-9.]+)"
)
PAT_MISSED = re.compile(r"Missed messages ([0-9]+) before ([0-9]+)")
PAT_TEST_OK = re.compile(r"TEST OK")
PAT_TEST_FAILED = re.compile(r"TEST FAILED")


def parse_key_value_line(line: str):
    out = {}
    for token in line.strip().split()[1:]:
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        out[key] = value
    return out


def parse_log_metrics(log_path: Path):
    runtime_ms = None
    sim_ms = None
    speedup = None

    try:
        with log_path.open(encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                match = PAT_RUNTIME.search(line)
                if match:
                    runtime_ms = int(match.group(1))
                    sim_ms = int(match.group(2))
                    speedup = float(match.group(3))
    except FileNotFoundError:
        pass

    return runtime_ms, sim_ms, speedup


def parse_testlog_metrics(testlog_path: Path):
    missed = None
    before = None
    root_removed = 0
    root_restored = 0
    test_ok = None
    metric = {}

    try:
        with testlog_path.open(encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                match = PAT_MISSED.search(line)
                if match:
                    missed = int(match.group(1))
                    before = int(match.group(2))
                if line.startswith("METRIC "):
                    metric = parse_key_value_line(line)
                if "moving root 2 hops away" in line:
                    root_removed += 1
                if "moving root back" in line:
                    root_restored += 1
                if PAT_TEST_OK.search(line):
                    test_ok = 1
                if PAT_TEST_FAILED.search(line):
                    test_ok = 0
    except FileNotFoundError:
        pass

    return missed, before, root_removed, root_restored, test_ok, metric


def mean(values):
    return sum(values) / len(values) if values else None


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


rows = list(csv.DictReader(QUICK.open(newline="", encoding="utf-8")))
run_rows = []
groups = defaultdict(list)
metric_fields = set()

for row in rows:
    log_path = Path(row["log_path"])
    testlog_path = Path(row["script_log_path"])

    runtime_ms, sim_ms, speedup = parse_log_metrics(log_path)
    missed, before, root_removed, root_restored, test_ok_from_script, metric = parse_testlog_metrics(testlog_path)

    csv_test_ok = int(row["test_ok"]) if row["test_ok"] != "" else None

    out = {
        "group": row["group"],
        "scene": row["scene"],
        "scale": row["scale"],
        "seed": row["seed"],
        "exit_status": row["exit_status"],
        "test_ok": "" if csv_test_ok is None else str(csv_test_ok),
        "test_ok_script": "" if test_ok_from_script is None else str(test_ok_from_script),
        "wall_sec": row["wall_sec"],
        "sim_runtime_ms": "" if runtime_ms is None else str(runtime_ms),
        "sim_time_ms": "" if sim_ms is None else str(sim_ms),
        "speedup": "" if speedup is None else f"{speedup:.6f}",
        "missed_messages": "" if missed is None else str(missed),
        "before_index": "" if before is None else str(before),
        "loss_ratio": "" if missed is None or before in (None, 0) else f"{missed / before:.6f}",
        "root_removed_events": str(root_removed),
        "root_restored_events": str(root_restored),
    }

    for key, value in sorted(metric.items()):
        metric_key = f"metric_{key}"
        out[metric_key] = value
        metric_fields.add(metric_key)

    run_rows.append(out)
    groups[(row["group"], row["scene"], row["scale"])].append(out)

run_fieldnames = [
    "group", "scene", "scale", "seed", "exit_status", "test_ok", "test_ok_script",
    "wall_sec", "sim_runtime_ms", "sim_time_ms", "speedup", "missed_messages",
    "before_index", "loss_ratio", "root_removed_events", "root_restored_events",
] + sorted(metric_fields)

with RUN_OUT.open("w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=run_fieldnames)
    writer.writeheader()
    writer.writerows(run_rows)

summary_rows = []
summary_metric_fields = []
for key in sorted(groups):
    items = groups[key]

    def as_float(field):
        return [float(item[field]) for item in items if item.get(field, "") != ""]

    def as_int(field):
        return [int(item[field]) for item in items if item.get(field, "") != ""]

    n = len(items)
    ok_count = sum(1 for item in items if item["test_ok"] == "1")
    missed = as_int("missed_messages")
    before = as_int("before_index")
    loss = as_float("loss_ratio")
    wall = as_float("wall_sec")
    speedup = as_float("speedup")
    runtime = as_float("sim_runtime_ms")

    summary = {
        "group": key[0],
        "scene": key[1],
        "scale": key[2],
        "n": str(n),
        "ok_count": str(ok_count),
        "ok_rate": f"{ok_count / n:.6f}",
        "avg_wall_sec": f"{mean(wall):.6f}" if wall else "",
        "avg_sim_runtime_ms": f"{mean(runtime):.6f}" if runtime else "",
        "avg_speedup": f"{mean(speedup):.6f}" if speedup else "",
        "avg_missed_messages": f"{mean(missed):.6f}" if missed else "",
        "avg_before_index": f"{mean(before):.6f}" if before else "",
        "avg_loss_ratio": f"{mean(loss):.6f}" if loss else "",
    }

    for field in sorted(metric_fields):
        values = [float(item[field]) for item in items if item.get(field, "") != ""]
        summary_field = f"avg_{field}"
        summary[summary_field] = f"{mean(values):.6f}" if values else ""
        if summary_field not in summary_metric_fields:
            summary_metric_fields.append(summary_field)

    summary_rows.append(summary)

summary_fieldnames = [
    "group", "scene", "scale", "n", "ok_count", "ok_rate", "avg_wall_sec",
    "avg_sim_runtime_ms", "avg_speedup", "avg_missed_messages", "avg_before_index",
    "avg_loss_ratio",
] + summary_metric_fields

with SUM_OUT.open("w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=summary_fieldnames)
    writer.writeheader()
    writer.writerows(summary_rows)

summary_map = {(row["group"], row["scene"], row["scale"]): row for row in summary_rows}
compare_rows = []
compare_metric_fields = []
for scene in sorted({row["scene"] for row in summary_rows}):
    for scale in sorted({row["scale"] for row in summary_rows}):
        base = summary_map.get(("baseline", scene, scale))
        exp = summary_map.get(("experiment", scene, scale))
        if not base or not exp:
            continue

        def num(src, field):
            return to_float(src.get(field, ""))

        b_ok = num(base, "ok_rate")
        e_ok = num(exp, "ok_rate")
        b_wall = num(base, "avg_wall_sec")
        e_wall = num(exp, "avg_wall_sec")
        b_miss = num(base, "avg_missed_messages")
        e_miss = num(exp, "avg_missed_messages")
        b_loss = num(base, "avg_loss_ratio")
        e_loss = num(exp, "avg_loss_ratio")
        b_speed = num(base, "avg_speedup")
        e_speed = num(exp, "avg_speedup")

        compare = {
            "scene": scene,
            "scale": scale,
            "baseline_ok_rate": base["ok_rate"],
            "experiment_ok_rate": exp["ok_rate"],
            "ok_rate_delta_exp_minus_base": f"{(e_ok - b_ok):.6f}" if b_ok is not None and e_ok is not None else "",
            "baseline_avg_wall_sec": base["avg_wall_sec"],
            "experiment_avg_wall_sec": exp["avg_wall_sec"],
            "wall_delta_sec_exp_minus_base": f"{(e_wall - b_wall):.6f}" if b_wall is not None and e_wall is not None else "",
            "baseline_avg_missed_messages": base["avg_missed_messages"],
            "experiment_avg_missed_messages": exp["avg_missed_messages"],
            "missed_delta_exp_minus_base": f"{(e_miss - b_miss):.6f}" if b_miss is not None and e_miss is not None else "",
            "baseline_avg_loss_ratio": base["avg_loss_ratio"],
            "experiment_avg_loss_ratio": exp["avg_loss_ratio"],
            "loss_ratio_delta_exp_minus_base": f"{(e_loss - b_loss):.6f}" if b_loss is not None and e_loss is not None else "",
            "baseline_avg_speedup": base["avg_speedup"],
            "experiment_avg_speedup": exp["avg_speedup"],
            "speedup_delta_exp_minus_base": f"{(e_speed - b_speed):.6f}" if b_speed is not None and e_speed is not None else "",
        }

        for field in summary_metric_fields:
            b_val = num(base, field)
            e_val = num(exp, field)
            compare[f"baseline_{field}"] = base.get(field, "")
            compare[f"experiment_{field}"] = exp.get(field, "")
            compare[f"delta_{field}_exp_minus_base"] = f"{(e_val - b_val):.6f}" if b_val is not None and e_val is not None else ""
            if field not in compare_metric_fields:
                compare_metric_fields.append(field)

        compare_rows.append(compare)

compare_fieldnames = [
    "scene", "scale", "baseline_ok_rate", "experiment_ok_rate", "ok_rate_delta_exp_minus_base",
    "baseline_avg_wall_sec", "experiment_avg_wall_sec", "wall_delta_sec_exp_minus_base",
    "baseline_avg_missed_messages", "experiment_avg_missed_messages", "missed_delta_exp_minus_base",
    "baseline_avg_loss_ratio", "experiment_avg_loss_ratio", "loss_ratio_delta_exp_minus_base",
    "baseline_avg_speedup", "experiment_avg_speedup", "speedup_delta_exp_minus_base",
]
for field in compare_metric_fields:
    compare_fieldnames.extend([
        f"baseline_{field}",
        f"experiment_{field}",
        f"delta_{field}_exp_minus_base",
    ])

with CMP_OUT.open("w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=compare_fieldnames)
    writer.writeheader()
    writer.writerows(compare_rows)

print("OK")
print(RUN_OUT)
print(SUM_OUT)
print(CMP_OUT)
