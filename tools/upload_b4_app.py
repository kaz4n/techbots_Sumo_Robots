# Uploads one fixed motor-disabled B4 application through guarded native staging.
# Keeps reviewed ownership and transport checks without a capture or retry path.
# Focused independent fixtures cover the B4 bindings and nine-call sequence.
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import types

ROOT = Path(__file__).absolute().parents[1]
RAW = 'state/analysis/P7_b4_app_upload_raw/'
COMPILED = 'state/analysis/P7_b4_app_compile_raw/'
SCOPE = RAW + 'upload01_scope.json'
OUTPUT = RAW + 'native_upload01'
PREPARATION = RAW + 'preparation.json'
RUN_ID = 'b4-app-m0-9044ebbb-load01'
SOURCE = '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'
BOARD = '2629958581'
ADAPTER_ROOT = '/home/arduino/sumox26_codex_build/' + RUN_ID + '-adapter'
MANIFEST_SHA = 'fc8e6fc1131c1952d5e1809f9dc6fb96763dd5e111749424e9ccfaec9b58d38c'
OLD_CALLER = 'state/analysis/P7_ordinary_app_run_raw/run.py'
OLD_CALLER_SHA = 'f48a8be9fa380a2a922613d188ae7622eafffdf3dc5fec12edc1372b4f7fc2d2'
ACTIONS_SHA = '7d5cd50fba630c5ca46bdc786f0959610c4c6e6b31059b7fbf13206c09faca57'
PLAN_SHA = '07726511930332b17c49c02c91a1f83df2d22bcc09502fd8255fa573bedee3b8'


def _module(name, path, raw, **injected):
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / path)
    module.__dict__.update(injected)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def _checked(path, digest):
    import stat
    target = ROOT / path
    for node in (target, *target.parents):
        info = node.lstat()
        plain = stat.S_ISREG if node == target else stat.S_ISDIR
        if not plain(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 1024:
            raise ValueError('Nonplain dependency: ' + str(node))
    raw = target.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError('Changed dependency: ' + path)
    return raw


actions = _module('_b4_upload_actions', RAW + 'actions.py',
                  _checked(RAW + 'actions.py', ACTIONS_SHA))
PLAN = json.loads(_checked(RAW + 'plan01.json', PLAN_SHA))
SCOPE_FILES, PROVENANCE = tuple(PLAN['scope_files']), tuple(PLAN['provenance'])
_old_source = _checked(OLD_CALLER, OLD_CALLER_SHA)
_old_import = b"actions = _module('actions', RAW + 'actions.py', (ROOT / RAW / 'actions.py').read_bytes())"
if _old_source.count(_old_import) != 1:
    raise ValueError('D212 action injection seam changed')
_old_source = _old_source.replace(_old_import, b'actions = INJECTED_ACTIONS')
legacy = _module('_b4_upload_d212', OLD_CALLER, _old_source, INJECTED_ACTIONS=actions)
PINS = dict(legacy.PINS, **{OLD_CALLER: OLD_CALLER_SHA,
    RAW + 'actions.py': ACTIONS_SHA, RAW + 'plan01.json': PLAN_SHA,
    RAW + 'remote.py': actions.ADAPTER_SHA})
helpers, compiler, current = legacy.helpers, legacy.compiler, legacy.current
STATIC, PROBE = legacy.STATIC, legacy.PROBE
BASELINE_LABELS, BASELINES = legacy.BASELINE_LABELS, legacy.BASELINES
safe_path, pinned_file = helpers.safe_path, helpers.pinned_file
canonical, sha, keys, require = helpers.canonical, helpers.sha, helpers.keys, helpers.require
decode, error_record = legacy.decode, legacy.error_record
native_arguments, command_record = legacy.native_arguments, legacy.command_record
ADB, ADB_SHA = legacy.ADB, legacy.ADB_SHA
for module in (legacy, legacy.legacy):
    module.__dict__.update(ROOT=ROOT, RAW=RAW, COMPILED=COMPILED, SCOPE=SCOPE,
        OUTPUT=OUTPUT, RUN_ID=RUN_ID, SOURCE=SOURCE, SCOPE_FILES=SCOPE_FILES,
        PINS=PINS, actions=actions, PREPARATION=PREPARATION, PROVENANCE=PROVENANCE,
        ADAPTER_ROOT=ADAPTER_ROOT, MANIFEST_SHA=MANIFEST_SHA)
legacy.legacy.CALLER_SHA = sha(Path(__file__).read_bytes())


class UploadRun(legacy.InertRun):
    def load_scope(self):
        path = self.root / SCOPE
        safe_path(path)
        self.scope_raw = path.read_bytes()
        self.scope = decode(self.scope_raw, 65536)
        keys(self.scope, ('schema', 'run_id', 'board', 'source_sha256',
                          'expected_identity', 'files'))
        for name, expected in (('schema', 'b4-app-upload-native-scope-v1'),
                               ('run_id', RUN_ID), ('board', BOARD), ('source_sha256', SOURCE)):
            require(type(self.scope[name]) is str and self.scope[name] == expected,
                    'Wrong upload scope identity')
        keys(self.scope['files'], SCOPE_FILES)
        require(all(type(v) is str and re.fullmatch('[0-9a-f]{64}', v)
                    for v in self.scope['files'].values()), 'Invalid scope pin')
        require(self.scope['files']['tools/upload_b4_app.py'] ==
                legacy.legacy.CALLER_SHA, 'Scope caller differs')
        require(actions.same(self.scope['expected_identity'], actions.EXPECTED_IDENTITY),
                'Wrong fixed board identity')
        self.expected_identity = copy.deepcopy(self.scope['expected_identity'])

    def load_inputs(self):
        self.fixed_pins = dict(PINS)
        self.fixed_bytes = {name: pinned_file(self.root, name, digest)
                            for name, digest in PINS.items()}
        raw = pinned_file(self.root, PREPARATION, self.scope['files'][PREPARATION])
        value = decode(raw, 65536)
        keys(value, ('schema', 'run_id', 'source_sha256', 'bindings', 'files'))
        require(value['schema'] == 'b4-app-upload-preparation-v1'
                and value['run_id'] == RUN_ID and value['source_sha256'] == SOURCE,
                'Wrong preparation identity')
        keys(value['files'], PROVENANCE)
        for name, pin in value['files'].items():
            keys(pin, ('bytes', 'sha256'))
            body = pinned_file(self.root, name, pin['sha256'])
            require(type(pin['bytes']) is int and 0 < pin['bytes'] == len(body),
                    'Wrong provenance size')
            self.fixed_bytes[name], self.fixed_pins[name] = body, pin['sha256']
        keys(value['bindings'], ('upload',))
        self.bindings = copy.deepcopy(value['bindings'])
        self.check_bindings()
        self.load_source()
        self.check_evidence()
        self.load_baselines()

    def check_bindings(self):
        require(actions.same(self.bindings, {'upload': actions.BINDINGS}),
                'Wrong fixed upload-only bindings')
        require(actions.same(self.expected_identity, actions.EXPECTED_IDENTITY),
                'Upload boot/identity differs')

    def load_source(self):
        raw = self.fixed_bytes[COMPILED + 'inputs_static.json']
        require(sha(raw) == MANIFEST_SHA, 'B4 manifest changed')
        value = decode(raw, 65536)
        keys(value, ('schema', 'source_sha256', 'boot_id', 'files'))
        require(value['schema'] == 'b4-app-m0-static-inputs-v1'
                and value['source_sha256'] == SOURCE
                and value['boot_id'] == self.expected_identity['boot_id']
                and type(value['files']) is dict and len(value['files']) == 130,
                'B4 source identity differs')
        for name, digest in value['files'].items():
            self.fixed_bytes[name] = pinned_file(self.root, name, digest)
            self.fixed_pins[name] = digest
        owner = types.SimpleNamespace(root=self.root, base=current)
        names = self.source_inventory()
        self.source_hashes, source = legacy.diagnostic.CompileDiagnostic.source_mapping(
            owner, self.fixed_bytes, names)
        require(source == SOURCE, 'Current source projection differs')
        sizes = {sha(raw): len(raw) for raw in self.fixed_bytes.values()}
        self.source_files = {name: dict(bytes=sizes[digest], sha256=digest)
                             for name, digest in self.source_hashes.items()}
        self.adapter_pin = dict(path=actions.ADAPTER, bytes=actions.ADAPTER_BYTES,
                                sha256=actions.ADAPTER_SHA)
        require(self.scope['files'][RAW + 'remote.py'] == actions.ADAPTER_SHA,
                'Scope adapter differs')

    def check_evidence(self):
        super().check_evidence()
        value = decode(self.fixed_bytes[COMPILED + 'native_static01/result.json'], 1048576)
        require(value['schema'] == 'b4-app-m0-static-compile-outcome-v1'
                and value['project'] == PLAN['profile']['project']
                and value['fqbn'] == PLAN['profile']['fqbn']
                and value['flags'] == PLAN['profile']['flags'],
                'Not the fixed inhibited B4 build')

    def prepare_commands(self):
        sources = {'helper': self.fixed_bytes[PROBE + 'static_remote.py'],
                   'support': self.fixed_bytes[STATIC + 'capture_remote.py'],
                   'upload': self.fixed_bytes[STATIC + 'upload_remote.py']}
        remote = {'upload': tuple(actions.build_command('upload', sources,
                    copy.deepcopy(self.bindings['upload']), self.adapter_pin))}
        self.commands = types.MappingProxyType(dict(remote))
        remote.update({label: tuple(receipt['argv'])
                       for label, receipt, unused in self.prerequisite_receipts})
        isolated = legacy.legacy.CAPABILITY_ARGV[:-1]
        remote['capabilities'] = isolated + (legacy.capability_program(
            sources['helper'], self.source_hashes, self.adapter_pin),)
        values = dict(BOOT=self.expected_identity['boot_id'], CLI=compiler.CLI,
                      CLI_SHA=compiler.CLI_SHA, REMOTE=ADAPTER_ROOT)
        claim = '\n'.join(name + '=' + repr(value) for name, value in values.items())
        claim += '\n' + compiler.IDENTITY
        claim += "Path(REMOTE).mkdir(mode=0o700)\nprint(json.dumps(identity))\n"
        remote['adapter-claim'] = isolated + (claim,)
        self.push_arguments = ('push', str(self.root / RAW / 'remote.py'), actions.ADAPTER)
        self.all_commands = types.MappingProxyType(remote)
        self.timeouts = types.MappingProxyType({**{name: 195 if name == 'upload' else 60
                                                  for name in remote}, 'adapter-push': 60})
        self.command_records = {name: command_record(argv, self.timeouts[name])
                                for name, argv in remote.items()}
        self.command_records['adapter-push'] = dict(
            argv_sha256=sha(canonical(list(self.push_arguments))), timeout=60)
        allowed = {(native_arguments(argv), self.timeouts[name], name)
                   for name, argv in remote.items()}
        allowed.add((self.push_arguments, 60, 'adapter-push'))
        self.allowed = frozenset(allowed)
        require(len(self.allowed) == 6, 'Wrong fixed upload allowlist')
        self.input_state = self.state_bytes()

    def claim(self):
        require(self.admitted and not self.claim_started, 'Missing admission or repeated claim')
        self.claim_started = True
        self.local()
        require(not os.path.lexists(self.output), 'Host attempt already consumed')
        self.output.mkdir(mode=0o700)
        info = self.output.stat()
        self.output_identity = (info.st_dev, info.st_ino)
        self.claimed = True
        inputs = {**self.scope['files'], **self.fixed_pins, SCOPE: sha(self.scope_raw),
                  ADB: ADB_SHA}
        self.write('inputs.json', {**self.identity_record(), 'input_hashes': inputs,
                   'commands': self.command_records,
                   'remote_evidence': {'upload': self.bindings['upload']['output']}})
        self.claim_ready = True

    def transport(self, arguments, timeout, label):
        require(type(self.counter) is int and self.counter < 9, 'Upload transport bound')
        limit = 2 if label in (*BASELINE_LABELS, 'capabilities') else 1
        require(self.command_counts.get(label, 0) < limit, 'Upload command already consumed')
        return super().transport(arguments, timeout, label)

    def intent(self, action, predecessor):
        require(type(action) is str and action == 'upload' and predecessor is None,
                'Only upload without predecessor is permitted')
        return super().intent(action, predecessor)

    def check_counters(self, result):
        require(type(self.counter) is int and self.counter == self.transport_calls <= 9,
                'Transport counter differs')
        require(self.dispatched_actions <= self.intent_actions <= {'upload'},
                'Invalid upload action set')
        if result['status'] == 'COMPLETED':
            expected = {name: 2 for name in (*BASELINE_LABELS, 'capabilities')}
            expected.update({name: 1 for name in ('adapter-claim', 'adapter-push', 'upload')})
            require(self.counter == 9 and self.command_counts == expected
                    and self.stage_ready and self.stage_intent_ready
                    and self.stage_claim_verified
                    and self.stage_dispatches == {'adapter-claim', 'adapter-push'}
                    and self.intent_actions == self.dispatched_actions == {'upload'},
                    'Incomplete successful upload dispatch set')
            require(type(result['upload_attempts']) is int and result['upload_attempts'] == 1,
                    'Wrong upload attempt count')
            require(not (self.local_errors or self.prerequisite_errors or self.transport_errors),
                    'Successful diagnostics contain errors')

    def stage_failure(self, error):
        result = dict(schema='b4-app-upload-sequence-v1', status='FAILED', upload=None,
                      upload_attempts=0, first_error=helpers.error_record(error), postcheck_errors=[])
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
                                    'finish': self.finish})


def main(argv=None):
    parser = argparse.ArgumentParser(description='One fixed inhibited B4 upload', allow_abbrev=False)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--execute', action='store_true')
    selection.add_argument('--check-only', action='store_true')
    parser.add_argument('--reviewed-head', required=True)
    args = parser.parse_args(argv)
    if not re.fullmatch('[0-9a-f]{40}', args.reviewed_head):
        parser.error('--reviewed-head must be forty lowercase hexadecimal characters')
    try:
        owner = UploadRun(args.reviewed_head)
        if args.check_only:
            owner.admit()
            return 0
        return 0 if owner.run()['status'] == 'COMPLETED' else 1
    except Exception as error:
        print(json.dumps(error_record(error), sort_keys=True), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
