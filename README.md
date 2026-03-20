# Pre-MRHOF Bad-Edge Filtering with Global Priors for RPL

This repository is a clean open-source scaffold for the code and experiment helpers behind the paper:

> Pre-MRHOF Bad-Edge Filtering with Global Priors for RPL

It is intentionally structured as a patch-style repository on top of Contiki-NG rather than a full fork. The goal is to make the ownership boundary clear:

- upstream Contiki-NG stays upstream;
- this repository contains the filter-specific modifications, new modules, and experiment helpers;
- large result directories, temporary logs, and submission assets are excluded.

## Upstream baseline

The experiments behind this release were developed against the following
Contiki-NG commit:

- `23e51c4d4e5ea13b0469159805f83cc1ba356449`

## Repository layout

- `patches/contiki-ng/tracked-changes.patch`
  - patch for tracked upstream files modified in-place.
- `patches/contiki-ng/new-files/`
  - new files that did not exist in the upstream checkout.
- `artifact/`
  - small reproduction helpers and compact summary artifacts.
- `docs/`
  - open-source scope and reproduction notes.

## What is included

Included code covers three parts:

1. RPL gate implementation
- `os/net/routing/rpl-lite/rpl-gate.c`
- `os/net/routing/rpl-lite/rpl-gate.h`
- `os/net/routing/rpl-classic/rpl-gate.c`
- `os/net/routing/rpl-classic/rpl-gate.h`
- tracked modifications to `rpl-mrhof.c`, `rpl-neighbor.c`, `rpl-icmp6.c`, `rpl-dag.c`, and project configuration headers through `tracked-changes.patch`

2. Experiment helpers
- `tests/14-rpl-lite/run_paper_matrix.py`
- `tests/14-rpl-lite/generate_rpl_gate_prior.py`
- `tests/14-rpl-lite/extract_metric_csv.py`
- `tests/14-rpl-lite/analyze_paper_metrics.py`
- formal run wrappers and significance scripts
- `tests/14-rpl-paper/generate_paper_csc.py`

3. Small artifact helpers
- figure generation helper
- footprint measurement helper
- compact CSV/Markdown summaries used in the manuscript workflow

## What is intentionally excluded

This scaffold does not include:

- full Contiki-NG source tree
- large simulation result directories
- temporary debug wrappers and local retry scripts
- LaTeX submission sources and PDFs
- local logs, caches, and generated paper assets
- generated prior headers such as `rpl-gate-prior-data.h`

The generated prior header is topology-dependent and should be regenerated from the provided scripts.

## Recommended release workflow

1. Create a fresh public repository from this scaffold.
2. Keep the repository under `BSD-3-Clause` and preserve upstream notices in patched files.
3. In the public repository README, pin the exact Contiki-NG commit used for experiments.
4. Add a small worked example showing how to regenerate `rpl-gate-prior-data.h`.
5. If artifact evaluation matters, publish large result directories separately as a release asset or companion artifact repository.

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

This repository does not ship the full result directories. Large experiment
outputs should be published as release assets or in a separate artifact
repository.

## License note

This scaffold uses `BSD-3-Clause`.

That choice is compatible with the upstream Contiki-NG licensing style and fits
the current release model:

- project-authored scripts and new files are released under `BSD-3-Clause`;
- modifications to upstream files are distributed as patches, while the
  original upstream notices remain with the upstream files they modify.

## Status

This scaffold is ready for cleanup into a public repository, but still expects a final pass on:

- author/maintainer metadata
- final public-facing examples
