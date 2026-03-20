# Pre-MRHOF Bad-Edge Filtering with Global Priors for RPL

This repository releases the code scaffold, Contiki-NG patch set, and compact reproduction helpers behind the paper:

> Pre-MRHOF Bad-Edge Filtering with Global Priors for RPL

It is intentionally structured as a patch-style repository on top of Contiki-NG rather than a full fork. The goal is to keep the ownership boundary clear:

- upstream Contiki-NG stays upstream;
- this repository contains the filter-specific modifications, new modules, experiment helpers, and processed summary data used in the manuscript;
- large raw result directories, temporary logs, and submission assets are excluded.

## At a glance

- Scope: pre-MRHOF bad-edge filtering for RPL in Contiki-NG
- Release style: patch-oriented, not a full upstream fork
- License: `BSD-3-Clause`
- Upstream baseline: Contiki-NG `23e51c4d4e5ea13b0469159805f83cc1ba356449`

## Quick start

Assume:

- `CONTIKI_NG=/path/to/contiki-ng`
- `REPO=/path/to/rpl-pre-mrhof-filter`

Apply the release to a clean checkout:

```bash
bash "$REPO/scripts/apply_to_contiki_ng.sh" "$CONTIKI_NG" "$REPO"
```

Then regenerate scenarios and prior data:

```bash
python3 "$CONTIKI_NG/tests/14-rpl-paper/generate_paper_csc.py"
python3 "$CONTIKI_NG/tests/14-rpl-lite/generate_rpl_gate_prior.py"
```

For a minimal sanity path, inspect the runner interfaces first:

```bash
python3 "$CONTIKI_NG/tests/14-rpl-lite/run_paper_matrix.py" --help
python3 "$CONTIKI_NG/tests/14-rpl-lite/extract_metric_csv.py" --help
```

## Repository layout

- `patches/contiki-ng/tracked-changes.patch`
  - patch for tracked upstream files modified in-place.
- `patches/contiki-ng/new-files/`
  - new files that did not exist in the upstream checkout.
- `artifact/`
  - small reproduction helpers and compact summary artifacts.
- `docs/`
  - scope, reproduction, and release notes.
- `scripts/`
  - helper commands for applying the release to a clean checkout.

## Included components

Included code covers three parts.

### 1. RPL gate implementation

- `os/net/routing/rpl-lite/rpl-gate.c`
- `os/net/routing/rpl-lite/rpl-gate.h`
- `os/net/routing/rpl-classic/rpl-gate.c`
- `os/net/routing/rpl-classic/rpl-gate.h`
- tracked modifications to `rpl-mrhof.c`, `rpl-neighbor.c`, `rpl-icmp6.c`, `rpl-dag.c`, and project configuration headers through `tracked-changes.patch`

### 2. Experiment helpers

- `tests/14-rpl-lite/run_paper_matrix.py`
- `tests/14-rpl-lite/generate_rpl_gate_prior.py`
- `tests/14-rpl-lite/extract_metric_csv.py`
- `tests/14-rpl-lite/analyze_paper_metrics.py`
- formal run wrappers and significance scripts
- `tests/14-rpl-paper/generate_paper_csc.py`

### 3. Lightweight artifact helpers

- figure generation helper
- footprint measurement helper
- compact CSV/Markdown summaries used in the manuscript workflow
- processed result overviews, appendix tables, overhead summaries, and statistical summaries

## Intentionally excluded

This repository does not include:

- the full Contiki-NG source tree
- large raw simulation result directories
- temporary debug wrappers and local retry scripts
- LaTeX submission sources and PDFs
- local logs, caches, and generated paper assets
- generated prior headers such as `rpl-gate-prior-data.h`

The generated prior header is topology-dependent and should be regenerated from the provided scripts. Processed summary data and compact manuscript-support artifacts are included under `artifact/`.

## Applying the code to a clean Contiki-NG checkout

Assume `CONTIKI_NG=/path/to/contiki-ng` and this repository root is `REPO`.

1. Apply tracked modifications:

```bash
git -C "$CONTIKI_NG" apply "$REPO/patches/contiki-ng/tracked-changes.patch"
```

2. Copy new files into the tree:

```bash
rsync -a "$REPO/patches/contiki-ng/new-files/" "$CONTIKI_NG/"
```

3. Regenerate topology-specific prior data before building the paper scenarios.

For convenience, the repository also includes a helper:

```bash
bash "$REPO/scripts/apply_to_contiki_ng.sh" "$CONTIKI_NG" "$REPO"
```

## Minimal reproduction

The smallest useful external path is:

1. Start from the pinned Contiki-NG commit.
2. Apply the patch and copy the new files.
3. Generate scenario files.
4. Generate topology-specific prior data.
5. Run a small matrix.
6. Extract metrics.

Example:

```bash
export CONTIKI_NG=/path/to/contiki-ng
export REPO=/path/to/rpl-pre-mrhof-filter

bash "$REPO/scripts/apply_to_contiki_ng.sh" "$CONTIKI_NG" "$REPO"

python3 "$CONTIKI_NG/tests/14-rpl-paper/generate_paper_csc.py"
python3 "$CONTIKI_NG/tests/14-rpl-lite/generate_rpl_gate_prior.py"
python3 "$CONTIKI_NG/tests/14-rpl-lite/run_paper_matrix.py" --help
python3 "$CONTIKI_NG/tests/14-rpl-lite/extract_metric_csv.py" --help
```

This repository does not ship the full raw result directories. Instead, it includes processed summary data sufficient to trace the reported tables and main comparisons. Large experiment outputs can be published separately as release assets or in a companion artifact repository.

## License

This scaffold uses `BSD-3-Clause`.

That choice is compatible with the upstream Contiki-NG licensing style and fits the current release model:

- project-authored scripts and new files are released under `BSD-3-Clause`;
- modifications to upstream files are distributed as patches, while the original upstream notices remain with the upstream files they modify.

## Current status

The repository is ready for public use as a code-and-patch release. The remaining optional polish items are:

- maintainer metadata
- richer public-facing examples
- separate publication of large result artifacts
