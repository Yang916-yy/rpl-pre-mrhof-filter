# Released Per-Seed Metrics

`metrics/` contains the valid per-seed rows used to reproduce the principal
paper tables. Machine-local log paths, runtime paths, and verbose internal
counters are removed. Each CSV retains the experiment identity and the paper's
three main metrics: PDR, final parent comparisons, and parent switches.

Run:

```bash
python3 artifact/reproduce_paper_tables.py
```

The command writes `artifact/reproduced_paper_tables.md` and fails if the
released data no longer match the key numerical ranges reported in the paper.

These CSVs are processed experiment outputs. To repeat the simulations from
scratch, follow `docs/reproduction.md`.
