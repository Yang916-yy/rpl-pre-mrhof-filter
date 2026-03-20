#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 CONTIKI_NG_PATH REPO_PATH" >&2
  exit 1
fi

CONTIKI_NG="$1"
REPO="$2"

PATCH_FILE="$REPO/patches/contiki-ng/tracked-changes.patch"
NEW_FILES_DIR="$REPO/patches/contiki-ng/new-files"

if [[ ! -d "$CONTIKI_NG/.git" ]]; then
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

echo "[1/2] applying tracked changes"
git -C "$CONTIKI_NG" apply "$PATCH_FILE"

echo "[2/2] copying new files"
cp -a "$NEW_FILES_DIR/." "$CONTIKI_NG/"

echo "done"
echo "next:"
echo "  python3 \"$CONTIKI_NG/tests/14-rpl-paper/generate_paper_csc.py\""
echo "  python3 \"$CONTIKI_NG/tests/14-rpl-lite/generate_rpl_gate_prior.py\""
