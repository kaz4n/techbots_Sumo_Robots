"""Compare current default, historical D134 default and current MATCH DWARF without an inferior or target connection."""
from pathlib import Path
from datetime import datetime, timezone
import json
import os
import re
import shlex
import subprocess

out = Path(__file__).resolve().parent
root = out.parents[2]
adb = str(Path(os.environ['LOCALAPPDATA']) / 'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
gdb = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-gdb'
types = ['countdown::Buttons', 'countdown::Controller', 'countdown::Lifecycle',
         'edge::Escape', 'fsm::Robot', 'fsm::RobotInput', 'fsm::RobotResult',
         'fsm::Robot::Pending', 'fsm::Robot::Tick', 'app::Runtime', 'app::Transaction',
         'app::TransactionReport', 'ui::DisplaySample', 'ui::Frame',
         'recorder::AttemptRecorder', 'recorder::FrameBuffer']
members = {
    'countdown::Buttons': ['candidate_', 'stable_', 'candidate_since_us_', 'initialized_', 'armed_', 'pressed_'],
    'countdown::Controller': ['stop_', 'buttons_', 'gate_', 'events_', 'logical_stop_'],
    'countdown::Lifecycle': ['controller_', 'services_', 'pending_', 'service_start_failed_'],
    'fsm::Robot': ['lifecycle_', 'escape_', 'fusion_', 'direct_', 'flank_', 'wait_',
        'result_', 'pending_', 'tick_', 'statistics_', 'state_', 'recording_incomplete_'],
    'fsm::RobotResult': ['token', 'fresh', 'outputs', 'menu', 'lifecycle', 'heading',
        'events', 'frame', 'frame_token', 'ticks', 'line_available', 'button_updated', 'button_sequence'],
    'app::Runtime': ['motor_port_', 'transaction_', 'dump_', 'adc_', 'estimator_',
        'calibration_', 'grants_', 'report_', 'decision_input_', 'decision_line_',
        'previous_state_', 'pending_token_', 'line_age_us_'],
    'app::Transaction': ['port_', 'gate_', 'robot_', 'recorder_', 'report_', 'previous_', 'last_decision_us_'],
    'app::TransactionReport': ['phase', 'robot', 'applied', 'halt', 'recorded'],
    'ui::DisplaySample': ['t_us', 'state', 'battery_available', 'battery_v', 'faults',
        'calibration_samples', 'service_unavailable'],
}
default_runtime_members = ['calibration_output_', 'output_bank_', 'output_last_token_',
    'output_decision_us_', 'output_observed_us_', 'output_total_us_', 'output_stall_us_']
profiles = [('current_default', out / 'app/receipt/verified.json'),
            ('D134_default', root / 'state/analysis/P5_native_compile_raw/app/receipt/verified.json'),
            ('D138_MATCH', root / 'state/analysis/P7_readiness_native_raw/app/receipt/verified.json')]
summary = {}
for label, receipt_path in profiles:
    folder = out / (label + '_abi')
    folder.mkdir(exist_ok=False)
    receipt = json.loads(receipt_path.read_text())
    elf = receipt['build_path'] + '/app.ino_debug.elf'
    queries = ['set language c++', 'set max-value-size unlimited']
    for typename in types:
        queries += ['echo TYPE ' + typename + '\\n', 'p sizeof(' + typename + ')',
                    'p alignof(' + typename + ')', 'ptype /o ' + typename]
    for typename, names in members.items():
        extra = ['match_start_eligible'] if typename == 'fsm::RobotResult' else ['start_status_available', 'start_ready'] if typename == 'ui::DisplaySample' else []
        profile_members = default_runtime_members if typename == 'app::Runtime' and label != 'D138_MATCH' else []
        for name in names + profile_members + (extra if label != 'D134_default' else []):
            queries += ['echo MEMBER ' + typename + ' ' + name + '\\n',
                        'p/d (unsigned long)&((' + typename + '*)0)->' + name]
    args = [gdb, '-nx', '-nh', '-batch', elf]
    for query in queries:
        args.extend(['-ex', query])
    prefix = [adb, '-s', '2629958581', 'shell', '-T']
    hash_args = ['sha256sum', '--', gdb, elf]
    hashed = subprocess.run(prefix + [shlex.join(hash_args)], capture_output=True, text=True, timeout=30)
    assert hashed.returncode == 0
    assert hashed.stdout.splitlines()[1].split()[0] == receipt['file_sha256'][elf]
    assert hashed.stdout.splitlines()[0].split()[0] == json.loads((root / 'state/analysis/P7_readiness_native_raw/inventory.json').read_text())['gdb_sha256']
    result = subprocess.run(prefix + [shlex.join(args)], capture_output=True, text=True, timeout=60)
    record = {'utc': datetime.now(timezone.utc).isoformat(), 'source_sha256': receipt['source_sha256'],
        'scope': 'File-only checked ELF DWARF; no inferior, target, MCU or compilation',
        'hash_args': hash_args, 'hash_returncode': hashed.returncode, 'hash_stdout': hashed.stdout,
        'hash_stderr': hashed.stderr, 'expected_debug_elf_sha256': receipt['file_sha256'][elf],
        'argv': args, 'returncode': result.returncode}
    (folder / 'stdout.txt').write_text(result.stdout)
    (folder / 'stderr.txt').write_text(result.stderr)
    (folder / 'receipt.json').write_text(json.dumps(record, indent=2) + '\n')
    assert result.returncode == 0, result.stderr
    sizes = {name: {'sizeof': int(size), 'alignof': int(align)} for name, size, align in
        re.findall(r'TYPE (\S+)\s+\$\d+ = (\d+)\s+\$\d+ = (\d+)', result.stdout)}
    offsets = {name + '::' + member: int(value) for name, member, value in
        re.findall(r'MEMBER (\S+) (\S+)\s+\$\d+ = (\d+)', result.stdout)}
    assert len(sizes) == len(types)
    assert len(offsets) == sum(len(names) for names in members.values()) + (3 if label != 'D134_default' else 0) + (len(default_runtime_members) if label != 'D138_MATCH' else 0)
    summary[label] = {'types': sizes, 'member_offsets': offsets}
summary['comparison'] = {}
for label in ('D134_default', 'D138_MATCH'):
    summary['comparison'][label] = {
        'types': {name: {'current': summary['current_default']['types'][name], 'baseline': values}
                  for name, values in summary[label]['types'].items()},
        'changed_common_offsets': {name: {'current': summary['current_default']['member_offsets'][name], 'baseline': value}
            for name, value in summary[label]['member_offsets'].items()
            if name in summary['current_default']['member_offsets'] and summary['current_default']['member_offsets'][name] != value},
    }
(out / 'abi_comparison.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary['comparison'], indent=2))
