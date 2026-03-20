#!/usr/bin/env bash
set -eu

source "$(cd "$(dirname "$0")" && pwd)/common_paths.sh"

ROOT="$PAPER_14_DIR"
GEN_DIR="${PAPER_GEN_DIR:-$PAPER_14_PAPER_DIR/generated}"
OUT_DIR="${PAPER_OUT_DIR:-$ROOT/paper-results-main}"
CSV="$OUT_DIR/paper_matrix_results.csv"

require_csc() {
  local path=$1
  if [ ! -f "$path" ]; then
    echo "missing scenario: $path" >&2
    exit 1
  fi
}

require_csc "$GEN_DIR/s1_stable_20.csc"
require_csc "$GEN_DIR/s1_stable_40.csc"
require_csc "$GEN_DIR/s1_stable_60.csc"
require_csc "$GEN_DIR/s2_disturb_20.csc"
require_csc "$GEN_DIR/s2_disturb_40.csc"
require_csc "$GEN_DIR/s2_disturb_60.csc"
require_csc "$GEN_DIR/s3_rootloss_20.csc"
require_csc "$GEN_DIR/s3_rootloss_40.csc"
require_csc "$GEN_DIR/s3_rootloss_60.csc"

mkdir -p "$OUT_DIR"

export PAPER_OUT_DIR="$OUT_DIR"
export PAPER_CSV="$CSV"
export PAPER_GEN_DIR="$GEN_DIR"
export PAPER_MD_PATH=
export PAPER_EXPECTED_SEEDS=20
export PAPER_REQUIRE_GATE_ON=1
export PAPER_GROUPS="baseline full"
export PAPER_SCENES="s1_stable s2_disturb s3_rootloss"
export PAPER_SCALES="20 40 60"
export PAPER_SEEDS="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20"

exec python3 "$ROOT/run_paper_matrix.py"
