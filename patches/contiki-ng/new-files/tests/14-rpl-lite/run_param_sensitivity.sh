#!/usr/bin/env bash
set -euo pipefail

TEST_DIR="$(cd "$(dirname "$0")" && pwd)"

LABEL="${1:?usage: run_param_sensitivity.sh <label> [ENV=VALUE ...]}"
shift || true

for kv in "$@"; do
  export "$kv"
done

OUT_DIR="${PAPER_OUT_DIR:-$TEST_DIR/paper-results-sensitivity-$LABEL}"

export PAPER_PLATFORM="rpl-lite"
export PAPER_TEST_DIR="$TEST_DIR"
export PAPER_OUT_DIR="$OUT_DIR"
export PAPER_GROUPS="${PAPER_GROUPS:-full}"
export PAPER_SCENES="${PAPER_SCENES:-s2_disturb s3_rootloss s5_local_failure}"
export PAPER_SCALES="${PAPER_SCALES:-40}"
export PAPER_SEEDS="${PAPER_SEEDS:-1 2 3 4 5 6 7 8 9 10}"
export PAPER_EXPECTED_SEEDS="${PAPER_EXPECTED_SEEDS:-10}"
export PAPER_MD_PATH=""

mkdir -p "$OUT_DIR"

echo "label=$LABEL"
echo "out_dir=$OUT_DIR"
echo "gate_t_mid=${PAPER_GATE_T_MID_Q8:-default}"
echo "gate_strict_tau=${PAPER_GATE_STRICT_TAU_Q8:-default}"
echo "gate_k_reserve=${PAPER_GATE_MIN_RESERVE_PARENTS:-default}"
echo "gate_bad_k=${PAPER_GATE_BAD_K:-default}"
echo "gate_good_m=${PAPER_GATE_GOOD_M:-default}"

python3 "$TEST_DIR/run_paper_matrix.py" \
  | tee "$OUT_DIR/runner.log"

