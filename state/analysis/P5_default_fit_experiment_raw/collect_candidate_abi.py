"""Compare checked candidate and baseline DWARF without an inferior or target connection."""
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
types = ['edge::Escape', 'edge::EscapeSample', 'fsm::Robot', 'fsm::RobotInput',
         'fsm::RobotResult', 'fsm::Robot::Pending', 'fsm::Robot::Tick',
         'app::Runtime', 'app::Transaction', 'app::TransactionReport']
members = {
    'edge::Escape': ['guard_', 'row_', 'current_', 'fault_', 'last_heading_deg_',
        'episode_data_', 'previous_mask_', 'selected_mask_', 'pivot_direction_',
        'episode_', 'pushed_out_'],
    'fsm::Robot': ['lifecycle_', 'escape_', 'fusion_', 'direct_', 'flank_', 'wait_',
        'result_', 'pending_', 'tick_', 'statistics_', 'state_', 'recording_incomplete_'],
    'app::Runtime': ['motor_port_', 'transaction_', 'dump_', 'adc_', 'estimator_',
        'calibration_', 'grants_', 'report_', 'decision_input_', 'decision_line_',
        'previous_state_', 'pending_token_', 'calibration_output_', 'output_stall_us_'],
    'app::Transaction': ['port_', 'gate_', 'robot_', 'recorder_', 'report_', 'previous_', 'last_decision_us_'],
}
profiles = [('candidate1', out / 'app_attempt02/receipt/verified.json'),
            ('D134_default', root / 'state/analysis/P5_native_compile_raw/app/receipt/verified.json')]
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
        for name in names + (['zero_window_active_'] if label == 'candidate1' and typename == 'edge::Escape' else []):
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
    result = subprocess.run(prefix + [shlex.join(args)], capture_output=True, text=True, timeout=60)
    record = {'utc': datetime.now(timezone.utc).isoformat(), 'source_sha256': receipt['source_sha256'],
        'scope': 'File-only checked ELF DWARF; no inferior, target, MCU or compilation',
        'hash_args': hash_args, 'hash_returncode': hashed.returncode, 'hash_stdout': hashed.stdout,
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
    summary[label] = {'types': sizes, 'member_offsets': offsets}
summary['existing_sizes_alignments_identical'] = summary['candidate1']['types'] == summary['D134_default']['types']
summary['existing_member_offsets_identical'] = all(
    summary['candidate1']['member_offsets'][name] == value
    for name, value in summary['D134_default']['member_offsets'].items())
(out / 'abi_comparison.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
