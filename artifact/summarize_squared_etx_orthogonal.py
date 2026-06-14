#!/usr/bin/env python3
import argparse
import csv
import itertools
import math
from pathlib import Path


METRICS = {
    "metric_pdr": ("PDR", "pp"),
    "metric_avg_delay_ms": ("Delay (ms)", "%"),
    "metric_recov_ms": ("Recovery (ms)", "%"),
    "metric_gate_cmp": ("Comparisons", "%"),
    "metric_gate_sw": ("Parent switches", "%"),
}


def mean(values):
    return sum(values) / len(values)


def sample_std(values):
    if len(values) < 2:
        return 0.0
    center = mean(values)
    return math.sqrt(sum((value - center) ** 2 for value in values) / (len(values) - 1))


def signflip_pvalue(differences):
    differences = [value for value in differences if abs(value) > 1e-12]
    observed = abs(sum(differences))
    extreme = 0
    total = 1 << len(differences)
    for signs in itertools.product((-1, 1), repeat=len(differences)):
        if abs(sum(sign * value for sign, value in zip(signs, differences))) >= observed - 1e-12:
            extreme += 1
    return extreme / total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_prefix", type=Path)
    args = parser.parse_args()

    with args.input_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    by_group = {"Squared-ETX": {}, "Squared-ETX+Full": {}}
    for row in rows:
        if row["group"] in by_group:
            by_group[row["group"]][(row["scene"], row["scale"], row["seed"])] = row

    output = []
    for scene in ("Temporary Root Displacement", "Root-Loss", "Local Failure"):
        keys = sorted(
            key for key in set(by_group["Squared-ETX"]) & set(by_group["Squared-ETX+Full"])
            if key[0] == scene
        )
        for metric, (label, delta_unit) in METRICS.items():
            baseline = [float(by_group["Squared-ETX"][key][metric]) for key in keys]
            combined = [float(by_group["Squared-ETX+Full"][key][metric]) for key in keys]
            differences = [candidate - reference for reference, candidate in zip(baseline, combined)]
            if delta_unit == "pp":
                delta = 100.0 * (mean(combined) - mean(baseline))
            else:
                delta = 100.0 * (mean(combined) - mean(baseline)) / mean(baseline)
            output.append({
                "scene": scene,
                "metric": metric.removeprefix("metric_"),
                "metric_label": label,
                "n_pairs": len(keys),
                "squared_etx_mean": mean(baseline),
                "squared_etx_sd": sample_std(baseline),
                "combined_mean": mean(combined),
                "combined_sd": sample_std(combined),
                "delta_vs_squared_etx": delta,
                "delta_unit": delta_unit,
                "p_value": signflip_pvalue(differences),
            })

    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    with args.output_prefix.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=output[0].keys())
        writer.writeheader()
        writer.writerows(output)

    lookup = {(row["scene"], row["metric"]): row for row in output}
    lines = [
        "# Squared-ETX Orthogonal Comparison",
        "",
        "Squared-ETX is compared with Squared-ETX plus the proposed filter using 20 paired seeds.",
        "",
        "| Scene | PDR delta (pp) | Delay delta | Recovery delta | Comparison delta | Switch delta |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for scene in ("Temporary Root Displacement", "Root-Loss", "Local Failure"):
        values = {}
        for metric in ("pdr", "avg_delay_ms", "recov_ms", "gate_cmp", "gate_sw"):
            row = lookup[(scene, metric)]
            suffix = " pp" if row["delta_unit"] == "pp" else "%"
            values[metric] = f"{row['delta_vs_squared_etx']:+.3f}{suffix} (p={row['p_value']:.6f})"
        lines.append(
            f"| {scene} | {values['pdr']} | {values['avg_delay_ms']} | "
            f"{values['recov_ms']} | {values['gate_cmp']} | {values['gate_sw']} |"
        )
    args.output_prefix.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
