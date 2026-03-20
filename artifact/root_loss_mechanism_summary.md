# Root-Loss Mechanism Analysis

Scope:
- Platform: `rpl-lite`
- Groups: `Baseline` vs `Full`
- Scene: `Root-Loss`
- Scales: `20 / 40 / 60`
- Source: existing formal runs in `paper-results-main`

## Key signals

| Scale | dPDR (pp) | dDelay (ms) | dRecov (%) | dgate_cmp (%) | dgate_sw (%) | dDIO | dDAO | dDIS | dfallback | dno_parent |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 | -0.420 | +3.98 | +5.5 | -71.4 | -19.9 | -689.9 | -30.9 | +35.7 | +161.7 | +46.0 |
| 40 | -0.393 | +3.24 | +0.7 | -63.5 | +2.1 | -142.0 | -50.7 | +54.8 | +495.4 | +294.9 |
| 60 | -0.192 | -98.90 | -1.6 | -60.9 | +0.5 | +206.2 | -283.8 | +92.8 | +863.5 | +263.2 |

Additional path signal:

| Scale | Baseline hops | Full hops | dhops |
|---|---:|---:|---:|
| 20 | 9.819 | 10.118 | +0.299 |
| 40 | 11.269 | 11.542 | +0.273 |
| 60 | 16.196 | 6.031 | -10.165 |

## Interpretation

1. At 20 and 40 nodes, the slight `PDR` loss and slower recovery are not caused by failed hard pruning itself.
   - The ablation results show that `Hard-Only` actually raises `PDR` above `Baseline` at both scales.
   - The degradation appears only after the full recovery layer is enabled.

2. The dominant mechanism at 20 and 40 nodes is:
   - candidate-space compression remains strong (`dgate_cmp = -71.4%` and `-63.5%`);
   - but `fallback`, `gate_sel_recovery`, and `gate_no_parent` all rise;
   - therefore the method reaches a smaller candidate set at the cost of temporarily narrower usable-parent availability during global root reconstruction.

3. The control-plane pattern is mixed rather than uniformly inflated.
   - At 20 and 40 nodes, `DIO` and `DAO` both decrease, while `DIS` rises.
   - This suggests that the main issue is not a simple increase in global control chatter, but more frequent recovery probing and temporary unavailability while the root-centered structure reforms.

4. The 60-node case behaves differently.
   - `PDR` remains statistically unchanged, but delay drops by almost `99 ms`.
   - This is explained by a large hop-count collapse (`16.20 -> 6.03`), indicating that the filtered set avoids very long detour paths after root restoration.
   - At the same time, `fallback`, `DIS`, and `no_parent` still increase, so this is not a uniform gain scenario.

## Writing-ready conclusion

Under `Root-Loss`, the most stable effect of the proposed method is still candidate-space compression. The slight delivery loss at 20 and 40 nodes is mainly associated with the conservative recovery layer, which introduces more fallback-driven recovery selections and slightly longer periods without a usable parent during global root reconstruction. At 60 nodes, the method still does not improve `PDR`, but it sharply shortens the resulting routes, which explains the large delay reduction despite continued recovery pressure.
