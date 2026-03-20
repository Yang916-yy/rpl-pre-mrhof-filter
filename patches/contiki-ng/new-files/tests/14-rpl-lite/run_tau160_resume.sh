#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common_paths.sh"
cd "$PAPER_14_DIR"
export PAPER_PLATFORM=rpl-lite
export PAPER_TEST_DIR="$PAPER_14_DIR"
export PAPER_OUT_DIR="${PAPER_OUT_DIR:-$PAPER_14_DIR/paper-results-sensitivity-tau160-test}"
export PAPER_GEN_DIR="${PAPER_GEN_DIR:-$PAPER_14_PAPER_DIR/generated}"
export PAPER_GROUPS=full
export PAPER_SCENES='s2_disturb s3_rootloss s5_local_failure'
export PAPER_SCALES=40
export PAPER_SEEDS='1 2 3 4 5 6 7 8 9 10'
export PAPER_EXPECTED_SEEDS=10
export PAPER_MD_PATH=
export PAPER_GATE_STRICT_TAU_Q8=160
./run_param_sensitivity.sh tau160_resume
