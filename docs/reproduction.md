# Reproduction Notes

## Minimal external reproduction path

1. Start from a clean Contiki-NG checkout.
2. Apply `tracked-changes.patch`.
3. Copy `new-files/` into the checkout.
4. Use `tests/14-rpl-paper/generate_paper_csc.py` to regenerate paper scenarios.
5. Use `tests/14-rpl-lite/generate_rpl_gate_prior.py` to regenerate prior headers.
6. Run a small sanity matrix with `tests/14-rpl-lite/run_paper_matrix.py`.
7. Use `tests/14-rpl-lite/extract_metric_csv.py` and `analyze_paper_metrics.py` to summarize outputs.

## Notes

- `rpl-gate-prior-data.h` is intentionally excluded because it is generated from the experiment topology.
- `Local Interference Corridor` is exploratory and should not be treated as a canonical benchmark.
- `RPL-classic + Root-Loss` is not a stable comparative baseline in the manuscript and should not be treated as a primary validation target.
