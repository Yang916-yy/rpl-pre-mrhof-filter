#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 CONTIKI_NG_PATH REPO_PATH" >&2
  exit 1
fi

CONTIKI_NG="$1"
REPO="$2"
EXPECTED_COMMIT="23e51c4d4e5ea13b0469159805f83cc1ba356449"

PATCH_FILE="$REPO/patches/contiki-ng/tracked-changes.patch"
NEW_FILES_DIR="$REPO/patches/contiki-ng/new-files"

if ! git -C "$CONTIKI_NG" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "error: $CONTIKI_NG does not look like a git checkout" >&2
  exit 1
fi

if [[ ! -f "$PATCH_FILE" ]]; then
  echo "error: missing patch file: $PATCH_FILE" >&2
  exit 1
fi

if [[ ! -d "$NEW_FILES_DIR" ]]; then
  echo "error: missing new-files directory: $NEW_FILES_DIR" >&2
  exit 1
fi

ACTUAL_COMMIT="$(git -C "$CONTIKI_NG" rev-parse HEAD)"
if [[ "$ACTUAL_COMMIT" != "$EXPECTED_COMMIT" ]]; then
  echo "error: expected Contiki-NG $EXPECTED_COMMIT" >&2
  echo "error: found $ACTUAL_COMMIT" >&2
  exit 1
fi

echo "[check] validating patch against $ACTUAL_COMMIT"
git -C "$CONTIKI_NG" apply --check "$PATCH_FILE"

echo "[1/2] applying tracked changes"
git -C "$CONTIKI_NG" apply "$PATCH_FILE"

echo "[2/2] copying new files"
cp -a "$NEW_FILES_DIR/." "$CONTIKI_NG/"

echo "done"
echo "next:"
echo "  python3 \"$CONTIKI_NG/tests/14-rpl-paper/generate_paper_csc.py\""
echo "  python3 \"$CONTIKI_NG/tests/14-rpl-lite/run_paper_matrix.py\" --list-cases"
