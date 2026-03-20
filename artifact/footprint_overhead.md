# Filter Footprint Overhead

Static firmware size from `TARGET=cooja` builds.
Flash = `text + data`; RAM = `data + bss`.

## rpl-lite

| Target | Baseline Flash | Hard-Only Flash | Full Flash | dFlash Hard | dFlash Full | Baseline RAM | Hard-Only RAM | Full RAM | dRAM Hard | dRAM Full |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| root-node | 291749 | 292505 | 292850 | +756 | +1101 | 124240 | 124272 | 124272 | +32 | +32 |
| sender-node | 292771 | 293527 | 293872 | +756 | +1101 | 124352 | 124384 | 124384 | +32 | +32 |
| receiver-node | 292197 | 292953 | 293298 | +756 | +1101 | 124304 | 124336 | 124336 | +32 | +32 |
| dis-sender | 291399 | 292155 | 292500 | +756 | +1101 | 124192 | 124224 | 124224 | +32 | +32 |

## rpl-classic

| Target | Baseline Flash | Hard-Only Flash | Full Flash | dFlash Hard | dFlash Full | Baseline RAM | Hard-Only RAM | Full RAM | dRAM Hard | dRAM Full |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| root-node | 303490 | 304312 | 304657 | +822 | +1167 | 141472 | 141504 | 141504 | +32 | +32 |
| sender-node | 304480 | 305302 | 305647 | +822 | +1167 | 141552 | 141584 | 141584 | +32 | +32 |
| receiver-node | 304331 | 305153 | 305498 | +822 | +1167 | 141552 | 141584 | 141584 | +32 | +32 |
| dis-sender | 303076 | 303898 | 304243 | +822 | +1167 | 141392 | 141424 | 141424 | +32 | +32 |

