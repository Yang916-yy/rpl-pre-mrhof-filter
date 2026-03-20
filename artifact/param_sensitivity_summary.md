# Parameter Sensitivity Summary

Reference: existing formal `rpl-lite | Full | scale=40` results. Sensitivity runs keep the same seeds and scenes, and vary one parameter at a time.

## Strict slack threshold (`tau_strict`)

| Setting | Scene | PDR | dPDR (pp) | dDelay (ms) | dRecov (%) | dgate_cmp (%) | dgate_sw (%) | dfallback |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `tau=160` | Temporary Root Displacement | 0.993969 | +0.030 | -2.51 | +4.9 | -73.8 | -40.9 | -5.9 |
| `tau=160` | Root-Loss | 0.728392 | -1.458 | +14.12 | +10.1 | -71.3 | -28.1 | -419.7 |
| `tau=160` | Local Failure | 0.995431 | +0.230 | -3.39 | +5.2 | +0.9 | +9.1 | -6.6 |
| `tau=224` | Temporary Root Displacement | 0.993370 | -0.030 | -1.00 | -1.3 | +0.2 | +7.8 | +1.3 |
| `tau=224` | Root-Loss | 0.749207 | +0.623 | +10.31 | -7.1 | +0.1 | -5.6 | -15.4 |
| `tau=224` | Local Failure | 0.995431 | +0.230 | -3.37 | +5.2 | +0.8 | +9.3 | -6.1 |

## Mid-band threshold (`T_mid`)

| Setting | Scene | PDR | dPDR (pp) | dDelay (ms) | dRecov (%) | dgate_cmp (%) | dgate_sw (%) | dfallback |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `Tmid=64` | Temporary Root Displacement | 0.992165 | -0.150 | +0.25 | -0.2 | -28.7 | +4.5 | +2.1 |
| `Tmid=64` | Root-Loss | 0.750350 | +0.738 | +48.71 | +1.6 | -21.6 | +5.3 | +10.6 |
| `Tmid=64` | Local Failure | 0.990816 | -0.232 | -3.12 | -0.7 | -22.5 | +62.3 | -7.0 |
| `Tmid=128` | Temporary Root Displacement | 0.994571 | +0.090 | -0.35 | +2.2 | +19.3 | +16.6 | +4.1 |
| `Tmid=128` | Root-Loss | 0.753357 | +1.039 | +31.09 | +6.6 | +10.8 | +6.6 | -4.0 |
| `Tmid=128` | Local Failure | 0.995384 | +0.225 | -4.02 | +5.8 | +9.8 | +30.7 | -8.8 |

## Reserved parent count (`K_reserve`)

| Setting | Scene | PDR | dPDR (pp) | dDelay (ms) | dRecov (%) | dgate_cmp (%) | dgate_sw (%) | dfallback |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `Kreserve=1` | Temporary Root Displacement | 0.992764 | -0.091 | +0.38 | -8.3 | +0.0 | +3.9 | +13.1 |
| `Kreserve=1` | Root-Loss | 0.750723 | +0.775 | -28.57 | -4.2 | -3.3 | +1.4 | +7.3 |
| `Kreserve=1` | Local Failure | 0.995408 | +0.227 | -2.57 | -0.5 | +0.3 | +11.4 | -2.4 |
| `Kreserve=3` | Temporary Root Displacement | 0.992749 | -0.092 | -0.46 | +4.8 | +0.5 | +6.6 | +1.5 |
| `Kreserve=3` | Root-Loss | 0.746294 | +0.332 | -49.64 | +5.6 | +4.7 | +1.1 | +32.0 |
| `Kreserve=3` | Local Failure | 0.995454 | +0.232 | -2.38 | -1.1 | +1.4 | +3.9 | -14.1 |

## Observations

- `tau_strict`: lowering `tau_strict` to `160` makes hard pruning much more aggressive. At `Temporary Root Displacement`, `dgate_cmp` reaches `-73.8%` relative to the default Full configuration, but under `Root-Loss` it also reduces PDR by `-1.458 pp` and increases recovery time by `+10.1%`. Raising it to `224` keeps all three scenes close to the default behavior, indicating that the default `192` already sits in the stable middle range.
- `T_mid`: `T_mid` mainly changes the balance between compression and stability. A lower value (`64`) cuts `gate_cmp` in all three scenes, but it also increases `gate_sw` sharply in `Local-Failure` (`+62.3%`) and adds substantial delay in `Root-Loss` (`+48.71 ms`). A higher value (`128`) weakens filtering and increases `gate_cmp` in all three scenes, especially `Temporary Root Displacement` (`+19.3%`).
- `K_reserve`: changing the reserved-parent count has a milder effect than `tau_strict` or `T_mid`. `K_reserve=1` is slightly more aggressive and keeps `gate_cmp` near or below the default, while `K_reserve=3` weakens compression, especially in `Root-Loss` (`+4.7%`), without producing clear delivery gains. This supports keeping the default value `2`.
