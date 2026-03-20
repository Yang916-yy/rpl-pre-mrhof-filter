#!/usr/bin/env bash
set +u

source "$(cd "$(dirname "$0")" && pwd)/common_paths.sh"

ROOT="$CONTIKI_NG_ROOT"
CONF="$PAPER_14_DIR/code/project-conf.h"
GEN_DIR="${PAPER_GEN_DIR:-$PAPER_14_DIR/generated-core}"
OUT_DIR="${PAPER_OUT_DIR:-$PAPER_14_DIR/quick-results}"
LOG_DIR="$OUT_DIR/logs"
CSV="$OUT_DIR/quick_compare_results.csv"
PRIOR_GEN="$PAPER_14_DIR/generate_rpl_gate_prior.py"
CONF_BAK="$(mktemp)"

cp "$CONF" "$CONF_BAK"
cleanup() {
  cp "$CONF_BAK" "$CONF"
  rm -f "$CONF_BAK"
}
trap cleanup EXIT

mkdir -p "$LOG_DIR"

declare -A DONE_CASES

set_group_mode() {
  local group="$1"
  local tmp
  tmp=$(mktemp)
  grep -v '^#define RPL_EXPERIMENTAL_MRHOF' "$CONF" | \
    grep -v '^#define RPL_CONF_WITH_EDGE_GATE' > "$tmp"
  if [ "$group" = "experiment" ]; then
    printf '#define RPL_CONF_WITH_EDGE_GATE 1\n' >> "$tmp"
  fi
  mv "$tmp" "$CONF"
}

check_exp_symbol() {
  cd "$PAPER_14_DIR/code" || return 1
  make TARGET=cooja clean >/dev/null 2>&1 || return 1
  make TARGET=cooja root-node.cooja >/dev/null 2>&1 || return 1
  if nm build/cooja/obj/rpl-neighbor.o | grep -q rpl_gate_parent_allowed; then
    echo ON
  else
    echo OFF
  fi
}

run_one() {
  local group="$1" scene="$2" scale="$3" seed="$4" idx="$5" total="$6"
  local csc="$GEN_DIR/${scene}_${scale}.csc"
  local log="$LOG_DIR/${group}_${scene}_${scale}_seed${seed}.log"
  local scriptlog="$LOG_DIR/${group}_${scene}_${scale}_seed${seed}.testlog"
  local start end wall status testok

  python3 "$PRIOR_GEN" "$csc" || return 1
  rm -f "$COOJA_DIR/COOJA.testlog" >/dev/null 2>&1 || true
  start=$(date +%s)
  if cd "$COOJA_DIR" && ./gradlew --no-daemon --console=plain run --args="--no-gui --autostart --random-seed=${seed} ${csc}" >"$log" 2>&1; then
    status=0
  else
    status=$?
  fi
  end=$(date +%s)
  wall=$((end - start))

  if [ -f "$COOJA_DIR/COOJA.testlog" ]; then
    cp "$COOJA_DIR/COOJA.testlog" "$scriptlog"
  else
    : > "$scriptlog"
  fi

  if grep -q 'TEST OK' "$scriptlog"; then
    testok=1
  else
    testok=0
  fi

  printf '%s,%s,%s,%s,%s,%s,%s,%s,%s\n' "$group" "$scene" "$scale" "$seed" "$status" "$testok" "$wall" "$log" "$scriptlog" >> "$CSV"
  printf '[%s/%s] group=%s scene=%s scale=%s seed=%s status=%s testok=%s wall=%ss\n' "$idx" "$total" "$group" "$scene" "$scale" "$seed" "$status" "$testok" "$wall"
}

main() {
  local groups=(baseline experiment)
  local scenes=(s1_stable s2_disturb s3_rootloss)
  local scales=(20)
  local seeds=(1 2 3)
  local total idx group scene scale seed symbol

  mkdir -p "$OUT_DIR" "$LOG_DIR"
  printf 'group,scene,scale,seed,exit_status,test_ok,wall_sec,log_path,script_log_path\n' > "$CSV"

  total=$(( ${#groups[@]} * ${#scenes[@]} * ${#scales[@]} * ${#seeds[@]} ))
  idx=0

  for group in "${groups[@]}"; do
    echo "=== configure group: $group ==="
    set_group_mode "$group"
    symbol=$(check_exp_symbol)
    echo "symbol_check=$symbol"

    if [ "$group" = "baseline" ] && [ "$symbol" != "OFF" ]; then
      echo "baseline symbol check failed" >&2
      exit 2
    fi
    if [ "$group" = "experiment" ] && [ "$symbol" != "ON" ]; then
      echo "experiment symbol check failed" >&2
      exit 3
    fi

    for scene in "${scenes[@]}"; do
      for scale in "${scales[@]}"; do
        for seed in "${seeds[@]}"; do
          idx=$((idx + 1))
          run_one "$group" "$scene" "$scale" "$seed" "$idx" "$total"
        done
      done
    done
  done

  echo "done: $CSV"
}

main "$@"
