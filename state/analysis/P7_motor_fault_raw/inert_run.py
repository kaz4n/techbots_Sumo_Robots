# Calls the fixed diagnostic upload and conditional capture once under a fresh scope.
# Reuses reviewed ownership and transport helpers without reviving consumed launchers.
# Independent host fixtures verify admission, bounded dispatch and durable failure closure.
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import types
import uuid

ROOT = Path(__file__).resolve().parents[3]
RAW = 'state/analysis/P7_motor_fault_raw/'
STATIC = 'state/analysis/P7_static_startup_raw/'
PROBE = 'state/analysis/P7_static_link_probe_raw/'
SCOPE = RAW + 'inert_run01_scope.json'
OUTPUT = RAW + 'native_inert_run01'
RUN_ID = 'motor-fault-8f592937-run01'
SOURCE = '8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36'
BOARD = '2629958581'
ADB = 'C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'
ADB_SHA = 'e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982'
SCOPE_FILES = (RAW + 'inert_run.py', RAW + 'test_inert_run.py',
               'state/analysis/P7_motor_fault_caller_contract.md',
               'state/reviews/P7_motor_fault_caller_review.md')
PINS = {
    STATIC + 'startup_run.py': 'c95888353c9d85c5d9b0e545553a9e9dcde372b5b313102dd14240ce38db4e0c',
    RAW + 'compile_motor_fault.py': '84efd00611b3a6a8129655005930ff58e555221f6bd8d88a23c7fa1c4381ac0d',
    RAW + 'inert_actions.py': '8ffb65c0f1284f261ae1237bcf260e866176e83433a3538908780962513f1104',
    RAW + 'action_preparation.json': '6b5df73026e11914c811ab274054bf4d26ff6b8438e8c9a86ad1ba9bce802835',
    PROBE + 'static_remote.py': '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8',
    STATIC + 'capture_remote.py': '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e',
    STATIC + 'upload_remote.py': 'e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1',
    STATIC + 'cli_initialization_inventory.json': 'aaa2c307b7ed1b8d7e00a737447a03a63a78cd4b7fb2145142b20e9501da1e62',
    STATIC + 'cli_builtin_files_inventory.json': 'a364beb814b36b9c56328b54a9de5fa0f4ad80a67003d40c7cc994a1917ba2cb'}
BASELINES = ('cli_initialization_inventory', 'cli_builtin_files_inventory')
BASELINE_LABELS = ('cli-initialization', 'cli-builtin-files')
PROVENANCE = (RAW + 'active_abi.json', RAW + 'active_verified.json',
              RAW + 'deployment_files01/result.json',
              RAW + 'installed_capture_modules02/result.json',
              STATIC + 'capture_bindings.json', STATIC + 'upload_bindings.json')
CAPABILITY = '''import base64,bz2,json,os,signal,sys
from pathlib import Path
signal.alarm(60)
literal=b'SumoX-26 fixed inert capability'
token=base64.b85encode(literal)
print(json.dumps({'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 'uid':os.getuid(),'no_bytecode':bool(sys.flags.dont_write_bytecode) and sys.dont_write_bytecode is True,
 'bz2':bz2.decompress(bz2.compress(literal))==literal,
 'base85':base64.b85decode(token)==literal and base64.b85encode(base64.b85decode(token))==token}))
'''
CAPABILITY_ARGV = ('/usr/bin/env', '-i', 'HOME=/home/arduino', 'USER=arduino',
                   'LOGNAME=arduino', 'PATH=/usr/bin:/bin', 'LANG=C', 'LC_ALL=C',
                   '/usr/bin/python3', '-I', '-B', '-c', CAPABILITY)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_pinned(name, relative):
    path = ROOT / relative
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PINS[relative], 'Module source changed: ' + relative)
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


helpers = load_pinned('fixed_inert_local_helpers', STATIC + 'startup_run.py')
helpers.safe_path(ROOT / (STATIC + 'startup_run.py'))
compiler = load_pinned('fixed_inert_transport', RAW + 'compile_motor_fault.py')
actions = load_pinned('fixed_inert_actions', RAW + 'inert_actions.py')
safe_path, pinned_file = helpers.safe_path, helpers.pinned_file
canonical, sha, keys = helpers.canonical, helpers.sha, helpers.keys
CALLER_SHA = sha(Path(__file__).read_bytes())


def decode(raw, limit):
    require(type(raw) is bytes and len(raw) <= limit, 'Reply exceeds its byte bound or is not bytes')
    return helpers.decode(raw)


def same(left, right):
    return canonical(left) == canonical(right)


def error_record(error):
    chain, seen, current = [], set(), error
    while current is not None and id(current) not in seen and len(chain) < 8:
        seen.add(id(current))
        chain.append({'type': type(current).__name__, 'message': str(current)})
        current = current.__cause__ if current.__cause__ is not None else current.__context__
    return {**chain[0], 'chain': chain, 'truncated': current is not None}


def native_arguments(remote):
    return ('shell', '-T', shlex.join(remote))


def command_record(remote, timeout):
    argv = [ADB, '-s', BOARD, *native_arguments(remote)]
    units = len(subprocess.list2cmdline(argv).encode('utf-16-le')) // 2 + 1
    require(units <= 30000, 'Windows command exceeds 30000 units including NUL')
    return {'argv_sha256': sha(canonical(list(remote))),
            'native_argv_sha256': sha(canonical(argv)),
            'command_utf16_units': units, 'timeout': timeout}


class InertRun:
    git = helpers.NativeRun.git
    head = helpers.NativeRun.head
    check_scope = helpers.NativeRun.check_scope
    check_output = helpers.NativeRun.check_output
    write = helpers.NativeRun.write

    def __init__(self, reviewed_head, *, root=None):
        self.reviewed_head = reviewed_head
        self.root = ROOT if root is None else Path(root).absolute()
        self.output = self.root / OUTPUT
        self.profile = {'scope': SCOPE}
        self.runner = self.probe = None
        self.git_checks, self.local_errors, self.prerequisite_errors = [], [], []
        self.transport_errors, self.finish_errors = [], []
        self.intent_actions, self.dispatched_actions = set(), set()
        self.counter, self.transport_calls = 0, 0
        self.command_counts, self.reply_hashes = {}, {}
        self.admitted = self.claimed = self.claim_started = self.run_started = False
        self.claim_ready = False

    def check_adb(self):
        safe_path(Path(ADB))
        require(sha(Path(ADB).read_bytes()) == ADB_SHA, 'Pinned ADB changed')

    def load_scope(self):
        path = self.root / SCOPE
        safe_path(path)
        self.scope_raw = path.read_bytes()
        self.scope = decode(self.scope_raw, 65536)
        keys(self.scope, ('schema', 'run_id', 'board', 'source_sha256', 'expected_identity', 'files'))
        for name, expected in (('schema', 'motor-fault-native-scope-v1'), ('run_id', RUN_ID),
                               ('board', BOARD), ('source_sha256', SOURCE)):
            require(type(self.scope[name]) is str and self.scope[name] == expected, 'Wrong scope identity')
        keys(self.scope['files'], SCOPE_FILES)
        for digest in self.scope['files'].values():
            require(type(digest) is str and re.fullmatch('[0-9a-f]{64}', digest), 'Invalid scope hash')
        require(self.scope['files'][RAW + 'inert_run.py'] == CALLER_SHA, 'Scope names a different caller source')
        identity = self.scope['expected_identity']
        require(type(identity) is dict, 'Missing expected identity')
        boot = identity.get('boot_id')
        require(type(boot) is str and bool(boot) and str(uuid.UUID(boot)) == boot, 'Noncanonical boot UUID')
        self.expected_identity = copy.deepcopy(identity)

    def load_inputs(self):
        self.fixed_pins = dict(PINS)
        self.fixed_bytes = {name: pinned_file(self.root, name, digest) for name, digest in PINS.items()}
        preparation = helpers.decode(self.fixed_bytes[RAW + 'action_preparation.json'])
        keys(preparation['provenance'], PROVENANCE)
        for name, value in preparation['provenance'].items():
            keys(value, ('bytes', 'sha256'))
            raw = pinned_file(self.root, name, value['sha256'])
            require(type(value['bytes']) is int and len(raw) == value['bytes'], 'Provenance size changed')
            self.fixed_bytes[name], self.fixed_pins[name] = raw, value['sha256']
        self.bindings = copy.deepcopy(preparation['bindings'])
        for value in self.bindings.values():
            value['boot_id'] = self.expected_identity['boot_id']
        self.prerequisite_receipts = []
        for label, filename in zip(BASELINE_LABELS, BASELINES):
            receipt = helpers.decode(self.fixed_bytes[STATIC + filename + '.json'])
            require(type(receipt['returncode']) is int and receipt['returncode'] == 0 and
                    receipt['stderr'] == '', 'Failed baseline receipt')
            expected = helpers.decode(receipt['stdout'])
            require(expected['status'] == 'COLLECTED', 'Failed baseline observation')
            identity = copy.deepcopy(self.expected_identity)
            identity['boot_id'] = expected['identity']['boot_id']
            require(same(identity, expected['identity']), 'Non-boot baseline identity differs')
            require(type(identity['uid']) is int and identity['uid'] == 1000, 'Wrong baseline UID')
            self.prerequisite_receipts.append((label, receipt, expected))

    def prepare_commands(self):
        sources = {'helper': self.fixed_bytes[PROBE + 'static_remote.py'],
                   'support': self.fixed_bytes[STATIC + 'capture_remote.py']}
        upload = {**sources, 'upload': self.fixed_bytes[STATIC + 'upload_remote.py']}
        remote = {name: tuple(actions.build_command(name, upload if name == 'upload' else sources,
                                                    copy.deepcopy(self.bindings[name])))
                  for name in ('upload', 'capture')}
        self.commands = types.MappingProxyType(dict(remote))
        remote.update({label: tuple(receipt['argv']) for label, receipt, unused in self.prerequisite_receipts})
        remote['capabilities'] = CAPABILITY_ARGV
        self.all_commands = types.MappingProxyType(remote)
        self.timeouts = types.MappingProxyType({name: {'upload': 195, 'capture': 630}.get(name, 60)
                                              for name in remote})
        self.command_records = {name: command_record(argv, self.timeouts[name]) for name, argv in remote.items()}
        self.allowed = frozenset((native_arguments(argv), self.timeouts[name], name) for name, argv in remote.items())
        require(len(self.allowed) == 5, 'Wrong fixed command allowlist')
        self.input_state = self.state_bytes()

    def state_bytes(self):
        return canonical({'scope': self.scope, 'pins': self.fixed_pins, 'bindings': self.bindings,
                          'identity': self.expected_identity, 'profile': self.profile,
                          'commands': {name: list(argv) for name, argv in self.commands.items()},
                          'all_commands': {name: list(argv) for name, argv in self.all_commands.items()},
                          'records': self.command_records, 'timeouts': dict(self.timeouts),
                          'allowed': sorted((list(argv), timeout, label) for argv, timeout, label in self.allowed),
                          'baselines': self.prerequisite_receipts})

    def check_state(self):
        require(sys.flags.dont_write_bytecode and sys.dont_write_bytecode is True, 'Startup and current Python -B required')
        require(self.output == self.root / OUTPUT and self.profile == {'scope': SCOPE}, 'Fixed owner/scope changed')
        require(self.runner is None and self.probe is None, 'Historical launcher context forbidden')
        require(self.state_bytes() == self.input_state, 'Prepared inputs or commands mutated')
        if self.claimed:
            self.check_output()

    def local(self):
        first = None
        for name, operation in (('prepared_state', self.check_state), ('pinned_local', lambda: helpers.NativeRun.local(self))):
            try:
                operation()
            except Exception as error:
                first = first if first is not None else error
                self.local_errors.append({'check': name, **error_record(error)})
        if first is not None:
            raise first

    def admit(self):
        require(not self.claim_started, 'Attempt already claimed')
        require(sys.flags.dont_write_bytecode and sys.dont_write_bytecode is True, 'Startup and current Python -B required')
        require(type(self.reviewed_head) is str and re.fullmatch('[0-9a-f]{40}', self.reviewed_head), 'Invalid reviewed HEAD')
        safe_path(self.root, directory=True)
        safe_path(self.output.parent, directory=True)
        require(not os.path.lexists(self.output), 'Host attempt already consumed')
        self.load_scope()
        self.load_inputs()
        self.prepare_commands()
        self.local()
        self.admitted = True

    def identity_record(self):
        return {'run_id': RUN_ID, 'board': BOARD, 'source_sha256': SOURCE,
                'reviewed_head': self.reviewed_head, 'scope_sha256': sha(self.scope_raw),
                'expected_identity': copy.deepcopy(self.expected_identity)}

    def claim(self):
        require(self.admitted and not self.claim_started, 'Missing admission or repeated claim')
        self.claim_started = True
        self.local()
        require(not os.path.lexists(self.output), 'Host attempt already consumed')
        self.output.mkdir(mode=0o700)
        info = self.output.stat()
        self.output_identity = (info.st_dev, info.st_ino)
        self.claimed = True
        inputs = {**self.scope['files'], **self.fixed_pins, SCOPE: sha(self.scope_raw), ADB: ADB_SHA}
        self.write('inputs.json', {**self.identity_record(), 'input_hashes': inputs,
                   'commands': self.command_records,
                   'remote_evidence': {name: self.bindings[name]['output'] for name in ('upload', 'capture')}})
        self.claim_ready = True

    def transport(self, arguments, timeout, label):
        require(self.claim_ready, 'Durable claim required before transport')
        require(type(arguments) in (list, tuple) and all(type(item) is str for item in arguments) and
                type(timeout) is int and type(label) is str and
                (tuple(arguments), timeout, label) in self.allowed, 'Command is outside the fixed allowlist')
        require(type(self.counter) is int and 0 <= self.counter < 11 and self.transport_calls < 11, 'Transport bound exceeded')
        limit = 1 if label in ('upload', 'capture') else 3
        require(self.command_counts.get(label, 0) < limit, 'Repeated command exceeds its bound')
        if label in ('upload', 'capture'):
            require(label in self.dispatched_actions, 'Native dispatch lacks consumed intent')
        self.check_adb()
        self.check_output()
        self.transport_calls += 1
        self.command_counts[label] = self.command_counts.get(label, 0) + 1
        first, outcome = None, None
        try:
            outcome = compiler.CompileOnce.transport(self, list(arguments), timeout, label)
        except Exception as error:
            first = error
            self.transport_errors.append({'check': label, **error_record(error)})
        try:
            self.check_output()
        except Exception as error:
            first = first if first is not None else error
            self.transport_errors.append({'check': label + '-owner', **error_record(error)})
        if first is not None:
            raise first
        return outcome

    def query(self, label, limit):
        reply, unused = self.transport(native_arguments(self.all_commands[label]), self.timeouts[label], label)
        require(type(reply.returncode) is int and reply.returncode == 0 and
                type(reply.stderr) is bytes and not reply.stderr, 'Invalid transport status/stderr')
        return decode(reply.stdout, limit)

    def check_prerequisite(self, label, expected):
        value = self.query(label, 1048576)
        require(value['status'] == 'COLLECTED' and same(value['identity'], self.expected_identity), 'Fresh prerequisite identity/status differs')
        current = {key: item for key, item in value.items() if key != 'identity'}
        old = {key: item for key, item in expected.items() if key != 'identity'}
        require(same(helpers.projection(current), helpers.projection(old)), 'CLI prerequisite content differs')

    def check_capability(self):
        value = self.query('capabilities', 4096)
        keys(value, ('boot_id', 'uid', 'no_bytecode', 'bz2', 'base85'))
        require(type(value['boot_id']) is str and value['boot_id'] == self.expected_identity['boot_id'] and
                type(value['uid']) is int and value['uid'] == 1000, 'Capability identity differs')
        require(all(value[name] is True for name in ('no_bytecode', 'bz2', 'base85')), 'Python capability unavailable')

    def prerequisites(self):
        first = None
        checks = [(label, lambda label=label, expected=expected: self.check_prerequisite(label, expected))
                  for label, unused, expected in self.prerequisite_receipts]
        checks.append(('capabilities', self.check_capability))
        for label, operation in checks:
            try:
                operation()
            except Exception as error:
                first = first if first is not None else error
                self.prerequisite_errors.append({'check': label, **error_record(error)})
        if first is not None:
            raise first

    def intent(self, action, predecessor):
        require(type(action) is str and action in ('upload', 'capture'), 'Wrong action')
        require(self.claim_ready and action not in self.intent_actions, 'Missing claim or repeated intent')
        self.local()
        if action == 'upload':
            require(predecessor is None and not self.intent_actions and not self.dispatched_actions, 'Wrong upload order')
        else:
            require(self.intent_actions == self.dispatched_actions == {'upload'}, 'Wrong capture order')
            actions.validate_reply('upload', predecessor)
            require(sha(canonical(predecessor)) == self.reply_hashes.get('upload'), 'Capture predecessor differs from actual upload')
        self.write(action + '_attempt.json', {**self.identity_record(), 'action': action,
                   'command': self.command_records[action],
                   'predecessor_sha256': None if predecessor is None else sha(canonical(predecessor))})
        self.intent_actions.add(action)

    def action(self, name):
        require(type(name) is str and name in ('upload', 'capture') and
                name in self.intent_actions and name not in self.dispatched_actions, 'Missing or consumed intent')
        self.local()
        self.dispatched_actions.add(name)
        reply = self.query(name, 65536)
        self.reply_hashes[name] = sha(canonical(reply))
        return reply

    def check_counters(self, result):
        require(type(self.counter) is int and self.counter == self.transport_calls <= 11, 'Transport counter differs')
        require(self.dispatched_actions <= self.intent_actions <= {'upload', 'capture'}, 'Invalid action sets')
        if result['status'] == 'COMPLETED':
            require(self.counter == 11 and self.intent_actions == self.dispatched_actions == {'upload', 'capture'} and
                    self.command_counts == {**{name: 3 for name in (*BASELINE_LABELS, 'capabilities')}, 'upload': 1, 'capture': 1},
                    'Incomplete successful transport/action set')
            require(type(result['upload_attempts']) is int and result['upload_attempts'] == 1 and
                    type(result['capture_attempts']) is int and result['capture_attempts'] == 1, 'Incomplete successful attempt counts')
            require(not (self.local_errors or self.prerequisite_errors or self.transport_errors), 'Successful result contains diagnostics')

    def failed_finish(self, result, check, error):
        record = {'check': check, **error_record(error)}
        self.finish_errors.append(record)
        result['status'] = 'FAILED'
        if result['first_error'] is None:
            result['first_error'] = helpers.error_record(error)
        result['postcheck_errors'].append(record)

    def diagnostics(self):
        return {'git': self.git_checks, 'local': self.local_errors,
                'prerequisites': self.prerequisite_errors, 'transport_errors': self.transport_errors,
                'finish_errors': self.finish_errors, 'commands': self.counter,
                'transport_calls': self.transport_calls, 'command_counts': self.command_counts,
                'intent_actions': sorted(self.intent_actions), 'dispatched_actions': sorted(self.dispatched_actions)}

    def finish(self, result):
        first = None
        try:
            self.check_counters(result)
        except Exception as error:
            first = error
            self.failed_finish(result, 'counters', error)
        try:
            self.write('final_checks.json', self.diagnostics())
        except Exception as error:
            first = first if first is not None else error
            self.failed_finish(result, 'final_checks.json', error)
        result['diagnostics'] = self.diagnostics()
        try:
            self.write('result.json', result)
        except Exception as error:
            first = first if first is not None else error
            self.failed_finish(result, 'result.json', error)
        if first is not None:
            raise first

    def run(self):
        require(not self.run_started, 'Run already consumed')
        self.run_started = True
        self.admit()
        self.claim()
        return actions.run_actions({'local': self.local, 'prerequisites': self.prerequisites,
                                    'intent': self.intent, 'upload': lambda: self.action('upload'),
                                    'capture': lambda: self.action('capture'), 'finish': self.finish})


def main(argv=None):
    parser = argparse.ArgumentParser(description='One fixed inert diagnostic attempt', allow_abbrev=False)
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
