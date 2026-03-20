#!/usr/bin/env python3
import math
import os
import xml.etree.ElementTree as ET
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
CONTIKI_NG_ROOT = THIS_DIR.parents[1]
SRC_DIR = Path(os.environ.get('PAPER_GENERATED_CORE_DIR', str(CONTIKI_NG_ROOT / 'tests' / '14-rpl-lite' / 'generated-core')))
OUT_ROOT = Path(os.environ.get('PAPER_14_PAPER_DIR', str(THIS_DIR)))
OUT_DIR = OUT_ROOT / 'generated'

SCENES = {
    's1_stable': {
        'template': SRC_DIR / 's1_stable_20.csc',
        'sender_id': 2,
        'root_id': 3,
        'receiver_start': [1, 4],
        'root_pos': (0.0, 0.0),
        'sender_pos': (132.8019872469463, 146.1533406452311),
        'topology': 'sparse',
    },
    's2_disturb': {
        'template': SRC_DIR / 's2_disturb_20.csc',
        'sender_id': 2,
        'root_id': 1,
        'receiver_start': [3],
        'root_pos': (8.0, 2.0),
        'sender_pos': (-7.19071602882406, 34.96668248624779),
        'topology': 'dense',
    },
    's3_rootloss': {
        'template': SRC_DIR / 's3_rootloss_20.csc',
        'sender_id': 2,
        'root_id': 3,
        'receiver_start': [1, 4],
        'root_pos': (0.0, 0.0),
        'sender_pos': (116.13379149678028, 88.36698920455684),
        'topology': 'sparse',
    },
    's4_noise': {
        'template': SRC_DIR / 's2_disturb_20.csc',
        'sender_id': 2,
        'root_id': 1,
        'receiver_start': [3],
        'root_pos': (8.0, 2.0),
        'sender_pos': (-7.19071602882406, 34.96668248624779),
        'topology': 'dense',
    },
    's5_local_failure': {
        'template': SRC_DIR / 's3_rootloss_20.csc',
        'sender_id': 2,
        'root_id': 3,
        'receiver_start': [1, 4],
        'root_pos': (0.0, 0.0),
        'sender_pos': (116.13379149678028, 88.36698920455684),
        'topology': 'sparse',
    },
}

SCALES = (20, 40, 60)
INTERF_BURSTS = (
    (int(os.environ.get('PAPER_INTERF_ON1_US', '1000000')), int(os.environ.get('PAPER_INTERF_OFF1_US', '1300000'))),
    (int(os.environ.get('PAPER_INTERF_ON2_US', '1600000')), int(os.environ.get('PAPER_INTERF_OFF2_US', '1900000'))),
    (int(os.environ.get('PAPER_INTERF_ON3_US', '2200000')), int(os.environ.get('PAPER_INTERF_OFF3_US', '2500000'))),
)
INTERF_TX_RANGE = float(os.environ.get('PAPER_INTERF_TX_RANGE', '50.0'))
INTERF_PROJ_MIN = float(os.environ.get('PAPER_INTERF_PROJ_MIN', '0.12'))
INTERF_PROJ_MAX = float(os.environ.get('PAPER_INTERF_PROJ_MAX', '0.88'))
INTERF_HALF_WIDTH = float(os.environ.get('PAPER_INTERF_HALF_WIDTH', '14.0'))
INTERF_BASE_RATIO_MIN = float(os.environ.get('PAPER_INTERF_BASE_RATIO_MIN', '0.84'))
INTERF_BASE_RATIO_MAX = float(os.environ.get('PAPER_INTERF_BASE_RATIO_MAX', '0.98'))
INTERF_BURST_DROP_MIN = float(os.environ.get('PAPER_INTERF_BURST_DROP_MIN', '0.25'))
INTERF_BURST_DROP_MAX = float(os.environ.get('PAPER_INTERF_BURST_DROP_MAX', '0.45'))
INTERF_MIN_RATIO = float(os.environ.get('PAPER_INTERF_MIN_RATIO', '0.42'))
INTERF_SIGNAL_BASE = float(os.environ.get('PAPER_INTERF_SIGNAL_BASE', '-61.0'))
INTERF_SIGNAL_SPAN = float(os.environ.get('PAPER_INTERF_SIGNAL_SPAN', '18.0'))
LOCAL_FAIL_ON_US = int(os.environ.get('PAPER_LOCAL_FAIL_ON_US', '1000000'))
LOCAL_FAIL_OFF_US = int(os.environ.get('PAPER_LOCAL_FAIL_OFF_US', '2000000'))
LOCAL_FAIL_SHIFT = float(os.environ.get('PAPER_LOCAL_FAIL_SHIFT', '120.0'))


def receiver_ids(scale: int, start):
    ids = []
    if start[0] == 1 and len(start) == 2:
        ids.append(1)
        ids.extend(range(start[1], scale + 1))
    else:
        ids.extend(range(start[0], scale + 1))
    return ids


def sparse_positions(count: int, sender_pos):
    sx, sy = sender_pos
    anchors = [(sx * t, sy * t) for t in (0.14, 0.28, 0.42, 0.56, 0.70, 0.84)]
    length = math.hypot(sx, sy)
    ux, uy = (sx / length, sy / length)
    px, py = (-uy, ux)
    offsets = [
        (0.0, 0.0), (0.0, 12.0), (0.0, -12.0), (6.0, 18.0), (-6.0, -18.0),
        (8.0, 0.0), (-8.0, 0.0), (12.0, 10.0), (-12.0, -10.0), (16.0, 0.0),
    ]
    out = []
    for idx in range(count):
        ax, ay = anchors[idx % len(anchors)]
        along, side = offsets[(idx // len(anchors)) % len(offsets)]
        x = ax + ux * along + px * side
        y = ay + uy * along + py * side
        out.append((round(x, 6), round(y, 6)))
    return out


def dense_positions(count: int):
    cols = 6
    rows = math.ceil(count / cols)
    x0 = -24.0
    y0 = 8.0
    dx = 12.0
    dy = 12.0
    out = []
    for r in range(rows):
        for c in range(cols):
            if len(out) >= count:
                break
            jitter_x = 3.0 if r % 2 else 0.0
            x = x0 + c * dx + jitter_x
            y = y0 + r * dy
            out.append((round(x, 6), round(y, 6)))
    return out


def make_mote(mid: int, pos):
    mote = ET.Element('mote')
    iface_pos = ET.SubElement(mote, 'interface_config')
    iface_pos.text = '\n          org.contikios.cooja.interfaces.Position\n          '
    ET.SubElement(iface_pos, 'pos', {'x': str(pos[0]), 'y': str(pos[1])})
    iface_id = ET.SubElement(mote, 'interface_config')
    iface_id.text = '\n          org.contikios.cooja.contikimote.interfaces.ContikiMoteID\n          '
    ET.SubElement(iface_id, 'id').text = str(mid)
    return mote


def clear_and_fill_motetype(motetype, motes):
    for old in list(motetype.findall('mote')):
        motetype.remove(old)
    for mote in motes:
        motetype.append(mote)


def project_point(pos, sender_pos):
    sx, sy = sender_pos
    seg_len2 = sx * sx + sy * sy
    seg_len = math.sqrt(seg_len2)
    x, y = pos
    proj = ((x * sx) + (y * sy)) / seg_len2
    cross = abs((x * sy) - (y * sx)) / seg_len
    return proj, cross


def choose_interference_edges(node_positions, sender_pos):
    ids = sorted(node_positions)
    edges = []
    affected = {}
    for src in ids:
        x1, y1 = node_positions[src]
        for dst in ids:
            if src == dst:
                continue
            x2, y2 = node_positions[dst]
            dist = math.hypot(x2 - x1, y2 - y1)
            if dist > INTERF_TX_RANGE + 1e-9:
                continue
            dist_ratio = min(1.0, dist / INTERF_TX_RANGE)
            base_ratio = INTERF_BASE_RATIO_MAX - (INTERF_BASE_RATIO_MAX - INTERF_BASE_RATIO_MIN) * (dist_ratio ** 1.7)
            base_ratio = round(max(INTERF_BASE_RATIO_MIN, min(INTERF_BASE_RATIO_MAX, base_ratio)), 3)
            signal = round(INTERF_SIGNAL_BASE - INTERF_SIGNAL_SPAN * dist_ratio, 3)
            mid = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
            proj, cross = project_point(mid, sender_pos)
            key = f'{src}-{dst}'
            edge = {
                'src': src,
                'dst': dst,
                'ratio': base_ratio,
                'signal': signal,
            }
            edges.append(edge)
            if INTERF_PROJ_MIN <= proj <= INTERF_PROJ_MAX and cross <= INTERF_HALF_WIDTH:
                burst_ratios = {}
                for burst_idx, _window in enumerate(INTERF_BURSTS, start=1):
                    frac = (((src * 17) + (dst * 19) + (burst_idx * 23)) % 101) / 100.0
                    drop = INTERF_BURST_DROP_MIN + frac * (INTERF_BURST_DROP_MAX - INTERF_BURST_DROP_MIN)
                    burst_ratio = max(INTERF_MIN_RATIO, base_ratio - drop)
                    burst_ratios[burst_idx] = round(burst_ratio, 3)
                affected[key] = {
                    'base': base_ratio,
                    'burst': burst_ratios,
                }
    return edges, affected


def set_directed_graph_medium(sim, edges):
    medium = sim.find('radiomedium')
    if medium is None:
        medium = ET.SubElement(sim, 'radiomedium')
    medium.clear()
    medium.text = 'org.contikios.cooja.radiomediums.DirectedGraphMedium'
    for edge in edges:
        edge_el = ET.SubElement(medium, 'edge')
        ET.SubElement(edge_el, 'source').text = str(edge['src'])
        dest_el = ET.SubElement(edge_el, 'dest')
        dest_el.text = 'org.contikios.cooja.radiomediums.DGRMDestinationRadio'
        ET.SubElement(dest_el, 'radio').text = str(edge['dst'])
        ET.SubElement(dest_el, 'ratio').text = str(edge['ratio'])
        ET.SubElement(dest_el, 'signal').text = str(edge['signal'])
        ET.SubElement(dest_el, 'lqi').text = '105'
        ET.SubElement(dest_el, 'delay').text = '0'
        ET.SubElement(dest_el, 'channel').text = '-1'


def patch_noise_script(script_text: str, affected_edges) -> str:
    original_schedule = 'GENERATE_MSG(1000000, "moving root 2 hops away");\nGENERATE_MSG(1500000, "moving root back");'
    schedule_lines = []
    for idx, (on_us, off_us) in enumerate(INTERF_BURSTS, start=1):
        schedule_lines.append(f'GENERATE_MSG({on_us}, "interf_on_{idx}");')
        schedule_lines.append(f'GENERATE_MSG({off_us}, "interf_off_{idx}");')
    base_map = ', '.join([f'"{key}":{cfg["base"]}' for key, cfg in affected_edges.items()])
    burst_maps = []
    for burst_idx, _window in enumerate(INTERF_BURSTS, start=1):
        entries = ', '.join([f'"{key}":{cfg["burst"][burst_idx]}' for key, cfg in affected_edges.items()])
        burst_maps.append(f'{burst_idx}:{{{entries}}}')
    burst_map = ', '.join(burst_maps)

    new_schedule = '\n'.join(schedule_lines) + (
        '\n\n'
        'var dgrm = sim.getRadioMedium();\n'
        'var dgrmEdges = {};\n'
        'var edgeArr = dgrm.getEdges();\n'
        'for(var i = 0; i < edgeArr.length; i++) {\n'
        '  var e = edgeArr[i];\n'
        '  var k = e.source.getMote().getID() + "-" + e.superDest.radio.getMote().getID();\n'
        '  dgrmEdges[k] = e;\n'
        '}\n'
        f'var interfBase = {{{base_map}}};\n'
        f'var interfBurst = {{{burst_map}}};\n'
        'var applyInterferenceRatios = function(mapObj) {\n'
        '  for(var key in mapObj) {\n'
        '    if(!mapObj.hasOwnProperty(key)) { continue; }\n'
        '    var e = dgrmEdges[key];\n'
        '    if(e) {\n'
        '      e.superDest.ratio = mapObj[key];\n'
        '    }\n'
        '  }\n'
        '};\n'
        'var applyInterferenceBurst = function(burst) {\n'
        '  applyInterferenceRatios(interfBurst[burst]);\n'
        '};\n'
        'var clearInterferenceBurst = function() {\n'
        '  applyInterferenceRatios(interfBase);\n'
        '};'
    )
    script_text = script_text.replace(original_schedule, new_schedule)

    old_block = (
        'if(msg.equals("moving root 2 hops away")) {\n'
        '        var root = sim.getMoteWithID(1);\n'
        '        root.getInterfaces().getPosition().setCoordinates(5, -20, 0);\n'
        '        log.log("moving root 2 hops away\\n");\n'
        '        eventMarkUs = -1;\n'
        '        recoveryHits = 0;\n'
        '        recoveryArmed = 0;\n'
        '    } else if(msg.equals("moving root back")) {\n'
        '        var root = sim.getMoteWithID(1);\n'
        '        root.getInterfaces().getPosition().setCoordinates(8, 2, 0);\n'
        '        log.log("moving root back\\n");\n'
        '        eventMarkUs = time;\n'
        '        recoveryHits = 0;\n'
        '        recoveryArmed = 1;'
    )
    new_block = (
        'if(msg.startsWith("interf_on_")) {\n'
        '        var burst = parseInt(msg.substring(10));\n'
        '        applyInterferenceBurst(burst);\n'
        '        log.log("local stochastic interference on burst=" + burst + "\\n");\n'
        '        eventMarkUs = -1;\n'
        '        recoveryHits = 0;\n'
        '        recoveryArmed = 0;\n'
        '    } else if(msg.startsWith("interf_off_")) {\n'
        '        var burst = parseInt(msg.substring(11));\n'
        '        clearInterferenceBurst();\n'
        '        log.log("local stochastic interference off burst=" + burst + "\\n");\n'
        '        if(burst == 3) {\n'
        '          eventMarkUs = time;\n'
        '          recoveryHits = 0;\n'
        '          recoveryArmed = 1;\n'
        '        } else {\n'
        '          eventMarkUs = -1;\n'
        '          recoveryHits = 0;\n'
        '          recoveryArmed = 0;\n'
        '        }'
    )
    if old_block not in script_text:
        raise RuntimeError('unexpected ScriptRunner structure for local interference patch')
    script_text = script_text.replace(old_block, new_block)
    return script_text


def choose_failure_nodes(root_pos, sender_pos, recv_ids_list, receiver_positions):
    sx, sy = sender_pos
    seg_len2 = sx * sx + sy * sy
    seg_len = math.sqrt(seg_len2)
    candidates = []
    for mid, (x, y) in zip(recv_ids_list, receiver_positions):
        proj = ((x * sx) + (y * sy)) / seg_len2
        cross = abs((x * sy) - (y * sx)) / seg_len
        if 0.15 <= proj <= 0.85:
            candidates.append((mid, (x, y), proj, cross))
    if not candidates:
        return []
    targets = [0.35, 0.50, 0.65] if len(recv_ids_list) < 30 else [0.32, 0.44, 0.56, 0.68]
    chosen = []
    used = set()
    for target in targets:
        ranked = sorted(
            candidates,
            key=lambda item: (abs(item[2] - target), item[3], abs(item[2] - 0.5))
        )
        for mid, pos, _proj, _cross in ranked:
            if mid not in used:
                chosen.append((mid, pos))
                used.add(mid)
                break
    return chosen


def failure_shift_position(pos):
    x, y = pos
    return (round(x + LOCAL_FAIL_SHIFT, 6), round(y + LOCAL_FAIL_SHIFT, 6))


def patch_local_failure_script(script_text: str, failed_nodes) -> str:
    original_schedule = 'GENERATE_MSG(0000000, "add-sink");\nGENERATE_MSG(1000000, "remove-sink");\nGENERATE_MSG(2000000, "add-sink");'
    ids = [mid for mid, _pos in failed_nodes]
    orig_map = ', '.join([f'"{mid}":[{pos[0]},{pos[1]}]' for mid, pos in failed_nodes])
    fail_map = ', '.join([f'"{mid}":[{failure_shift_position(pos)[0]},{failure_shift_position(pos)[1]}]' for mid, pos in failed_nodes])
    new_schedule = (
        'GENERATE_MSG(0000000, "add-sink");\n'
        f'GENERATE_MSG({LOCAL_FAIL_ON_US}, "local_fail_on");\n'
        f'GENERATE_MSG({LOCAL_FAIL_OFF_US}, "local_fail_off");\n\n'
        f'var localFailIds = [{",".join(str(v) for v in ids)}];\n'
        f'var localFailOrig = {{{orig_map}}};\n'
        f'var localFailShift = {{{fail_map}}};\n'
        'var applyLocalFailure = function() {\n'
        '  for(var i = 0; i < localFailIds.length; i++) {\n'
        '    var mid = localFailIds[i];\n'
        '    var p = localFailShift[String(mid)];\n'
        '    sim.getMoteWithID(mid).getInterfaces().getPosition().setCoordinates(p[0], p[1], 0);\n'
        '  }\n'
        '};\n'
        'var clearLocalFailure = function() {\n'
        '  for(var i = 0; i < localFailIds.length; i++) {\n'
        '    var mid = localFailIds[i];\n'
        '    var p = localFailOrig[String(mid)];\n'
        '    sim.getMoteWithID(mid).getInterfaces().getPosition().setCoordinates(p[0], p[1], 0);\n'
        '  }\n'
        '};'
    )
    script_text = script_text.replace(original_schedule, new_schedule)

    old_block = (
        'if(msg.equals("remove-sink")) {\n'
        '        m = sim.getMoteWithID(3);\n'
        '        sim.removeMote(m);\n'
        '        log.log("removed sink\\n");\n'
        '        eventMarkUs = -1;\n'
        '        recoveryHits = 0;\n'
        '        recoveryArmed = 0;\n'
        '    } else if(msg.equals("add-sink")) {\n'
        '        if(!sim.getMoteWithID(3)) {\n'
        '            m = sim.getMoteTypes()[1].generateMote(sim);\n'
        '            m.getInterfaces().getMoteID().setMoteID(3);\n'
        '            sim.addMote(m);\n'
        '            log.log("added sink\\n");\n'
        '            eventMarkUs = time;\n'
        '            recoveryHits = 0;\n'
        '            recoveryArmed = 1;\n'
        '         } else {\n'
        '            log.log("did not add sink as it was already there\\n");      \n'
        '         }\n'
        '    } else if(msg.startsWith("Sending")) {'
    )
    new_block = (
        'if(msg.equals("add-sink")) {\n'
        '        if(!sim.getMoteWithID(3)) {\n'
        '            m = sim.getMoteTypes()[1].generateMote(sim);\n'
        '            m.getInterfaces().getMoteID().setMoteID(3);\n'
        '            sim.addMote(m);\n'
        '            log.log("added sink\\n");\n'
        '         } else {\n'
        '            log.log("did not add sink as it was already there\\n");      \n'
        '         }\n'
        '    } else if(msg.equals("local_fail_on")) {\n'
        '        applyLocalFailure();\n'
        '        log.log("local failure on\\n");\n'
        '        eventMarkUs = -1;\n'
        '        recoveryHits = 0;\n'
        '        recoveryArmed = 0;\n'
        '    } else if(msg.equals("local_fail_off")) {\n'
        '        clearLocalFailure();\n'
        '        log.log("local failure off\\n");\n'
        '        eventMarkUs = time;\n'
        '        recoveryHits = 0;\n'
        '        recoveryArmed = 1;\n'
        '    } else if(msg.startsWith("Sending")) {'
    )
    if old_block not in script_text:
        raise RuntimeError('unexpected ScriptRunner structure for local failure patch')
    script_text = script_text.replace(old_block, new_block)
    return script_text



def generate_scene(scene_key: str, scale: int):
    spec = SCENES[scene_key]
    tree = ET.parse(spec['template'])
    root = tree.getroot()
    sim = root.find('simulation')
    if sim is None:
        raise RuntimeError(f'missing simulation in {spec["template"]}')

    title = sim.find('title')
    if title is not None:
        title.text = f'paper-{scene_key}-{scale}'

    motetypes = sim.findall('motetype')
    sender_mt = next(mt for mt in motetypes if (mt.findtext('description') or '').strip() == 'Sender')
    root_mt = next(mt for mt in motetypes if 'root' in (mt.findtext('description') or '').strip().lower())
    recv_mt = next(mt for mt in motetypes if (mt.findtext('description') or '').strip() == 'Receiver')

    clear_and_fill_motetype(sender_mt, [make_mote(spec['sender_id'], spec['sender_pos'])])
    clear_and_fill_motetype(root_mt, [make_mote(spec['root_id'], spec['root_pos'])])

    recv_ids = receiver_ids(scale, spec['receiver_start'])
    recv_pos = sparse_positions(len(recv_ids), spec['sender_pos']) if spec['topology'] == 'sparse' else dense_positions(len(recv_ids))
    recv_motes = [make_mote(mid, pos) for mid, pos in zip(recv_ids, recv_pos)]
    clear_and_fill_motetype(recv_mt, recv_motes)

    if scene_key == 's4_noise':
        all_nodes = {
            spec['sender_id']: spec['sender_pos'],
            spec['root_id']: spec['root_pos'],
        }
        all_nodes.update({mid: pos for mid, pos in zip(recv_ids, recv_pos)})
        all_edges, affected_edges = choose_interference_edges(all_nodes, spec['sender_pos'])
        if not affected_edges:
            raise RuntimeError(f'no local interference edges selected for {scene_key}_{scale}')
        set_directed_graph_medium(sim, all_edges)
        script = None
        for plugin in root.findall('plugin'):
            plugin_type = (plugin.text or '').strip()
            if plugin_type == 'org.contikios.cooja.plugins.ScriptRunner':
                script = plugin.find('./plugin_config/script')
                break
        if script is None or script.text is None:
            raise RuntimeError('missing ScriptRunner script for noise scene')
        script.text = patch_noise_script(script.text, affected_edges)
    elif scene_key == 's5_local_failure':
        failed_nodes = choose_failure_nodes(spec['root_pos'], spec['sender_pos'], recv_ids, recv_pos)
        if not failed_nodes:
            raise RuntimeError(f'no local failure nodes selected for {scene_key}_{scale}')
        script = None
        for plugin in root.findall('plugin'):
            plugin_type = (plugin.text or '').strip()
            if plugin_type == 'org.contikios.cooja.plugins.ScriptRunner':
                script = plugin.find('./plugin_config/script')
                break
        if script is None or script.text is None:
            raise RuntimeError('missing ScriptRunner script for local failure scene')
        script.text = patch_local_failure_script(script.text, failed_nodes)

    ET.indent(tree, space='  ')
    out_path = OUT_DIR / f'{scene_key}_{scale}.csc'
    tree.write(out_path, encoding='utf-8', xml_declaration=True)
    return out_path


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for scene in SCENES:
        for scale in SCALES:
            print(generate_scene(scene, scale))


if __name__ == '__main__':
    main()
