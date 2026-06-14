# Reproduction and Provenance

## Two reproduction levels

### 1. Recompute reported tables

This path requires only Python 3:

```bash
python3 artifact/reproduce_paper_tables.py
```

Inputs are the sanitized valid rows in `data/metrics/`. The output is
`artifact/reproduced_paper_tables.md`. The script checks:

- all main cells contain 20 matched Baseline/Full seeds;
- comparison reduction remains 55.6%--71.4%;
- the maximum absolute PDR change under coordinate error remains at most
  0.551 percentage points;
- the Squared-ETX comparison reductions match the released paired runs.

### 2. Repeat the Cooja experiments

Use Linux and a clean Contiki-NG checkout at:

```text
23e51c4d4e5ea13b0469159805f83cc1ba356449
```

Initialize the Cooja submodule before applying the release:

```bash
git -C /path/to/contiki-ng submodule update --init tools/cooja
```

Apply the release:

```bash
bash scripts/apply_to_contiki_ng.sh /path/to/contiki-ng /path/to/this-repo
```

The copied `tests/14-rpl-paper/templates/` directory contains the three base
CSC inputs. Generate all 20/40/60-node scenarios with:

```bash
python3 /path/to/contiki-ng/tests/14-rpl-paper/generate_paper_csc.py
```

Each runner regenerates the topology-specific prior before every seed.

## Experiment-to-data mapping

| Released CSV | Simulation source |
|---|---|
| `main.csv` | `run_formal_main.sh` |
| `local_failure.csv` | `run_formal_local_failure.sh` |
| `ablation.csv` | `run_formal_ablation.sh` |
| `ablation_local_failure.csv` | `run_formal_ablation_local_failure.sh` |
| `prior_noise05.csv`--`prior_noise30.csv` | `run_prior_robustness_suite.sh` |
| `squared_etx.csv` | `run_squared_etx_orthogonal.sh` |

`extract_metric_csv.py` reads the final `METRIC` line and `TEST OK` marker
from each Cooja test log. `export_public_metrics.py` then removes local paths
and counters not used by the principal paper tables.

## Seed policy

- Main, prior robustness, and Squared-ETX: seeds 1--20.
- Hard-Only ablation: seeds 1--10.
- Variants use the same seed numbers as their paired reference.
- Coordinate perturbation uses the Cooja case seed by default.

## Canonical settings

- Strict slack threshold: 192 (Q8).
- Mid-band threshold: 96 (Q8).
- Reserved candidates: 2.
- Structural-prior mode: geometry.
- Coordinate error: 0 for the main experiment.

## Valid-run policy

A row is accepted only when:

- Cooja exits through the experiment runner;
- the test log contains `TEST OK`;
- the test log contains a complete `METRIC` record;
- gated variants report `gate_on=1`.

The runner restores `project-conf.h` after completion or failure and resumes
from valid rows already recorded in `paper_matrix_results.csv`.

## Expected runtime

Runtime depends strongly on CPU and Cooja version. The full release contains
many hundreds of simulations; use the one-seed smoke command in the root
README before launching the complete suite.
