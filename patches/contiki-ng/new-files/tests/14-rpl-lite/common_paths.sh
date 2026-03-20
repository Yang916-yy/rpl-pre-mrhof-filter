#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="${PAPER_TEST_DIR:-$SCRIPT_DIR}"
CONTIKI_NG_ROOT="${CONTIKI_NG_ROOT:-$(CDPATH= cd -- "$TEST_DIR/../.." && pwd)}"
PAPER_14_DIR="${PAPER_14_DIR:-$CONTIKI_NG_ROOT/tests/14-rpl-lite}"
PAPER_14_PAPER_DIR="${PAPER_14_PAPER_DIR:-$CONTIKI_NG_ROOT/tests/14-rpl-paper}"
PAPER_15_DIR="${PAPER_15_DIR:-$CONTIKI_NG_ROOT/tests/15-rpl-classic}"
COOJA_DIR="${COOJA_DIR:-$CONTIKI_NG_ROOT/tools/cooja}"
