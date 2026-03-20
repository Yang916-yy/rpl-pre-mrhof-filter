# Results Appendix

This file consolidates the detailed result tables that were previously split across multiple `formal_*.md` files. Source data are regenerated from the original experiment CSV files, not copied from the older markdown snapshots.

## Static Footprint Overhead

The table below summarizes the static ROM/RAM overhead of the filter itself. Flash is `text + data`; RAM is `data + bss`. The deltas are stable across the measured node roles, so only the implementation-level increments are listed here.

| Implementation | Hard-Only dFlash | Full dFlash | Hard-Only dRAM | Full dRAM |
|---|---:|---:|---:|---:|
| rpl-lite | +756 B | +1101 B | +32 B | +32 B |
| rpl-classic | +822 B | +1167 B | +32 B | +32 B |

## Exploratory Local Interference Corridor (20 seeds)

The table below summarizes the two exploratory 20-seed corridor configurations. Both settings produce large `gate_cmp` reductions, but neither yet yields a disturbance benchmark that is simultaneously stable, fair, and repeatable across scales.

| Setting | Scale | Baseline PDR | Full PDR | dPDR (pp) | dLost | dDelay (ms) | dRecov (ms) | dgate_cmp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| strong20 | 40 | 0.997990 | 0.997867 | -0.0123 | +0.0196 | -1.885 | -2307.291 | -4495022 |
| strong20 | 60 | 0.998795 | 0.998488 | -0.0307 | +0.0500 | -1.792 | -7159.600 | -8761833 |
| tuned20 | 40 | 0.999738 | 0.999095 | -0.0643 | +0.0630 | -0.599 | +4899.118 | -4497973 |
| tuned20 | 60 | 0.999396 | 0.998644 | -0.0752 | +0.1250 | -1.352 | +8410.560 | -8774663 |

## rpl-lite Main: Baseline vs Full

### Disturbance | 20

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 2.050000 | 1.400000 | -0.650000 |
| PDR | 0.987644 | 0.991544 | 0.003900 |
| Delay (ms) | 48.589 | 40.649 | -7.940050 |
| Hops | 1.952650 | 1.632600 | -0.320050 |
| Recov (ms) | 152216.0 | 148192.8 | -4023.2 |
| DIO | 3036.6 | 3023.7 | -12.900 |
| DAO | 126.70 | 119.35 | -7.350000 |
| DIS | 0.050000 | 0.100000 | 0.050000 |
| gate_cmp | 1205699.1 | 357145.8 | -848553.3 |
| gate_sw | 29.900 | 24.200 | -5.700000 |
| gate_fallback | 0.000000 | 6.100000 | 6.100000 |
| gate_hard_cur | 0.000000 | 223.00 | 223.00 |
| gate_frozen_cur | 0.000000 | 1.050000 | 1.050000 |

### Disturbance | 40

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 1.900000 | 1.050000 | -0.850000 |
| PDR | 0.988533 | 0.993669 | 0.005136 |
| Delay (ms) | 48.655 | 39.487 | -9.168550 |
| Hops | 1.994700 | 1.596200 | -0.398500 |
| Recov (ms) | 147165.1 | 144213.9 | -2951.2 |
| DIO | 6265.2 | 6244.3 | -20.950 |
| DAO | 275.70 | 256.45 | -19.250 |
| DIS | 5.100000 | 5.100000 | 0.000000 |
| gate_cmp | 6583944.8 | 2068341.3 | -4515603.5 |
| gate_sw | 86.350 | 69.400 | -16.950 |
| gate_fallback | 0.000000 | 8.700000 | 8.700000 |
| gate_hard_cur | 0.000000 | 725.35 | 725.35 |
| gate_frozen_cur | 0.000000 | 2.050000 | 2.050000 |

### Disturbance | 60

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 1.900000 | 1.000000 | -0.900000 |
| PDR | 0.988540 | 0.993963 | 0.005423 |
| Delay (ms) | 48.564 | 41.892 | -6.672350 |
| Hops | 1.993400 | 1.726500 | -0.266900 |
| Recov (ms) | 145180.8 | 141229.2 | -3951.6 |
| DIO | 9484.3 | 9440.5 | -43.800 |
| DAO | 426.90 | 408.95 | -17.950 |
| DIS | 14.000 | 13.950 | -0.050000 |
| gate_cmp | 13171878.6 | 4373084.2 | -8798794.3 |
| gate_sw | 154.55 | 135.35 | -19.200 |
| gate_fallback | 0.000000 | 8.350000 | 8.350000 |
| gate_hard_cur | 0.000000 | 1235.0 | 1235.0 |
| gate_frozen_cur | 0.000000 | 3.000000 | 3.000000 |

### Root-Loss | 20

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 15.850 | 16.100 | 0.250000 |
| PDR | 0.759079 | 0.754883 | -0.004196 |
| Delay (ms) | 183.33 | 187.30 | 3.976450 |
| Hops | 9.819400 | 10.118 | 0.298900 |
| Recov (ms) | 195032.1 | 205713.1 | 10680.9 |
| DIO | 3722.7 | 3032.8 | -689.95 |
| DAO | 371.05 | 340.20 | -30.850 |
| DIS | 512.95 | 548.65 | 35.700 |
| gate_cmp | 437653.7 | 125267.6 | -312386.1 |
| gate_sw | 740.85 | 593.15 | -147.70 |
| gate_fallback | 0.000000 | 161.70 | 161.70 |
| gate_hard_cur | 0.000000 | 110.00 | 110.00 |
| gate_frozen_cur | 0.000000 | 9.300000 | 9.300000 |

### Root-Loss | 40

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 16.600 | 16.900 | 0.300000 |
| PDR | 0.746900 | 0.742972 | -0.003928 |
| Delay (ms) | 188.14 | 191.38 | 3.243800 |
| Hops | 11.269 | 11.542 | 0.272800 |
| Recov (ms) | 192965.5 | 194400.7 | 1435.2 |
| DIO | 5917.4 | 5775.4 | -142.00 |
| DAO | 1040.0 | 989.25 | -50.700 |
| DIS | 1059.2 | 1114.0 | 54.850 |
| gate_cmp | 2024301.2 | 739669.1 | -1284632.1 |
| gate_sw | 909.05 | 928.40 | 19.350 |
| gate_fallback | 0.000000 | 495.40 | 495.40 |
| gate_hard_cur | 0.000000 | 493.00 | 493.00 |
| gate_frozen_cur | 0.000000 | 17.700 | 17.700 |

### Root-Loss | 60

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 16.950 | 17.050 | 0.100000 |
| PDR | 0.742016 | 0.740093 | -0.001923 |
| Delay (ms) | 224.87 | 125.97 | -98.901 |
| Hops | 16.196 | 6.030900 | -10.165 |
| Recov (ms) | 193222.0 | 190097.9 | -3124.2 |
| DIO | 9983.0 | 10189.2 | 206.20 |
| DAO | 2524.9 | 2241.2 | -283.75 |
| DIS | 1418.9 | 1511.7 | 92.800 |
| gate_cmp | 7565466.5 | 2955683.4 | -4609783.0 |
| gate_sw | 1667.0 | 1675.8 | 8.800000 |
| gate_fallback | 0.000000 | 863.45 | 863.45 |
| gate_hard_cur | 0.000000 | 1173.0 | 1173.0 |
| gate_frozen_cur | 0.000000 | 38.900 | 38.900 |

### Stable | 20

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 0.400000 | 0.400000 | 0.000000 |
| PDR | 0.974583 | 0.974583 | 0.000000 |
| Delay (ms) | 193.71 | 193.71 | 0.000000 |
| Hops | 7.664150 | 7.664150 | 0.000000 |
| Recov (ms) | -1.000000 | -1.000000 | 0.000000 |
| DIO | 466.90 | 466.90 | 0.000000 |
| DAO | 19.200 | 19.200 | 0.000000 |
| DIS | 21.600 | 21.600 | 0.000000 |
| gate_cmp | 27960.5 | 11285.6 | -16675.0 |
| gate_sw | 19.200 | 19.200 | 0.000000 |
| gate_fallback | 0.000000 | 0.000000 | 0.000000 |
| gate_hard_cur | 0.000000 | 71.000 | 71.000 |
| gate_frozen_cur | 0.000000 | 0.000000 | 0.000000 |

### Stable | 40

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 0.200000 | 0.150000 | -0.050000 |
| PDR | 0.987500 | 0.990625 | 0.003125 |
| Delay (ms) | 151.69 | 152.60 | 0.912300 |
| Hops | 6.071850 | 6.094850 | 0.023000 |
| Recov (ms) | -1.000000 | -1.000000 | 0.000000 |
| DIO | 974.15 | 974.05 | -0.100000 |
| DAO | 41.850 | 41.400 | -0.450000 |
| DIS | 25.250 | 25.200 | -0.050000 |
| gate_cmp | 299256.3 | 122652.1 | -176604.2 |
| gate_sw | 41.850 | 41.400 | -0.450000 |
| gate_fallback | 0.000000 | 0.000000 | 0.000000 |
| gate_hard_cur | 0.000000 | 374.00 | 374.00 |
| gate_frozen_cur | 0.000000 | 0.000000 | 0.000000 |

### Stable | 60

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 0.050000 | 0.050000 | 0.000000 |
| PDR | 0.996875 | 0.996875 | 0.000000 |
| Delay (ms) | 153.60 | 152.92 | -0.682250 |
| Hops | 6.148400 | 6.138450 | -0.009950 |
| Recov (ms) | -1.000000 | -1.000000 | 0.000000 |
| DIO | 1486.3 | 1488.5 | 2.100000 |
| DAO | 62.950 | 63.250 | 0.300000 |
| DIS | 32.750 | 32.900 | 0.150000 |
| gate_cmp | 1241061.3 | 550530.9 | -690530.4 |
| gate_sw | 62.900 | 63.150 | 0.250000 |
| gate_fallback | 0.000000 | 0.000000 | 0.000000 |
| gate_hard_cur | 0.000000 | 919.00 | 919.00 |
| gate_frozen_cur | 0.000000 | 0.000000 | 0.000000 |

## rpl-lite Local-Failure: Baseline vs Full

### Local Failure | 20

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 0.950000 | 0.650000 | -0.300000 |
| PDR | 0.985583 | 0.990116 | 0.004533 |
| Delay (ms) | 120.13 | 119.90 | -0.234600 |
| Hops | 4.775750 | 4.773350 | -0.002400 |
| Recov (ms) | 151143.5 | 150573.6 | -569.95 |
| DIO | 1705.5 | 1670.8 | -34.750 |
| DAO | 145.25 | 144.45 | -0.800000 |
| DIS | 80.050 | 91.800 | 11.750 |
| gate_cmp | 229574.3 | 98161.0 | -131413.3 |
| gate_sw | 301.20 | 279.75 | -21.450 |
| gate_fallback | 0.000000 | 27.700 | 27.700 |
| gate_hard_cur | 0.000000 | 110.00 | 110.00 |
| gate_frozen_cur | 0.000000 | 7.350000 | 7.350000 |

### Local Failure | 40

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 0.850000 | 0.450000 | -0.400000 |
| PDR | 0.987063 | 0.993135 | 0.006072 |
| Delay (ms) | 124.06 | 124.79 | 0.726350 |
| Hops | 4.990600 | 4.991400 | 0.000800 |
| Recov (ms) | 149413.2 | 154278.3 | 4865.1 |
| DIO | 3148.4 | 3044.1 | -104.35 |
| DAO | 192.55 | 181.75 | -10.800 |
| DIS | 119.55 | 141.45 | 21.900 |
| gate_cmp | 1779447.6 | 708180.8 | -1071266.8 |
| gate_sw | 259.15 | 181.10 | -78.050 |
| gate_fallback | 0.000000 | 34.650 | 34.650 |
| gate_hard_cur | 0.000000 | 493.00 | 493.00 |
| gate_frozen_cur | 0.000000 | 9.450000 | 9.450000 |

### Local Failure | 60

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 2.000000 | 1.150000 | -0.850000 |
| PDR | 0.969580 | 0.982505 | 0.012925 |
| Delay (ms) | 121.25 | 121.35 | 0.099450 |
| Hops | 4.899500 | 4.899650 | 0.000150 |
| Recov (ms) | 151132.5 | 152299.9 | 1167.4 |
| DIO | 4664.9 | 4641.7 | -23.200 |
| DAO | 252.80 | 263.95 | 11.150 |
| DIS | 110.85 | 129.00 | 18.150 |
| gate_cmp | 6899858.4 | 2936204.0 | -3963654.5 |
| gate_sw | 265.40 | 286.80 | 21.400 |
| gate_fallback | 0.000000 | 30.250 | 30.250 |
| gate_hard_cur | 0.000000 | 1173.0 | 1173.0 |
| gate_frozen_cur | 0.000000 | 8.450000 | 8.450000 |

## rpl-lite Ablation: Baseline vs Hard-Only vs Full

### Disturbance | 20

| Metric | Baseline | Hard-Only | Full |
|---|---:|---:|---:|
| Lost |  | 2.000000 |  |
| PDR |  | 0.987923 |  |
| Delay (ms) |  | 48.721 |  |
| Hops |  | 1.954100 |  |
| Recov (ms) |  | 135216.6 |  |
| DIO |  | 3030.4 |  |
| DAO |  | 121.90 |  |
| DIS |  | 0.100000 |  |
| gate_cmp |  | 363121.5 |  |
| gate_sw |  | 25.700 |  |
| gate_fallback |  | 0.000000 |  |

### Disturbance | 40

| Metric | Baseline | Hard-Only | Full |
|---|---:|---:|---:|
| Lost |  | 2.000000 |  |
| PDR |  | 0.987930 |  |
| Delay (ms) |  | 48.545 |  |
| Hops |  | 1.985600 |  |
| Recov (ms) |  | 157228.6 |  |
| DIO |  | 6227.9 |  |
| DAO |  | 257.90 |  |
| DIS |  | 5.300000 |  |
| gate_cmp |  | 2085861.1 |  |
| gate_sw |  | 69.800 |  |
| gate_fallback |  | 0.000000 |  |

### Root-Loss | 20

| Metric | Baseline | Hard-Only | Full |
|---|---:|---:|---:|
| Lost |  | 15.100 |  |
| PDR |  | 0.769720 |  |
| Delay (ms) |  | 132.07 |  |
| Hops |  | 5.761900 |  |
| Recov (ms) |  | 186623.6 |  |
| DIO |  | 3076.3 |  |
| DAO |  | 312.60 |  |
| DIS |  | 498.60 |  |
| gate_cmp |  | 136476.4 |  |
| gate_sw |  | 528.20 |  |
| gate_fallback |  | 0.000000 |  |

### Root-Loss | 40

| Metric | Baseline | Hard-Only | Full |
|---|---:|---:|---:|
| Lost |  | 16.100 |  |
| PDR |  | 0.754895 |  |
| Delay (ms) |  | 192.31 |  |
| Hops |  | 11.998 |  |
| Recov (ms) |  | 193981.8 |  |
| DIO |  | 5835.9 |  |
| DAO |  | 957.30 |  |
| DIS |  | 1081.3 |  |
| gate_cmp |  | 786674.1 |  |
| gate_sw |  | 907.20 |  |
| gate_fallback |  | 0.000000 |  |

## rpl-lite Local-Failure Ablation: Baseline vs Hard-Only vs Full

### Local Failure | 20

| Metric | Baseline | Hard-Only | Full |
|---|---:|---:|---:|
| Lost |  | 1.000000 |  |
| PDR |  | 0.984709 |  |
| Delay (ms) |  | 111.81 |  |
| Hops |  | 4.527600 |  |
| Recov (ms) |  | 153175.3 |  |
| DIO |  | 1688.7 |  |
| DAO |  | 140.30 |  |
| DIS |  | 88.100 |  |
| gate_cmp |  | 103884.8 |  |
| gate_sw |  | 272.70 |  |
| gate_fallback |  | 0.000000 |  |

### Local Failure | 40

| Metric | Baseline | Hard-Only | Full |
|---|---:|---:|---:|
| Lost |  | 0.500000 |  |
| PDR |  | 0.992354 |  |
| Delay (ms) |  | 122.48 |  |
| Hops |  | 4.878100 |  |
| Recov (ms) |  | 173078.1 |  |
| DIO |  | 3163.7 |  |
| DAO |  | 210.70 |  |
| DIS |  | 117.30 |  |
| gate_cmp |  | 725531.8 |  |
| gate_sw |  | 300.30 |  |
| gate_fallback |  | 0.000000 |  |

### Local Failure | 60

| Metric | Baseline | Hard-Only | Full |
|---|---:|---:|---:|
| Lost |  | 2.000000 |  |
| PDR |  | 0.969604 |  |
| Delay (ms) |  | 122.56 |  |
| Hops |  | 4.920000 |  |
| Recov (ms) |  | 174109.8 |  |
| DIO |  | 4676.8 |  |
| DAO |  | 266.30 |  |
| DIS |  | 106.90 |  |
| gate_cmp |  | 2970368.2 |  |
| gate_sw |  | 289.70 |  |
| gate_fallback |  | 0.000000 |  |

## rpl-classic Generalization: Baseline vs Full

### Root-Loss | 20

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 40.500 | 47.400 | 6.900000 |
| PDR | 0.381212 | 0.277622 | -0.103590 |
| Delay (ms) | 108.63 | 114.68 | 6.042300 |
| Hops | 4.437800 | 4.734500 | 0.296700 |
| Recov (ms) | 1398798.9 | 326655.1 | -1072143.8 |
| DIO | 7361.9 | 9124.7 | 1762.8 |
| DAO | 922.60 | 6880.6 | 5958.0 |
| DIS | 736.70 | 833.00 | 96.300 |
| gate_cmp | 144657.9 | 156179.8 | 11521.9 |
| gate_sw | 530.10 | 5570.2 | 5040.1 |
| gate_fallback | 0.000000 | 111.70 | 111.70 |
| gate_hard_cur | 0.000000 | 107.70 | 107.70 |
| gate_frozen_cur | 0.000000 | 5.600000 | 5.600000 |

### Root-Loss | 40

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 40.800 | 44.300 | 3.500000 |
| PDR | 0.378858 | 0.323566 | -0.055292 |
| Delay (ms) | 120.18 | 135.20 | 15.021 |
| Hops | 4.918800 | 5.609100 | 0.690300 |
| Recov (ms) | 1446554.1 | 643281.5 | -803272.6 |
| DIO | 13670.6 | 18016.8 | 4346.2 |
| DAO | 3291.5 | 17512.7 | 14221.2 |
| DIS | 1412.5 | 1428.4 | 15.900 |
| gate_cmp | 1319064.1 | 1360443.0 | 41378.9 |
| gate_sw | 1881.7 | 13389.8 | 11508.1 |
| gate_fallback | 0.000000 | 344.60 | 344.60 |
| gate_hard_cur | 0.000000 | 490.20 | 490.20 |
| gate_frozen_cur | 0.000000 | 13.100 | 13.100 |

### Temporary Root Displacement | 20

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 3.400000 | 1.300000 | -2.100000 |
| PDR | 0.979482 | 0.992143 | 0.012661 |
| Delay (ms) | 49.353 | 49.144 | -0.209600 |
| Hops | 1.957500 | 1.952700 | -0.004800 |
| Recov (ms) | 145745.5 | 145417.8 | -327.70 |
| DIO | 4280.8 | 4287.6 | 6.800000 |
| DAO | 467.40 | 481.70 | 14.300 |
| DIS | 5.600000 | 5.100000 | -0.500000 |
| gate_cmp | 593379.5 | 144047.9 | -449331.6 |
| gate_sw | 191.40 | 212.50 | 21.100 |
| gate_fallback | 0.000000 | 40.700 | 40.700 |
| gate_hard_cur | 0.000000 | 223.00 | 223.00 |
| gate_frozen_cur | 0.000000 | 2.100000 | 2.100000 |

### Temporary Root Displacement | 40

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 2.900000 | 1.200000 | -1.700000 |
| PDR | 0.982519 | 0.992753 | 0.010234 |
| Delay (ms) | 48.625 | 48.553 | -0.071800 |
| Hops | 1.972300 | 1.984200 | 0.011900 |
| Recov (ms) | 145902.8 | 164362.3 | 18459.5 |
| DIO | 8598.5 | 8615.6 | 17.100 |
| DAO | 958.20 | 964.60 | 6.400000 |
| DIS | 16.100 | 15.600 | -0.500000 |
| gate_cmp | 2784839.4 | 825554.2 | -1959285.2 |
| gate_sw | 294.10 | 344.70 | 50.600 |
| gate_fallback | 0.000000 | 101.30 | 101.30 |
| gate_hard_cur | 0.000000 | 726.00 | 726.00 |
| gate_frozen_cur | 0.000000 | 10.700 | 10.700 |

## rpl-classic Local-Failure Generalization: Baseline vs Full

### Local Failure | 20

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 0.400000 | 0.400000 | 0.000000 |
| PDR | 0.993893 | 0.993893 | 0.000000 |
| Delay (ms) | 124.63 | 124.82 | 0.193300 |
| Hops | 4.966000 | 4.967600 | 0.001600 |
| Recov (ms) | 140775.7 | 157752.7 | 16977.0 |
| DIO | 2365.8 | 3256.7 | 890.90 |
| DAO | 385.90 | 330.70 | -55.200 |
| DIS | 60.400 | 71.800 | 11.400 |
| gate_cmp | 167760.7 | 126030.8 | -41729.9 |
| gate_sw | 154.90 | 134.80 | -20.100 |
| gate_fallback | 0.000000 | 1436.1 | 1436.1 |
| gate_hard_cur | 0.000000 | 110.00 | 110.00 |
| gate_frozen_cur | 0.000000 | 12.000 | 12.000 |

### Local Failure | 40

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 0.500000 | 0.400000 | -0.100000 |
| PDR | 0.992354 | 0.993916 | 0.001562 |
| Delay (ms) | 121.75 | 127.25 | 5.509100 |
| Hops | 4.920600 | 5.117800 | 0.197200 |
| Recov (ms) | 142859.2 | 142683.5 | -175.70 |
| DIO | 4345.2 | 4986.9 | 641.70 |
| DAO | 864.00 | 705.00 | -159.00 |
| DIS | 74.200 | 98.000 | 23.800 |
| gate_cmp | 1044048.3 | 583888.8 | -460159.5 |
| gate_sw | 376.80 | 306.40 | -70.400 |
| gate_fallback | 0.000000 | 1011.2 | 1011.2 |
| gate_hard_cur | 0.000000 | 493.00 | 493.00 |
| gate_frozen_cur | 0.000000 | 34.800 | 34.800 |

### Local Failure | 60

| Metric | Baseline | Full | Delta (F-B) |
|---|---:|---:|---:|
| Lost | 1.900000 | 1.200000 | -0.700000 |
| PDR | 0.971072 | 0.981771 | 0.010699 |
| Delay (ms) | 121.29 | 117.24 | -4.050700 |
| Hops | 4.967600 | 4.829000 | -0.138600 |
| Recov (ms) | 155549.0 | 154964.9 | -584.10 |
| DIO | 6212.4 | 7332.8 | 1120.4 |
| DAO | 1358.2 | 1074.6 | -283.60 |
| DIS | 62.400 | 121.90 | 59.500 |
| gate_cmp | 3591330.0 | 2463873.8 | -1127456.2 |
| gate_sw | 581.10 | 448.90 | -132.20 |
| gate_fallback | 0.000000 | 585.90 | 585.90 |
| gate_hard_cur | 0.000000 | 1173.0 | 1173.0 |
| gate_frozen_cur | 0.000000 | 41.400 | 41.400 |

