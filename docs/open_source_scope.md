# Open-Source Scope

## Include

### Core filter code
- `patches/contiki-ng/tracked-changes.patch`
- `patches/contiki-ng/new-files/os/net/routing/rpl-lite/rpl-gate.c`
- `patches/contiki-ng/new-files/os/net/routing/rpl-lite/rpl-gate.h`
- `patches/contiki-ng/new-files/os/net/routing/rpl-classic/rpl-gate.c`
- `patches/contiki-ng/new-files/os/net/routing/rpl-classic/rpl-gate.h`

### Experiment orchestration
- `patches/contiki-ng/new-files/tests/14-rpl-lite/*.py`
- `patches/contiki-ng/new-files/tests/14-rpl-lite/run_*.sh`
- `patches/contiki-ng/new-files/tests/14-rpl-paper/generate_paper_csc.py`

### Lightweight artifact helpers
- `artifact/generate_paper_figures.py`
- `artifact/measure_filter_footprint.py`
- compact summaries in `artifact/`

## Exclude

### Submission-only assets
- `paper_elscas_en.tex`
- `paper_submission_en.pdf`
- `paper_draft_*.md`
- reviewer/revision planning notes

### Local temporary assets
- `tmp_*`
- `*.log`
- `__pycache__/`
- generated LaTeX aux files

### Large experiment outputs
- `paper-results*/`
- generated scenario dumps
- noise/interference sweep outputs

### Generated topology-specific headers
- `rpl-gate-prior-data.h`
- any generated `.csc` scenario output

## Rationale

The public repository should expose the method and reproduction path, not the entire local working directory. Large result directories and submission assets make ownership, licensing, and reuse boundaries less clear.
