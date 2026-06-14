# Structural Candidate-Space Compression for RPL

This repository contains the Contiki-NG implementation, experiment runners,
scenario templates, released per-seed metrics, and analysis scripts for:

> Structural Candidate-Space Compression for Efficient RPL Parent Selection

The filter removes structurally implausible candidates before MRHOF or
Squared-ETX ranks the survivors. The release is maintained as a patch against
an exact Contiki-NG revision rather than as a fork.

## Reproducibility status

- Upstream Contiki-NG commit:
  `23e51c4d4e5ea13b0469159805f83cc1ba356449`
- Main experiments: 20 matched seeds at 20, 40, and 60 nodes
- Released metrics: PDR, final parent comparisons, and parent switches
- Analysis dependencies: Python 3 standard library only
- Simulation environment: Linux, Contiki-NG Cooja, and its normal build
  dependencies

## Fast result verification

The released per-seed CSVs are sufficient to recompute the paper's main,
ablation, prior-robustness, and Squared-ETX tables:

```bash
python3 artifact/reproduce_paper_tables.py
```

The command writes `artifact/reproduced_paper_tables.md` and exits with an
error if key reported ranges no longer match the released data.

## Reproduce simulations from scratch

```bash
git clone https://github.com/contiki-ng/contiki-ng.git
cd contiki-ng
git checkout 23e51c4d4e5ea13b0469159805f83cc1ba356449
git submodule update --init tools/cooja

export CONTIKI_NG="$PWD"
export REPO=/path/to/rpl-pre-mrhof-filter
bash "$REPO/scripts/apply_to_contiki_ng.sh" "$CONTIKI_NG" "$REPO"

python3 tests/14-rpl-paper/generate_paper_csc.py
python3 tests/14-rpl-lite/run_paper_matrix.py --help
python3 tests/14-rpl-lite/run_paper_matrix.py --list-cases
```

Run the canonical matrices:

```bash
bash tests/14-rpl-lite/run_formal_main.sh
bash tests/14-rpl-lite/run_formal_local_failure.sh
bash tests/14-rpl-lite/run_formal_ablation.sh
bash tests/14-rpl-lite/run_formal_ablation_local_failure.sh
bash tests/14-rpl-lite/run_prior_robustness_suite.sh
bash tests/14-rpl-lite/run_squared_etx_orthogonal.sh
```

Extract metrics from any completed result directory:

```bash
python3 tests/14-rpl-lite/extract_metric_csv.py \
  tests/14-rpl-lite/paper-results-main
```

The runners are resumable: valid completed `(group, scene, scale, seed)` rows
in `paper_matrix_results.csv` are skipped.

## One-seed smoke test

Before launching the full matrix, run one paired 20-node case:

```bash
PAPER_GROUPS="baseline full" \
PAPER_SCENES="s2_disturb" \
PAPER_SCALES="20" \
PAPER_SEEDS="1" \
PAPER_EXPECTED_SEEDS="1" \
PAPER_GEN_DIR="$CONTIKI_NG/tests/14-rpl-paper/generated" \
PAPER_OUT_DIR="$CONTIKI_NG/tests/14-rpl-lite/paper-results-smoke" \
python3 "$CONTIKI_NG/tests/14-rpl-lite/run_paper_matrix.py"

python3 "$CONTIKI_NG/tests/14-rpl-lite/extract_metric_csv.py" \
  "$CONTIKI_NG/tests/14-rpl-lite/paper-results-smoke"
```

## Repository layout

- `patches/contiki-ng/tracked-changes.patch`: modifications to upstream files.
- `patches/contiki-ng/new-files/`: filter modules, runners, and scenario inputs.
- `data/metrics/`: sanitized valid per-seed rows used by the paper.
- `artifact/`: table reproduction, statistical summaries, and footprint data.
- `docs/reproduction.md`: detailed experiment-to-table provenance.
- `scripts/apply_to_contiki_ng.sh`: applies this release to a clean checkout.

## Principal experiment groups

- `Baseline`: standard MRHOF.
- `Full`: structural hard filtering plus the recovery safeguard.
- `Hard-Only`: structural hard filtering without the safeguard.
- `Squared-ETX`: Contiki-NG Squared-ETX MRHOF.
- `Squared-ETX+Full`: Squared-ETX preceded by the proposed filter.

The structural-prior suite applies coordinate errors of 5%, 10%, 20%, and
30% of radio range while retaining the same scenario and radio seeds.

## Implementation footprint

For RPL-lite Cooja builds, Hard-Only adds 756 B of flash and 32 B of RAM.
Full adds 1101 B of flash and 32 B of RAM. Build-level measurements and the
measurement helper are under `artifact/`.

## Data policy

The repository includes compact per-seed metrics but not verbose Cooja logs.
Published CSVs contain no machine-local paths. Scenario files and prior
headers are deterministically generated from the released templates and
scripts.

## License

Project-authored code and scripts are released under `BSD-3-Clause`.
Modifications to Contiki-NG are distributed as a patch while preserving the
upstream licensing boundary.
