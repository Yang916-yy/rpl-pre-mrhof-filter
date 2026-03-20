#!/usr/bin/env bash
set -eu

source "$(cd "$(dirname "$0")" && pwd)/common_paths.sh"

ROOT="$PAPER_14_DIR"
CLASSIC_TEST="${PAPER_CLASSIC_TEST_DIR:-$PAPER_15_DIR}"
GEN_DIR="${PAPER_GEN_DIR:-$CLASSIC_TEST/generated-paper}"
OUT_DIR="${PAPER_OUT_DIR:-$CLASSIC_TEST/paper-results-generalization}"
CSV="$OUT_DIR/paper_matrix_results.csv"

require_csc() {
  local path=$1
  if [ ! -f "$path" ]; then
    echo "missing scenario: $path" >&2
    exit 1
  fi
}

require_csc "$GEN_DIR/s2_disturb_20.csc"
require_csc "$GEN_DIR/s2_disturb_40.csc"
require_csc "$GEN_DIR/s2_disturb_60.csc"
require_csc "$GEN_DIR/s3_rootloss_20.csc"
require_csc "$GEN_DIR/s3_rootloss_40.csc"
require_csc "$GEN_DIR/s3_rootloss_60.csc"

mkdir -p "$OUT_DIR"

export PAPER_PLATFORM=rpl-classic
export PAPER_TEST_DIR="$CLASSIC_TEST"
export PAPER_OUT_DIR="$OUT_DIR"
export PAPER_CSV="$CSV"
export PAPER_GEN_DIR="$GEN_DIR"
export PAPER_MD_PATH=
export PAPER_EXPECTED_SEEDS=10
export PAPER_REQUIRE_GATE_ON=1
export PAPER_GROUPS="baseline full"
export PAPER_SCENES="s2_disturb s3_rootloss"
export PAPER_SCALES="20 40 60"
export PAPER_SEEDS="1 2 3 4 5 6 7 8 9 10"

exec python3 "$ROOT/run_paper_matrix.py"
