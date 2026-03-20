# Release Checklist

## Before publishing

- Confirm the exact upstream Contiki-NG commit is correct.
- Decide the public repository name and visibility.
- Confirm the repository-level `BSD-3-Clause` license is acceptable for release.
- Add maintainer contact information.
- Remove any file that still depends on local absolute paths.
- Check that no result directory or local log slipped into the repository.
- Check that no generated `rpl-gate-prior-data.h` is shipped by mistake.

## Before announcing reproducibility

- Run `scripts/apply_to_contiki_ng.sh` against a fresh checkout.
- Regenerate paper scenarios with `tests/14-rpl-paper/generate_paper_csc.py`.
- Regenerate priors with `tests/14-rpl-lite/generate_rpl_gate_prior.py`.
- Run at least one small matrix successfully.
- Regenerate one small metric CSV successfully.

## Optional but useful

- Add a tagged release matching the paper submission.
- Publish larger result archives as release assets.
- Add a short architecture figure to `docs/`.
- Add a sample command sequence for `rpl-lite` and one for `rpl-classic`.
