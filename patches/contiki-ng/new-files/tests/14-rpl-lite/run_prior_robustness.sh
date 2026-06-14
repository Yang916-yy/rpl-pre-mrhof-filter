#!/usr/bin/env bash
set -euo pipefail

TEST_DIR="$(cd "$(dirname "$0")" && pwd)"
LABEL="${1:?usage: run_prior_robustness.sh <label> [ENV=VALUE ...]}"
shift || true

for kv in "$@"; do
  export "$kv"
done

OUT_DIR="${PAPER_OUT_DIR:-$TEST_DIR/paper-results-prior-$LABEL}"
GEN_DIR="${PAPER_GEN_DIR:-$TEST_DIR/../14-rpl-paper/generated}"

export PAPER_PLATFORM="rpl-lite"
export PAPER_TEST_DIR="$TEST_DIR"
export PAPER_OUT_DIR="$OUT_DIR"
export PAPER_GEN_DIR="$GEN_DIR"
export PAPER_GROUPS="${PAPER_GROUPS:-full}"
export PAPER_SCENES="${PAPER_SCENES:-s2_disturb s3_rootloss s5_local_failure}"
export PAPER_SCALES="${PAPER_SCALES:-40}"
export PAPER_SEEDS="${PAPER_SEEDS:-1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20}"
export PAPER_EXPECTED_SEEDS="${PAPER_EXPECTED_SEEDS:-20}"
export PAPER_PRIOR_NOISE_SEED="${PAPER_PRIOR_NOISE_SEED:-case}"
export PAPER_MD_PATH=""

mkdir -p "$OUT_DIR"

echo "label=$LABEL"
echo "out_dir=$OUT_DIR"
echo "prior_mode=${PAPER_PRIOR_MODE:-geometry}"
echo "prior_coordinate_noise_pct=${PAPER_PRIOR_COORD_NOISE_PCT:-0}"
echo "prior_noise_seed=$PAPER_PRIOR_NOISE_SEED"
echo "seeds=$PAPER_SEEDS"

python3 "$TEST_DIR/run_paper_matrix.py" | tee "$OUT_DIR/runner.log"
