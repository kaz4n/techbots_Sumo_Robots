"""Recheck collected app modes against D098 and its reusable offline ELF decoder."""
import ast
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
REVIEW = ROOT / 'state/reviews/P2_bridge_dependency_review_raw'
sys.path.insert(0, str(REVIEW))
from elf_review import Elf


def load_function(filename, name):
    tree = ast.parse((REVIEW / filename).read_text())
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
    assert len(nodes) == 1
    scope = dict(re=re, struct=struct)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(REVIEW / filename), 'exec'), scope)
    return scope[name]


relocations = load_function('compare_objects.py', 'relocations')
function = load_function('verify_elfs.py', 'function')
BASE = ROOT / 'state/analysis/P2_bridge_dependency_raw'
baseline = json.loads((BASE / 'target_570ef35f_candidate.json').read_text())
baseline_elf = Elf(BASE / 'candidate_elf/app.ino.elf')
project = re.compile(r'^_ZNK?(?:3app|3imu|5power|6motors|8line_qtr|11opp_sensors|2ui|8recorder|3fsm|4edge|9countdown|10opp_fusion|8governor|6motion|7openers|5stall|8logframe|7qtr_cal)')
STARTUP = ('main', 'setup', 'loop', 'initVariant', '_Z10__loopHookv',
           '_Z20start_static_threadsv', '_GLOBAL__sub_I_setup')


def object_comparison(audit):
    before = {obj['path']: obj for obj in baseline['objects']}
    after = {obj['path']: obj for obj in audit['objects']}
    assert before.keys() == after.keys()
    rows = []
    for name in sorted(before):
        old = {s['name']: s for s in before[name]['alloc_sections']}
        new = {s['name']: s for s in after[name]['alloc_sections']}
        old_r = relocations(before[name]['relocations']['stdout'])
        new_r = relocations(after[name]['relocations']['stdout'])
        common = old.keys() & new.keys()
        rows.append(dict(path=name, common_sections=len(common),
            changed=[s for s in sorted(common) if old[s] != new[s]],
            relocation_changed=[s for s in sorted(common) if old_r.get(s, []) != new_r.get(s, [])],
            removed=sorted(old.keys() - new.keys()), added=sorted(new.keys() - old.keys())))
    return dict(objects=len(rows), common_sections=sum(row['common_sections'] for row in rows),
                changed_objects=[row for row in rows if any(row[key] for key in
                                 ('changed', 'relocation_changed', 'removed', 'added'))], details=rows)


def metadata_checks(audit, mode):
    flags = ('-DMATCH=1', '-DMOTORS_ALLOWED=1') if mode.startswith('match') else ('-DMATCH=0', '-DMOTORS_ALLOWED=0')
    commands = json.loads(audit['metadata']['compile_commands.json']['text'])
    for command in commands:
        assert all(flag in command['arguments'] for flag in flags)
        if not command['file'].endswith('/tls-syms.S'):
            assert '-DARDUINO_LIBRARY_DISCOVERY_PHASE=0' in command['arguments']
        assert not any('/Arduino/libraries/' in arg for arg in command['arguments'])
    forbidden = ('Arduino_RouterBridge', 'Arduino_RPClite', 'MsgPack', 'DebugLog', 'ArxTypeTraits', 'ArxContainer')
    for name, entry in audit['metadata'].items():
        data = entry['text'].encode()
        assert len(data) == entry['bytes'] and hashlib.sha256(data).hexdigest() == entry['sha256']
        if name.endswith('.d'):
            assert not any(token in entry['text'] for token in forbidden), name
    assert audit['metadata']['sketch/app.ino.cpp']['sha256'] == baseline['metadata']['sketch/app.ino.cpp']['sha256']
    return dict(commands=len(commands), dependency_files=sum(n.endswith('.d') for n in audit['metadata']),
                metadata_files=len(audit['metadata']), generated_ino_sha256=audit['metadata']['sketch/app.ino.cpp']['sha256'])


def native_checks(audit):
    assert audit['source_files'] == baseline['source_files']
    assert audit['base_sha256'] == baseline['base_sha256']
    for key in ('native_names', 'math_aliases', 'math_symbols', 'math_missing', 'base_static_threads'):
        assert audit[key] == baseline[key], key
    for key in ('native_exports', 'math_exports'):
        assert audit[key]['returncode'] == 0
        assert audit[key]['stdout'] == baseline[key]['stdout']
        values = re.findall(r'^\$\d+ = (0x[0-9a-f]+)$', audit[key]['stdout'], re.M)
        count = len(audit['native_names']) if key == 'native_exports' else len(audit['math_symbols'])
        assert len(values) == count and all(int(value, 16) > 0 for value in values)
    return dict(native=len(audit['native_names']), aeabi=len(audit['math_symbols']),
                unchanged_loader=audit['base_sha256'], static_threads=audit['base_static_threads'])


def elf_checks(audit, folder):
    entries = []
    for record in audit['records']:
        path = folder / Path(record['path']).name
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == record['sha256']
        elf = Elf(path)
        undefined = sorted({s['name'] for s in elf.symbols if s['section_index'] == 0 and s['name']})
        assert undefined == sorted(line.split()[-1] for line in record['undefined']['stdout'].splitlines())
        assert undefined == sorted({s['name'] for s in baseline_elf.symbols if s['section_index'] == 0 and s['name']})
        entries.append(dict(name=path.name, sha256=record['sha256'], bytes=len(data), imports=len(undefined)))
    elf = Elf(folder / 'app.ino.elf')
    account = elf.account()
    assert len(account['init']) == 1 and account['init'][0]['name'] == '_GLOBAL__sub_I_setup'
    assert not account['fini']
    startup = {name: function(elf, name) for name in STARTUP}
    for name, entry in startup.items():
        old = function(baseline_elf, name)
        for key in ('normalized_bytes_hex', 'relocations', 'bss_targets'):
            assert entry[key] == old[key], (folder.name, name, key)
    assert startup['_Z10__loopHookv']['symbol']['bind'] == 1
    assert startup['_Z10__loopHookv']['bytes_hex'] == '7047'
    assert 'main' in [r['name'] for r in elf.relocations if r['section'] == '.exported_sym']
    owners = {name: next(s['size'] for s in elf.symbols if s['name'] == name)
              for name in ('_ZN12_GLOBAL__N_17runtimeE', '_ZN12_GLOBAL__N_17sourcesE')}
    assert owners == {'_ZN12_GLOBAL__N_17runtimeE': 168888, '_ZN12_GLOBAL__N_17sourcesE': 848}
    assert all(not any(token in s['name'] for token in ('Bridge', 'msgpack', 'Rpc', 'RPC', 'ZephyrSerial')) for s in elf.symbols)
    old_project = {s['name'] for s in baseline_elf.symbols if s['type'] == 2 and project.match(s['name'])}
    new_project = {s['name'] for s in elf.symbols if s['type'] == 2 and project.match(s['name'])}
    assert not old_project - new_project
    added_functions = sorted(elf.functions().keys() - baseline_elf.functions().keys())
    return dict(elfs=entries, account=account, startup=startup, owners=owners,
                retained_project_functions=len(old_project), project_functions=len(new_project),
                added_project_functions=sorted(new_project - old_project),
                added_functions={name: function(elf, name) for name in added_functions})


def package_checks(audit, folder):
    elf = (folder / 'app.ino.elf').read_bytes()
    packaged = (folder / 'app.ino.elf-zsk.bin').read_bytes()
    assert len(elf) == len(packaged) and elf[16:] == packaged[16:]
    command = audit['properties']['recipe.hooks.objcopy.postobjcopy.1.pattern']
    immediate = folder.name.endswith('immediate')
    assert ('-immediate' in command) == immediate
    default = OUT / 'bench-default/app.ino.elf-zsk.bin'
    changes = []
    if folder.name == 'bench-immediate':
        before = default.read_bytes()
        changes = [dict(offset=i, before=a, after=b) for i, (a, b) in enumerate(zip(before, packaged)) if a != b]
        assert changes == [dict(offset=14, before=0, after=4)]
    return dict(bytes=len(packaged), sha256=hashlib.sha256(packaged).hexdigest(),
                header_hex=packaged[:16].hex(), body_after_16_exact_elf=True,
                immediate_argument=immediate, observed_default_immediate_delta=changes)


results = {}
for mode in ('bench-default', 'bench-immediate', 'match-immediate'):
    folder = OUT / mode
    if not (folder / 'audit.json').exists():
        continue
    audit = json.loads((folder / 'audit.json').read_text())
    assert all(audit['checks'].values())
    result = dict(objects=object_comparison(audit), metadata=metadata_checks(audit, mode),
                  native=native_checks(audit), packaging=package_checks(audit, folder),
                  **elf_checks(audit, folder))
    if mode != 'match-immediate':
        assert not result['objects']['changed_objects']
        assert result['account']['sha256'] == hashlib.sha256(baseline_elf.raw).hexdigest()
    else:
        expected = {
            'sketch/src/hal/motor_port_unoq.cpp.o': [
                '.text._ZN6motors8UnoQPort11writeEnableEPvb',
                '.text._ZN6motors8UnoQPort8writePwmEPvNS_7ChannelEjj'],
            'sketch/src/hal/motors.cpp.o': [
                '.text._ZN6motors9MotorGate8transactERKN4core7OutputsERN3fsm12PreviousTickE']}
        assert {row['path']: row['changed'] for row in result['objects']['changed_objects']} == expected
        for row in result['objects']['changed_objects']:
            assert row['relocation_changed'] == row['changed'] and not row['added'] and not row['removed']
        assert set(result['added_functions']) == {'__aeabi_d2uiz'}
        assert result['added_functions']['__aeabi_d2uiz']['symbol']['size'] == 10
    results[mode] = result

report = dict(scope='Completed checked-build source/object/ELF audit, not independent review or runtime qualification',
              reused_decoder={name: hashlib.sha256((REVIEW / name).read_bytes()).hexdigest() for name in
                              ('elf_review.py', 'compare_objects.py', 'verify_elfs.py')}, modes=results)
(OUT / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({mode: dict(payload=row['account']['compiler_payload'],
    conditional_peak=row['account']['conditional_pristine_peak_consumption'],
    conditional_largest=row['account']['conditional_largest_payload'],
    changed_objects=row['objects']['changed_objects']) for mode, row in results.items()}, indent=2))
