# Checks the public P0 ADB transport contract with isolated command substitutes.
# Keeps explicit device selection and inert-build safeguards independent of implementation.
# Run under WSL with unittest; these checks never contact an actual board or ADB server.
import itertools
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[2]
HELPER = Path(__file__).with_name('fake_command.py')
BASH = shutil.which('bash')
SERIAL = 'fixture.UNO_Q-01:5555'
SSH_TARGET = 'fixture@board.invalid'
INVENTORY = (
    ('uname', '-srmo'),
    ('arduino-cli', 'version'),
    ('arduino-cli', 'core', 'list'),
    ('arduino-cli', 'board', 'details', '--fqbn', 'arduino:zephyr:unoq'),
    ('arduino-cli', 'lib', 'list'),
    ('rsync', '--version'),
    ('python3', '--version'),
    ('ss', '-ltn'),
)
SKETCH = '''#include "src/config.h"
#include "local.h"
#include "detail/header with spaces.h"
#include "src/core/value.h"
#include "src/hal/value.h"
void setup() {}
void loop() {}
'''

FAKE_ADB = r'''#!/usr/bin/python3
import json
import os
from pathlib import Path
import runpy
import shlex
import shutil
import sys

helper = runpy.run_path(os.environ['ADB_TEST_HELPER'])
record = helper['record']
args = sys.argv[1:]
record('adb', args=args)
if args[:2] != ['-s', os.environ['ADB_TEST_SERIAL']]:
    record('rejected_remote', reason='Missing exact explicit device', args=args)
    raise SystemExit(91)
if os.environ.get('FAKE_FAIL') == 'adb':
    print('Synthetic ADB transport failure', file=sys.stderr)
    raise SystemExit(55)

root = Path(os.environ['ADB_TEST_REMOTE_ROOT']).resolve()
if len(args) == 5 and args[2] == 'push':
    source, destination = Path(args[3]), Path(args[4])
    record('push', source=str(source), destination=str(destination))
    if os.environ.get('FAKE_FAIL') == 'push':
        print('Synthetic push failure', file=sys.stderr)
        raise SystemExit(42)
    local_root = Path(os.environ['ADB_TEST_STAGE_ROOT']).resolve()
    if (not source.is_file() or source.is_symlink()
            or not source.resolve().is_relative_to(local_root)
            or not destination.resolve().is_relative_to(root)
            or not destination.parent.is_dir()):
        record('rejected_remote', reason='Unsafe or missing exact file destination')
        raise SystemExit(92)
    shutil.copyfile(source, destination)
    raise SystemExit(0)

if len(args) != 5 or args[2:4] != ['shell', '-T']:
    record('rejected_remote', reason='Expected one non-PTY shell command', args=args)
    raise SystemExit(93)
command = shlex.split(args[4])
record('adb_shell', command=command)
mode = os.environ.get('ADB_TEST_MODE', 'flash')
if mode == 'preflight':
    response = json.loads(os.environ['ADB_TEST_RESPONSES']).get(shlex.join(command))
    if response is None:
        record('rejected_remote', reason='Not a read-only inventory command', args=command)
        raise SystemExit(94)
    sys.stdout.write(response['stdout'])
    sys.stderr.write(response['stderr'])
    raise SystemExit(response['returncode'])
if command and command[0] == 'mkdir':
    for value in command[1:]:
        if value in ('-p', '--'):
            continue
        folder = Path(value).resolve()
        if not folder.is_relative_to(root):
            record('rejected_remote', reason='mkdir escaped isolated remote root')
            raise SystemExit(95)
        folder.mkdir(parents=True, exist_ok=True)
    raise SystemExit(0)
if command and command[0] == 'arduino-cli' and mode == 'flash':
    raise SystemExit(helper['fake_arduino'](command[1:]))
if command and command[0] == 'python3' and mode == 'logs':
    raise SystemExit(helper['fake_remote_python'](command[1:]))
record('rejected_remote', reason='Unexpected remote command', args=command)
raise SystemExit(96)
'''

FAKE_SSH = r'''#!/usr/bin/python3
import json
import os
import shlex
import sys

args = sys.argv[1:]
target = 'fixture@board.invalid'
command = shlex.split(' '.join(args[args.index(target) + 1:])) if target in args else []
with open(os.environ['FAKE_TRACE'], 'a', encoding='utf-8') as output:
    output.write(json.dumps({'kind': 'ssh', 'args': args, 'command': command}) + '\n')
response = json.loads(os.environ['ADB_TEST_RESPONSES']).get(shlex.join(command))
if response is None:
    raise SystemExit(97)
sys.stdout.write(response['stdout'])
sys.stderr.write(response['stderr'])
raise SystemExit(response['returncode'])
'''


class AdbTransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sumo-adb-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'checkout with spaces'
        self.root.mkdir()
        # Production tools and reviewed source are opaque inputs, never imported.
        shutil.copytree(PROJECT / 'tools', self.root / 'tools')
        self.bin = self.base / 'bin'
        self.bin.mkdir()
        for name in ('python3', 'dirname'):
            executable = shutil.which(name)
            self.assertIsNotNone(executable)
            (self.bin / name).symlink_to(executable)
        self.adb = self.bin / 'adb'
        self.adb.write_text(FAKE_ADB, encoding='utf-8')
        self.adb.chmod(0o755)
        self.helper = self.base / 'fake_commands.py'
        shutil.copyfile(HELPER, self.helper)
        self.remote = self.base / 'remote-root'
        self.trace = self.base / 'trace.jsonl'
        self.secret = 'fixture-only-secret-must-not-be-dumped'
        self.responses = {shlex.join(command): dict(returncode=0,
            stdout='Synthetic inventory: ' + shlex.join(command) + '\n',
            stderr='Synthetic diagnostic\n') for command in INVENTORY}
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(('SUMO_', 'FAKE_', 'ADB_TEST_'))}
        self.env.update(PATH=str(self.bin), SUMO_TRANSPORT='adb',
            SUMO_ADB_SERIAL=SERIAL, SUMO_REMOTE_ROOT=str(self.remote),
            FAKE_TRACE=str(self.trace), ADB_TEST_SERIAL=SERIAL,
            ADB_TEST_HELPER=str(self.helper), ADB_TEST_REMOTE_ROOT=str(self.remote),
            ADB_TEST_STAGE_ROOT=str(self.root / 'build/stage'),
            ADB_TEST_SECRET=self.secret)
        self.events = []
        self.make_fixture()

    def write(self, relative, text):
        destination = self.root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding='utf-8')

    def make_fixture(self):
        self.write('src/config.h', '#pragma once\n#define FIXTURE_VALUE 20\n')
        for module in ('core', 'hal'):
            self.write(f'src/{module}/value.h', '#pragma once\n')
            self.write(f'src/{module}/value.cpp', '#include "../config.h"\n#include "value.h"\n')
        for target in ('bench/p0_matrix', 'bench/p0_timing', 'bench/other', 'src/app'):
            self.write(f'{target}/{Path(target).name}.ino', SKETCH)
            self.write(f'{target}/local.h', '#pragma once\n#define LOCAL 10\n')
            self.write(f'{target}/detail/header with spaces.h', '#pragma once\n')

    def use_reviewed_sources(self):
        for relative in ('src', 'bench/p0_matrix', 'bench/p0_timing'):
            destination = (self.root / relative).resolve()
            self.assertTrue(destination.is_relative_to(self.root.resolve()))
            shutil.rmtree(destination)
            shutil.copytree(PROJECT / relative, destination)

    def run_tool(self, *args, tool='flash.sh', changes=None):
        self.trace.unlink(missing_ok=True)
        mode = {'flash.sh': 'flash', 'preflight.sh': 'preflight', 'logs.sh': 'logs'}[tool]
        env = dict(self.env, ADB_TEST_MODE=mode,
                   ADB_TEST_RESPONSES=json.dumps(self.responses))
        for key, value in (changes or {}).items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = value
        result = subprocess.run([BASH, str(self.root / 'tools' / tool), *args],
            cwd=self.root, env=env, text=True, input='UNTRUSTED KEYBOARD INPUT\n',
            capture_output=True, timeout=20, check=False)
        self.events = ([json.loads(line) for line in self.trace.read_text().splitlines()]
                       if self.trace.exists() else [])
        self.assertNotIn(self.secret, result.stdout + result.stderr)
        self.assertNotIn('rejected_remote', [event['kind'] for event in self.events])
        return result

    def commands(self, name):
        return [event['args'] for event in self.events
                if event['kind'] == 'arduino' and event['args'][0] == name]

    def assert_failed(self, result, before_transport=False):
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertTrue((result.stdout + result.stderr).strip())
        if before_transport:
            self.assertEqual([], self.events)

    def assert_shell_contract(self, serial=SERIAL):
        for event in self.events:
            if event['kind'] != 'adb':
                continue
            args = event['args']
            self.assertEqual(['-s', serial], args[:2])
            self.assertEqual(5, len(args))
            if args[2] == 'shell':
                self.assertEqual('-T', args[3])
                self.assertTrue(shlex.split(args[4]))
            else:
                self.assertEqual('push', args[2])
            self.assertNotIn('devices', args)
            self.assertNotIn('--delete', args)

    def assert_no_motion_command(self):
        self.assertEqual([], self.commands('upload'))
        self.assertFalse({'remote_python', 'socket_connect'} &
                         {event['kind'] for event in self.events})
        for event in self.events:
            if event['kind'] == 'adb_shell':
                self.assertFalse({'upload', 'reset', 'start', 'reboot', 'monitor',
                                  'rm', 'env', 'printenv'} & set(event['command']))

    def test_preflight_json_names_explicit_serial_and_requires_no_ssh_or_root(self):
        result = self.run_tool(tool='preflight.sh', changes={'SUMO_REMOTE_ROOT': None})
        self.assertEqual(0, result.returncode, result.stderr)
        document = json.loads(result.stdout)
        self.assertEqual('adb', document['transport'])
        self.assertEqual(SERIAL, document['target'])
        self.assertEqual('INVENTORY-COLLECTED', document['status'])
        self.assertTrue(document['limitations'])
        self.assertCountEqual(INVENTORY, [tuple(check['command']) for check in document['checks']])
        for check in document['checks']:
            self.assertEqual('OK', check['status'])
            expected = self.responses[shlex.join(check['command'])]
            for field in ('returncode', 'stdout', 'stderr'):
                self.assertEqual(expected[field], check[field])
        self.assert_shell_contract()
        self.assertFalse((self.root / 'build').exists())
        self.assertFalse((self.bin / 'ssh').exists())
        self.assertFalse((self.bin / 'rsync').exists())
        self.assert_no_motion_command()

    def test_preflight_failed_command_remains_in_incomplete_json(self):
        failure = dict(returncode=23, stdout='partial\n', stderr='synthetic unavailable\n')
        self.responses[shlex.join(INVENTORY[1])] = failure
        result = self.run_tool(tool='preflight.sh')
        self.assert_failed(result)
        document = json.loads(result.stdout)
        self.assertEqual('INCOMPLETE', document['status'])
        check, = [entry for entry in document['checks'] if tuple(entry['command']) == INVENTORY[1]]
        self.assertEqual('FAILED', check['status'])
        for field, value in failure.items():
            self.assertEqual(value, check[field])
        self.assert_shell_contract()

    def test_serial_grammar_accepts_explicit_alphanumeric_and_documented_punctuation(self):
        for serial in ('A', '0', 'board_01-test.local:5555'):
            with self.subTest(serial=serial):
                result = self.run_tool(tool='preflight.sh', changes={
                    'SUMO_ADB_SERIAL': serial, 'ADB_TEST_SERIAL': serial})
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(serial, json.loads(result.stdout)['target'])
                self.assert_shell_contract(serial)

    def test_invalid_transport_never_falls_back_or_contacts_a_device(self):
        for transport in ('', 'ADB', 'auto', 'usb', ' adb', 'adb ', 'ssh;adb'):
            with self.subTest(transport=transport):
                result = self.run_tool(tool='preflight.sh', changes={'SUMO_TRANSPORT': transport})
                self.assert_failed(result, before_transport=True)

    def test_missing_or_invalid_serial_never_automatically_selects_a_device(self):
        for serial in (None, '', '-d', '_board', ':5555', 'two devices',
                       'board;uname', 'board\nuname', 'board/one', '$(uname)'):
            with self.subTest(serial=serial):
                result = self.run_tool(tool='preflight.sh', changes={'SUMO_ADB_SERIAL': serial})
                self.assert_failed(result, before_transport=True)
                self.assertIn('SUMO_ADB_SERIAL', result.stdout + result.stderr)

    def test_unset_transport_remains_ssh_and_does_not_use_available_adb(self):
        result = self.run_tool(tool='preflight.sh', changes={'SUMO_TRANSPORT': None})
        self.assert_failed(result, before_transport=True)
        self.assertIn('SUMO_SSH_TARGET', result.stdout + result.stderr)

    def test_default_and_explicit_ssh_preserve_strict_settings_and_ignore_adb_options(self):
        ssh = self.bin / 'ssh'
        ssh.write_text(FAKE_SSH, encoding='utf-8')
        ssh.chmod(0o755)
        for transport in (None, 'ssh'):
            result = self.run_tool(tool='preflight.sh', changes={
                'SUMO_TRANSPORT': transport, 'SUMO_SSH_TARGET': SSH_TARGET,
                'SUMO_ADB_SERIAL': None, 'SUMO_ADB_EXECUTABLE': '/missing/adb'})
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(SSH_TARGET, json.loads(result.stdout)['target'])
            self.assertTrue(self.events)
            for event in self.events:
                self.assertEqual('ssh', event['kind'])
                args = event['args']
                options = [arg[2:] for arg in args if arg.startswith('-o') and arg != '-o']
                options += [args[index + 1] for index, arg in enumerate(args[:-1]) if arg == '-o']
                self.assertIn('StrictHostKeyChecking=yes', options)
                self.assertIn('BatchMode=yes', options)
                self.assertNotIn('UserKnownHostsFile=/dev/null', options)

    def test_explicit_executable_path_with_spaces_and_path_name_both_work(self):
        explicit = self.base / 'command tools' / 'adb substitute'
        explicit.parent.mkdir()
        shutil.copyfile(self.adb, explicit)
        explicit.chmod(0o755)
        named = self.bin / 'adb-alternate'
        shutil.copyfile(self.adb, named)
        named.chmod(0o755)
        for executable in (str(explicit), named.name):
            with self.subTest(executable=executable):
                result = self.run_tool('app', '--compile-only',
                                       changes={'SUMO_ADB_EXECUTABLE': executable})
                self.assertEqual(0, result.returncode, result.stderr)
                self.assert_shell_contract()
                self.assert_no_motion_command()

    def test_missing_empty_directory_and_nonexecutable_adb_fail_locally(self):
        no_execute = self.base / 'not-executable'
        no_execute.write_text(FAKE_ADB, encoding='utf-8')
        no_execute.chmod(0o644)
        for executable in ('', '/missing/adb', 'unavailable-adb', str(self.bin), str(no_execute)):
            with self.subTest(executable=executable):
                result = self.run_tool(tool='preflight.sh',
                                       changes={'SUMO_ADB_EXECUTABLE': executable})
                self.assert_failed(result, before_transport=True)
        self.adb.unlink()
        self.assert_failed(self.run_tool(tool='preflight.sh'), before_transport=True)

    def test_remote_root_retains_strict_absolute_dedicated_path_validation(self):
        for root in (None, '', '/', '//', '///', 'relative', '../outside', '/tmp/root space',
                     '/tmp/$(touch-injected)', '/tmp/remote;uname'):
            with self.subTest(root=root):
                result = self.run_tool('app', '--compile-only', changes={'SUMO_REMOTE_ROOT': root})
                self.assert_failed(result, before_transport=True)

    def test_compile_only_argument_orders_and_match_never_upload_start_or_reset(self):
        for target in ('app', 'bench/p0_matrix'):
            for match in (False, True):
                args = [target, '--compile-only'] + (['--match'] if match else [])
                for order in itertools.permutations(args):
                    with self.subTest(order=order):
                        result = self.run_tool(*order)
                        self.assertEqual(0, result.returncode, result.stderr)
                        self.assert_no_motion_command()
                        self.assert_shell_contract()
                        command, = self.commands('compile')
                        expected = 'arduino:zephyr:unoq' + (':wait_linux_boot=no' if match else '')
                        self.assertEqual(expected, command[command.index('--fqbn') + 1])
                        self.assertIn(f'-DMATCH={int(match)} -DMOTORS_ALLOWED={int(match)}',
                                      ' '.join(command))

    def test_explicit_startup_options_keep_inert_macros_and_separate_artifacts(self):
        artifacts = []
        for startup in ('default', 'immediate'):
            result = self.run_tool('bench/p0_matrix', '--startup', startup, '--compile-only')
            self.assertEqual(0, result.returncode, result.stderr)
            self.assert_no_motion_command()
            command, = self.commands('compile')
            suffix = ':wait_linux_boot=no' if startup == 'immediate' else ''
            self.assertEqual('arduino:zephyr:unoq' + suffix,
                             command[command.index('--fqbn') + 1])
            self.assertIn('-DMATCH=0 -DMOTORS_ALLOWED=0', ' '.join(command))
            artifacts.append(command[command.index('--output-dir') + 1])
        self.assertNotEqual(*artifacts)

    def test_each_staged_regular_file_is_pushed_once_to_its_exact_remote_filename(self):
        self.write('bench/p0_matrix/src/local probe.h', '#pragma once\n')
        result = self.run_tool('bench/p0_matrix', '--compile-only')
        self.assertEqual(0, result.returncode, result.stderr)
        command, = self.commands('compile')
        remote_stage = Path(command[-1])
        self.assertTrue(remote_stage.is_relative_to(self.remote))
        self.assertRegex(str(remote_stage), r'[a-f0-9]{64}')
        stage = self.root / 'build/stage/p0_matrix'
        self.assertEqual(SKETCH, (stage / 'p0_matrix.ino').read_text())
        for name in ('local.h', 'detail/header with spaces.h', 'src/local probe.h',
                     'src/config.h', 'src/core/value.h', 'src/core/value.cpp',
                     'src/hal/value.h', 'src/hal/value.cpp'):
            self.assertTrue((stage / name).is_file(), name)
        pushes = [event for event in self.events if event['kind'] == 'push']
        expected = sorted(path.relative_to(stage) for path in stage.rglob('*') if path.is_file())
        self.assertEqual(len(expected), len(pushes))
        self.assertCountEqual([str(remote_stage / relative) for relative in expected],
                              [event['destination'] for event in pushes])
        for relative in expected:
            self.assertEqual((stage / relative).read_bytes(), (remote_stage / relative).read_bytes())
        compile_index = self.events.index(next(event for event in self.events
            if event['kind'] == 'arduino' and event['args'][0] == 'compile'))
        self.assertTrue(all(self.events.index(event) < compile_index for event in pushes))
        self.assert_shell_contract()
        self.assert_no_motion_command()

    def test_content_address_is_stable_then_changes_with_source_without_deletion(self):
        roots = []
        for iteration in range(3):
            if iteration == 2:
                self.write('bench/p0_matrix/local.h', '#pragma once\n#define LOCAL 11\n')
            result = self.run_tool('bench/p0_matrix', '--compile-only')
            self.assertEqual(0, result.returncode, result.stderr)
            command, = self.commands('compile')
            roots.append(command[-1])
            self.assert_no_motion_command()
        self.assertEqual(roots[0], roots[1])
        self.assertNotEqual(roots[1], roots[2])
        self.assertTrue(Path(roots[0]).is_dir())
        self.assertTrue(Path(roots[2]).is_dir())

    def test_reviewed_default_inert_upload_follows_compile_with_same_artifact(self):
        self.use_reviewed_sources()
        for target in ('bench/p0_matrix', 'bench/p0_timing'):
            with self.subTest(target=target):
                result = self.run_tool(target)
                self.assertEqual(0, result.returncode, result.stderr)
                compiled, = self.commands('compile')
                uploaded, = self.commands('upload')
                calls = [event['args'][0] for event in self.events if event['kind'] == 'arduino']
                self.assertLess(calls.index('compile'), calls.index('upload'))
                self.assertIn('-DMATCH=0 -DMOTORS_ALLOWED=0', ' '.join(compiled))
                self.assertEqual(compiled[compiled.index('--output-dir') + 1],
                                 uploaded[uploaded.index('--input-dir') + 1])
                self.assertEqual('arduino:zephyr:unoq', uploaded[uploaded.index('--fqbn') + 1])
                self.assertNotIn('--port', uploaded)
                self.assertNotIn('/dev/ttyHS1', uploaded)
                self.assert_shell_contract()

    def test_adb_does_not_bypass_match_allowlist_startup_or_unreviewed_source_guards(self):
        cases = (('app',), ('bench/other',), ('bench/p0_matrix',),
                 ('app', '--match'), ('bench/p0_timing', '--match'),
                 ('app', '--match', '--compile-only', '--startup', 'default'),
                 ('app', '--compile-only', '--startup', 'unknown'))
        for args in cases:
            with self.subTest(args=args):
                self.assert_failed(self.run_tool(*args), before_transport=True)
        self.use_reviewed_sources()
        self.assert_failed(self.run_tool('bench/p0_matrix', '--startup', 'immediate'),
                           before_transport=True)

    def test_reviewed_upload_rejects_added_or_changed_source_before_adb(self):
        self.use_reviewed_sources()
        for relative in ('src/config.h', 'src/core/extra.cpp', 'bench/p0_timing/extra.h'):
            path = self.root / relative
            original = path.read_bytes() if path.exists() else None
            path.write_bytes((original or b'') + b'\n// unreviewed fixture change\n')
            with self.subTest(relative=relative):
                self.assert_failed(self.run_tool('bench/p0_timing'), before_transport=True)
            if original is None:
                path.unlink()
            else:
                path.write_bytes(original)

    def test_push_failure_prevents_compile_and_upload(self):
        result = self.run_tool('app', '--compile-only', changes={'FAKE_FAIL': 'push'})
        self.assert_failed(result)
        self.assertTrue(any(event['kind'] == 'push' for event in self.events))
        self.assertEqual([], self.commands('compile'))
        self.assertEqual([], self.commands('upload'))

    def test_compile_failure_prevents_reviewed_inert_upload(self):
        self.use_reviewed_sources()
        result = self.run_tool('bench/p0_timing', changes={'FAKE_FAIL': 'compile'})
        self.assert_failed(result)
        self.assertEqual(1, len(self.commands('compile')))
        self.assertEqual([], self.commands('upload'))

    def test_missing_or_wrong_core_blocks_compile_and_upload(self):
        for version in ('', '0.9.0', '1.0.1'):
            with self.subTest(version=version):
                result = self.run_tool('app', '--compile-only',
                                       changes={'FAKE_CORE_VERSION': version})
                self.assert_failed(result)
                self.assertEqual([], self.commands('compile'))
                self.assertEqual([], self.commands('upload'))

    def test_adb_shell_failure_stops_compile_and_is_not_successful_inventory(self):
        result = self.run_tool('app', '--compile-only', changes={'FAKE_FAIL': 'adb'})
        self.assert_failed(result)
        self.assertEqual([], self.commands('compile'))
        self.assertEqual([], self.commands('upload'))
        result = self.run_tool(tool='preflight.sh', changes={'FAKE_FAIL': 'adb'})
        self.assert_failed(result)
        document = json.loads(result.stdout)
        self.assertEqual('INCOMPLETE', document['status'])
        self.assertTrue(document['checks'])
        self.assertTrue(all(check['status'] == 'FAILED' for check in document['checks']))

    def test_preflight_ambiguous_or_transport_failure_stops_but_missing_utility_continues(self):
        first_key = shlex.join(INVENTORY[0])
        original = self.responses[first_key]
        for status in (1, 124, 255):
            with self.subTest(status=status):
                self.responses[first_key] = dict(returncode=status, stdout='',
                    stderr='Synthetic transport or ambiguous ADB failure\n')
                result = self.run_tool(tool='preflight.sh')
                self.assert_failed(result)
                document = json.loads(result.stdout)
                self.assertEqual('INCOMPLETE', document['status'])
                self.assertEqual(1, len(document['checks']))
                self.assertEqual(status, document['checks'][0]['returncode'])
                self.assertEqual(1, len([event for event in self.events if event['kind'] == 'adb']))
        self.responses[first_key] = original
        self.responses[shlex.join(('rsync', '--version'))] = dict(returncode=127,
            stdout='', stderr='Synthetic remote rsync unavailable\n')
        result = self.run_tool(tool='preflight.sh')
        self.assert_failed(result)
        document = json.loads(result.stdout)
        self.assertEqual('INCOMPLETE', document['status'])
        self.assertEqual(len(INVENTORY), len(document['checks']))
        failed, = [check for check in document['checks'] if check['status'] == 'FAILED']
        self.assertEqual(['rsync', '--version'], failed['command'])
        self.assertEqual(127, failed['returncode'])

    def test_logs_use_explicit_adb_and_execute_receive_only_monitor_request(self):
        result = self.run_tool(tool='logs.sh', changes={'SUMO_REMOTE_ROOT': None})
        self.assert_failed(result)  # The substitute reports a finite stream then disconnects.
        self.assertIn('fixture monitor counter=7', result.stdout)
        connections = [event['endpoint'] for event in self.events if event['kind'] == 'socket_connect']
        self.assertEqual([['127.0.0.1', 7500]], connections)
        self.assertTrue(any(event['kind'] == 'socket_recv' for event in self.events))
        self.assertFalse({'socket_send', 'stdin_read', 'push'} &
                         {event['kind'] for event in self.events})
        self.assertEqual([], self.commands('compile'))
        self.assertEqual([], self.commands('upload'))
        self.assert_shell_contract()

    def test_preflight_and_logs_reject_unrequested_arguments_before_adb(self):
        for tool in ('preflight.sh', 'logs.sh'):
            for args in (('--send',), ('--compile-only',), ('app',)):
                with self.subTest(tool=tool, args=args):
                    self.assert_failed(self.run_tool(*args, tool=tool), before_transport=True)


if __name__ == '__main__':
    unittest.main()
