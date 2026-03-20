from __future__ import annotations

import argparse
import csv
import re
import subprocess
from pathlib import Path

TARGETS = ["root-node", "sender-node", "receiver-node", "dis-sender"]
GROUPS = {
    "Baseline": [],
    "Hard-Only": [
        "#define RPL_CONF_WITH_EDGE_GATE 1",
        "#define RPL_CONF_EDGE_GATE_ENABLE_HARD_PRUNE 1",
        "#define RPL_CONF_EDGE_GATE_ENABLE_SOFT_GATING 0",
    ],
    "Full": [
        "#define RPL_CONF_WITH_EDGE_GATE 1",
        "#define RPL_CONF_EDGE_GATE_ENABLE_HARD_PRUNE 1",
        "#define RPL_CONF_EDGE_GATE_ENABLE_SOFT_GATING 1",
    ],
}
DEFINE_PREFIXES = [
    "#define RPL_CONF_WITH_EDGE_GATE",
    "#define RPL_CONF_EDGE_GATE_ENABLE_HARD_PRUNE",
    "#define RPL_CONF_EDGE_GATE_ENABLE_SOFT_GATING",
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contiki-ng-win",
        type=Path,
        default=None,
        help="Windows-visible path to a Contiki-NG checkout",
    )
    parser.add_argument(
        "--contiki-ng-linux",
        default=None,
        help="Linux path to the same Contiki-NG checkout inside WSL",
    )
    return parser.parse_args()


def run_wsl(cmd: str, cwd_linux: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["wsl", "-d", "Ubuntu-22.04", "bash", "-lc", f"cd '{cwd_linux}' && {cmd}"],
        text=True,
        capture_output=True,
        check=True,
    )


def set_group_mode(conf: Path, lines: list[str]) -> None:
    original = conf.read_text(encoding="utf-8").splitlines()
    kept = [line for line in original if not any(line.startswith(prefix) for prefix in DEFINE_PREFIXES)]
    kept.extend(lines)
    conf.write_text("\n".join(kept) + "\n", encoding="utf-8")


def measure_one(code_dir_linux: str, target: str) -> tuple[int, int, int]:
    run_wsl(f"make clean >/dev/null && make TARGET=cooja {target}.cooja >/dev/null", code_dir_linux)
    out = run_wsl(f"size build/cooja/{target}.cooja", code_dir_linux).stdout.splitlines()
    for line in out:
        m = re.match(rf"\s*(\d+)\s+(\d+)\s+(\d+)\s+\d+\s+\w+\s+build/cooja/{re.escape(target)}\.cooja", line)
        if m:
            return tuple(int(x) for x in m.groups())
    raise RuntimeError(f"size output parse failed for {code_dir} {target}: {out}")


def main() -> None:
    args = parse_args()
    if args.contiki_ng_win is None or args.contiki_ng_linux is None:
        raise SystemExit(
            "provide both --contiki-ng-win and --contiki-ng-linux, "
            "for example: --contiki-ng-win \\\\wsl.localhost\\Ubuntu-22.04\\home\\user\\contiki-ng "
            "--contiki-ng-linux /home/user/contiki-ng"
        )
    contiki_ng_win = args.contiki_ng_win.resolve()
    contiki_ng_linux = args.contiki_ng_linux.rstrip("/")
    cases = [
        ("rpl-lite", contiki_ng_win / "tests" / "14-rpl-lite" / "code", f"{contiki_ng_linux}/tests/14-rpl-lite/code"),
        ("rpl-classic", contiki_ng_win / "tests" / "15-rpl-classic" / "code", f"{contiki_ng_linux}/tests/15-rpl-classic/code"),
    ]
    csv_path = Path("footprint_overhead.csv")
    md_path = Path("footprint_overhead.md")
    rows: list[dict[str, object]] = []

    for platform, code_dir, code_dir_linux in cases:
        conf = code_dir / "project-conf.h"
        backup = conf.read_text(encoding="utf-8")
        try:
            for group, defines in GROUPS.items():
                set_group_mode(conf, defines)
                for target in TARGETS:
                    text, data, bss = measure_one(code_dir_linux, target)
                    rows.append(
                        {
                            "platform": platform,
                            "group": group,
                            "target": target,
                            "text": text,
                            "data": data,
                            "bss": bss,
                            "flash": text + data,
                            "ram": data + bss,
                        }
                    )
        finally:
            conf.write_text(backup, encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["platform", "group", "target", "text", "data", "bss", "flash", "ram"])
        writer.writeheader()
        writer.writerows(rows)

    grouped: dict[tuple[str, str], dict[str, dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((row["platform"], row["target"]), {})[row["group"]] = row

    lines = [
        "# Filter Footprint Overhead",
        "",
        "Static firmware size from `TARGET=cooja` builds.",
        "Flash = `text + data`; RAM = `data + bss`.",
        "",
    ]
    for platform in ["rpl-lite", "rpl-classic"]:
        lines.append(f"## {platform}")
        lines.append("")
        lines.append("| Target | Baseline Flash | Hard-Only Flash | Full Flash | dFlash Hard | dFlash Full | Baseline RAM | Hard-Only RAM | Full RAM | dRAM Hard | dRAM Full |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for target in TARGETS:
            base = grouped[(platform, target)]["Baseline"]
            hard = grouped[(platform, target)]["Hard-Only"]
            full = grouped[(platform, target)]["Full"]
            lines.append(
                "| {target} | {bf} | {hf} | {ff} | {dhf:+d} | {dff:+d} | {br} | {hr} | {fr} | {dhr:+d} | {dfr:+d} |".format(
                    target=target,
                    bf=base["flash"],
                    hf=hard["flash"],
                    ff=full["flash"],
                    dhf=hard["flash"] - base["flash"],
                    dff=full["flash"] - base["flash"],
                    br=base["ram"],
                    hr=hard["ram"],
                    fr=full["ram"],
                    dhr=hard["ram"] - base["ram"],
                    dfr=full["ram"] - base["ram"],
                )
            )
        lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
