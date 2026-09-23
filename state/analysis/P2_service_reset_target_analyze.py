# Audit the frozen D103 target source, retained paths, ABI and loader allocations.
# Reuse the earlier offline ELF routines with an explicit new 87-file invariant.
# Preserve all historical checks and distinguish this model from runtime evidence.
import ast
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'state/analysis/P2_service_reset_raw'
REVIEW = ROOT / 'state/reviews/P2_bridge_dependency_review_raw'
SOURCE = '1fbd72385c9a729be869bebaaabcc28b5614aa8ff23616843d7b2809a187301f'
sys.path.insert(0, str(REVIEW))
from elf_review import Elf

prior_path = ROOT / 'state/analysis/P2_app_dump_raw/target_analyze.py'
tree = ast.parse(prior_path.read_text())
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
audit_node = next(node for node in functions if node.name == 'audit_folder')
counts = [node for node in ast.walk(audit_node) if isinstance(node, ast.Constant) and node.value == 85]
assert len(counts) == 2, 'The reused D101 audit must retain its two explicit source-count invariants'
for node in counts:
    node.value = 87
scope = dict(ROOT=ROOT, OUT=OUT, REVIEW=REVIEW, Path=Path, json=json, ast=ast,
             hashlib=hashlib, re=re, struct=struct, Elf=Elf)
exec(compile(ast.Module(body=functions, type_ignores=[]), str(prior_path), 'exec'), scope)
scope['prior_function'] = scope['load_function']('verify_elfs.py', 'function')
scope['relocations'] = scope['load_function']('compare_objects.py', 'relocations')
base = ROOT / 'state/analysis/P2_app_acceptance_raw/bench-default'
scope['baseline'] = json.loads((base / 'audit.json').read_text())
scope['baseline_elf'] = Elf(base / 'app.ino.elf')
order_path = ROOT / 'state/analysis/P2_frame_packing_target_analyze.py'
order = next(n for n in ast.parse(order_path.read_text()).body
             if isinstance(n, ast.FunctionDef) and n.name == 'allocation_order')
exec(compile(ast.Module(body=[order], type_ignores=[]), str(order_path), 'exec'), scope)

EXPECTED_CHANGED = ['src/app/runtime.cpp', 'src/app/runtime.h', 'src/app/runtime_inputs.cpp',
    'src/app/runtime_service.cpp', 'src/app/transaction.cpp', 'src/app/transaction.h',
    'src/app/transaction_service.cpp', 'src/hal/ui_display.cpp', 'src/hal/ui_display.h']
SERVICE = ['_ZN3app7Runtime4stepEv', '_ZN3app7Runtime17applyServiceResetEv', '_ZN3app7Runtime19observeServiceResetEv',
    '_ZN3app7Runtime16pendServiceResetEv', '_ZN3app7Runtime11serviceNoneEj',
    '_ZN3app7Runtime11serviceModeEj', '_ZN3app7Runtime22checkServiceContinuityEj',
    '_ZN3app11Transaction27resetStoppedRobotForServiceEv',
    '_ZN3app11Transaction25rememberStoppedCompletionEv', '_ZN3fsm5Robot5resetEv']
builds = {}
for mode in ('bench-default', 'match-immediate'):
    folder = OUT / ('target_1fbd7238_' + mode)
    audit = json.loads((folder / 'audit.json').read_text())
    assert audit['source_sha256'] == SOURCE and audit['mode'] == mode
    result = scope['audit_folder'](folder)
    current = Elf(folder / 'app.ino.elf')
    old_folder = ROOT / ('state/analysis/P2_frame_packing_raw/target_3bf0da00_' + mode)
    old_audit = json.loads((old_folder / 'audit.json').read_text())
    old = Elf(old_folder / 'app.ino.elf').account()
    assert not old_audit['source_files'].keys() - audit['source_files'].keys()
    changed = [n for n, h in audit['source_files'].items() if old_audit['source_files'].get(n) != h]
    assert changed == EXPECTED_CHANGED
    assert sorted(audit['source_files'].keys() - old_audit['source_files'].keys()) == [
        'src/app/runtime_service.cpp', 'src/app/transaction_service.cpp']
    result['d102_changed_source_files'] = changed
    result['service_functions'] = {name: scope['function'](current, name) for name in SERVICE}
    assert result['owners']['_ZN12_GLOBAL__N_17runtimeE'] == 166304
    result['allocation_order'] = scope['allocation_order'](result['memory']['account'])
    assert result['memory']['temporary_symbols_fit'] and result['memory']['complete_peak_deficit'] == 0
    scope['baseline'] = old_audit
    result['d102_same_mode_objects'] = scope['compare_objects'](audit)
    scope['baseline'] = json.loads((base / 'audit.json').read_text())
    result['d102_memory_change'] = dict(previous=old,
        compiler_payload_increase=result['memory']['account']['compiler_payload']-old['compiler_payload'],
        conditional_peak_increase=result['memory']['account']['conditional_pristine_peak_consumption']-
                                  old['conditional_pristine_peak_consumption'])
    builds[mode] = result

# Mode differences may affect only MotorGate's expected compile-time branches.
default_audit = json.loads((OUT / 'target_1fbd7238_bench-default/audit.json').read_text())
match_audit = json.loads((OUT / 'target_1fbd7238_match-immediate/audit.json').read_text())
scope['baseline'] = default_audit
mode_objects = scope['compare_objects'](match_audit)
assert not mode_objects['added_objects']
assert mode_objects['changes'] == [
    dict(path='sketch/src/hal/motor_port_unoq.cpp.o', changed=[
        '.text._ZN6motors8UnoQPort11writeEnableEPvb',
        '.text._ZN6motors8UnoQPort8writePwmEPvNS_7ChannelEjj'], added=[], removed=[]),
    dict(path='sketch/src/hal/motors.cpp.o', changed=[
        '.text._ZN6motors9MotorGate8transactERKN4core7OutputsERN3fsm12PreviousTickE'],
         added=[], removed=[])]
for name in SERVICE:
    for key in ('normalized_bytes_hex', 'relocations', 'bss_targets'):
        assert builds['bench-default']['service_functions'][name][key] == builds['match-immediate']['service_functions'][name][key]

abi_dir = OUT / 'target_abi_caller_path'
abi_run = json.loads((abi_dir / 'receipt.json').read_text())
abi_data = json.loads((abi_dir / 'stdout.json').read_text())
assert abi_run['returncode'] == 0 and not (abi_dir / 'stderr.txt').read_text()
assert abi_run['source_sha256'] == SOURCE
assert all(c['returncode'] == 0 and not c['stderr'] for c in abi_data['commands'])
verified = json.loads((OUT / 'target_1fbd7238_bench-default/build_receipt/verified.json').read_text())
for path, digest in abi_data['file_sha256'].items():
    if path in verified['file_sha256']:
        assert digest == verified['file_sha256'][path]
values = [int(v) for v in re.findall(r'^\$\d+ = (\d+)$', abi_data['commands'][0]['stdout'], re.M)]
assert values == [166304, 8, 162544, 8, 2640, 8, 159200, 126300]
types = dict(Runtime=dict(size=values[0], alignment=values[1]),
             Transaction=dict(size=values[2], alignment=values[3]),
             Robot=dict(size=values[4], alignment=values[5]),
             AttemptRecorder=dict(size=values[6]), FrameBuffer=dict(size=values[7]))
disassembly = {c['argv'][-2].removeprefix('--disassemble='): c['stdout'] for c in abi_data['commands']
               if '--disassemble=' in c['argv'][-2]}
robot_reset = disassembly['_ZN3fsm5Robot5resetEv']
assert 'stmdb\tsp!, {r4, r5, r6, r7, r8, r9, sl, fp, lr}' in robot_reset
assert re.search(r'subw\s+sp, sp, #2644', robot_reset)
assert re.search(r'addw\s+sp, sp, #2644', robot_reset)
assert 'push\t{r3, r4, r5, r6, r7, lr}' in disassembly['_ZN3app11Transaction27resetStoppedRobotForServiceEv']
assert 'stmdb\tsp!, {r0, r1, r4, r5, r6, r7, r8, lr}' in disassembly['_ZN3app7Runtime17applyServiceResetEv']
assert 'push\t{r0, r1, r2, r3, r4, r5, r6, lr}' in disassembly['_ZN3app7Runtime4stepEv']
for caller, callee in [('_ZN3app7Runtime4stepEv', '_ZN3app7Runtime17applyServiceResetEv'),
    ('_ZN3app7Runtime17applyServiceResetEv', '_ZN3app11Transaction27resetStoppedRobotForServiceEv'),
    ('_ZN3app11Transaction27resetStoppedRobotForServiceEv', '_ZN3fsm5Robot5resetEv')]:
    assert any(r['name'] == callee for r in builds['bench-default']['service_functions'][caller]['relocations'])
stack_text = abi_data['commands'][1]['stdout']
assert '$1 = 32768' in stack_text and '$2 = 262144' in stack_text
assert '$3 = (const void * const) 0x0' in stack_text
loader_name = next(n for n in disassembly if n.startswith('loader.'))
assert '<llext_bootstrap>' in disassembly[loader_name]
assert 'blx\tr6' in disassembly['llext_bootstrap']
assert '<' + loader_name + '>' in disassembly['main']
assert not any('CONFIG_USERSPACE' in row or 'CONFIG_INIT_STACKS' in row for row in abi_data['config_selected'])
for name, payload in disassembly.items():
    (abi_dir / (name + '.txt')).write_text(payload)
stack = dict(robot_reset_saved_register_bytes=36, robot_reset_local_bytes=2644,
             robot_reset_direct_frame_bytes=2680, main_stack_reserved_bytes=32768,
             immediate_caller_frames=dict(transaction_reset=24, runtime_apply_service_reset=32, runtime_step=32),
             path=['installed main', loader_name, 'llext_bootstrap', 'exported sketch main',
                   'loop', 'Runtime::step', 'Runtime::applyServiceReset',
                   'Transaction::resetStoppedRobotForService', 'Robot::reset'],
             no_userspace_thread=True, stack_watermark_export_present=False,
             limitation='Direct reset frame and reserved main stack only; caller/callee/interrupt use and actual high-water/WCET remain unmeasured')
sources = json.loads((ROOT / 'state/analysis/P2_memory_validation_raw/source_receipt.json').read_text())
for source in sources:
    assert hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256']
report = dict(scope='Exact frozen source/offline ELF/target ABI and conditional loader model; no runtime qualification',
    reused_analyzer_sha256=hashlib.sha256(prior_path.read_bytes()).hexdigest(),
    reused_allocation_order_sha256=hashlib.sha256(order_path.read_bytes()).hexdigest(),
    explicit_source_count_adaptation=dict(previous=85, selected=87, replaced_constants=2),
    pinned_source_receipts=sources, builds=builds, mode_object_comparison=mode_objects,
    target_types=types, reset_stack=stack,
    abi_receipt_sha256=hashlib.sha256((abi_dir / 'receipt.json').read_bytes()).hexdigest())
(OUT / 'target_summary.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({name: dict(payload=r['memory']['account']['compiler_payload'],
    peak=r['memory']['account']['conditional_pristine_peak_consumption'],
    largest=r['memory']['conditional_largest_after_peak'], runtime=r['owners']['_ZN12_GLOBAL__N_17runtimeE'])
    for name, r in builds.items()}, indent=2))
