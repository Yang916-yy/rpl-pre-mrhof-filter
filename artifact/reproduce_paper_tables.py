#!/usr/bin/env python3
"""Recompute the paper's principal tables from released per-seed metrics."""

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


METRICS = ("pdr", "gate_cmp", "gate_sw")
SCENES = (
    "Stable",
    "Temporary Root Displacement",
    "Root-Loss",
    "Local Failure",
)
SCENE_ALIASES = {
    "Disturbance": "Temporary Root Displacement",
    "Local-Failure": "Local Failure",
}


def load(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def value(row, metric):
    return float(row[f"metric_{metric}"])


def mean(values):
    if not isinstance(values, (list, tuple)):
        values = list(values)
    return sum(values) / len(values)


def index(rows):
    output = {}
    for row in rows:
        scene = SCENE_ALIASES.get(row["scene"], row["scene"])
        key = (row["group"], scene, int(row["scale"]), int(row["seed"]))
        output[key] = row
    return output


def paired_delta(rows, reference, candidate, scene, scale, metric):
    indexed = index(rows)
    keys = [
        (scene, scale, seed)
        for seed in range(1, 21)
        if (reference, scene, scale, seed) in indexed
        and (candidate, scene, scale, seed) in indexed
    ]
    if len(keys) != 20:
        raise ValueError(
            f"expected 20 pairs for {reference}/{candidate}, {scene}, {scale}; "
            f"found {len(keys)}"
        )
    baseline = [
        value(indexed[(reference, one_scene, one_scale, seed)], metric)
        for one_scene, one_scale, seed in keys
    ]
    combined = [
        value(indexed[(candidate, one_scene, one_scale, seed)], metric)
        for one_scene, one_scale, seed in keys
    ]
    baseline_mean = mean(baseline)
    combined_mean = mean(combined)
    if metric == "pdr":
        delta = 100.0 * (combined_mean - baseline_mean)
    else:
        delta = 100.0 * (combined_mean - baseline_mean) / baseline_mean
    return baseline_mean, combined_mean, delta


def merge(*row_sets):
    output = []
    for rows in row_sets:
        output.extend(rows)
    return output


def table_main(data_dir):
    rows = merge(load(data_dir / "main.csv"), load(data_dir / "local_failure.csv"))
    lines = [
        "## Main results: Full relative to Baseline",
        "",
        "| Scenario | Nodes | Delta PDR (pp) | Delta comparisons (%) | Delta switches (%) |",
        "|---|---:|---:|---:|---:|",
    ]
    comparison_deltas = []
    for scene in SCENES:
        for scale in (20, 40, 60):
            deltas = {}
            for metric in METRICS:
                _, _, deltas[metric] = paired_delta(
                    rows, "Baseline", "Full", scene, scale, metric
                )
            comparison_deltas.append(deltas["gate_cmp"])
            lines.append(
                f"| {scene} | {scale} | {deltas['pdr']:+.3f} | "
                f"{deltas['gate_cmp']:+.3f} | {deltas['gate_sw']:+.3f} |"
            )
    if not (-71.5 < min(comparison_deltas) < -71.3):
        raise AssertionError("main comparison minimum no longer matches the paper")
    if not (-55.7 < max(comparison_deltas) < -55.5):
        raise AssertionError("main comparison maximum no longer matches the paper")
    return lines


def table_ablation(data_dir):
    baseline_rows = merge(
        load(data_dir / "main.csv"),
        load(data_dir / "local_failure.csv"),
    )
    hard_rows = merge(
        load(data_dir / "ablation.csv"),
        load(data_dir / "ablation_local_failure.csv"),
    )
    rows = merge(baseline_rows, hard_rows)
    indexed = index(rows)
    lines = [
        "## Forty-node ablation",
        "",
        "| Scenario | Baseline PDR (%) | Hard PDR (%) | Full PDR (%) | "
        "Hard/Full comparison delta (%) | Hard/Full switches |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for scene in SCENES[1:]:
        scale = 40
        means = defaultdict(dict)
        for group in ("Baseline", "Hard-Only", "Full"):
            group_rows = [
                indexed[(group, scene, scale, seed)]
                for seed in range(1, 21)
                if (group, scene, scale, seed) in indexed
            ]
            if len(group_rows) not in (10, 20):
                raise ValueError(
                    f"expected 10 or 20 rows for {group}, {scene}; found {len(group_rows)}"
                )
            for metric in METRICS:
                means[group][metric] = mean(value(row, metric) for row in group_rows)
        hard_cmp = (
            100.0
            * (means["Hard-Only"]["gate_cmp"] - means["Baseline"]["gate_cmp"])
            / means["Baseline"]["gate_cmp"]
        )
        full_cmp = (
            100.0
            * (means["Full"]["gate_cmp"] - means["Baseline"]["gate_cmp"])
            / means["Baseline"]["gate_cmp"]
        )
        lines.append(
            f"| {scene} | {100 * means['Baseline']['pdr']:.2f} | "
            f"{100 * means['Hard-Only']['pdr']:.2f} | "
            f"{100 * means['Full']['pdr']:.2f} | "
            f"{hard_cmp:.1f}/{full_cmp:.1f} | "
            f"{means['Hard-Only']['gate_sw']:.1f}/{means['Full']['gate_sw']:.1f} |"
        )
    return lines


def table_prior(data_dir):
    exact = merge(load(data_dir / "main.csv"), load(data_dir / "local_failure.csv"))
    exact = [
        row
        for row in exact
        if row["group"] == "Full"
        and SCENE_ALIASES.get(row["scene"], row["scene"]) in SCENES[1:]
        and int(row["scale"]) == 40
    ]
    exact_index = {
        (SCENE_ALIASES.get(row["scene"], row["scene"]), int(row["seed"])): row
        for row in exact
    }
    lines = [
        "## Coordinate-error robustness at 40 nodes",
        "",
        "| Error | Delta PDR range (pp) | Delta comparisons range (%) | "
        "Delta switches range (%) |",
        "|---:|---:|---:|---:|",
    ]
    max_abs_pdr = 0.0
    for error in (5, 10, 20, 30):
        rows = load(data_dir / f"prior_noise{error:02d}.csv")
        candidate_index = {
            (SCENE_ALIASES.get(row["scene"], row["scene"]), int(row["seed"])): row
            for row in rows
            if row["group"] == "Full" and int(row["scale"]) == 40
        }
        deltas = defaultdict(list)
        for scene in SCENES[1:]:
            keys = [(scene, seed) for seed in range(1, 21)]
            for metric in METRICS:
                reference = mean(value(exact_index[key], metric) for key in keys)
                candidate = mean(value(candidate_index[key], metric) for key in keys)
                delta = (
                    100.0 * (candidate - reference)
                    if metric == "pdr"
                    else 100.0 * (candidate - reference) / reference
                )
                deltas[metric].append(delta)
        max_abs_pdr = max(max_abs_pdr, *(abs(item) for item in deltas["pdr"]))
        lines.append(
            f"| {error}% | [{min(deltas['pdr']):+.3f}, {max(deltas['pdr']):+.3f}] | "
            f"[{min(deltas['gate_cmp']):+.1f}, {max(deltas['gate_cmp']):+.1f}] | "
            f"[{min(deltas['gate_sw']):+.1f}, {max(deltas['gate_sw']):+.1f}] |"
        )
    if max_abs_pdr > 0.551:
        raise AssertionError("prior-error PDR bound no longer matches the paper")
    return lines


def table_squared(data_dir):
    rows = load(data_dir / "squared_etx.csv")
    lines = [
        "## Filter gain over Squared-ETX at 40 nodes",
        "",
        "| Scenario | Delta PDR (pp) | Delta comparisons (%) | Delta switches (%) |",
        "|---|---:|---:|---:|",
    ]
    expected_comparisons = (-65.963, -56.870, -53.597)
    for scene, expected in zip(SCENES[1:], expected_comparisons):
        deltas = {}
        for metric in METRICS:
            _, _, deltas[metric] = paired_delta(
                rows, "Squared-ETX", "Squared-ETX+Full", scene, 40, metric
            )
        if not math.isclose(deltas["gate_cmp"], expected, abs_tol=0.002):
            raise AssertionError(f"Squared-ETX result changed for {scene}")
        lines.append(
            f"| {scene} | {deltas['pdr']:+.3f} | "
            f"{deltas['gate_cmp']:+.3f} | {deltas['gate_sw']:+.3f} |"
        )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "metrics",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "reproduced_paper_tables.md",
    )
    args = parser.parse_args()

    sections = []
    for builder in (table_main, table_ablation, table_prior, table_squared):
        sections.extend(builder(args.data_dir))
        sections.append("")
    args.output.write_text("\n".join(sections), encoding="utf-8")
    print(f"verified released metrics and wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
