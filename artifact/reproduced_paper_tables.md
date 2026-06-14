## Main results: Full relative to Baseline

| Scenario | Nodes | Delta PDR (pp) | Delta comparisons (%) | Delta switches (%) |
|---|---:|---:|---:|---:|
| Stable | 20 | +0.000 | -59.637 | +0.000 |
| Stable | 40 | +0.312 | -59.014 | -1.075 |
| Stable | 60 | +0.000 | -55.640 | +0.397 |
| Temporary Root Displacement | 20 | +0.390 | -70.379 | -19.064 |
| Temporary Root Displacement | 40 | +0.514 | -68.585 | -19.629 |
| Temporary Root Displacement | 60 | +0.542 | -66.800 | -12.423 |
| Root-Loss | 20 | -0.420 | -71.377 | -19.937 |
| Root-Loss | 40 | -0.393 | -63.461 | +2.129 |
| Root-Loss | 60 | -0.192 | -60.932 | +0.528 |
| Local Failure | 20 | +0.453 | -57.242 | -7.122 |
| Local Failure | 40 | +0.607 | -60.202 | -30.118 |
| Local Failure | 60 | +1.292 | -57.445 | +8.063 |

## Forty-node ablation

| Scenario | Baseline PDR (%) | Hard PDR (%) | Full PDR (%) | Hard/Full comparison delta (%) | Hard/Full switches |
|---|---:|---:|---:|---:|---:|
| Temporary Root Displacement | 98.85 | 98.79 | 99.37 | -68.3/-68.6 | 69.8/69.4 |
| Root-Loss | 74.69 | 75.49 | 74.30 | -61.1/-63.5 | 907.2/928.4 |
| Local Failure | 98.71 | 99.24 | 99.31 | -59.2/-60.2 | 300.3/181.1 |

## Coordinate-error robustness at 40 nodes

| Error | Delta PDR range (pp) | Delta comparisons range (%) | Delta switches range (%) |
|---:|---:|---:|---:|
| 5% | [-0.002, +0.304] | [+0.1, +5.8] | [+1.7, +4.2] |
| 10% | [-0.091, +0.550] | [+2.1, +10.7] | [-7.2, +13.8] |
| 20% | [-0.062, +0.170] | [+7.7, +20.7] | [+3.1, +64.1] |
| 30% | [-0.150, +0.147] | [+13.3, +30.8] | [-0.5, +20.3] |

## Filter gain over Squared-ETX at 40 nodes

| Scenario | Delta PDR (pp) | Delta comparisons (%) | Delta switches (%) |
|---|---:|---:|---:|
| Temporary Root Displacement | -0.030 | -65.963 | -17.386 |
| Root-Loss | -0.190 | -56.870 | +10.054 |
| Local Failure | -0.077 | -53.597 | +3.392 |
