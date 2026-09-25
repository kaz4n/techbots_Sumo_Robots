# Calls one fixed static inhibited upload and conditional passive capture.
# Reuses reviewed ownership/transport with one small exclusive adapter staging.
# Independent contract tests cover admission, sequencing and failure evidence.
import argparse
import base64
import bz2
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import sys
import types

ROOT = Path(__file__).absolute().parents[3]
RAW = 'state/analysis/P7_app_motor_fault_run_raw/'
OLD = 'state/analysis/P7_motor_fault_raw/'
STATIC = 'state/analysis/P7_static_startup_raw/'
PROBE = 'state/analysis/P7_static_link_probe_raw/'
COMPILED = 'state/analysis/P7_app_motor_fault_compile_raw/'
SCOPE = RAW + 'inert_run01_scope.json'
OUTPUT = RAW + 'native_inert_run01'
PREPARATION = RAW + 'preparation.json'
RUN_ID = 'app-motor-fault-21df6ae8-run01'
SOURCE = '21df6ae82cca4b09dc6b1e0de5bc719cf98ec6887800d5ce8297522e491a7950'
BOARD = '2629958581'
ADAPTER_ROOT = '/home/arduino/sumox26_codex_build/' + RUN_ID + '-adapter'
MANIFEST_SHA = 'd4eae97c1c47a1ce0fa24c9d7e3ae44857a565cd7b85b9c17be45143654d3eb5'
PROVENANCE = tuple(COMPILED + name for name in (
    'inputs_static.json', 'native_static01/result.json', 'native_static01/artifacts.json',
    'native_abi_static01/result.json', 'native_abi_static01/local_result.json',
    'abi_static01_interpreted.json', 'native_entry_static01/result.json',
    'native_entry_static01/local_result.json', 'native_entry_static01/entry.json')) + tuple(
    'state/reviews/P7_app_motor_fault_' + name + '.md' for name in (
        'native_actual_review', 'abi_actual_review', 'entry_actual_review'))
SCOPE_FILES = tuple(RAW + name for name in (
    'preparation.json', 'run.py', 'actions.py', 'remote.py',
    'test_run.py', 'test_actions.py', 'test_remote.py')) + (
    'state/analysis/P7_app_motor_fault_caller_contract.md',
    'state/analysis/P7_app_motor_fault_run_contract.md',
    'state/reviews/P7_app_motor_fault_caller_review.md',
    'state/reviews/P7_app_motor_fault_remote_source_review.md')
PINS = {
    OLD + 'inert_run.py': '8b47b1d6e9073179e4f587e09ce04e1a1c0cfc6797daf3151d0a7126d279f56a',
    OLD + 'inert_actions.py': '8ffb65c0f1284f261ae1237bcf260e866176e83433a3538908780962513f1104',
    OLD + 'compile_motor_fault.py': '84efd00611b3a6a8129655005930ff58e555221f6bd8d88a23c7fa1c4381ac0d',
    STATIC + 'startup_run.py': 'c95888353c9d85c5d9b0e545553a9e9dcde372b5b313102dd14240ce38db4e0c',
    PROBE + 'static_remote.py': '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8',
    STATIC + 'capture_remote.py': '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e',
    STATIC + 'upload_remote.py': 'e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1',
    STATIC + 'cli_initialization_inventory.json': 'aaa2c307b7ed1b8d7e00a737447a03a63a78cd4b7fb2145142b20e9501da1e62',
    STATIC + 'cli_builtin_files_inventory.json': 'a364beb814b36b9c56328b54a9de5fa0f4ad80a67003d40c7cc994a1917ba2cb',
    'tools/compile_app_motor_fault.py': 'cf0c826feca483a78ce9839d0037d1e005a0ce73a3aa01df1ad4b309729ed25a',
    'state/analysis/P7_current_app_compile_raw/compile_current_app.py':
        'aed3fbf4db5c962761affd5a3e2e52b1002feaaefe4e44f9f34df6ec78ba5ede'}


def _module(name, path, raw):
    module = types.ModuleType('_app_inert_' + name)
    module.__file__ = str(ROOT / path)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


actions = _module('actions', RAW + 'actions.py', (ROOT / RAW / 'actions.py').read_bytes())


def _pinned_module(name, path):
    return _module(name, path, actions.checked_source(ROOT / path, PINS[path]))


helpers = _pinned_module('helpers', STATIC + 'startup_run.py')
compiler = _pinned_module('compiler', OLD + 'compile_motor_fault.py')
current = _pinned_module('current', 'state/analysis/P7_current_app_compile_raw/compile_current_app.py')
diagnostic = _pinned_module('diagnostic', 'tools/compile_app_motor_fault.py')
safe_path, pinned_file = helpers.safe_path, helpers.pinned_file
canonical, sha, keys, require = helpers.canonical, helpers.sha, helpers.keys, helpers.require


def _legacy():
    path = OLD + 'inert_run.py'
    source = actions.checked_source(ROOT / path, PINS[path]).decode('utf-8')
    substitutions = {
        "helpers = load_pinned('fixed_inert_local_helpers', STATIC + 'startup_run.py')": 'helpers = INJECTED_HELPERS',
        "compiler = load_pinned('fixed_inert_transport', RAW + 'compile_motor_fault.py')": 'compiler = INJECTED_COMPILER',
        "actions = load_pinned('fixed_inert_actions', RAW + 'inert_actions.py')": 'actions = INJECTED_ACTIONS'}
    for old, new in substitutions.items():
        require(source.count(old) == 1, 'Legacy seam changed')
        source = source.replace(old, new)
    source = source.replace('motor-fault-', 'app-motor-fault-').replace(
        "RAW + 'inert_run.py'", "RAW + 'run.py'")
    source = source.replace('< 11', '< 13').replace('<= 11', '<= 13').replace('== 11', '== 13')
    source = source.replace("limit = 1 if label in ('upload', 'capture') else 3",
                            "limit = 1 if label in ('upload', 'capture', 'adapter-claim', 'adapter-push') else 3")
    module = types.ModuleType('_app_inert_legacy')
    module.__dict__.update(__file__=str(ROOT / path), INJECTED_HELPERS=helpers,
                           INJECTED_COMPILER=compiler, INJECTED_ACTIONS=actions)
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    module.__dict__.update(ROOT=ROOT, RAW=RAW, SCOPE=SCOPE, OUTPUT=OUTPUT, RUN_ID=RUN_ID,
                           SOURCE=SOURCE, SCOPE_FILES=SCOPE_FILES, PINS=PINS,
                           CALLER_SHA=sha(Path(__file__).read_bytes()))
    return module


legacy = _legacy()
decode, error_record = legacy.decode, legacy.error_record
native_arguments, command_record = legacy.native_arguments, legacy.command_record
ADB, ADB_SHA = legacy.ADB, legacy.ADB_SHA
BASELINE_LABELS, BASELINES = legacy.BASELINE_LABELS, legacy.BASELINES


def capability_program(helper_raw, expected, pin):
    packed = bz2.compress(canonical(dict(helper=helper_raw.decode(), manifest=expected)), 9)
    prefix = ('import base64,bz2,hashlib,json,os,signal,sys,types\n'
              'from pathlib import Path\nsignal.alarm(60)\npacket=json.loads(bz2.decompress(base64.b64decode(' +
              repr(base64.b64encode(packed).decode()) + ')))\n')
    return prefix + 'SOURCE=' + repr(SOURCE) + '\npin=' + repr(pin) + '\n' + '''raw=packet['helper'].encode()
if hashlib.sha256(raw).hexdigest()!='8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8':raise ValueError('Helper drift')
h=types.ModuleType('fixed_app_source');exec(compile(raw,'/__sumox__/helper.py','exec'),h.__dict__)
h.SOURCE=SOURCE;h.SKETCH='/home/arduino/sumox26_codex_build/'+SOURCE+'/app_motor_fault'
root=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
try:
 data=h.source_data();h.source_action(root,{'manifest':packet['manifest']},data)
 adapter=h.logical_read(root,pin['path'],pin['bytes'])
 if len(adapter)!=pin['bytes'] or h.sha256(adapter)!=pin['sha256']:raise ValueError('Adapter drift')
 boot=h.boot_id(root)
finally:os.close(root)
literal=b'SumoX-26 fixed inert capability';token=base64.b85encode(literal)
print(json.dumps({'boot_id':boot,'uid':os.getuid(),'no_bytecode':bool(sys.flags.dont_write_bytecode) and sys.dont_write_bytecode is True,
 'bz2':bz2.decompress(bz2.compress(literal))==literal,'base85':base64.b85decode(token)==literal and base64.b85encode(base64.b85decode(token))==token,
 'adapter_bytes':len(adapter),'adapter_sha256':h.sha256(adapter),'source_sha256':SOURCE,'source_files':data['files']}))
'''


class InertRun(legacy.InertRun):
    def __init__(self, reviewed_head, *, root=None):
        super().__init__(reviewed_head, root=root)
        self.stage_started = self.stage_ready = False
        self.stage_intent_ready = self.stage_claim_verified = False
        self.stage_dispatches = set()

    def head(self):
        super().head()
        changes = self.git('status', '--porcelain', '--untracked-files=all').decode('utf-8').splitlines()
        prefix = OUTPUT + '/'
        require(all(self.claimed and line.startswith('?? ' + prefix) for line in changes),
                'Unrelated untracked files exist')

    def load_inputs(self):
        self.fixed_pins = dict(PINS)
        self.fixed_bytes = {name: pinned_file(self.root, name, digest) for name, digest in PINS.items()}
        raw = pinned_file(self.root, PREPARATION, self.scope['files'][PREPARATION])
        preparation = decode(raw, 65536)
        keys(preparation, ('schema', 'run_id', 'source_sha256', 'bindings', 'files'))
        require(preparation['schema'] == 'app-motor-fault-run-preparation-v1' and
                preparation['run_id'] == RUN_ID and preparation['source_sha256'] == SOURCE,
                'Wrong preparation identity')
        keys(preparation['files'], PROVENANCE)
        for name, pin in preparation['files'].items():
            keys(pin, ('bytes', 'sha256'))
            data = pinned_file(self.root, name, pin['sha256'])
            require(type(pin['bytes']) is int and pin['bytes'] > 0 and len(data) == pin['bytes'],
                    'Provenance size changed')
            self.fixed_bytes[name], self.fixed_pins[name] = data, pin['sha256']
        keys(preparation['bindings'], ('upload', 'capture'))
        self.bindings = copy.deepcopy(preparation['bindings'])
        require(all(value['boot_id'] == self.expected_identity['boot_id']
                    for value in self.bindings.values()), 'Binding boot differs')
        self.load_source()
        self.check_evidence()
        self.load_baselines()

    def load_source(self):
        raw = self.fixed_bytes[COMPILED + 'inputs_static.json']
        require(sha(raw) == MANIFEST_SHA, 'D188 manifest changed')
        value = decode(raw, 65536)
        keys(value, ('schema', 'source_sha256', 'boot_id', 'files'))
        require(value['schema'] == 'app-motor-fault-static-inputs-v1' and
                value['source_sha256'] == SOURCE and value['boot_id'] == self.expected_identity['boot_id']
                and type(value['files']) is dict and len(value['files']) == 127, 'D188 source identity differs')
        for name, digest in value['files'].items():
            self.fixed_bytes[name] = pinned_file(self.root, name, digest)
            self.fixed_pins[name] = digest
        owner = types.SimpleNamespace(root=self.root, base=current)
        names = self.source_inventory()
        self.source_hashes, source = diagnostic.CompileDiagnostic.source_mapping(owner, self.fixed_bytes, names)
        require(source == SOURCE, 'Current source projection differs')
        sizes = {sha(raw): len(raw) for raw in self.fixed_bytes.values()}
        self.source_files = {name: dict(bytes=sizes[digest], sha256=digest)
                             for name, digest in self.source_hashes.items()}
        self.adapter_pin = dict(path=actions.ADAPTER, bytes=actions.ADAPTER_BYTES, sha256=actions.ADAPTER_SHA)
        require(self.scope['files'][RAW + 'remote.py'] == actions.ADAPTER_SHA,
                'Scope adapter differs')

    def source_inventory(self):
        owner = types.SimpleNamespace(root=self.root, base=current)
        return diagnostic.CompileDiagnostic.source_names(owner)

    def check_evidence(self):
        values = {name: decode(self.fixed_bytes[COMPILED + name], 1048576) for name in (
            'native_static01/result.json', 'native_static01/artifacts.json',
            'native_abi_static01/local_result.json', 'abi_static01_interpreted.json',
            'native_entry_static01/local_result.json', 'native_entry_static01/entry.json')}
        compiled = values['native_static01/result.json']
        require(compiled['status'] == 'COMPILE_CHECKED' and compiled['source_sha256'] == SOURCE and
                compiled['boot_id'] == self.expected_identity['boot_id'] and compiled['first_error'] is None,
                'Actual compiler evidence is not successful')
        require(values['native_static01/artifacts.json']['status'] == 'ARTIFACTS_CHECKED', 'Artifacts unqualified')
        require(values['native_abi_static01/local_result.json']['status'] == 'FAILED' and
                values['abi_static01_interpreted.json']['status'] == 'OFFLINE_ABI_INTERPRETED' and
                values['abi_static01_interpreted.json']['abi']['status'] == 'STATIC_ABI_OBSERVED',
                'Original ABI failure and interpretation disposition differ')
        require(values['native_entry_static01/local_result.json']['status'] == 'STATIC_ENTRY_OBSERVED' and
                values['native_entry_static01/local_result.json']['first_error'] is None and
                values['native_entry_static01/entry.json']['status'] == 'STATIC_ENTRY_OBSERVED',
                'Actual entry evidence is not successful')

    def load_baselines(self):
        self.prerequisite_receipts = []
        for label, filename in zip(BASELINE_LABELS, BASELINES):
            receipt = helpers.decode(self.fixed_bytes[STATIC + filename + '.json'])
            require(type(receipt['returncode']) is int and receipt['returncode'] == 0 and
                    receipt['stderr'] == '', 'Failed baseline receipt')
            expected = helpers.decode(receipt['stdout'])
            identity = copy.deepcopy(self.expected_identity)
            identity['boot_id'] = expected['identity']['boot_id']
            require(expected['status'] == 'COLLECTED' and canonical(identity) == canonical(expected['identity'])
                    and type(identity['uid']) is int and identity['uid'] == 1000, 'Baseline identity differs')
            self.prerequisite_receipts.append((label, receipt, expected))

    def prepare_commands(self):
        sources = {'helper': self.fixed_bytes[PROBE + 'static_remote.py'],
                   'support': self.fixed_bytes[STATIC + 'capture_remote.py'],
                   'upload': self.fixed_bytes[STATIC + 'upload_remote.py']}
        remote = {name: tuple(actions.build_command(name, sources, copy.deepcopy(self.bindings[name]),
                                                    self.adapter_pin)) for name in ('upload', 'capture')}
        self.commands = types.MappingProxyType(dict(remote))
        remote.update({label: tuple(receipt['argv']) for label, receipt, unused in self.prerequisite_receipts})
        isolated = legacy.CAPABILITY_ARGV[:-1]
        remote['capabilities'] = isolated + (capability_program(sources['helper'], self.source_hashes, self.adapter_pin),)
        values = dict(BOOT=self.expected_identity['boot_id'], CLI=compiler.CLI,
                      CLI_SHA=compiler.CLI_SHA, REMOTE=ADAPTER_ROOT)
        claim = '\n'.join(name + '=' + repr(value) for name, value in values.items()) + '\n' + compiler.IDENTITY
        claim += "Path(REMOTE).mkdir(mode=0o700)\nprint(json.dumps(identity))\n"
        remote['adapter-claim'] = isolated + (claim,)
        self.push_arguments = ('push', str(self.root / RAW / 'remote.py'), actions.ADAPTER)
        self.all_commands = types.MappingProxyType(remote)
        self.timeouts = types.MappingProxyType({**{name: {'upload': 195, 'capture': 630}.get(name, 60)
                                                  for name in remote}, 'adapter-push': 60})
        self.command_records = {name: command_record(argv, self.timeouts[name]) for name, argv in remote.items()}
        self.command_records['adapter-push'] = dict(argv_sha256=sha(canonical(list(self.push_arguments))), timeout=60)
        allowed = {(native_arguments(argv), self.timeouts[name], name) for name, argv in remote.items()}
        allowed.add((self.push_arguments, 60, 'adapter-push'))
        self.allowed = frozenset(allowed)
        require(len(self.allowed) == 7, 'Wrong fixed command allowlist')
        self.input_state = self.state_bytes()

    def state_bytes(self):
        return canonical(dict(inherited=super().state_bytes().decode(), source_hashes=self.source_hashes,
                              source_files=self.source_files, adapter_pin=self.adapter_pin,
                              push_arguments=self.push_arguments))

    def transport(self, arguments, timeout, label):
        if label in ('adapter-claim', 'adapter-push'):
            require(self.stage_started is True and self.stage_intent_ready is True and
                    not self.stage_ready and label not in self.stage_dispatches,
                    'Staging dispatch lacks durable unused intent')
            if label == 'adapter-claim':
                require(not self.stage_dispatches, 'Adapter claim must be first')
            else:
                require(self.stage_claim_verified is True and self.stage_dispatches == {'adapter-claim'},
                        'Adapter push requires the verified exclusive claim')
            self.stage_dispatches.add(label)
        try:
            return super().transport(arguments, timeout, label)
        except Exception as error:
            primary = current.failure_guard(error, 'transport')
            if primary is error:
                raise
            raise primary from error

    def check_capability(self):
        value = self.query('capabilities', 65536)
        keys(value, ('boot_id', 'uid', 'no_bytecode', 'bz2', 'base85',
                     'adapter_bytes', 'adapter_sha256', 'source_sha256', 'source_files'))
        require(value['boot_id'] == self.expected_identity['boot_id'] and
                type(value['uid']) is int and value['uid'] == 1000 and
                all(value[name] is True for name in ('no_bytecode', 'bz2', 'base85')), 'Capability identity/API differs')
        require(type(value['adapter_bytes']) is int and value['adapter_bytes'] == actions.ADAPTER_BYTES and
                value['adapter_sha256'] == actions.ADAPTER_SHA and value['source_sha256'] == SOURCE and
                canonical(value['source_files']) == canonical(self.source_files), 'Adapter/source observation differs')

    def stage(self):
        require(self.claim_ready and not self.stage_started, 'Missing claim or staging already consumed')
        self.stage_started = True
        self.local()
        self.write('adapter_attempt.json', {**self.identity_record(), 'adapter': self.adapter_pin,
                   'commands': {name: self.command_records[name] for name in ('adapter-claim', 'adapter-push')}})
        self.stage_intent_ready = True
        value = self.query('adapter-claim', 4096)
        keys(value, ('uid', 'user', 'boot_id', 'cli_sha256', 'free_bytes', 'conflicts'))
        require(type(value['uid']) is int and value['uid'] == 1000 and value['user'] == 'arduino' and
                value['boot_id'] == self.expected_identity['boot_id'] and value['cli_sha256'] == compiler.CLI_SHA and
                type(value['free_bytes']) is int and value['free_bytes'] >= 1073741824 and value['conflicts'] == [],
                'Adapter claim identity differs')
        self.stage_claim_verified = True
        self.local()
        reply, unused = self.transport(self.push_arguments, 60, 'adapter-push')
        require(type(reply.returncode) is int and reply.returncode == 0, 'Adapter transfer failed')
        self.stage_ready = True

    def intent(self, action, predecessor):
        require(self.stage_ready, 'Checked staging required before action intent')
        return super().intent(action, predecessor)

    def check_counters(self, result):
        require(type(self.counter) is int and self.counter == self.transport_calls <= 13, 'Transport counter differs')
        require(self.dispatched_actions <= self.intent_actions <= {'upload', 'capture'}, 'Invalid action sets')
        if result['status'] == 'COMPLETED':
            expected = {name: 3 for name in (*BASELINE_LABELS, 'capabilities')}
            expected.update({name: 1 for name in ('adapter-claim', 'adapter-push', 'upload', 'capture')})
            require(self.stage_ready and self.counter == 13 and self.command_counts == expected and
                    self.stage_intent_ready and self.stage_claim_verified and
                    self.stage_dispatches == {'adapter-claim', 'adapter-push'} and
                    self.intent_actions == self.dispatched_actions == {'upload', 'capture'}, 'Incomplete successful dispatch set')
            require(type(result['upload_attempts']) is int and result['upload_attempts'] == 1 and
                    type(result['capture_attempts']) is int and result['capture_attempts'] == 1,
                    'Incomplete successful attempt counts')
            require(not (self.local_errors or self.prerequisite_errors or self.transport_errors), 'Successful diagnostics contain errors')

    def diagnostics(self):
        return {**super().diagnostics(), 'staging': {
            'started': self.stage_started, 'intent_ready': self.stage_intent_ready,
            'claim_verified': self.stage_claim_verified, 'ready': self.stage_ready,
            'dispatched': sorted(self.stage_dispatches)}}

    def stage_failure(self, error):
        result = dict(schema='app-motor-fault-sequence-v1', status='FAILED', upload=None, capture=None,
                      upload_attempts=0, capture_attempts=0, first_error=helpers.error_record(error), postcheck_errors=[])
        for name in ('local', 'prerequisites'):
            try:
                getattr(self, name)()
            except Exception as closing:
                result['postcheck_errors'].append(dict(check=name, **error_record(closing)))
        try:
            self.finish(result)
        except Exception as closing:
            error.sequence_result = result
            raise error from closing
        return result

    def run(self):
        require(not self.run_started, 'Run already consumed')
        self.run_started = True
        self.admit()
        self.claim()
        try:
            self.stage()
        except Exception as error:
            return self.stage_failure(error)
        return actions.run_actions({'local': self.local, 'prerequisites': self.prerequisites,
                                    'intent': self.intent, 'upload': lambda: self.action('upload'),
                                    'capture': lambda: self.action('capture'), 'finish': self.finish})


def main(argv=None):
    parser = argparse.ArgumentParser(description='One fixed inhibited static diagnostic attempt', allow_abbrev=False)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--execute', action='store_true')
    selection.add_argument('--check-only', action='store_true')
    parser.add_argument('--reviewed-head', required=True)
    args = parser.parse_args(argv)
    if not re.fullmatch('[0-9a-f]{40}', args.reviewed_head):
        parser.error('--reviewed-head must be forty lowercase hexadecimal characters')
    try:
        owner = InertRun(args.reviewed_head)
        if args.check_only:
            owner.admit()
            return 0
        return 0 if owner.run()['status'] == 'COMPLETED' else 1
    except Exception as error:
        print(json.dumps(error_record(error), sort_keys=True), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
