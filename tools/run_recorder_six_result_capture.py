# Executes the fixed recorder failure capture through the reviewed D219 owner.
# Binds fresh ABI data, immutable staging and exact retrieval without reflashing.
# Focused caller fixtures cover projection, source identity, closure and refusals.
import argparse
import ast
import base64
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import types

import recorder_six_result_abi as abi
import recorder_six_result_capture as capture

ROOT = Path(__file__).absolute().parents[1]
SELF = 'tools/run_recorder_six_result_capture.py'
RAW = abi.RAW + '/'
SCOPE = RAW + 'capture_scope01.json'
DATA = RAW + 'capture_inputs01.json'
STAGED = RAW + 'capture_adapter01.py'
OUTPUT = RAW + 'native_capture01'
CONTRACT = 'state/analysis/P7_recorder_six_result_caller_contract.md'
OLD = 'tools/capture_b4_recorder.py'
OLD_PIN = (22155, 'd5042c4d13337b2cd2c4599b88af92fbb15c566601750ca82ca07b8f1ae50349')
ACTION = 'state/analysis/P7_b4_recorder_run_raw/actions.py'
ACTION_PIN = (25620, '59f1b3ba14e87796f5eafaa79f4da60e88c0d52560d8ba334ffb92fd7d18c336')
HELPER = 'state/analysis/P7_static_link_probe_raw/static_remote.py'
SUPPORT = 'state/analysis/P7_static_startup_raw/capture_remote.py'
ABI_FILES = tuple(RAW + 'native_abi01/' + name for name in ('inputs.json', 'result.json', 'local_result.json', 'abi.json'))
SELECTED = {SELF, CONTRACT, abi.SELF, 'tools/recorder_six_result_capture.py', abi.RAW + '/plan.json',
            *ABI_FILES, *(abi.COMPILE_RAW + '/' + n for n in ('inputs.json', 'result.json', 'artifacts.json', 'staged_files.json'))}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(',', ':')) + '\n').encode()


def replace_once(raw, old, new):
    require(raw.count(old) == 1, 'Reviewed projection seam differs: ' + repr(old[:80]))
    return raw.replace(old, new)


def module_from(raw, path, **injected):
    module = types.ModuleType('_recorder_capture_' + path.stem)
    module.__file__ = str(path)
    module.__dict__.update(injected)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def old_caller(root):
    raw = abi.pinned(root / OLD, OLD_PIN[1])
    require(len(raw) == OLD_PIN[0], 'D219 caller size differs')
    # No inherited lifecycle method changes: only pushed file and result schema.
    raw = replace_once(raw, b'str(self.root / "tools/b4_recorder_capture.py")',
                       b'str(self.root / STAGED)')
    raw = replace_once(raw, b'"b4-recorder-sequence-v1"', b'"recorder-failure-sequence-v1"')
    return module_from(raw, root / OLD, STAGED=STAGED)


def adapter_source(spec, source):
    require(type(source) is bytes and len(source) == 11770 and
            sha(source) == '2dfd19f72aa913660f8b32b113093047976d03c218bb793a7aa973b0d2765d5d', 'Capture helper changed')
    tail = ('\n_FIXED_SPEC = ' + repr(spec) + '\n_FIXED_SPEC_SHA = ' + repr(sha(capture.canonical(spec))) +
            '\n_fixed_collect = collect\ndef collect(dependencies, *, bindings):\n'
            '    return _fixed_collect(dependencies, spec=_FIXED_SPEC, spec_sha256=_FIXED_SPEC_SHA, input_bindings=bindings)\n')
    value = source + tail.encode()
    require(len(value) <= 1048576, 'Staged fixed adapter exceeds bound')
    return value


def verified_abi(root, digest):
    require(type(digest) is str and re.fullmatch('[0-9a-f]{64}', digest), 'Exact accepted ABI hash required')
    raw = abi.pinned(root / ABI_FILES[-1], digest)
    files = {name: (root / name).read_bytes() for name in ABI_FILES}
    values = {name.rsplit('/', 1)[1]: json.loads(body) for name, body in files.items()}
    local, result, inputs = values['local_result.json'], values['result.json'], values['inputs.json']
    require(local['status'] == 'STATIC_ABI_OBSERVED' and local['first_error'] is None and
            local['final_checks'] == [dict(name='local', status='PASS')] and
            type(local['transport_calls']) is int and local['transport_calls'] == 1,
            'ABI local closure differs')
    require(result['scope'] == 'D238_FILE_ONLY_ABI' and result['status'] == 'OBSERVED' and
            result['first_error'] is None, 'ABI remote result differs')
    parser, reader, old = (abi.verified_module(root, name) for name in (abi.D209, abi.D173, abi.D188))
    packet = json.loads((root / abi.COMPILE_RAW / 'artifacts.json').read_bytes())
    pins = {abi.OWNER + '/' + name: row['sha256'] for name, row in packet['files'].items()}
    pins.update(reader.TOOLS)
    core = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0'
    pins[core + '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'] = packet['loader']['sha256']
    pins[core + '/variants/arduino_uno_q_stm32u585xx/tls-syms.S'] = packet['tls_source']['sha256']
    require(result['final_checks'] == [dict(path=name, status='PASS') for name in pins] +
            [dict(path='board_identity', status='PASS')], 'ABI remote closure differs')
    require(inputs['remote_pins'] == pins and len(pins) == 12 and inputs['source_sha256'] == abi.SOURCE and
            inputs['compile_head'] == abi.COMPILE_HEAD and inputs['boot_id'] == abi.BOOT and
            inputs['commands'] == abi.queries(reader), 'ABI inputs differ from exact recorder image')
    observed = abi.summarize(result, packet['layout']['validator_report'], parser, reader, old.checked_command)
    require(capture.same(observed, json.loads(raw)), 'ABI summary differs from original file-tool results')
    spec = capture.build_spec(raw, digest, abi)
    return spec, files


def prepare_bindings(root, digest):
    root = Path(root).absolute()
    require(sys.dont_write_bytecode and all(not os.path.lexists(root / n) for n in (SCOPE, DATA, STAGED)),
            'Use Python -B and an unused capture binding owner')
    spec, evidence = verified_abi(root, digest)
    legacy = old_caller(root)
    source = adapter_source(spec, (root / 'tools/recorder_six_result_capture.py').read_bytes())
    files = {name: dict(bytes=(root / name).stat().st_size, sha256=sha((root / name).read_bytes())) for name in sorted(SELECTED)}
    pin = dict(path=capture.bindings()['output'] + '-adapter/remote.py', bytes=len(source), sha256=sha(source))
    data = dict(schema='recorder-failure-capture-inputs-v1', abi_sha256=digest, spec=spec,
                spec_sha256=sha(capture.canonical(spec)), adapter_pin=pin, files=files)
    data_raw = canonical(data)
    scope_files = {name: pin['sha256'] for name, pin in files.items()}
    scope_files.update({DATA: sha(data_raw), STAGED: sha(source)})
    scope = dict(schema='recorder-failure-native-scope-v1', run_id=capture.RUN_ID, board='2629958581',
                 source_sha256=abi.SOURCE, expected_identity=legacy.actions.EXPECTED_IDENTITY, files=scope_files)
    for name, body in ((STAGED, source), (DATA, data_raw), (SCOPE, canonical(scope))):
        with (root / name).open('xb') as target:
            target.write(body)
    return dict(status='BINDINGS_PREPARED_OFFLINE', files=[STAGED, DATA, SCOPE], spec_sha256=data['spec_sha256'])


def project_actions(actions, spec, pin):
    old_run, old_source = actions.RUN_ID, actions.SOURCE
    bootstrap = actions._BOOTSTRAP_SOURCE.replace(old_run, capture.RUN_ID).replace(old_source, abi.SOURCE)
    bootstrap = replace_once(bootstrap, 'fixed-b4-recorder-capture-v1', 'fixed-recorder-failure-capture-v1')
    bootstrap = replace_once(bootstrap, 'b4-recorder-action-v1', 'recorder-failure-action-v1')
    bootstrap = replace_once(bootstrap, str(actions.ADAPTER_BYTES), str(pin['bytes']))
    bootstrap = replace_once(bootstrap, actions.ADAPTER_SHA, pin['sha256'])
    plan = capture.read_plan(spec)
    ram_end, files_count = len(plan) - 6, len(plan) - 11
    counts = dict(commands=len(plan), reads=len(plan), requested_bytes=sum(row[2] for row in plan))
    text = actions._RETRIEVAL_SOURCE
    lines = text.splitlines(keepends=True)
    replacements = {'OUTPUT': capture.bindings()['output'], 'RUN_ID': capture.RUN_ID,
                    'SOURCE': abi.SOURCE, 'PLAN': plan, 'COUNTS': counts}
    for node in reversed(ast.parse(text).body):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in replacements:
            key = node.targets[0].id
            lines[node.lineno - 1:node.end_lineno] = [key + '=' + repr(replacements[key]) + '\n']
    text = ''.join(lines)
    for old, new in [('b4-recorder-capture-result-v1', 'recorder-failure-capture-result-v1'),
                     (" and report['wait'] is None", ''), ('len(reads)==26', 'len(reads)==' + str(len(plan))),
                     ('range(7,19)', 'range(6,' + str(ram_end) + ')'),
                     ("'closing_file_checks':13", "'closing_file_checks':" + str(files_count))]:
        text = replace_once(text, old, new)
    actions.RUN_ID, actions.SOURCE, actions.OUTPUT = capture.RUN_ID, abi.SOURCE, capture.bindings()['output']
    actions.BINDINGS, actions.PLAN = capture.bindings(), plan
    actions.ADAPTER_PIN, actions.ADAPTER_BYTES, actions.ADAPTER_SHA = pin, pin['bytes'], pin['sha256']
    actions.ADAPTER = pin['path']
    actions._BOOTSTRAP_SOURCE, actions._RETRIEVAL_SOURCE = bootstrap, text
    return plan, counts


def validate_reply(reply, legacy, plan, counts):
    actions = legacy.actions
    actions.keys(reply, ('schema', 'action', 'run_id', 'source_sha256', 'report', 'report_origin',
                        'remote_result_path', 'full_result_bytes', 'full_result_sha256', 'first_error', 'postcheck_errors'))
    expected = dict(schema='recorder-failure-action-v1', action='capture', run_id=capture.RUN_ID,
                    source_sha256=abi.SOURCE, report_origin='returned', first_error=None, postcheck_errors=[],
                    remote_result_path=capture.bindings()['output'] + '/capture_result.json')
    require(all(actions.same(reply[k], v) for k, v in expected.items()) and len(canonical(reply)) <= 65536,
            'Capture envelope differs')
    report = reply['report']; raw = canonical(report)
    require(type(reply['full_result_bytes']) is int and reply['full_result_bytes'] == len(raw) <= 65536 and
            reply['full_result_sha256'] == sha(raw), 'Capture report identity differs')
    actions.keys(report, ('schema', 'run_id', 'source_sha256', 'status', 'counts', 'started_utc', 'finished_utc',
        'started_monotonic', 'finished_monotonic', 'wait', 'reads', 'first_error', 'postcheck_errors', 'analysis'))
    expected = dict(schema='recorder-failure-capture-result-v1', run_id=capture.RUN_ID, source_sha256=abi.SOURCE,
                    status='COLLECTED', counts=counts, first_error=None, postcheck_errors=[])
    require(all(actions.same(report[k], v) for k, v in expected.items()), 'Capture completion differs')
    finite = legacy.helpers.finite
    start, end = finite(report['started_monotonic']), finite(report['finished_monotonic'])
    wait = report['wait']; actions.keys(wait, ('requested_seconds', 'before', 'after'))
    require(type(wait['requested_seconds']) is int and wait['requested_seconds'] == 2 and
            0 <= end - start < 600 and start <= finite(wait['before']) <= finite(wait['after']) <= end and
            wait['after'] - wait['before'] >= 2, 'Capture timing bracket differs')
    require(type(report['reads']) is list and len(report['reads']) == len(plan), 'Capture read count differs')
    for i, (row, (name, address, size)) in enumerate(zip(report['reads'], plan)):
        actions.keys(row, ('name', 'address', 'bytes', 'sha256', 'file'))
        require(all(actions.same(row[k], v) for k, v in dict(name=name, address=address, bytes=size,
                file='{:02d}-{}.bin'.format(i, name)).items()) and
                type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']), 'Capture read differs')
    flash = report['analysis']['flash']
    require(set(flash) == set(capture.FLASH_KEYS) and all(v is True for v in flash.values()) and
            report['analysis']['coherence'] == 'UNPROVEN' and report['analysis']['decode_errors'] == [], 'Capture analysis failed')
    for i in range(6):
        other = len(plan) - 5 + i if i < 5 else len(plan) - 6
        require(report['reads'][i]['sha256'] == report['reads'][other]['sha256'], 'Flash brackets differ')
    return report


def export_packet(owner, packet, reply, legacy, spec, plan):
    a = legacy.actions
    a.keys(packet, ('status', 'identity_before', 'identity_after', 'files', 'closing_file_checks'))
    selected = list(range(6, len(plan) - 6))
    require(packet['status'] == 'FILE_ONLY_RESULTS_VERIFIED' and a.same(packet['identity_before'], a.EXPECTED_IDENTITY) and
            a.same(packet['identity_after'], a.EXPECTED_IDENTITY) and type(packet['closing_file_checks']) is int and
            packet['closing_file_checks'] == len(selected) + 1 and len(packet['files']) == len(selected) + 1,
            'Retrieval closure differs')
    names = [('capture_result.json', None)] + [('{:02d}-{}.bin'.format(i, plan[i][0]), plan[i][2]) for i in selected]
    files = {}
    for row, (name, size) in zip(packet['files'], names):
        a.keys(row, ('path', 'bytes', 'sha256', 'data_base64'))
        require(row['path'] == a.OUTPUT + '/' + name and type(row['bytes']) is int and
                0 < row['bytes'] <= 65536 and (size is None or size == row['bytes']) and
                type(row['data_base64']) is str and len(row['data_base64']) <= 87384, 'Retrieved file differs')
        body = base64.b64decode(row['data_base64'], validate=True)
        require(base64.b64encode(body).decode() == row['data_base64'] and len(body) == row['bytes'] and sha(body) == row['sha256'],
                'Retrieved bytes differ')
        files[name] = body
    require(sum(map(len, files.values())) <= 262144 and files['capture_result.json'] == canonical(reply['report']),
            'Durable report differs')
    samples = []
    for i in selected:
        row = reply['report']['reads'][i]; body = files[row['file']]
        require(sha(body) == row['sha256'], 'Raw status differs from report')
        samples.append((row['name'], row['address'], body))
    observed = capture.analysis(spec, samples, reply['report']['analysis']['flash'])
    require(a.same(observed, reply['report']['analysis']), 'Raw status analysis differs')
    owner.write_bytes('capture_envelope.json', canonical(reply))
    for name, body in files.items():
        owner.write_bytes(name, body)
    result = dict(bundle_status='PASS', coherence='UNPROVEN', analysis=observed,
                  files={name: dict(bytes=len(body), sha256=sha(body)) for name, body in files.items()})
    owner.write('export.json', result); owner.local()
    return result


def owner_type(root):
    root = Path(root).absolute(); legacy = old_caller(root)
    data = json.loads((root / DATA).read_bytes())
    require(data['schema'] == 'recorder-failure-capture-inputs-v1', 'Capture input schema differs')
    require(set(data['files']) == SELECTED, 'Capture provenance inventory differs')
    spec, evidence = verified_abi(root, data['abi_sha256'])
    require(capture.same(spec, data['spec']) and sha(capture.canonical(spec)) == data['spec_sha256'], 'Derived capture spec differs')
    adapter = adapter_source(spec, (root / 'tools/recorder_six_result_capture.py').read_bytes())
    require((root / STAGED).read_bytes() == adapter and data['adapter_pin'] ==
            dict(path=capture.bindings()['output'] + '-adapter/remote.py', bytes=len(adapter), sha256=sha(adapter)), 'Staged adapter differs')
    plan, counts = project_actions(legacy.actions, spec, data['adapter_pin'])
    scope_files = tuple(data['files']) + (DATA, STAGED)
    modules = (legacy, legacy.legacy, legacy.legacy.legacy)
    for module in modules:
        module.__dict__.update(ROOT=root, RAW=RAW, SCOPE=SCOPE, OUTPUT=OUTPUT, RUN_ID=capture.RUN_ID, SOURCE=abi.SOURCE,
            SCOPE_FILES=scope_files, ADAPTER_ROOT=capture.bindings()['output'] + '-adapter')
    old_capability = legacy.legacy.capability_program
    legacy.legacy.capability_program = lambda *a: replace_once(old_capability(*a), "+SOURCE+'/app'", "+SOURCE+'/recorder'")
    legacy.actions.validate_capture_reply = lambda reply: validate_reply(reply, legacy, plan, counts)

    class RecorderCapture(legacy.CaptureRun):
        def load_scope(self):
            self.scope_raw = (self.root / SCOPE).read_bytes(); self.scope = legacy.decode(self.scope_raw, 65536)
            expected = dict(schema='recorder-failure-native-scope-v1', run_id=capture.RUN_ID, board='2629958581',
                source_sha256=abi.SOURCE, expected_identity=legacy.actions.EXPECTED_IDENTITY,
                files={**{k: p['sha256'] for k, p in data['files'].items()}, DATA: sha((root / DATA).read_bytes()), STAGED: sha(adapter)})
            require(legacy.actions.same(self.scope, expected), 'Capture scope differs')
            self.expected_identity = copy.deepcopy(expected['expected_identity'])

        def load_inputs(self):
            self.fixed_pins = dict(legacy.PINS, **{OLD: OLD_PIN[1], ACTION: ACTION_PIN[1]})
            self.fixed_pins.update({name: pin['sha256'] for name, pin in data['files'].items()})
            self.fixed_bytes = {name: abi.pinned(self.root / name, digest) for name, digest in self.fixed_pins.items()}
            require(all(type(pin['bytes']) is int and pin['bytes'] == len(self.fixed_bytes[name])
                        for name, pin in data['files'].items()), 'Capture provenance extent differs')
            delivery = abi.verified_module(self.root, abi.DELIVERY)
            compiled = delivery.make_owner(dict(action='--check-only', attempt=abi.ATTEMPT, reviewed_head=abi.COMPILE_HEAD), root=self.root)
            compiled.admission()
            self.source_hashes = compiled.expected_stage
            self.source_files = {name: dict(bytes=len(body), sha256=sha(body)) for name, body in compiled.staged_bytes.items()}
            self.fixed_pins.update(compiled.inputs['files']); self.fixed_bytes.update(compiled.code)
            self.bindings = {'capture': capture.bindings()}; self.adapter_pin = data['adapter_pin']
            self.load_baselines()

        def export_bundle(self, packet, reply):
            return export_packet(self, packet, reply, legacy, spec, plan)

    return RecorderCapture


def main(argv=None):
    parser = argparse.ArgumentParser(allow_abbrev=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare-bindings', action='store_true')
    group.add_argument('--check-only', action='store_true')
    group.add_argument('--execute', action='store_true')
    parser.add_argument('--abi-sha256'); parser.add_argument('--reviewed-head')
    args = parser.parse_args(argv)
    require(sys.dont_write_bytecode, 'Python -B required')
    if args.prepare_bindings:
        require(args.reviewed_head is None, 'Binding preparation does not admit a native HEAD')
        print(json.dumps(prepare_bindings(ROOT, args.abi_sha256), indent=2)); return 0
    require(args.abi_sha256 is None and type(args.reviewed_head) is str and re.fullmatch('[0-9a-f]{40}', args.reviewed_head),
            'Exact collector HEAD required')
    owner = owner_type(ROOT)(args.reviewed_head, root=ROOT)
    if args.check_only:
        owner.admit(); return 0
    return 0 if owner.run()['status'] == 'COMPLETED' else 1


if __name__ == '__main__':
    sys.exit(main())
