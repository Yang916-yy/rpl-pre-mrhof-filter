#!/usr/bin/env bash
set -euo pipefail

TEST_DIR="$(cd "$(dirname "$0")" && pwd)"

run_variant() {
  local label="$1"
  shift
  "$TEST_DIR/run_prior_robustness.sh" "$label" "$@"
}

# Exact-prior results already exist in the main experiment.
run_variant noise05 PAPER_PRIOR_MODE=geometry PAPER_PRIOR_COORD_NOISE_PCT=5
run_variant noise10 PAPER_PRIOR_MODE=geometry PAPER_PRIOR_COORD_NOISE_PCT=10
run_variant noise20 PAPER_PRIOR_MODE=geometry PAPER_PRIOR_COORD_NOISE_PCT=20
run_variant noise30 PAPER_PRIOR_MODE=geometry PAPER_PRIOR_COORD_NOISE_PCT=30
run_variant hop PAPER_PRIOR_MODE=hop PAPER_PRIOR_COORD_NOISE_PCT=0
