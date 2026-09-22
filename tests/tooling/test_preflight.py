# Checks the P0 read-only inventory contract through the public shell command.
# Keeps SSH, board commands, and credentials isolated from the real environment.
# Run with Python unittest under WSL; these checks do not validate real hardware.
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[2]
BASH = shutil.which('bash')
TARGET = 'fixture@board.invalid'
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
FAKE_SSH = r'''#!/usr/bin/python3
import json
import os
from pathlib import Path
import shlex
import sys

args = sys.argv[1:]
target = 'fixture@board.invalid'
command = shlex.split(' '.join(args[args.index(target) + 1:])) if target in args else []
with open(os.environ['PREFLIGHT_FAKE_TRACE'], 'a', encoding='utf-8') as output:
    output.write(json.dumps({'args': args, 'command': command}) + '\n')
responses = json.loads(os.environ['PREFLIGHT_FAKE_RESPONSES'])
response = responses.get(shlex.join(command))
if response is None:
    print('Rejected command outside the read-only fixture contract', file=sys.stderr)
    raise SystemExit(98)
if os.environ.get('PREFLIGHT_FAKE_SSH_FAILURE'):
    print(os.environ['PREFLIGHT_FAKE_SSH_FAILURE'], file=sys.stderr)
    raise SystemExit(255)
sys.stdout.write(response['stdout'])
sys.stderr.write(response['stderr'])
raise SystemExit(response['returncode'])
'''


class PreflightContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sumo-preflight-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Copy scripts as opaque executables; assertions use the public contract.
        shutil.copytree(PROJECT / 'tools', self.root / 'tools')
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        (self.bin / 'ssh').write_text(FAKE_SSH, encoding='utf-8')
        (self.bin / 'ssh').chmod(0o755)
        self.trace = self.root / 'ssh.jsonl'
        self.responses = {
            shlex.join(command): {
                'returncode': 0,
                'stdout': f'Synthetic inventory: {shlex.join(command)}\nsecond line\n',
                'stderr': f'Synthetic diagnostic: {command[0]}\n',
            } for command in INVENTORY
        }
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(('SUMO_', 'PREFLIGHT_'))}
        self.secret = 'fixture-only-private-environment-value'
        self.env.update(PATH=str(self.bin) + os.pathsep + self.env['PATH'],
                        SUMO_SSH_TARGET=TARGET,
                        PREFLIGHT_FAKE_TRACE=str(self.trace),
                        PREFLIGHT_SECRET_SENTINEL=self.secret)

    def run_preflight(self, *args, changes=None):
        self.trace.unlink(missing_ok=True)
        env = dict(self.env, PREFLIGHT_FAKE_RESPONSES=json.dumps(self.responses))
        for key, value in (changes or {}).items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = value
        result = subprocess.run(
            [BASH, str(self.root / 'tools/preflight.sh'), *args],
            cwd=self.root, env=env, text=True, input='UNTRUSTED KEYBOARD INPUT\n',
            capture_output=True, timeout=15, check=False)
        self.events = ([json.loads(line) for line in self.trace.read_text().splitlines()]
                       if self.trace.exists() else [])
        self.assertNotIn(self.secret, result.stdout + result.stderr)
        for event in self.events:
            self.assertIn(tuple(event['command']), INVENTORY,
                          'Preflight must only request the fixed read-only inventory')
        return result

    def inventory_document(self, result, expected_status):
        document = json.loads(result.stdout)
        self.assertEqual(expected_status, document['status'])
        self.assertEqual(TARGET, document['target'])
        self.assertIsInstance(document['limitations'], list)
        self.assertTrue(document['limitations'], 'Inventory must disclose validation limits')
        self.assertTrue(all(isinstance(item, str) and item.strip()
                            for item in document['limitations']))
        self.assertIsInstance(document['checks'], list)
        self.assertEqual(len(document['checks']), len(self.events))
        self.assertCountEqual([event['command'] for event in self.events],
                              [check['command'] for check in document['checks']])
        for check in document['checks']:
            self.assertTrue(isinstance(check['name'], str) and check['name'])
            self.assertIsInstance(check['command'], list)
            self.assertIn(tuple(check['command']), INVENTORY)
            self.assertIn(check['status'], ('OK', 'FAILED'))
            self.assertIsInstance(check['returncode'], int)
            self.assertIsInstance(check['stdout'], str)
            self.assertIsInstance(check['stderr'], str)
        return document

    def assert_failed_without_transport(self, result):
        self.assertNotEqual(0, result.returncode)
        self.assertTrue((result.stdout + result.stderr).strip())
        self.assertEqual([], self.events)

    def test_complete_inventory_is_json_and_needs_no_remote_build_root(self):
        self.assertNotIn('SUMO_REMOTE_ROOT', self.env)
        result = self.run_preflight()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        document = self.inventory_document(result, 'INVENTORY-COLLECTED')
        self.assertCountEqual(INVENTORY, [tuple(check['command'])
                                          for check in document['checks']])
        for check in document['checks']:
            self.assertEqual('OK', check['status'])
            expected = self.responses[shlex.join(check['command'])]
            for field in ('returncode', 'stdout', 'stderr'):
                self.assertEqual(expected[field], check[field])
        self.assertFalse((self.root / 'build').exists(), 'Inventory must not stage firmware')

    def test_every_ssh_invocation_requires_known_host_and_noninteractive_auth(self):
        result = self.run_preflight()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(len(INVENTORY), len(self.events))
        for event in self.events:
            args = event['args']
            options = [arg[2:] for arg in args if arg.startswith('-o') and arg != '-o']
            options += [args[index + 1] for index, arg in enumerate(args[:-1])
                        if arg == '-o']
            self.assertIn('StrictHostKeyChecking=yes', options)
            self.assertIn('BatchMode=yes', options)
            self.assertFalse(any(option.lower() in (
                'stricthostkeychecking=no', 'stricthostkeychecking=accept-new',
                'batchmode=no', 'userknownhostsfile=/dev/null') for option in options))
            self.assertEqual(1, args.count(TARGET))

    def test_any_failed_inventory_command_makes_result_incomplete(self):
        for command in INVENTORY:
            with self.subTest(command=command):
                key = shlex.join(command)
                original = self.responses[key]
                failed = dict(returncode=23, stdout='partial inventory\n',
                              stderr='Synthetic command unavailable\n')
                self.responses[key] = failed
                result = self.run_preflight()
                self.responses[key] = original
                self.assertNotEqual(0, result.returncode)
                document = self.inventory_document(result, 'INCOMPLETE')
                matches = [check for check in document['checks']
                           if tuple(check['command']) == command]
                self.assertEqual(1, len(matches))
                self.assertEqual('FAILED', matches[0]['status'])
                for field in ('returncode', 'stdout', 'stderr'):
                    self.assertEqual(failed[field], matches[0][field])

    def test_ssh_authentication_failure_is_never_a_successful_inventory(self):
        error = 'fixture@board.invalid: Permission denied (publickey).\n'
        result = self.run_preflight(changes={'PREFLIGHT_FAKE_SSH_FAILURE': error})
        self.assertNotEqual(0, result.returncode)
        document = self.inventory_document(result, 'INCOMPLETE')
        self.assertTrue(document['checks'])
        for check in document['checks']:
            self.assertEqual('FAILED', check['status'])
            self.assertEqual(255, check['returncode'])
            self.assertEqual('', check['stdout'])
            self.assertIn(error.strip(), check['stderr'])

    def test_ssh_reported_connection_timeout_is_recorded_without_waiting(self):
        error = 'ssh: connect to host board.invalid port 22: Connection timed out'
        result = self.run_preflight(changes={'PREFLIGHT_FAKE_SSH_FAILURE': error})
        self.assertNotEqual(0, result.returncode)
        document = self.inventory_document(result, 'INCOMPLETE')
        self.assertTrue(document['checks'])
        self.assertTrue(all(check['status'] == 'FAILED' for check in document['checks']))
        self.assertTrue(all(error in check['stderr'] for check in document['checks']))

    def test_missing_or_empty_target_fails_before_transport(self):
        for target in (None, ''):
            with self.subTest(target=target):
                result = self.run_preflight(changes={'SUMO_SSH_TARGET': target})
                self.assert_failed_without_transport(result)
                self.assertIn('SUMO_SSH_TARGET', result.stdout + result.stderr)

    def test_missing_ssh_fails_locally_and_cannot_reach_real_ssh(self):
        isolated_bin = self.root / 'without-ssh'
        isolated_bin.mkdir()
        for command in ('python3', 'dirname'):
            executable = shutil.which(command)
            self.assertIsNotNone(executable)
            (isolated_bin / command).symlink_to(executable)
        result = self.run_preflight(changes={'PATH': str(isolated_bin)})
        self.assert_failed_without_transport(result)
        self.assertIn('ssh', (result.stdout + result.stderr).lower())

    def test_extra_arguments_fail_before_transport(self):
        for args in (('app',), ('--compile-only',), ('--match',),
                     ('--startup', 'immediate'), ('--unknown',)):
            with self.subTest(args=args):
                self.assert_failed_without_transport(self.run_preflight(*args))

    def test_option_or_shell_injection_targets_fail_before_transport(self):
        for target in ('-oProxyCommand=echo', 'fixture@board.invalid;uname',
                       'fixture@board.invalid\nuname'):
            with self.subTest(target=target):
                result = self.run_preflight(changes={'SUMO_SSH_TARGET': target})
                self.assert_failed_without_transport(result)


if __name__ == '__main__':
    unittest.main()
