import csv
import os
import re
from collections import defaultdict
from pathlib import Path

BASE = Path(os.environ.get('PAPER_TEST_DIR', str(Path(__file__).resolve().parent)))
CORE = BASE / 'core-results' / 'core_matrix_results.csv'
RUN_OUT = BASE / 'core-results' / 'paper_metrics_runs.csv'
SUM_OUT = BASE / 'core-results' / 'paper_metrics_summary.csv'
CMP_OUT = BASE / 'core-results' / 'paper_metrics_compare.csv'

PAT = re.compile(r"Simulation\.java:450\].*Runtime: ([0-9]+) ms\. Simulated time: ([0-9]+) ms\. Speedup: ([0-9.]+)")

rows = list(csv.DictReader(open(CORE, newline='', encoding='utf-8')))
run_rows = []
cell = defaultdict(list)

for r in rows:
    runtime_ms = None
    sim_ms = None
    speedup = None
    lp = r['log_path']
    try:
        with open(lp, encoding='utf-8', errors='ignore') as f:
            for line in f:
                m = PAT.search(line)
                if m:
                    runtime_ms = int(m.group(1))
                    sim_ms = int(m.group(2))
                    speedup = float(m.group(3))
    except FileNotFoundError:
        pass

    oneh = (3600.0 / speedup) if speedup else None
    out = {
        'group': r['group'],
        'scene': r['scene'],
        'scale': r['scale'],
        'seed': r['seed'],
        'exit_status': r['exit_status'],
        'test_ok': r['test_ok'],
        'wall_sec': r['wall_sec'],
        'sim_runtime_ms': '' if runtime_ms is None else str(runtime_ms),
        'sim_time_ms': '' if sim_ms is None else str(sim_ms),
        'speedup': '' if speedup is None else f'{speedup:.6f}',
        'real_s_per_1h_sim': '' if oneh is None else f'{oneh:.6f}',
    }
    run_rows.append(out)
    cell[(r['group'], r['scene'], r['scale'])].append(out)

with open(RUN_OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(run_rows[0].keys()))
    w.writeheader()
    w.writerows(run_rows)

sum_rows = []
for k in sorted(cell):
    arr = cell[k]
    def nums(field):
        return [float(x[field]) for x in arr if x[field] != '']
    n = len(arr)
    ok = sum(1 for x in arr if x['test_ok'] == '1')
    wall = nums('wall_sec')
    rt = nums('sim_runtime_ms')
    sp = nums('speedup')
    oneh = nums('real_s_per_1h_sim')
    sum_rows.append({
        'group': k[0],
        'scene': k[1],
        'scale': k[2],
        'n': str(n),
        'ok_count': str(ok),
        'ok_rate': f'{ok/n:.6f}',
        'avg_wall_sec': f'{sum(wall)/len(wall):.6f}' if wall else '',
        'avg_sim_runtime_ms': f'{sum(rt)/len(rt):.6f}' if rt else '',
        'avg_speedup': f'{sum(sp)/len(sp):.6f}' if sp else '',
        'avg_real_s_per_1h_sim': f'{sum(oneh)/len(oneh):.6f}' if oneh else '',
    })

with open(SUM_OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(sum_rows[0].keys()))
    w.writeheader()
    w.writerows(sum_rows)

m = {(r['group'], r['scene'], r['scale']): r for r in sum_rows}
cmp_rows = []
for scene in sorted(set(r['scene'] for r in sum_rows)):
    for scale in sorted(set(r['scale'] for r in sum_rows)):
        b = m.get(('baseline', scene, scale))
        e = m.get(('experiment', scene, scale))
        if not b or not e:
            continue
        def f(v):
            return float(v) if v != '' else None
        b_ok, e_ok = f(b['ok_rate']), f(e['ok_rate'])
        b_wall, e_wall = f(b['avg_wall_sec']), f(e['avg_wall_sec'])
        b_sp, e_sp = f(b['avg_speedup']), f(e['avg_speedup'])
        b_1h, e_1h = f(b['avg_real_s_per_1h_sim']), f(e['avg_real_s_per_1h_sim'])
        cmp_rows.append({
            'scene': scene,
            'scale': scale,
            'baseline_ok_rate': b['ok_rate'],
            'experiment_ok_rate': e['ok_rate'],
            'ok_rate_delta_exp_minus_base': f'{(e_ok-b_ok):.6f}' if b_ok is not None and e_ok is not None else '',
            'baseline_avg_wall_sec': b['avg_wall_sec'],
            'experiment_avg_wall_sec': e['avg_wall_sec'],
            'wall_delta_sec_exp_minus_base': f'{(e_wall-b_wall):.6f}' if b_wall is not None and e_wall is not None else '',
            'baseline_avg_speedup': b['avg_speedup'],
            'experiment_avg_speedup': e['avg_speedup'],
            'speedup_delta_exp_minus_base': f'{(e_sp-b_sp):.6f}' if b_sp is not None and e_sp is not None else '',
            'baseline_real_s_per_1h_sim': b['avg_real_s_per_1h_sim'],
            'experiment_real_s_per_1h_sim': e['avg_real_s_per_1h_sim'],
            'real_s_per_1h_delta_exp_minus_base': f'{(e_1h-b_1h):.6f}' if b_1h is not None and e_1h is not None else '',
        })

with open(CMP_OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(cmp_rows[0].keys()))
    w.writeheader()
    w.writerows(cmp_rows)

print('OK')
print(RUN_OUT)
print(SUM_OUT)
print(CMP_OUT)
