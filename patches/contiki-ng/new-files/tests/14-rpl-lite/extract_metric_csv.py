#!/usr/bin/env python3
import csv
import sys
from collections import defaultdict
from pathlib import Path


def parse_key_value_line(line: str):
    out = {}
    for token in line.strip().split()[1:]:
        if '=' not in token:
            continue
        key, value = token.split('=', 1)
        out[key] = value
    return out


def mean(values):
    return sum(values) / len(values) if values else None


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def collect_metric(testlog_path: Path):
    metric = {}
    test_ok = 0
    try:
        with testlog_path.open(encoding='utf-8', errors='ignore') as fh:
            for line in fh:
                if line.startswith('METRIC '):
                    metric = parse_key_value_line(line)
                elif line.strip() == 'TEST OK':
                    test_ok = 1
    except FileNotFoundError:
        return {}, 0
    return metric, test_ok


def main():
    if len(sys.argv) != 2:
        print('usage: extract_metric_csv.py <results_dir>', file=sys.stderr)
        return 2

    results_dir = Path(sys.argv[1]).resolve()
    input_csv = results_dir / 'paper_matrix_results.csv'
    if not input_csv.exists():
        print(f'missing {input_csv}', file=sys.stderr)
        return 2

    run_out = results_dir / 'metric_runs.csv'
    summary_out = results_dir / 'metric_summary.csv'
    compare_out = results_dir / 'metric_compare.csv'

    rows = list(csv.DictReader(input_csv.open(newline='', encoding='utf-8')))
    metric_fields = set()
    run_rows = []
    grouped = defaultdict(list)

    for row in rows:
        testlog_path = Path(row['script_log_path'])
        metric, test_ok_script = collect_metric(testlog_path)
        out = {
            'platform': row['platform'],
            'group': row['group'],
            'scene': row['scene'],
            'scale': row['scale'],
            'seed': row['seed'],
            'exit_status': row['exit_status'],
            'test_ok': row['test_ok'],
            'test_ok_script': str(test_ok_script),
            'wall_sec': row['wall_sec'],
            'log_path': row['log_path'],
            'script_log_path': row['script_log_path'],
        }
        for key, value in sorted(metric.items()):
            field = f'metric_{key}'
            out[field] = value
            metric_fields.add(field)
        run_rows.append(out)
        grouped[(row['group'], row['scene'], row['scale'])].append(out)

    run_fieldnames = [
        'platform', 'group', 'scene', 'scale', 'seed', 'exit_status', 'test_ok',
        'test_ok_script', 'wall_sec', 'log_path', 'script_log_path',
    ] + sorted(metric_fields)
    with run_out.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=run_fieldnames)
        writer.writeheader()
        writer.writerows(run_rows)

    summary_rows = []
    summary_metric_fields = []
    for key in sorted(grouped):
        items = grouped[key]

        def nums(field):
            vals = []
            for item in items:
                value = item.get(field, '')
                if value != '':
                    vals.append(float(value))
            return vals

        summary = {
            'group': key[0],
            'scene': key[1],
            'scale': key[2],
            'n': str(len(items)),
            'ok_count': str(sum(1 for item in items if item['test_ok'] == '1')),
        }
        wall = nums('wall_sec')
        summary['avg_wall_sec'] = f'{mean(wall):.6f}' if wall else ''

        for field in sorted(metric_fields):
            values = nums(field)
            out_field = f'avg_{field}'
            summary[out_field] = f'{mean(values):.6f}' if values else ''
            if out_field not in summary_metric_fields:
                summary_metric_fields.append(out_field)

        summary_rows.append(summary)

    summary_fields = ['group', 'scene', 'scale', 'n', 'ok_count', 'avg_wall_sec'] + summary_metric_fields
    with summary_out.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(summary_rows)

    summary_map = {(r['group'], r['scene'], r['scale']): r for r in summary_rows}
    compare_rows = []
    compare_metric_fields = []
    for scene in sorted({row['scene'] for row in summary_rows}):
        for scale in sorted({row['scale'] for row in summary_rows}):
            base = summary_map.get(('Baseline', scene, scale))
            full = summary_map.get(('Full', scene, scale))
            if not base or not full:
                continue
            compare = {
                'scene': scene,
                'scale': scale,
                'baseline_avg_wall_sec': base['avg_wall_sec'],
                'full_avg_wall_sec': full['avg_wall_sec'],
            }
            b_wall = to_float(base['avg_wall_sec'])
            f_wall = to_float(full['avg_wall_sec'])
            compare['delta_wall_sec_full_minus_baseline'] = f'{(f_wall - b_wall):.6f}' if b_wall is not None and f_wall is not None else ''
            for field in summary_metric_fields:
                b_val = to_float(base.get(field, ''))
                f_val = to_float(full.get(field, ''))
                compare[f'baseline_{field}'] = base.get(field, '')
                compare[f'full_{field}'] = full.get(field, '')
                compare[f'delta_{field}_full_minus_baseline'] = f'{(f_val - b_val):.6f}' if b_val is not None and f_val is not None else ''
                if field not in compare_metric_fields:
                    compare_metric_fields.append(field)
            compare_rows.append(compare)

    compare_fields = ['scene', 'scale', 'baseline_avg_wall_sec', 'full_avg_wall_sec', 'delta_wall_sec_full_minus_baseline']
    for field in compare_metric_fields:
        compare_fields.extend([f'baseline_{field}', f'full_{field}', f'delta_{field}_full_minus_baseline'])
    with compare_out.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=compare_fields)
        writer.writeheader()
        writer.writerows(compare_rows)

    print(run_out)
    print(summary_out)
    print(compare_out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
