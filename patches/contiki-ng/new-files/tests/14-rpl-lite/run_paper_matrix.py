#!/usr/bin/env python3
import csv
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

GROUP_LABELS = {
    'baseline': 'Baseline',
    'hard_only': 'Hard-Only',
    'soft_only': 'Soft-Only',
    'full': 'Full',
}

SCENE_LABELS = {
    's1_stable': 'Stable',
    's2_disturb': 'Temporary Root Displacement',
    's3_rootloss': 'Root-Loss',
    's4_noise': 'Local Interference Corridor',
    's5_local_failure': 'Local Failure',
}

CONF_LINES = {
    'baseline': [],
    'hard_only': [
        '#define RPL_CONF_WITH_EDGE_GATE 1',
        '#define RPL_CONF_EDGE_GATE_ENABLE_HARD_PRUNE 1',
        '#define RPL_CONF_EDGE_GATE_ENABLE_SOFT_GATING 0',
    ],
    'soft_only': [
        '#define RPL_CONF_WITH_EDGE_GATE 1',
        '#define RPL_CONF_EDGE_GATE_ENABLE_HARD_PRUNE 0',
        '#define RPL_CONF_EDGE_GATE_ENABLE_SOFT_GATING 1',
    ],
    'full': [
        '#define RPL_CONF_WITH_EDGE_GATE 1',
        '#define RPL_CONF_EDGE_GATE_ENABLE_HARD_PRUNE 1',
        '#define RPL_CONF_EDGE_GATE_ENABLE_SOFT_GATING 1',
    ],
}

CSV_HEADER = [
    'platform', 'group', 'scene', 'scale', 'seed',
    'exit_status', 'test_ok', 'wall_sec', 'log_path', 'script_log_path'
]

DEFINE_PREFIXES = [
    '#define RPL_EXPERIMENTAL_MRHOF',
    '#define RPL_CONF_WITH_EDGE_GATE',
    '#define RPL_CONF_EDGE_GATE_ENABLE_HARD_PRUNE',
    '#define RPL_CONF_EDGE_GATE_ENABLE_SOFT_GATING',
    '#define RPL_CONF_EDGE_GATE_T_NEAR_Q8',
    '#define RPL_CONF_EDGE_GATE_T_MID_Q8',
    '#define RPL_CONF_EDGE_GATE_STRICT_SLACK_TAU_Q8',
    '#define RPL_CONF_EDGE_GATE_RECOVERY_TAU_Q8',
    '#define RPL_CONF_EDGE_GATE_MID_DEGRADE_OFF_Q8',
    '#define RPL_CONF_EDGE_GATE_MID_DEGRADE_ON_Q8',
    '#define RPL_CONF_EDGE_GATE_NEAR_DEGRADE_OFF_Q8',
    '#define RPL_CONF_EDGE_GATE_NEAR_DEGRADE_ON_Q8',
    '#define RPL_CONF_EDGE_GATE_NEAR_ETX_OFF_Q8',
    '#define RPL_CONF_EDGE_GATE_NEAR_ETX_ON_Q8',
    '#define RPL_CONF_EDGE_GATE_BAD_K',
    '#define RPL_CONF_EDGE_GATE_GOOD_M',
    '#define RPL_CONF_EDGE_GATE_MIN_FREEZE_TIME',
    '#define RPL_CONF_EDGE_GATE_MIN_RESERVE_PARENTS',
]

@dataclass(frozen=True)
class Case:
    group: str
    scene: str
    scale: str
    seed: str

    @property
    def group_label(self) -> str:
        return GROUP_LABELS.get(self.group, self.group)

    @property
    def scene_label(self) -> str:
        return SCENE_LABELS.get(self.scene, self.scene)

    @property
    def done_key(self) -> Tuple[str, str, str, str, str]:
        return (os.environ.get('PAPER_PLATFORM', 'rpl-lite'), self.group_label, self.scene_label, self.scale, self.seed)


class Runner:
    def __init__(self) -> None:
        this_dir = Path(__file__).resolve().parent
        self.root = Path(os.environ.get('CONTIKI_NG_ROOT', str(this_dir.parents[1])))
        self.platform = os.environ.get('PAPER_PLATFORM', 'rpl-lite')
        default_test_dir = self.root / 'tests' / ('14-rpl-lite' if self.platform == 'rpl-lite' else '15-rpl-classic')
        self.test_dir = Path(os.environ.get('PAPER_TEST_DIR', str(default_test_dir)))
        self.cooja_dir = self.root / 'tools' / 'cooja'
        self.conf = self.test_dir / 'code' / 'project-conf.h'
        self.gen_dir = Path(os.environ.get('PAPER_GEN_DIR', str(self.test_dir / 'generated-core')))
        self.out_dir = Path(os.environ.get('PAPER_OUT_DIR', str(self.test_dir / 'paper-results')))
        self.log_dir = self.out_dir / 'logs'
        self.csv_path = Path(os.environ.get('PAPER_CSV', str(self.out_dir / 'paper_matrix_results.csv')))
        self.prior_gen = self.root / 'tests' / '14-rpl-lite' / 'generate_rpl_gate_prior.py'
        self.tracker = self.root / 'tests' / '14-rpl-lite' / 'update_experiment_tracker.py'
        self.md_path = os.environ.get('PAPER_MD_PATH', '')
        self.hop_penalty_q8 = os.environ.get('PAPER_HOP_PENALTY_Q8', '32')
        self.relu_threshold_q8 = os.environ.get('PAPER_RELU_THRESHOLD_Q8', '-1')
        self.relu_alpha_q8 = os.environ.get('PAPER_RELU_ALPHA_Q8', '256')
        self.require_gate_on = os.environ.get('PAPER_REQUIRE_GATE_ON', '1') != '0'
        self.expected_seeds = int(os.environ.get('PAPER_EXPECTED_SEEDS', '20'))
        self.groups = self._split_env('PAPER_GROUPS', 'baseline hard_only soft_only full')
        self.scenes = self._split_env('PAPER_SCENES', 's1_stable s2_disturb s3_rootloss')
        self.scales = self._split_env('PAPER_SCALES', '20 40 60')
        self.seeds = self._split_env('PAPER_SEEDS', ' '.join(str(i) for i in range(1, 21)))
        self.extra_defines = self._collect_extra_defines()
        self.done_cases: Set[Tuple[str, str, str, str, str]] = set()
        self.conf_backup: Optional[Path] = None

    def _split_env(self, key: str, default: str) -> List[str]:
        return os.environ.get(key, default).split()

    def _collect_extra_defines(self) -> List[str]:
        env_to_define = [
            ('PAPER_GATE_T_NEAR_Q8', 'RPL_CONF_EDGE_GATE_T_NEAR_Q8'),
            ('PAPER_GATE_T_MID_Q8', 'RPL_CONF_EDGE_GATE_T_MID_Q8'),
            ('PAPER_GATE_STRICT_TAU_Q8', 'RPL_CONF_EDGE_GATE_STRICT_SLACK_TAU_Q8'),
            ('PAPER_GATE_RECOVERY_TAU_Q8', 'RPL_CONF_EDGE_GATE_RECOVERY_TAU_Q8'),
            ('PAPER_GATE_MID_DEGRADE_OFF_Q8', 'RPL_CONF_EDGE_GATE_MID_DEGRADE_OFF_Q8'),
            ('PAPER_GATE_MID_DEGRADE_ON_Q8', 'RPL_CONF_EDGE_GATE_MID_DEGRADE_ON_Q8'),
            ('PAPER_GATE_NEAR_DEGRADE_OFF_Q8', 'RPL_CONF_EDGE_GATE_NEAR_DEGRADE_OFF_Q8'),
            ('PAPER_GATE_NEAR_DEGRADE_ON_Q8', 'RPL_CONF_EDGE_GATE_NEAR_DEGRADE_ON_Q8'),
            ('PAPER_GATE_NEAR_ETX_OFF_Q8', 'RPL_CONF_EDGE_GATE_NEAR_ETX_OFF_Q8'),
            ('PAPER_GATE_NEAR_ETX_ON_Q8', 'RPL_CONF_EDGE_GATE_NEAR_ETX_ON_Q8'),
            ('PAPER_GATE_BAD_K', 'RPL_CONF_EDGE_GATE_BAD_K'),
            ('PAPER_GATE_GOOD_M', 'RPL_CONF_EDGE_GATE_GOOD_M'),
            ('PAPER_GATE_MIN_FREEZE_TIME', 'RPL_CONF_EDGE_GATE_MIN_FREEZE_TIME'),
            ('PAPER_GATE_MIN_RESERVE_PARENTS', 'RPL_CONF_EDGE_GATE_MIN_RESERVE_PARENTS'),
        ]
        lines: List[str] = []
        for env_key, define_name in env_to_define:
            value = os.environ.get(env_key)
            if value is not None and value != '':
                lines.append(f'#define {define_name} {value}')
        extra = os.environ.get('PAPER_EXTRA_DEFINES', '').strip()
        if extra:
            for token in extra.split():
                if '=' not in token:
                    continue
                name, value = token.split('=', 1)
                lines.append(f'#define {name} {value}')
        return lines

    def run_cmd(self, cmd: List[str], cwd: Optional[Path] = None, stdout=None, stderr=None, check=False) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, cwd=str(cwd) if cwd else None, stdout=stdout, stderr=stderr, text=True, check=check)

    def ensure_dirs(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        if not self.csv_path.exists():
            with self.csv_path.open('w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADER)

    def backup_conf(self) -> None:
        fd, tmp = tempfile.mkstemp(prefix='project-conf.', suffix='.bak')
        os.close(fd)
        self.conf_backup = Path(tmp)
        shutil.copyfile(self.conf, self.conf_backup)

    def restore_conf(self) -> None:
        if self.conf_backup and self.conf_backup.exists():
            shutil.copyfile(self.conf_backup, self.conf)
            self.conf_backup.unlink(missing_ok=True)
            self.conf_backup = None

    def set_group_mode(self, group: str) -> None:
        if group not in CONF_LINES:
            raise RuntimeError(f'unknown group: {group}')
        original = self.conf.read_text(encoding='utf-8').splitlines()
        kept = [line for line in original if not any(line.startswith(prefix) for prefix in DEFINE_PREFIXES)]
        kept.extend(CONF_LINES[group])
        kept.extend(self.extra_defines)
        self.conf.write_text('\n'.join(kept) + '\n', encoding='utf-8')

    def check_exp_symbol(self) -> str:
        code_dir = self.test_dir / 'code'
        with open(os.devnull, 'w') as devnull:
            self.run_cmd(['make', 'TARGET=cooja', 'clean'], cwd=code_dir, stdout=devnull, stderr=devnull)
            self.run_cmd(['make', 'TARGET=cooja', 'root-node.cooja'], cwd=code_dir, stdout=devnull, stderr=devnull)
        obj = 'build/cooja/obj/rpl-neighbor.o' if self.platform == 'rpl-lite' else 'build/cooja/obj/rpl-dag.o'
        nm = self.run_cmd(['nm', obj], cwd=code_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return 'ON' if 'rpl_gate_parent_allowed' in nm.stdout else 'OFF'

    def parse_metrics(self, script_log: Path) -> Dict[str, str]:
        if not script_log.exists():
            return {}
        metrics: Dict[str, str] = {}
        for line in script_log.read_text(encoding='utf-8', errors='ignore').splitlines():
            if line.startswith('METRIC '):
                for token in line.split()[1:]:
                    if '=' in token:
                        k, v = token.split('=', 1)
                        metrics[k] = v
        return metrics

    def sample_valid(self, group_label: str, script_log: Path) -> bool:
        if not script_log.exists():
            return False
        text = script_log.read_text(encoding='utf-8', errors='ignore')
        if 'TEST OK' not in text or 'METRIC ' not in text:
            return False
        if self.require_gate_on and group_label != 'Baseline':
            metrics = self.parse_metrics(script_log)
            return metrics.get('gate_on') == '1'
        return True

    def load_existing_cases(self) -> None:
        existing = 0
        with self.csv_path.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                script_log = Path(row['script_log_path'])
                if not self.sample_valid(row['group'], script_log):
                    continue
                self.done_cases.add((row['platform'], row['group'], row['scene'], row['scale'], row['seed']))
                existing += 1
        if existing:
            print(f'resume: found {existing} finished rows in {self.csv_path}')

    def build_cases(self) -> List[Case]:
        cases: List[Case] = []
        for group in self.groups:
            for scene in self.scenes:
                for scale in self.scales:
                    csc = self.gen_dir / f'{scene}_{scale}.csc'
                    if not csc.exists():
                        continue
                    for seed in self.seeds:
                        case = Case(group, scene, scale, seed)
                        if case.done_key in self.done_cases:
                            continue
                        cases.append(case)
        return cases

    def update_tracker(self) -> None:
        if not self.md_path:
            return
        try:
            self.run_cmd([sys.executable, str(self.tracker), str(self.csv_path), self.md_path, str(self.expected_seeds)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def append_row(self, row: List[str]) -> None:
        with self.csv_path.open('a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def run_case(self, case: Case, idx: int, total: int) -> None:
        csc = self.gen_dir / f'{case.scene}_{case.scale}.csc'
        log = self.log_dir / f'{case.group}_{case.scene}_{case.scale}_seed{case.seed}.log'
        script_log = self.log_dir / f'{case.group}_{case.scene}_{case.scale}_seed{case.seed}.testlog'
        self.run_cmd([
            sys.executable, str(self.prior_gen), str(csc),
            '--hop-penalty-q8', self.hop_penalty_q8,
            '--relu-threshold-q8', self.relu_threshold_q8,
            '--relu-alpha-q8', self.relu_alpha_q8,
        ], check=True)
        cooja_testlog = self.cooja_dir / 'COOJA.testlog'
        cooja_testlog.unlink(missing_ok=True)
        import time
        start = time.time()
        with log.open('w', encoding='utf-8') as logf:
            proc = self.run_cmd([
                './gradlew', '--no-daemon', '--console=plain', 'run',
                f'--args=--no-gui --autostart --random-seed={case.seed} {csc}'
            ], cwd=self.cooja_dir, stdout=logf, stderr=subprocess.STDOUT)
        wall = int(time.time() - start)
        if cooja_testlog.exists():
            shutil.copyfile(cooja_testlog, script_log)
        else:
            script_log.write_text('', encoding='utf-8')
        test_ok = 1 if self.sample_valid(case.group_label, script_log) else 0
        self.append_row([
            self.platform, case.group_label, case.scene_label, case.scale, case.seed,
            str(proc.returncode), str(test_ok), str(wall), str(log), str(script_log)
        ])
        self.update_tracker()
        print(f'[{idx}/{total}] platform={self.platform} group={case.group_label} scene={case.scene_label} scale={case.scale} seed={case.seed} status={proc.returncode} testok={test_ok} wall={wall}s')
        if test_ok:
            self.done_cases.add(case.done_key)

    def validate_group(self, group: str) -> None:
        symbol = self.check_exp_symbol()
        print(f'symbol_check={symbol}')
        if group == 'baseline' and symbol != 'OFF':
            raise RuntimeError('baseline symbol check failed')
        if group != 'baseline' and symbol != 'ON':
            raise RuntimeError(f'edge-gate symbol check failed for {group}')

    def run(self) -> int:
        self.ensure_dirs()
        self.backup_conf()
        try:
            self.load_existing_cases()
            self.update_tracker()
            cases = self.build_cases()
            print(f'pending_cases={len(cases)}')
            if not cases:
                print(f'done: {self.csv_path}')
                return 0
            by_group: Dict[str, List[Case]] = {}
            for case in cases:
                by_group.setdefault(case.group, []).append(case)
            idx = 0
            total = len(cases)
            for group in self.groups:
                group_cases = by_group.get(group, [])
                print(f'=== configure group: {group} ===')
                self.set_group_mode(group)
                self.validate_group(group)
                for case in group_cases:
                    idx += 1
                    self.run_case(case, idx, total)
            self.update_tracker()
            print(f'done: {self.csv_path}')
            return 0
        finally:
            self.restore_conf()


def main() -> int:
    runner = Runner()
    return runner.run()

if __name__ == '__main__':
    raise SystemExit(main())
