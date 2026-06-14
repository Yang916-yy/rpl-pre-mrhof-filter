#!/usr/bin/env python3
import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


VARIANTS = {
    "exact": None,
    "noise05": "paper-results-prior-noise05/metric_runs.csv",
    "noise10": "paper-results-prior-noise10/metric_runs.csv",
    "noise20": "paper-results-prior-noise20/metric_runs.csv",
    "noise30": "paper-results-prior-noise30/metric_runs.csv",
    "hop": "paper-results-prior-hop/metric_runs.csv",
}

SCENES = {
    "Temporary Root Displacement": "Disturbance",
    "Disturbance": "Disturbance",
    "Root-Loss": "Root-Loss",
    "Local Failure": "Local Failure",
}

METRICS = {
    "pdr": ("PDR", True),
    "avg_delay_ms": ("Avg. delay (ms)", False),
    "p95_delay_ms": ("P95 delay (ms)", False),
    "recov_ms": ("Recovery (ms)", False),
    "gate_cmp": ("Comparisons", False),
    "gate_sw": ("Parent switches", False),
    "control": ("Control messages", False),
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def load_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def metric_value(row, metric):
    if metric == "control":
        return sum(float(row[f"metric_{name}"]) for name in ("dio", "dao", "dis"))
    value = float(row[f"metric_{metric}"])
    if metric == "recov_ms" and value < 0:
        return None
    return value


def mean(values):
    return sum(values) / len(values)


def sample_std(values):
    if len(values) < 2:
        return 0.0
    center = mean(values)
    return math.sqrt(sum((value - center) ** 2 for value in values) / (len(values) - 1))


def ci95(values):
    return 1.96 * sample_std(values) / math.sqrt(len(values)) if values else float("nan")


def select_exact_rows(test_dir):
    rows = []
    sources = [
        test_dir / "paper-results-main" / "metric_runs.csv",
        test_dir / "paper-results-local-failure" / "metric_runs.csv",
    ]
    for source in sources:
        for row in load_csv(source):
            if row["group"] != "Full" or row["scale"] != "40":
                continue
            if row["scene"] not in ("Disturbance", "Root-Loss", "Local Failure"):
                continue
            rows.append(row)
    return rows


def select_variant_rows(test_dir, relative_path):
    return [
        row
        for row in load_csv(test_dir / relative_path)
        if row["group"] == "Full" and row["scale"] == "40"
    ]


def index_rows(rows):
    indexed = {}
    for row in rows:
        scene = SCENES[row["scene"]]
        indexed[(scene, int(row["seed"]))] = row
    return indexed


def summarize(exact, candidate, variant):
    output = []
    for scene in ("Disturbance", "Root-Loss", "Local Failure"):
        keys = sorted(set(exact) & set(candidate))
        keys = [key for key in keys if key[0] == scene]
        for metric, (label, higher_better) in METRICS.items():
            pairs = []
            for key in keys:
                exact_value = metric_value(exact[key], metric)
                candidate_value = metric_value(candidate[key], metric)
                if exact_value is not None and candidate_value is not None:
                    pairs.append((exact_value, candidate_value))
            exact_values = [pair[0] for pair in pairs]
            candidate_values = [pair[1] for pair in pairs]
            differences = [pair[1] - pair[0] for pair in pairs]
            exact_mean = mean(exact_values)
            candidate_mean = mean(candidate_values)
            if metric == "pdr":
                delta = 100.0 * (candidate_mean - exact_mean)
                delta_unit = "pp"
            else:
                delta = 100.0 * (candidate_mean - exact_mean) / exact_mean
                delta_unit = "%"
            output.append({
                "variant": variant,
                "scene": scene,
                "metric": metric,
                "metric_label": label,
                "n": len(pairs),
                "exact_mean": exact_mean,
                "exact_sd": sample_std(exact_values),
                "variant_mean": candidate_mean,
                "variant_sd": sample_std(candidate_values),
                "paired_difference_mean": mean(differences),
                "paired_difference_ci95": ci95(differences),
                "delta_vs_exact": delta,
                "delta_unit": delta_unit,
                "better_direction": "higher" if higher_better else "lower",
            })
    return output


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def format_value(metric, value):
    if metric == "pdr":
        return f"{value:.4f}"
    if metric in ("avg_delay_ms", "p95_delay_ms", "recov_ms"):
        return f"{value:.1f}"
    return f"{value:.0f}"


def write_markdown(path, rows):
    lookup = {(row["variant"], row["scene"], row["metric"]): row for row in rows}
    lines = [
        "# Structural-Prior Robustness Summary",
        "",
        "All variants use the same 20 Cooja seeds as the exact-prior experiment. "
        "Values are mean +/- sample SD. Deltas are relative to exact prior; "
        "PDR uses percentage points and all other metrics use percent.",
        "",
    ]
    for scene in ("Disturbance", "Root-Loss", "Local Failure"):
        lines.extend([
            f"## {scene}",
            "",
            "| Variant | PDR | Delta | Delay (ms) | Delta | Recovery (ms) | Delta | Comparisons | Delta | Switches | Delta | Control | Delta |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        exact_rows = {metric: lookup[("noise05", scene, metric)] for metric in METRICS}
        exact_cells = []
        for metric in ("pdr", "avg_delay_ms", "recov_ms", "gate_cmp", "gate_sw", "control"):
            row = exact_rows[metric]
            exact_cells.extend([
                f"{format_value(metric, row['exact_mean'])} +/- {format_value(metric, row['exact_sd'])}",
                "0",
            ])
        lines.append("| Exact | " + " | ".join(exact_cells) + " |")
        for variant in ("noise05", "noise10", "noise20", "noise30", "hop"):
            cells = []
            for metric in ("pdr", "avg_delay_ms", "recov_ms", "gate_cmp", "gate_sw", "control"):
                row = lookup[(variant, scene, metric)]
                delta = row["delta_vs_exact"]
                delta_text = f"{delta:+.3f} pp" if metric == "pdr" else f"{delta:+.1f}%"
                cells.extend([
                    f"{format_value(metric, row['variant_mean'])} +/- {format_value(metric, row['variant_sd'])}",
                    delta_text,
                ])
            lines.append(f"| {variant} | " + " | ".join(cells) + " |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    exact = index_rows(select_exact_rows(args.test_dir))
    all_rows = []
    for variant, relative_path in VARIANTS.items():
        if variant == "exact":
            continue
        candidate = index_rows(select_variant_rows(args.test_dir, relative_path))
        all_rows.extend(summarize(exact, candidate, variant))
    write_csv(args.output_dir / "prior_robustness_summary.csv", all_rows)
    write_markdown(args.output_dir / "prior_robustness_summary.md", all_rows)


if __name__ == "__main__":
    main()
