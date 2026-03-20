#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "$0")" && pwd)/common_paths.sh"

ROOT="$CONTIKI_NG_ROOT"
TEST_DIR="$PAPER_14_DIR"
GEN_DIR="${PAPER_GEN_DIR:-$PAPER_14_PAPER_DIR/generated}"
OUT_DIR="${PAPER_OUT_DIR:-$TEST_DIR/paper-results-local-failure}"
CSV="$OUT_DIR/paper_matrix_results.csv"

mkdir -p "$OUT_DIR"

export PAPER_GEN_DIR="$GEN_DIR"
export PAPER_OUT_DIR="$OUT_DIR"
export PAPER_CSV="$CSV"
export PAPER_GROUPS="baseline full"
export PAPER_SCENES="s5_local_failure"
export PAPER_SCALES="20 40 60"
export PAPER_SEEDS="1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20"
export PAPER_REQUIRE_GATE_ON=1

# Fixed Local-Failure configuration validated by 2-seed sanity.
export PAPER_LOCAL_FAIL_SHIFT=260.0
export PAPER_LOCAL_FAIL_ON_US=1000000
export PAPER_LOCAL_FAIL_OFF_US=2500000

python3 "$PAPER_14_PAPER_DIR/generate_paper_csc.py"
python3 "$TEST_DIR/run_paper_matrix.py"
