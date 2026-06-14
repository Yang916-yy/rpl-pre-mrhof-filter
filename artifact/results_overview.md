# Results Overview

Keep these files as the final result set:

- `paper_draft_cn.md`: current Chinese manuscript draft
- `paper_core_tables.md`: core tables intended for the paper body
- `results_appendix.md`: consolidated detailed result tables regenerated from original CSVs
- `statistical_summary.md`: statistical summary
- `overhead_summary.md`: overhead summary
- `pvalue_summary_all.md`: consolidated p-value summary
- `algorithm_formulation_verified.md`: verified method formulation
- `reference_pool_28.md`: literature pool
- `generate_paper_figures.py`: figure generator
- `figures/`: final PDFs used for the paper

Sanitized valid per-seed metrics for the principal paper tables are released
under `data/metrics/`. Verbose raw logs and machine-local runner CSVs remain
outside the repository.

Superseded fragments were removed after consolidation:

- split `formal_*.md` result files
- split `pvalue_summary_*.md` files
- temporary patch/sanity scripts
- superseded figure versions (`v2`, `v3`, ...)
