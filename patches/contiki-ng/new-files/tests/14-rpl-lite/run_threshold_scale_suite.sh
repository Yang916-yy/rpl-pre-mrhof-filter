#!/usr/bin/env bash
set -euo pipefail

TEST_DIR="$(cd "$(dirname "$0")" && pwd)"
GEN_DIR="${PAPER_GEN_DIR:-$TEST_DIR/../14-rpl-paper/generated}"
SEEDS="${PAPER_SEEDS:-1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20}"
SCENES="${PAPER_SCENES:-s2_disturb s3_rootloss s5_local_failure}"
SCALES="${PAPER_SCALES:-20 40 60}"

run_variant() {
  local label="$1"
  shift
  PAPER_SEEDS="$SEEDS" \
  PAPER_EXPECTED_SEEDS=20 \
  PAPER_GEN_DIR="$GEN_DIR" \
  PAPER_SCENES="$SCENES" \
  PAPER_SCALES="$SCALES" \
    "$TEST_DIR/run_param_sensitivity.sh" "$label" "$@"
}

run_variant tau160 PAPER_GATE_STRICT_TAU_Q8=160
run_variant tau224 PAPER_GATE_STRICT_TAU_Q8=224
run_variant tmid64 PAPER_GATE_T_MID_Q8=64
run_variant tmid128 PAPER_GATE_T_MID_Q8=128
