#!/usr/bin/env python3
import argparse
import heapq
import math
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
CONTIKI_NG_ROOT = THIS_DIR.parents[1]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("csc", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            os.environ.get(
                "PAPER_PRIOR_OUTPUT",
                str(CONTIKI_NG_ROOT / "os" / "net" / "routing" / "rpl-lite" / "rpl-gate-prior-data.h"),
            )
        ),
    )
    parser.add_argument("--hop-penalty-q8", type=int, default=32)
    parser.add_argument("--relu-threshold-q8", type=int, default=-1)
    parser.add_argument("--relu-alpha-q8", type=int, default=256)
    parser.add_argument("--prior-mode", choices=("geometry", "hop"), default="geometry")
    parser.add_argument("--coordinate-noise-pct", type=float, default=0.0)
    parser.add_argument("--noise-seed", type=int, default=0)
    return parser.parse_args()


def parse_simulation(csc_path: Path):
    tree = ET.parse(csc_path)
    root = tree.getroot()
    sim = root.find("simulation")
    if sim is None:
        raise ValueError("missing <simulation>")

    medium = sim.find("radiomedium")
    tx_range = float(medium.findtext("transmitting_range", default="0")) if medium is not None else 0.0
    dgrm_edges = []

    nodes = {}
    root_id = None
    for motetype in sim.findall("motetype"):
        source = (motetype.findtext("source") or "").strip()
        description = (motetype.findtext("description") or "").strip().lower()
        is_root = "root-node.c" in source or "rpl root" in description or description == "root"

        for mote in motetype.findall("mote"):
            mote_id = None
            pos = None
            for iface in mote.findall("interface_config"):
                iface_text = (iface.text or "").strip()
                if iface_text.endswith("Position"):
                    pos_elem = iface.find("pos")
                    if pos_elem is not None:
                        pos = (float(pos_elem.attrib["x"]), float(pos_elem.attrib["y"]))
                elif iface_text.endswith("ContikiMoteID"):
                    id_text = iface.findtext("id")
                    if id_text:
                        mote_id = int(id_text)
            if mote_id is None or pos is None:
                continue
            nodes[mote_id] = pos
            if is_root:
                root_id = mote_id

    if root_id is None:
        raise ValueError("failed to detect RPL root in CSC")
    if medium is not None and (medium.text or "").strip().endswith("DirectedGraphMedium"):
        for edge in medium.findall("edge"):
            src_text = edge.findtext("source")
            dest_radio_text = edge.findtext("./dest/radio")
            if not src_text or not dest_radio_text:
                continue
            dgrm_edges.append((int(src_text), int(dest_radio_text)))
        if dgrm_edges and tx_range <= 0:
            max_dist = 0.0
            for src, dst in dgrm_edges:
                if src not in nodes or dst not in nodes:
                    continue
                x1, y1 = nodes[src]
                x2, y2 = nodes[dst]
                max_dist = max(max_dist, math.hypot(x2 - x1, y2 - y1))
            tx_range = max_dist
    return tx_range, root_id, nodes, dgrm_edges


def perturb_coordinates(nodes, tx_range, noise_pct, noise_seed):
    if noise_pct <= 0:
        return dict(nodes)

    rng = random.Random(noise_seed)
    max_error = tx_range * noise_pct / 100.0
    perturbed = {}
    for node_id in sorted(nodes):
        angle = rng.uniform(0.0, 2.0 * math.pi)
        radius = max_error * math.sqrt(rng.random())
        x, y = nodes[node_id]
        perturbed[node_id] = (
            x + radius * math.cos(angle),
            y + radius * math.sin(angle),
        )
    return perturbed


def build_graph(nodes, prior_nodes, tx_range, hop_penalty_q8,
                args_relu_threshold_q8, args_relu_alpha_q8, dgrm_edges,
                prior_mode):
    ids = sorted(nodes)
    max_id = ids[-1] if ids else 0
    cost = [[0] * (max_id + 1) for _ in range(max_id + 1)]
    adj = {node_id: [] for node_id in ids}

    if tx_range <= 0:
        raise ValueError("invalid transmitting_range")

    edge_set = set(dgrm_edges) if dgrm_edges else None

    for src in ids:
        for dst in ids:
            if src == dst:
                continue
            if edge_set is not None and (src, dst) not in edge_set:
                continue
            px1, py1 = prior_nodes[src]
            px2, py2 = prior_nodes[dst]
            prior_dist = math.hypot(px2 - px1, py2 - py1)
            if edge_set is not None or prior_dist <= tx_range + 1e-9:
                geom_q8 = int(round((prior_dist / tx_range) * 256.0))
                relu_extra_q8 = 0
                if args_relu_threshold_q8 >= 0 and geom_q8 > args_relu_threshold_q8:
                    relu_part_q8 = geom_q8 - args_relu_threshold_q8
                    relu_extra_q8 = int(round((relu_part_q8 * args_relu_alpha_q8) / 256.0))
                weight_q8 = 256 if prior_mode == "hop" else geom_q8 + hop_penalty_q8 + relu_extra_q8
                cost[src][dst] = weight_q8
                adj[src].append((dst, weight_q8))

    return max_id, cost, adj


def dijkstra(root_id, ids, adj):
    inf = 0xFFFF
    dist = {node_id: inf for node_id in ids}
    dist[root_id] = 0
    heap = [(0, root_id)]

    while heap:
        cur_d, node = heapq.heappop(heap)
        if cur_d != dist[node]:
            continue
        for neigh, weight in adj[node]:
            cand = cur_d + weight
            if cand < dist[neigh]:
                dist[neigh] = cand
                heapq.heappush(heap, (cand, neigh))

    return dist


def emit_header(output, root_id, max_id, tx_range_q8, hop_penalty_q8, dist, cost):
    lines = [
        "#ifndef RPL_GATE_PRIOR_DATA_H_",
        "#define RPL_GATE_PRIOR_DATA_H_",
        "",
        "#define RPL_GATE_PRIOR_ENABLED 1",
        f"#define RPL_GATE_PRIOR_ROOT_ID {root_id}",
        f"#define RPL_GATE_PRIOR_MAX_NODE_ID {max_id}",
        f"#define RPL_GATE_PRIOR_TX_RANGE_Q8 {tx_range_q8}",
        f"#define RPL_GATE_PRIOR_HOP_PENALTY_Q8 {hop_penalty_q8}",
        "",
        "static const uint16_t rpl_gate_prior_d_q8[] = {",
    ]

    for idx in range(max_id + 1):
        lines.append(f"  {dist.get(idx, 0xFFFF)},")

    lines.extend([
        "};",
        "",
        "static const uint16_t rpl_gate_prior_struct_cost_q8[] = {",
    ])

    for src in range(max_id + 1):
        row = ", ".join(str(cost[src][dst]) for dst in range(max_id + 1))
        lines.append(f"  {row},")

    lines.extend([
        "};",
        "",
        "#endif /* RPL_GATE_PRIOR_DATA_H_ */",
        "",
    ])

    output.write_text("\n".join(lines))


def main():
    args = parse_args()
    tx_range, root_id, nodes, dgrm_edges = parse_simulation(args.csc)
    prior_nodes = perturb_coordinates(nodes, tx_range, args.coordinate_noise_pct, args.noise_seed)
    max_id, cost, adj = build_graph(
        nodes,
        prior_nodes,
        tx_range,
        args.hop_penalty_q8,
        args.relu_threshold_q8,
        args.relu_alpha_q8,
        dgrm_edges,
        args.prior_mode,
    )
    dist = dijkstra(root_id, sorted(nodes), adj)
    emit_header(args.output, root_id, max_id, int(round(tx_range * 256.0)), args.hop_penalty_q8, dist, cost)


if __name__ == "__main__":
    main()
