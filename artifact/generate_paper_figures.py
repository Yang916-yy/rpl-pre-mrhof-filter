
import re
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

ARTIFACT_ROOT = Path(os.environ.get('PAPER_ARTIFACT_ROOT', str(Path(__file__).resolve().parent)))
CONTIKI_NG_ROOT = Path(os.environ.get('CONTIKI_NG_WIN_ROOT', ''))
ROOT = ARTIFACT_ROOT
OUT = Path(os.environ.get('PAPER_FIG_OUT', str(ROOT / 'figures')))
OUT.mkdir(exist_ok=True)
PARAM_SENS = ROOT / 'param_sensitivity_summary.csv'

def save_figure(fig, basename, **kwargs):
    fig.savefig(OUT / f'{basename}.pdf', **kwargs)
    fig.savefig(OUT / f'{basename}.png', dpi=240, **kwargs)

matplotlib.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 9,
})

LITE_MAIN = Path(os.environ.get('PAPER_LITE_MAIN_COMPARE', str(CONTIKI_NG_ROOT / 'tests' / '14-rpl-lite' / 'paper-results-main' / 'metric_compare.csv')))
LITE_LOCAL = Path(os.environ.get('PAPER_LITE_LOCAL_COMPARE', str(CONTIKI_NG_ROOT / 'tests' / '14-rpl-lite' / 'paper-results-local-failure' / 'metric_compare.csv')))
CLASSIC_MAIN = Path(os.environ.get('PAPER_CLASSIC_MAIN_COMPARE', str(CONTIKI_NG_ROOT / 'tests' / '15-rpl-classic' / 'paper-results-generalization' / 'metric_compare.csv')))
CLASSIC_LOCAL = Path(os.environ.get('PAPER_CLASSIC_LOCAL_COMPARE', str(CONTIKI_NG_ROOT / 'tests' / '15-rpl-classic' / 'paper-results-generalization-localfail' / 'metric_compare.csv')))
LOCALFAIL_CSC = Path(os.environ.get('PAPER_LOCALFAIL_CSC', str(CONTIKI_NG_ROOT / 'tests' / '14-rpl-paper' / 'generated' / 's5_local_failure_40.csc')))

SCENE_LABELS = {
    'Stable': 'Stable',
    'Disturbance': 'Root Displacement',
    'Root-Loss': 'Root Loss',
    'Local Failure': 'Local Failure',
}
SCALES = [20, 40, 60]


def cmp_reduction(df):
    return 100.0 * (df['baseline_avg_metric_gate_cmp'] - df['full_avg_metric_gate_cmp']) / df['baseline_avg_metric_gate_cmp']


def pdr_gain_pp(df):
    return 100.0 * (df['full_avg_metric_pdr'] - df['baseline_avg_metric_pdr'])


def read_df(path):
    df = pd.read_csv(path)
    df['cmp_reduction_pct'] = cmp_reduction(df)
    df['pdr_baseline_pct'] = 100.0 * df['baseline_avg_metric_pdr']
    df['pdr_full_pct'] = 100.0 * df['full_avg_metric_pdr']
    df['pdr_gain_pp'] = pdr_gain_pp(df)
    return df


def make_lite_core_results():
    df = pd.concat([read_df(LITE_MAIN), read_df(LITE_LOCAL)], ignore_index=True)
    ordered_scenes = ['Stable', 'Disturbance', 'Root-Loss', 'Local Failure']
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 7.8), constrained_layout=True)
    axes = axes.ravel()

    for idx, (ax, scene) in enumerate(zip(axes, ordered_scenes)):
        sub = df[df['scene'] == scene].sort_values('scale')
        x = range(len(sub))
        ax2 = ax.twinx()
        # Keep the PDR axis above the reduction bars from the twin axis.
        ax.set_zorder(ax2.get_zorder() + 1)
        ax.patch.set_alpha(0.0)
        ax.plot(x, sub['pdr_baseline_pct'], marker='o', linewidth=2.0, color='#1f4e79', label='Baseline PDR', zorder=5)
        ax.plot(x, sub['pdr_full_pct'], marker='s', linewidth=2.0, color='#c0392b', label='Full PDR', zorder=5)
        bars = ax2.bar(x, sub['cmp_reduction_pct'], width=0.42, color='#c9d7e8', edgecolor='#6c8ebf', label='gate_cmp reduction', zorder=1)
        ax.set_title(SCENE_LABELS[scene])
        ax.set_xticks(list(x), [str(v) for v in sub['scale']])
        ax.set_xlabel('Network size')
        ax.set_ylabel('PDR (%)')
        ax2.set_ylabel('gate_cmp reduction (%)')
        ax.set_ylim(70, 101)
        ax2.set_ylim(0, 100)
        ax.grid(True, axis='y', linestyle='--', linewidth=0.6, alpha=0.5)
        # Avoid the central column becoming unreadable in the 2x2 layout.
        if idx % 2 == 0:
            ax2.set_ylabel('')
            ax2.tick_params(axis='y', right=False, labelright=False)
        else:
            ax.set_ylabel('')
            ax.tick_params(axis='y', left=False, labelleft=False)
        for rect, val in zip(bars, sub['cmp_reduction_pct']):
            ax2.text(
                rect.get_x() + rect.get_width()/2,
                rect.get_height() + 1.0,
                f'{val:.0f}%',
                ha='center',
                va='bottom',
                fontsize=8,
                zorder=6,
                bbox=dict(facecolor='white', edgecolor='none', pad=0.2, alpha=0.9),
            )

    # Rebuild the legend explicitly; do not create extra twin axes here.
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    legend_items = [
        Line2D([0], [0], color='#1f4e79', marker='o', linewidth=2.0, label='Baseline PDR'),
        Line2D([0], [0], color='#c0392b', marker='s', linewidth=2.0, label='Full PDR'),
        Patch(facecolor='#c9d7e8', edgecolor='#6c8ebf', label='gate_cmp reduction'),
    ]
    fig.legend(handles=legend_items, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle('rpl-lite: core results across four formal scenarios', y=1.05, fontsize=13)
    save_figure(fig, 'fig1_rpl_lite_core_results', bbox_inches='tight')
    plt.close(fig)


def parse_local_failure_topology(csc_path):
    text = csc_path.read_text(encoding='utf-8')
    root = ET.fromstring(text)
    positions = {}
    current_pos = None
    for mote in root.iter('mote'):
        mid = None
        pos = None
        for iface in mote.findall('interface_config'):
            txt = (iface.text or '').strip()
            if 'Position' in txt:
                p = iface.find('pos')
                if p is not None:
                    pos = (float(p.attrib['x']), float(p.attrib['y']))
            elif 'ContikiMoteID' in txt:
                i = iface.find('id')
                if i is not None:
                    mid = int(i.text)
        if mid is not None and pos is not None:
            positions[mid] = pos
    tr_match = re.search(r'<transmitting_range>([0-9.]+)</transmitting_range>', text)
    tx_range = float(tr_match.group(1)) if tr_match else 50.0
    ids_match = re.search(r'var localFailIds = \[([^\]]+)\];', text)
    fail_ids = [int(x.strip()) for x in ids_match.group(1).split(',')] if ids_match else []
    shift_match = re.search(r'var localFailShift = \{([^;]+)\};', text)
    fail_shift = {}
    if shift_match:
        entries = re.findall(r'"(\d+)":\[([0-9.\-]+),([0-9.\-]+)\]', shift_match.group(1))
        for mid, x, y in entries:
            fail_shift[int(mid)] = (float(x), float(y))
    return positions, tx_range, fail_ids, fail_shift


def make_local_failure_topology():
    positions, tx_range, fail_ids, fail_shift = parse_local_failure_topology(LOCALFAIL_CSC)
    root_id, sender_id = 3, 2
    fig, ax = plt.subplots(figsize=(8.8, 6.4), constrained_layout=True)

    ids = sorted(positions)
    for i, a in enumerate(ids):
        xa, ya = positions[a]
        for b in ids[i+1:]:
            xb, yb = positions[b]
            d = math.hypot(xa - xb, ya - yb)
            if d <= tx_range:
                ax.plot([xa, xb], [ya, yb], color='#d9d9d9', linewidth=0.45, zorder=1)

    normal_ids = [mid for mid in ids if mid not in fail_ids and mid not in (root_id, sender_id)]
    ax.scatter([positions[i][0] for i in normal_ids], [positions[i][1] for i in normal_ids], s=28, color='#5b8db8', alpha=0.9, label='Normal nodes', zorder=3)
    ax.scatter([positions[root_id][0]], [positions[root_id][1]], s=180, marker='*', color='#2e8b57', edgecolor='black', linewidth=0.6, label='Root', zorder=5)
    ax.scatter([positions[sender_id][0]], [positions[sender_id][1]], s=90, marker='s', color='#d97a00', edgecolor='black', linewidth=0.6, label='Sender', zorder=5)
    ax.scatter([positions[i][0] for i in fail_ids], [positions[i][1] for i in fail_ids], s=110, marker='o', facecolor='#d62728', edgecolor='black', linewidth=0.6, label='Failed relays', zorder=6)

    for mid in fail_ids:
        x0, y0 = positions[mid]
        x1, y1 = fail_shift[mid]
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle='->', color='#7f7f7f', lw=1.0, linestyle='--'), zorder=4)
        ax.scatter([x1], [y1], s=70, marker='x', color='#7f7f7f', linewidth=1.6, zorder=7)
        ax.text(x0 + 3, y0 + 3, str(mid), fontsize=8, color='#333333')

    ax.plot([positions[root_id][0], positions[sender_id][0]], [positions[root_id][1], positions[sender_id][1]], linestyle=':', color='#444444', linewidth=1.0, zorder=2)
    ax.set_title('Local-Failure topology (40 nodes) and displaced relay set')
    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')
    ax.set_aspect('equal', adjustable='box')
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.35)
    ax.legend(loc='upper left', frameon=False)
    save_figure(fig, 'fig2_local_failure_topology', bbox_inches='tight')
    plt.close(fig)


def make_transferability():
    lite_main = read_df(LITE_MAIN)
    lite_local = read_df(LITE_LOCAL)
    classic_main = read_df(CLASSIC_MAIN)
    classic_local = read_df(CLASSIC_LOCAL)

    lite = pd.concat([
        lite_main[lite_main['scene'].isin(['Disturbance', 'Temporary Root Displacement'])].assign(platform='rpl-lite', scene_label='Root Displacement'),
        lite_local.assign(platform='rpl-lite', scene_label='Local Failure'),
    ], ignore_index=True)
    classic = pd.concat([
        classic_main[classic_main['scene'].isin(['Disturbance', 'Temporary Root Displacement'])].assign(platform='rpl-classic', scene_label='Root Displacement'),
        classic_local.assign(platform='rpl-classic', scene_label='Local Failure'),
    ], ignore_index=True)
    df = pd.concat([lite, classic], ignore_index=True)

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.3), constrained_layout=True)
    for ax, scene_label in zip(axes, ['Root Displacement', 'Local Failure']):
        sub = df[df['scene_label'] == scene_label].sort_values(['scale','platform'])
        scales = sorted(sub['scale'].unique())
        xpos = {s: i for i, s in enumerate(scales)}
        x = list(range(len(scales)))
        width = 0.18
        ax2 = ax.twinx()
        for idx, platform in enumerate(['rpl-lite', 'rpl-classic']):
            subp = sub[sub['platform'] == platform].sort_values('scale')
            xsub = [xpos[s] for s in subp['scale']]
            shift = (-0.5 + idx) * width * 1.6
            color = '#c0392b' if platform == 'rpl-lite' else '#6a3d9a'
            edge = '#7f1d1d' if platform == 'rpl-lite' else '#3b1f54'
            ax.bar([i + shift for i in xsub], subp['pdr_gain_pp'], width=width, color=color, edgecolor=edge, alpha=0.82, label=f'{platform} dPDR' if scene_label == 'Root Displacement' else None)
            ax2.plot([i + shift for i in xsub], subp['cmp_reduction_pct'], marker='o' if platform == 'rpl-lite' else 's', linewidth=2.0, color=color, linestyle='--', label=f'{platform} gate_cmp reduction' if scene_label == 'Root Displacement' else None)
        ax.axhline(0, color='#555555', linewidth=0.8)
        ax.set_xticks(x, [str(s) for s in scales])
        ax.set_xlabel('Network size')
        ax.set_ylabel('dPDR (percentage points)')
        ax2.set_ylabel('gate_cmp reduction (%)')
        ax.set_title(scene_label)
        ax.grid(True, axis='y', linestyle='--', linewidth=0.5, alpha=0.4)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    legend_items = [
        Patch(facecolor='#c0392b', edgecolor='#7f1d1d', label='rpl-lite dPDR'),
        Patch(facecolor='#6a3d9a', edgecolor='#3b1f54', label='rpl-classic dPDR'),
        Line2D([0], [0], color='#c0392b', marker='o', linestyle='--', linewidth=2.0, label='rpl-lite gate_cmp reduction'),
        Line2D([0], [0], color='#6a3d9a', marker='s', linestyle='--', linewidth=2.0, label='rpl-classic gate_cmp reduction'),
    ]
    fig.legend(handles=legend_items, loc='upper center', ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.03))
    fig.suptitle('Transferability of the filtering policy across implementations', y=1.08, fontsize=13)
    save_figure(fig, 'fig3_transferability', bbox_inches='tight')
    plt.close(fig)


def parse_packet_progress(log_path, on_marker, off_marker):
    lines = Path(log_path).read_text(encoding='utf-8', errors='ignore').splitlines()
    seq_pat = re.compile(r'^\d+\s+([*_]+)$')
    current_bitmap = ''
    event_on = None
    event_off = None
    for line in lines:
        m = seq_pat.match(line.strip())
        if m:
            current_bitmap = m.group(1)
            continue
        if on_marker in line and event_on is None:
            event_on = len(current_bitmap)
        if off_marker in line and event_off is None:
            event_off = len(current_bitmap)
    final_bitmap = current_bitmap
    recv_idx = [i+1 for i,c in enumerate(final_bitmap) if c == '*']
    lost_idx = [i+1 for i,c in enumerate(final_bitmap) if c == '_']
    cum_recv = []
    total = 0
    for c in final_bitmap:
        if c == '*':
            total += 1
        cum_recv.append(total)
    return {
        'bitmap': final_bitmap,
        'recv_idx': recv_idx,
        'lost_idx': lost_idx,
        'cum_recv': cum_recv,
        'event_on': event_on,
        'event_off': event_off,
    }


def make_recovery_process_examples():
    examples = [
        {
            'title': 'Temporary Root Displacement (40 nodes, seed 1)',
            'baseline': Path(os.environ.get('PAPER_RECOVERY_EXAMPLE_BASELINE_DISTURB', str(CONTIKI_NG_ROOT / 'tests' / '14-rpl-lite' / 'paper-results-main' / 'logs' / 'baseline_s2_disturb_40_seed1.testlog'))),
            'full': Path(os.environ.get('PAPER_RECOVERY_EXAMPLE_FULL_DISTURB', str(CONTIKI_NG_ROOT / 'tests' / '14-rpl-lite' / 'paper-results-main' / 'logs' / 'full_s2_disturb_40_seed1.testlog'))),
            'on': 'moving root 2 hops away',
            'off': 'moving root back',
        },
        {
            'title': 'Local Failure (40 nodes, seed 10)',
            'baseline': Path(os.environ.get('PAPER_RECOVERY_EXAMPLE_BASELINE_LOCALFAIL', str(CONTIKI_NG_ROOT / 'tests' / '14-rpl-lite' / 'paper-results-local-failure' / 'logs' / 'baseline_s5_local_failure_40_seed10.testlog'))),
            'full': Path(os.environ.get('PAPER_RECOVERY_EXAMPLE_FULL_LOCALFAIL', str(CONTIKI_NG_ROOT / 'tests' / '14-rpl-lite' / 'paper-results-local-failure' / 'logs' / 'full_s5_local_failure_40_seed10.testlog'))),
            'on': 'local failure on',
            'off': 'local failure off',
        },
    ]

    fig, axes = plt.subplots(2, 2, figsize=(11.2, 7.2), constrained_layout=True)
    for col, ex in enumerate(examples):
        b = parse_packet_progress(ex['baseline'], ex['on'], ex['off'])
        f = parse_packet_progress(ex['full'], ex['on'], ex['off'])
        max_n = max(len(b['bitmap']), len(f['bitmap']))

        ax = axes[0, col]
        for y, data, label, color in [(1, b, 'Baseline', '#1f4e79'), (0, f, 'Full', '#c0392b')]:
            if data['recv_idx']:
                ax.scatter(data['recv_idx'], [y]*len(data['recv_idx']), s=16, color=color, marker='s', label=label if y==1 else None, zorder=3)
            if data['lost_idx']:
                ax.scatter(data['lost_idx'], [y]*len(data['lost_idx']), s=26, color='#111111', marker='x', linewidth=1.1, zorder=4)
        on = min(v for v in [b['event_on'], f['event_on']] if v is not None)
        off = min(v for v in [b['event_off'], f['event_off']] if v is not None)
        ax.axvspan(on, off, color='#d9d9d9', alpha=0.5, zorder=1)
        ax.set_xlim(1, max_n)
        ax.set_ylim(-0.6, 1.6)
        ax.set_yticks([0,1], ['Full', 'Baseline'])
        ax.set_xlabel('Packet index')
        ax.set_title(ex['title'])
        ax.set_ylabel('Reception status')
        ax.grid(True, axis='x', linestyle='--', linewidth=0.4, alpha=0.35)
        ax.text((on+off)/2, 1.45, 'event window', ha='center', va='center', fontsize=9, color='#444444')

        ax2 = axes[1, col]
        ax2.plot(range(1, len(b['cum_recv'])+1), b['cum_recv'], color='#1f4e79', linewidth=2.0, label='Baseline')
        ax2.plot(range(1, len(f['cum_recv'])+1), f['cum_recv'], color='#c0392b', linewidth=2.0, label='Full')
        ax2.axvspan(on, off, color='#d9d9d9', alpha=0.5, zorder=1)
        ax2.set_xlim(1, max_n)
        ax2.set_xlabel('Packet index')
        ax2.set_ylabel('Cumulative received packets')
        ax2.grid(True, linestyle='--', linewidth=0.5, alpha=0.4)

    handles = [
        plt.Line2D([0],[0], marker='s', color='#1f4e79', linestyle='None', markersize=6, label='Baseline received'),
        plt.Line2D([0],[0], marker='s', color='#c0392b', linestyle='None', markersize=6, label='Full received'),
        plt.Line2D([0],[0], marker='x', color='#111111', linestyle='None', markersize=6, label='Lost packet'),
    ]
    fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle('Recovery trajectories after disturbance: representative packet-sequence views', y=1.06, fontsize=13)
    save_figure(fig, 'fig4_recovery_process_examples', bbox_inches='tight')
    plt.close(fig)




def build_prior_tree(positions, root_id, tx_range, hop_penalty_q8=32):
    ids = sorted(positions)
    adj = {i: [] for i in ids}
    for src in ids:
        x1, y1 = positions[src]
        for dst in ids:
            if src == dst:
                continue
            x2, y2 = positions[dst]
            dist = math.hypot(x2 - x1, y2 - y1)
            if dist <= tx_range + 1e-9:
                geom_q8 = int(round((dist / tx_range) * 256.0))
                w = geom_q8 + hop_penalty_q8
                adj[src].append((dst, w))
    import heapq
    d = {i: 10**18 for i in ids}
    parent = {root_id: None}
    d[root_id] = 0
    pq = [(0, root_id)]
    while pq:
        cd, u = heapq.heappop(pq)
        if cd != d[u]:
            continue
        for v, w in adj[u]:
            nd = cd + w
            if nd < d[v]:
                d[v] = nd
                parent[v] = u
                heapq.heappush(pq, (nd, v))
    return d, parent, adj


def draw_comm_graph(ax, positions, tx_range, color='#d9d9d9', lw=0.45):
    ids = sorted(positions)
    for i, a in enumerate(ids):
        xa, ya = positions[a]
        for b in ids[i+1:]:
            xb, yb = positions[b]
            if math.hypot(xa-xb, ya-yb) <= tx_range + 1e-9:
                ax.plot([xa, xb], [ya, yb], color=color, linewidth=lw, zorder=1)


def draw_tree(ax, positions, parent, root_id, color, label=None, lw=2.1):
    first = True
    for child, par in parent.items():
        if child == root_id or par is None:
            continue
        x0, y0 = positions[child]
        x1, y1 = positions[par]
        ax.plot([x0, x1], [y0, y1], color=color, linewidth=lw, alpha=0.95, zorder=3, label=(label if first else None))
        first = False


def sender_route(parent, sender_id, root_id):
    route = [sender_id]
    cur = sender_id
    seen = {cur}
    while cur != root_id and cur in parent and parent[cur] is not None and parent[cur] not in seen:
        cur = parent[cur]
        route.append(cur)
        seen.add(cur)
    return route


def draw_route(ax, positions, route, color, label=None, lw=3.8):
    first = True
    for a, b in zip(route[:-1], route[1:]):
        ax.plot([positions[a][0], positions[b][0]], [positions[a][1], positions[b][1]], color=color, linewidth=lw, zorder=4, label=(label if first else None))
        first = False


def make_structural_local_failure_view():
    positions, tx_range, fail_ids, fail_shift = parse_local_failure_topology(LOCALFAIL_CSC)
    root_id, sender_id = 3, 2
    d0, parent0, _ = build_prior_tree(positions, root_id, tx_range)
    route0 = sender_route(parent0, sender_id, root_id)
    fail_positions = dict(positions)
    for mid in fail_ids:
        fail_positions[mid] = fail_shift[mid]
    d1, parent1, _ = build_prior_tree(fail_positions, root_id, tx_range)
    route1 = sender_route(parent1, sender_id, root_id)

    fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.6), constrained_layout=True)
    panels = [
        ('Before local failure', axes[0], positions, parent0, route0, False),
        ('During local failure', axes[1], fail_positions, parent1, route1, True),
    ]
    for title, ax, pos, parent, route, failing in panels:
        draw_comm_graph(ax, pos, tx_range)
        draw_tree(ax, pos, parent, root_id, color='#7aa6d1', label='Prior backbone')
        draw_route(ax, pos, route, color='#c0392b', label='Sender-root route')
        normal_ids = [i for i in pos if i not in (root_id, sender_id) and (not failing or i not in fail_ids)]
        ax.scatter([pos[i][0] for i in normal_ids], [pos[i][1] for i in normal_ids], s=24, color='#5b8db8', zorder=5)
        ax.scatter([pos[root_id][0]], [pos[root_id][1]], s=180, marker='*', color='#2e8b57', edgecolor='black', linewidth=0.6, zorder=7)
        ax.scatter([pos[sender_id][0]], [pos[sender_id][1]], s=90, marker='s', color='#d97a00', edgecolor='black', linewidth=0.6, zorder=7)
        if failing:
            ax.scatter([pos[i][0] for i in fail_ids], [pos[i][1] for i in fail_ids], s=110, marker='o', facecolor='#d62728', edgecolor='black', linewidth=0.6, zorder=8, label='Failed relays')
        else:
            ax.scatter([pos[i][0] for i in fail_ids], [pos[i][1] for i in fail_ids], s=90, marker='o', facecolor='#f4a3a3', edgecolor='black', linewidth=0.5, zorder=6, label='Relays to be failed')
        for mid in fail_ids:
            x, y = pos[mid]
            ax.text(x + 2.5, y + 2.5, str(mid), fontsize=7.5, color='#333333')
        ax.set_title(title)
        ax.set_xlabel('X coordinate')
        ax.set_ylabel('Y coordinate')
        ax.set_aspect('equal', adjustable='box')
        ax.grid(True, linestyle='--', linewidth=0.45, alpha=0.35)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    legend_items = [
        Line2D([0],[0], color='#7aa6d1', linewidth=2.1, label='Prior backbone'),
        Line2D([0],[0], color='#c0392b', linewidth=3.8, label='Sender-root route'),
        Line2D([0],[0], marker='*', color='w', markerfacecolor='#2e8b57', markeredgecolor='black', markersize=12, linestyle='None', label='Root'),
        Line2D([0],[0], marker='s', color='w', markerfacecolor='#d97a00', markeredgecolor='black', markersize=8, linestyle='None', label='Sender'),
        Line2D([0],[0], marker='o', color='w', markerfacecolor='#d62728', markeredgecolor='black', markersize=8, linestyle='None', label='Failed relay set'),
    ]
    fig.legend(handles=legend_items, loc='upper center', ncol=5, frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle('Node/link-level structural view of Local-Failure and prior-guided rerouting', y=1.07, fontsize=13)
    save_figure(fig, 'fig5_local_failure_structure', bbox_inches='tight')
    plt.close(fig)




def compute_prior_from_original(positions, root_id, tx_range, hop_penalty_q8=32):
    ids = sorted(positions)
    struct = {}
    adj = {i: [] for i in ids}
    for src in ids:
        x1, y1 = positions[src]
        for dst in ids:
            if src == dst:
                continue
            x2, y2 = positions[dst]
            dist = math.hypot(x2 - x1, y2 - y1)
            if dist <= tx_range + 1e-9:
                geom_q8 = int(round((dist / tx_range) * 256.0))
                w = geom_q8 + hop_penalty_q8
                struct[(src, dst)] = w
                adj[src].append((dst, w))
    import heapq
    d = {i: 10**18 for i in ids}
    d[root_id] = 0
    pq = [(0, root_id)]
    while pq:
        cd, u = heapq.heappop(pq)
        if cd != d[u]:
            continue
        for v, w in adj[u]:
            nd = cd + w
            if nd < d[v]:
                d[v] = nd
                heapq.heappush(pq, (nd, v))
    return d, struct


def full_retained_candidate_links(original_positions, active_positions, root_id, tx_range, t_mid_q8=96, strict_tau_q8=192):
    d, struct = compute_prior_from_original(original_positions, root_id, tx_range)
    ids = sorted(active_positions)
    candidates = []
    child_best = {}
    for a in ids:
        xa, ya = active_positions[a]
        for b in ids:
            if a == b:
                continue
            xb, yb = active_positions[b]
            if math.hypot(xa-xb, ya-yb) > tx_range + 1e-9:
                continue
            if a not in d or b not in d:
                continue
            struct_cost = struct.get((a, b), 0)
            prior_valid = ((a, b) in struct)
            progress = d[a] - d[b]
            path_proxy = d[b] + struct_cost if prior_valid else 10**18
            geo_slack = max(0, path_proxy - d[a]) if prior_valid else 0
            candidates.append({'child': a, 'parent': b, 'prior_valid': prior_valid, 'progress': progress, 'path_proxy': path_proxy, 'geo_slack': geo_slack})
            if prior_valid and progress > 0:
                child_best[a] = min(child_best.get(a, 10**18), path_proxy)
    retained = set()
    pruned = set()
    for c in candidates:
        child = c['child']; parent = c['parent']
        hard = False
        if c['prior_valid']:
            if c['progress'] <= 0:
                hard = True
            elif c['geo_slack'] > strict_tau_q8:
                hard = True
            elif child_best.get(child, 10**18) != 10**18 and c['path_proxy'] > child_best[child] + t_mid_q8:
                hard = True
        # use undirected representation for farther->nearer direction only
        if d.get(child, 10**18) > d.get(parent, 10**18):
            edge = tuple(sorted((child, parent)))
            if hard:
                pruned.add(edge)
            else:
                retained.add(edge)
    pruned -= retained
    return retained, pruned




def make_baseline_vs_full_linkspace():
    positions, tx_range, fail_ids, fail_shift = parse_local_failure_topology(LOCALFAIL_CSC)
    root_id, sender_id = 3, 2

    # Use original positions as the main canvas. Failed relays are shown as removed,
    # instead of plotting their far-away displaced coordinates, to keep the visual focus
    # on the affected routing corridor.
    active_for_links = dict(positions)
    for mid in fail_ids:
        active_for_links[mid] = fail_shift[mid]

    retained, pruned = full_retained_candidate_links(positions, active_for_links, root_id, tx_range)
    d0, parent0, _ = build_prior_tree(positions, root_id, tx_range)
    route0 = sender_route(parent0, sender_id, root_id)

    # Failure-time route is reconstructed on the active topology, but rendered back onto
    # the original corridor by omitting the displaced coordinates from the main view.
    d1, parent1, _ = build_prior_tree(active_for_links, root_id, tx_range)
    route1 = sender_route(parent1, sender_id, root_id)

    ids = sorted(positions)
    baseline_edges = set()
    for i, a in enumerate(ids):
        xa, ya = positions[a]
        for b in ids[i+1:]:
            xb, yb = positions[b]
            if math.hypot(xa-xb, ya-yb) <= tx_range + 1e-9:
                # Only keep edges around the main corridor and failure neighborhood.
                baseline_edges.add((a, b))

    relevant = set(fail_ids) | set(route0) | set(route1) | {root_id, sender_id}
    for n in ids:
        pn = positions[n]
        if any(math.hypot(pn[0] - positions[f][0], pn[1] - positions[f][1]) <= tx_range * 1.15 for f in fail_ids):
            relevant.add(n)
        if any(math.hypot(pn[0] - positions[r][0], pn[1] - positions[r][1]) <= tx_range * 0.9 for r in route0):
            relevant.add(n)

    def filter_edges(edges):
        out = set()
        for a, b in edges:
            if a in relevant and b in relevant:
                out.add((a, b))
        return out

    baseline_edges = filter_edges(baseline_edges)
    retained_edges = filter_edges(retained)
    pruned_edges = filter_edges(pruned)

    xs = [positions[n][0] for n in relevant]
    ys = [positions[n][1] for n in relevant]
    xspan = max(xs) - min(xs)
    yspan = max(ys) - min(ys)
    pad_x = max(14.0, 0.10 * xspan)
    pad_y = max(14.0, 0.10 * yspan)
    xmin, xmax = min(xs) - pad_x, max(xs) + pad_x
    ymin, ymax = min(ys) - pad_y, max(ys) + pad_y

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 5.1), constrained_layout=False)
    fig.subplots_adjust(top=0.79, bottom=0.10, left=0.05, right=0.985, wspace=0.04)

    def draw_nodes(ax):
        normal_ids = [i for i in relevant if i not in (root_id, sender_id) and i not in fail_ids]
        ax.scatter([positions[i][0] for i in normal_ids], [positions[i][1] for i in normal_ids], s=42, color='#5b8db8', zorder=4)
        ax.scatter([positions[root_id][0]], [positions[root_id][1]], s=230, marker='*', color='#2e8b57', edgecolor='black', linewidth=0.8, zorder=6)
        ax.scatter([positions[sender_id][0]], [positions[sender_id][1]], s=120, marker='s', color='#d97a00', edgecolor='black', linewidth=0.8, zorder=6)
        ax.scatter([positions[i][0] for i in fail_ids], [positions[i][1] for i in fail_ids], s=160, marker='o', facecolor='#ffffff', edgecolor='#d62728', linewidth=1.8, zorder=7)
        ax.scatter([positions[i][0] for i in fail_ids], [positions[i][1] for i in fail_ids], s=190, marker='x', color='#d62728', linewidth=2.0, zorder=8)
        for mid in fail_ids:
            x, y = positions[mid]
            ax.text(x + 1.5, y + 1.5, str(mid), fontsize=8.5, color='#222222', zorder=8)
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_aspect('equal', adjustable='box')
        ax.grid(False)
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticks([])
        ax.set_yticks([])

    def draw_edge_set(ax, edges, color, lw, alpha=0.9, ls='-'):
        for a, b in edges:
            ax.plot([positions[a][0], positions[b][0]], [positions[a][1], positions[b][1]], color=color, linewidth=lw, alpha=alpha, linestyle=ls, zorder=2)

    # Panel 1: baseline space
    ax = axes[0]
    draw_edge_set(ax, baseline_edges, '#9fbcd6', 1.6, 0.85)
    draw_nodes(ax)
    draw_route(ax, positions, [n for n in route0 if n in positions], color='#444444', label=None, lw=2.4)
    ax.set_title('Baseline space')
    ax.text(0.03, 0.95, f'candidate links: {len(baseline_edges)}', transform=ax.transAxes, fontsize=9.3, ha='left', va='top', bbox=dict(facecolor='white', edgecolor='none', alpha=0.86, pad=1.4))

    # Panel 2: difference map
    ax = axes[1]
    draw_edge_set(ax, retained_edges, '#4c78a8', 2.0, 0.98)
    draw_edge_set(ax, pruned_edges, '#d62728', 1.7, 0.9, '--')
    draw_nodes(ax)
    draw_route(ax, positions, [n for n in route0 if n in positions], color='#666666', label=None, lw=2.1)
    visible_route1 = [n for n in route1 if n in positions]
    if len(visible_route1) >= 2:
        draw_route(ax, positions, visible_route1, color='#f39c12', label=None, lw=3.1)
    ax.set_title('Difference map')
    ax.text(0.03, 0.95, f'pruned: {len(pruned_edges)}\nretained: {len(retained_edges)}', transform=ax.transAxes, fontsize=9.3, ha='left', va='top', bbox=dict(facecolor='white', edgecolor='none', alpha=0.86, pad=1.4))

    from matplotlib.lines import Line2D
    legend_items = [
        Line2D([0],[0], color='#9fbcd6', linewidth=1.6, label='Baseline candidate link'),
        Line2D([0],[0], color='#4c78a8', linewidth=2.0, label='Full retained link'),
        Line2D([0],[0], color='#d62728', linewidth=1.7, linestyle='--', label='Pruned by Full'),
        Line2D([0],[0], color='#666666', linewidth=2.1, label='Pre-failure route'),
        Line2D([0],[0], color='#f39c12', linewidth=3.1, label='Failure-time route'),
        Line2D([0],[0], marker='x', color='#d62728', markersize=9, linestyle='None', label='Failed relay'),
    ]
    fig.legend(handles=legend_items, loc='upper center', ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.96))
    fig.suptitle('Local-Failure (40 nodes): candidate-space difference between Baseline and Full', y=0.995, fontsize=12.4)
    save_figure(fig, 'fig6_baseline_vs_full_linkspace', bbox_inches='tight')
    plt.close(fig)




def parse_basic_topology(csc_path):
    text = Path(csc_path).read_text(encoding='utf-8')
    root = ET.fromstring(text)
    sim = root.find('simulation')
    tx_range = float(sim.find('radiomedium').findtext('transmitting_range'))
    positions = {}
    for mote in root.iter('mote'):
        mid = None
        pos = None
        for iface in mote.findall('interface_config'):
            t = (iface.text or '').strip()
            if 'Position' in t:
                p = iface.find('pos')
                if p is not None:
                    pos = (float(p.attrib['x']), float(p.attrib['y']))
            elif 'ContikiMoteID' in t:
                i = iface.find('id')
                if i is not None:
                    mid = int(i.text)
        if mid is not None and pos is not None:
            positions[mid] = pos
    return positions, tx_range



def make_stable_linkspace_comparison():
    stable_csc = Path(os.environ.get('PAPER_STABLE_CSC', str(CONTIKI_NG_ROOT / 'tests' / '14-rpl-paper' / 'generated' / 's1_stable_40.csc')))
    positions, tx_range = parse_basic_topology(stable_csc)
    root_id, sender_id = 3, 2

    retained, pruned = full_retained_candidate_links(positions, positions, root_id, tx_range)
    d0, parent0, _ = build_prior_tree(positions, root_id, tx_range)
    route0 = sender_route(parent0, sender_id, root_id)

    ids = sorted(positions)
    baseline_edges = set()
    for i, a in enumerate(ids):
        xa, ya = positions[a]
        for b in ids[i+1:]:
            xb, yb = positions[b]
            if math.hypot(xa-xb, ya-yb) <= tx_range + 1e-9:
                baseline_edges.add((a, b))

    relevant = set(route0) | {root_id, sender_id}
    for n in ids:
        pn = positions[n]
        if any(math.hypot(pn[0] - positions[r][0], pn[1] - positions[r][1]) <= tx_range * 0.9 for r in route0):
            relevant.add(n)

    def filter_edges(edges):
        return {(a, b) for a, b in edges if a in relevant and b in relevant}

    baseline_edges = filter_edges(baseline_edges)
    retained_edges = filter_edges(retained)
    pruned_edges = filter_edges(pruned)

    xs = [positions[n][0] for n in relevant]
    ys = [positions[n][1] for n in relevant]
    xspan = max(xs) - min(xs)
    yspan = max(ys) - min(ys)
    pad_x = max(14.0, 0.10 * xspan)
    pad_y = max(14.0, 0.10 * yspan)
    xmin, xmax = min(xs) - pad_x, max(xs) + pad_x
    ymin, ymax = min(ys) - pad_y, max(ys) + pad_y

    fig, axes = plt.subplots(1, 2, figsize=(10.4, 5.1), constrained_layout=False)
    fig.subplots_adjust(top=0.79, bottom=0.10, left=0.05, right=0.985, wspace=0.04)

    def draw_nodes(ax):
        normal_ids = [i for i in relevant if i not in (root_id, sender_id)]
        ax.scatter([positions[i][0] for i in normal_ids], [positions[i][1] for i in normal_ids], s=38, color='#5b8db8', zorder=4)
        ax.scatter([positions[root_id][0]], [positions[root_id][1]], s=195, marker='*', color='#2e8b57', edgecolor='black', linewidth=0.7, zorder=6)
        ax.scatter([positions[sender_id][0]], [positions[sender_id][1]], s=105, marker='s', color='#d97a00', edgecolor='black', linewidth=0.7, zorder=6)
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_aspect('equal', adjustable='box')
        ax.grid(False)
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticks([])
        ax.set_yticks([])

    def draw_edge_set(ax, edges, color, lw, alpha=0.9, ls='-'):
        for a, b in edges:
            ax.plot([positions[a][0], positions[b][0]], [positions[a][1], positions[b][1]], color=color, linewidth=lw, alpha=alpha, linestyle=ls, zorder=2)

    ax = axes[0]
    draw_edge_set(ax, baseline_edges, '#9fbcd6', 1.45, 0.84)
    draw_nodes(ax)
    draw_route(ax, positions, route0, color='#444444', lw=2.2)
    ax.set_title('Baseline space', fontsize=10.5)
    ax.text(0.03, 0.95, f'cand. links: {len(baseline_edges)}', transform=ax.transAxes, fontsize=8.8, ha='left', va='top', bbox=dict(facecolor='white', edgecolor='none', alpha=0.86, pad=1.2))

    ax = axes[1]
    draw_edge_set(ax, retained_edges, '#4c78a8', 1.85, 0.96)
    draw_edge_set(ax, pruned_edges, '#d62728', 1.5, 0.88, '--')
    draw_nodes(ax)
    draw_route(ax, positions, route0, color='#666666', lw=1.95)
    ax.set_title('Difference map', fontsize=10.5)
    ax.text(0.03, 0.95, f'pruned: {len(pruned_edges)}\nretained: {len(retained_edges)}', transform=ax.transAxes, fontsize=8.8, ha='left', va='top', bbox=dict(facecolor='white', edgecolor='none', alpha=0.86, pad=1.2))

    from matplotlib.lines import Line2D
    legend_items = [
        Line2D([0],[0], color='#9fbcd6', linewidth=1.45, label='Baseline candidate'),
        Line2D([0],[0], color='#4c78a8', linewidth=1.85, label='Full retained'),
        Line2D([0],[0], color='#d62728', linewidth=1.5, linestyle='--', label='Pruned'),
        Line2D([0],[0], color='#666666', linewidth=1.95, label='Backbone route'),
    ]
    fig.legend(handles=legend_items, loc='upper center', ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.95))
    fig.suptitle('Stable (40 nodes): structural pruning without performance loss', y=0.995, fontsize=12.5)
    save_figure(fig, 'fig7_stable_baseline_vs_full_linkspace', bbox_inches='tight')
    plt.close(fig)


def make_parameter_sensitivity_heatmap():
    df = pd.read_csv(PARAM_SENS)
    scene_order = ['Temporary Root Displacement', 'Root-Loss', 'Local Failure']
    setting_order = [
        ('tau=160', 'tau160'),
        ('default-tau', 'tau192'),
        ('tau=224', 'tau224'),
        ('Tmid=64', 'T64'),
        ('default-tmid', 'T96'),
        ('Tmid=128', 'T128'),
        ('Kreserve=1', 'K1'),
        ('default-kreserve', 'K2'),
        ('Kreserve=3', 'K3'),
    ]

    default_rows = []
    for scene in scene_order:
        default_rows.extend([
            {'parameter': 'default-tau', 'scene': scene, 'dpdr_pp': 0.0, 'drecov_pct': 0.0, 'dgate_cmp_pct': 0.0},
            {'parameter': 'default-tmid', 'scene': scene, 'dpdr_pp': 0.0, 'drecov_pct': 0.0, 'dgate_cmp_pct': 0.0},
            {'parameter': 'default-kreserve', 'scene': scene, 'dpdr_pp': 0.0, 'drecov_pct': 0.0, 'dgate_cmp_pct': 0.0},
        ])
    df = pd.concat([df, pd.DataFrame(default_rows)], ignore_index=True)

    metrics = [
        ('dpdr_pp', 'dPDR (pp)', '#1f4e79'),
        ('drecov_pct', 'dRecov (%)', '#8b1e3f'),
        ('dgate_cmp_pct', 'dgate_cmp (%)', '#2c6e49'),
    ]

    for col in ['dpdr_pp', 'drecov_pct', 'dgate_cmp_pct']:
        df[col] = pd.to_numeric(df[col])

    fig, axes = plt.subplots(3, 1, figsize=(8.3, 6.8), constrained_layout=False)
    fig.subplots_adjust(top=0.92, bottom=0.11, left=0.20, right=0.98, hspace=0.28)

    for ax, (metric, title, text_color) in zip(axes, metrics):
        grid = []
        for scene in scene_order:
            row = []
            for key, _ in setting_order:
                val = float(df[(df['scene'] == scene) & (df['parameter'] == key)][metric].iloc[0])
                row.append(val)
            grid.append(row)
        grid = pd.DataFrame(grid, index=scene_order, columns=[label for _, label in setting_order])
        vmax = max(abs(grid.values.min()), abs(grid.values.max()))
        vmax = max(vmax, 1e-6)
        norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
        im = ax.imshow(grid.values, cmap='RdBu_r', norm=norm, aspect='auto')
        ax.set_title(title, fontsize=11)
        ax.set_yticks(range(len(scene_order)), scene_order)
        ax.set_xticks(range(len(setting_order)), [label for _, label in setting_order])
        ax.tick_params(axis='x', rotation=0)
        for x in [2.5, 5.5]:
            ax.axvline(x, color='#666666', linewidth=1.0)
        for i in range(len(scene_order)):
            for j in range(len(setting_order)):
                val = grid.values[i, j]
                fmt = f'{val:+.3f}' if metric == 'dpdr_pp' else f'{val:+.1f}'
                ax.text(j, i, fmt, ha='center', va='center', fontsize=8, color='black')
        cbar = fig.colorbar(im, ax=ax, fraction=0.022, pad=0.02)
        cbar.ax.tick_params(labelsize=8)

    fig.suptitle('Parameter sensitivity at 40 nodes relative to the default Full configuration', fontsize=12.5)
    fig.text(0.5, 0.04, 'Settings grouped as tau_strict / T_mid / K_reserve', ha='center', fontsize=9)
    save_figure(fig, 'fig8_parameter_sensitivity', bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    make_lite_core_results()
    make_local_failure_topology()
    make_transferability()
    make_recovery_process_examples()
    make_structural_local_failure_view()
    make_baseline_vs_full_linkspace()
    make_stable_linkspace_comparison()
    make_parameter_sensitivity_heatmap()
    print('generated:', *(str(p) for p in sorted(OUT.glob('*.pdf'))), sep='\n')
