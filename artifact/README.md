# Artifact Contents

This directory contains the analysis scripts and processed summaries that
support the manuscript.

## Direct table reproduction

Run from the repository root:

```bash
python3 artifact/reproduce_paper_tables.py
```

The script reads `data/metrics/`, verifies the principal numerical claims,
and writes `artifact/reproduced_paper_tables.md`.

## Included

- processed summary tables used in the paper and appendix
- compact CSV summaries for sensitivity and footprint overhead
- figure-generation and footprint-measurement helpers
- prior-robustness and Squared-ETX analysis scripts

## Not included

- verbose Cooja logs
- local retry wrappers and build products
- paper submission sources and PDFs
