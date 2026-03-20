from pathlib import Path
import csv
import math
import itertools
import sys

LOWER_BETTER = {
    'metric_lost', 'metric_avg_delay_ms', 'metric_avg_hops', 'metric_recov_ms',
    'metric_dio', 'metric_dao', 'metric_dis', 'metric_gate_cmp', 'metric_gate_sw',
    'metric_gate_fallback', 'metric_gate_hard_cur', 'metric_gate_frozen_cur',
    'metric_conv_ms', 'metric_p95_delay_ms', 'metric_jitter_ms'
}
HIGHER_BETTER = {
    'metric_pdr', 'metric_recv'
}
DISPLAY = {
    'metric_lost': 'lost',
    'metric_pdr': 'pdr',
    'metric_avg_delay_ms': 'avg_delay_ms',
    'metric_avg_hops': 'avg_hops',
    'metric_recov_ms': 'recov_ms',
    'metric_dio': 'dio',
    'metric_dao': 'dao',
    'metric_dis': 'dis',
    'metric_gate_cmp': 'gate_cmp',
    'metric_gate_sw': 'gate_sw',
    'metric_gate_fallback': 'gate_fallback',
    'metric_gate_hard_cur': 'gate_hard_cur',
    'metric_gate_frozen_cur': 'gate_frozen_cur',
}
MAIN_METRICS = [
    'metric_lost','metric_pdr','metric_avg_delay_ms','metric_avg_hops','metric_recov_ms',
    'metric_dio','metric_dao','metric_dis','metric_gate_cmp','metric_gate_sw','metric_gate_fallback'
]
ABLATION_METRICS = MAIN_METRICS + ['metric_gate_hard_cur','metric_gate_frozen_cur']
CLASSIC_METRICS = MAIN_METRICS


def parse_float(s):
    try:
        return float(s)
    except Exception:
        return None


def exact_signflip_pvalue(diffs):
    vals = [d for d in diffs if abs(d) > 1e-12]
    n = len(vals)
    if n == 0:
        return 1.0
    total = 1 << n
    obs = abs(sum(vals))
    extreme = 0
    for mask in range(total):
        s = 0.0
        for i, d in enumerate(vals):
            s += d if ((mask >> i) & 1) else -d
        if abs(s) >= obs - 1e-12:
            extreme += 1
    return extreme / total


def mean(xs):
    return sum(xs) / len(xs) if xs else float('nan')


def sample_std(xs):
    n = len(xs)
    if n < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def ci95(xs):
    n = len(xs)
    if n == 0:
        return float('nan')
    if n == 1:
        return 0.0
    return 1.96 * sample_std(xs) / math.sqrt(n)


def format_ms(v):
    return 'NA' if v is None or math.isnan(v) else f'{v:.6f}'


def rel_improvement(base_vals, cand_vals, metric):
    b = mean(base_vals)
    c = mean(cand_vals)
    if abs(b) < 1e-12:
        return float('nan')
    if metric in LOWER_BETTER:
        return (b - c) / abs(b) * 100.0
    if metric in HIGHER_BETTER:
        return (c - b) / abs(b) * 100.0
    return float('nan')


def load_rows(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def filter_valid(rows):
    out = []
    for r in rows:
        if r.get('test_ok') != '1':
            continue
        grp = r.get('group', '')
        gate_on = r.get('metric_gate_on', '')
        if grp != 'Baseline' and grp != 'Hard-Only' and gate_on not in ('1', '1.0'):
            continue
        out.append(r)
    return out


def pair_rows(rows, groups):
    by_group = {g: {} for g in groups}
    for r in rows:
        g = r['group']
        if g not in by_group:
            continue
        key = (r['scene'], r['scale'], r['seed'])
        by_group[g][key] = r
    common = set.intersection(*(set(m.keys()) for m in by_group.values()))
    return by_group, sorted(common)


def metric_values(by_group, keys, group, metric):
    vals = []
    for k in keys:
        v = parse_float(by_group[group][k].get(metric, ''))
        if v is None:
            continue
        if metric == 'metric_recov_ms' and v < 0:
            continue
        vals.append((k, v))
    return vals


def compare(rows, ref_group, cand_group, metrics):
    by_group, common = pair_rows(rows, [ref_group, cand_group])
    grouped = {}
    for scene, scale, _ in common:
        grouped.setdefault((scene, scale), []).append((scene, scale))
    results = []
    seen = sorted(set((scene, scale) for scene, scale, _ in common), key=lambda x: (x[0], int(x[1])))
    for scene, scale in seen:
        scene_keys = [k for k in common if k[0] == scene and k[1] == scale]
        for metric in metrics:
            ref_pairs = metric_values(by_group, scene_keys, ref_group, metric)
            cand_pairs = metric_values(by_group, scene_keys, cand_group, metric)
            ref_map = dict(ref_pairs)
            cand_map = dict(cand_pairs)
            keys2 = sorted(set(ref_map) & set(cand_map))
            ref_vals = [ref_map[k] for k in keys2]
            cand_vals = [cand_map[k] for k in keys2]
            diffs = [cand_map[k] - ref_map[k] for k in keys2]
            p = exact_signflip_pvalue(diffs) if keys2 else float('nan')
            results.append({
                'scene': scene,
                'scale': scale,
                'ref_group': ref_group,
                'cand_group': cand_group,
                'metric': DISPLAY.get(metric, metric),
                'n_pairs': len(keys2),
                'ref_mean': mean(ref_vals) if ref_vals else float('nan'),
                'ref_std': sample_std(ref_vals) if ref_vals else float('nan'),
                'ref_ci95': ci95(ref_vals) if ref_vals else float('nan'),
                'cand_mean': mean(cand_vals) if cand_vals else float('nan'),
                'cand_std': sample_std(cand_vals) if cand_vals else float('nan'),
                'cand_ci95': ci95(cand_vals) if cand_vals else float('nan'),
                'delta_mean': mean(diffs) if diffs else float('nan'),
                'delta_std': sample_std(diffs) if diffs else float('nan'),
                'delta_ci95': ci95(diffs) if diffs else float('nan'),
                'rel_impr_pct': rel_improvement(ref_vals, cand_vals, metric) if ref_vals and cand_vals else float('nan'),
                'p_value': p,
            })
    return results


def write_csv(path, rows):
    if not rows:
        return
    fields = list(rows[0].keys())
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def fmt(v, digits=6):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return 'NA'
    return f'{v:.{digits}f}'


def write_md(path, title, rows):
    sections = {}
    for r in rows:
        sections.setdefault((r['ref_group'], r['cand_group'], r['scene'], r['scale']), []).append(r)
    lines = [f'# {title}', '', '??? seed ??????????????exact sign-flip randomization test??', '']
    for key in sorted(sections.keys(), key=lambda x: (x[0], x[1], x[2], int(x[3]))):
        ref_group, cand_group, scene, scale = key
        lines.append(f'## {ref_group} vs {cand_group} | {scene} {scale}')
        lines.append('')
        lines.append('| Metric | n | Ref mean?std | Cand mean?std | Delta mean | Rel improvement % | p-value |')
        lines.append('|---|---:|---:|---:|---:|---:|---:|')
        for r in sections[key]:
            lines.append(
                f"| {r['metric']} | {r['n_pairs']} | {fmt(r['ref_mean'])} ? {fmt(r['ref_std'])} | {fmt(r['cand_mean'])} ? {fmt(r['cand_std'])} | {fmt(r['delta_mean'])} | {fmt(r['rel_impr_pct'], 2)} | {fmt(r['p_value'], 6)} |"
            )
        lines.append('')
    Path(path).write_text('\n'.join(lines), encoding='utf-8')


def main(argv):
    if len(argv) != 4:
        raise SystemExit('usage: stat_significance.py <mode> <input_metric_runs.csv> <out_prefix>')
    mode, input_csv, out_prefix = argv[1], argv[2], argv[3]
    rows = filter_valid(load_rows(input_csv))
    results = []
    if mode == 'main':
        results.extend(compare(rows, 'Baseline', 'Full', MAIN_METRICS))
        title = 'P-Value Summary: Main Experiments'
    elif mode == 'ablation':
        # Compare only on overlapping seeds.
        results.extend(compare(rows, 'Baseline', 'Hard-Only', ABLATION_METRICS))
        # mix Full rows from main if provided in merged CSV; otherwise caller should merge externally.
        title = 'P-Value Summary: Ablation'
    elif mode == 'classic':
        results.extend(compare(rows, 'Baseline', 'Full', CLASSIC_METRICS))
        title = 'P-Value Summary: rpl-classic Generalization'
    else:
        raise SystemExit(f'unknown mode: {mode}')
    out_csv = out_prefix + '.csv'
    out_md = out_prefix + '.md'
    write_csv(out_csv, results)
    write_md(out_md, title, results)
    print(out_csv)
    print(out_md)

if __name__ == '__main__':
    main(sys.argv)
