#!/usr/bin/env python3
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path


def sample_valid(row: dict) -> bool:
    script_log = row.get("script_log_path", "")
    if not script_log:
        return row.get("test_ok") == "1"

    path = Path(script_log)
    if not path.exists():
        return row.get("test_ok") == "1"

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return row.get("test_ok") == "1"

    return ("TEST OK" in text) and ("METRIC " in text)


def load_completed(csv_path: Path, expected: int):
    done = defaultdict(set)
    if not csv_path.exists():
        return {}

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not sample_valid(row):
                continue
            key = "|".join([
                row.get("platform", ""),
                row.get("group", ""),
                row.get("scene", ""),
                row.get("scale", ""),
            ])
            done[key].add(row.get("seed", ""))

    return {k: len(v) >= expected for k, v in done.items()}


def update_markdown(md_path: Path, completed: dict):
    text = md_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^- \[(?: |x)\] (?:~~)?`([^`]+)`(?:~~)? <!-- TRACK:([^>]+) -->$",
        re.MULTILINE,
    )

    def repl(match):
        label = match.group(1)
        key = match.group(2)
        if completed.get(key, False):
            return f"- [x] ~~`{label}`~~ <!-- TRACK:{key} -->"
        return f"- [ ] `{label}` <!-- TRACK:{key} -->"

    new_text = pattern.sub(repl, text)
    if new_text != text:
        md_path.write_text(new_text, encoding="utf-8")


def main():
    if len(sys.argv) < 3:
        print("usage: update_experiment_tracker.py <csv> <md> [expected_seeds]", file=sys.stderr)
        return 2

    csv_path = Path(sys.argv[1])
    md_path = Path(sys.argv[2])
    expected = int(sys.argv[3]) if len(sys.argv) > 3 else 20

    completed = load_completed(csv_path, expected)
    update_markdown(md_path, completed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
