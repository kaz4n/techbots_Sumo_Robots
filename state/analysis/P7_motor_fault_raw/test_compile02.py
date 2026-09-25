# Tests D167's closed attempt selectors and per-instance compile ownership.
# Preserves historical inputs and child machinery while isolating paths in RAM.
# Uses opaque caller import and controlled transport substitutes; no native calls.
import ast
import base64
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

RAW = Path(__file__).resolve().parent
CALLER = RAW / 'compile_motor_fault.py'
PRESERVED = json.loads((RAW / 'ownership_preserved.json').read_text(encoding='utf-8'))
PATH_NAMES = ('ROOT', 'RAW', 'OUTPUT', 'INPUTS', 'STAGE', 'REMOTE', 'SKETCH')


class Compile02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        name = '_sumox_compile02_contract_fixture'
        spec = importlib.util.spec_from_file_location(name, CALLER)
        cls.caller = importlib.util.module_from_spec(spec)
        sys.modules[name] = cls.caller
        cls.addClassCleanup(sys.modules.pop, name, None)
        spec.loader.exec_module(cls.caller)

    def setUp(self):
        if not Path('/dev/shm').is_dir():
            self.skipTest('Linux RAM scratch required')
        temporary = tempfile.TemporaryDirectory(prefix='sumox-compile02-', dir='/dev/shm')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.raw = self.root / 'state/analysis/P7_motor_fault_raw'
        self.raw.mkdir(parents=True)
        self.remote_parent = Path('/fixture/remote')
        paths = {'ROOT': self.root, 'RAW': self.raw,
                 'OUTPUT': self.raw / 'native_compile01',
                 'INPUTS': self.raw / 'compile_inputs.json',
                 'STAGE': self.root / 'build/stage/motor_fault',
                 'REMOTE': self.remote_parent / 'motor-fault-compile01',
                 'SKETCH': self.remote_parent / 'motor-fault-compile01/motor_fault'}
        for name, value in paths.items():
            if isinstance(getattr(self.caller, name), str):
                value = str(value)
            patcher = mock.patch.object(self.caller, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        # Opaque pinned helper and inert bytes satisfy fixture identity reads only.
        support = Path(self.caller.SUPPORT)
        destination = self.root / support
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(RAW.parents[2] / support, destination)
        adb = self.root / 'fixture-adb'
        adb.write_bytes(b'Harmless test bytes; subprocess dispatch is substituted.\n')
        for name, value in (('ADB', str(adb)), ('ADB_SHA', hashlib.sha256(adb.read_bytes()).hexdigest())):
            patcher = mock.patch.object(self.caller, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.globals_before = {name: getattr(self.caller, name) for name in PATH_NAMES}
        for name, marker in (('compile_inputs.json', 'one'), ('compile_inputs02.json', 'two')):
            (self.raw / name).write_text(json.dumps({marker + '.txt': 'a' * 64}), encoding='utf-8')
        guard = mock.patch.object(subprocess, 'run', side_effect=AssertionError('native dispatch forbidden'))
        self.native = guard.start()
        self.addCleanup(guard.stop)

    def assert_globals_unchanged(self):
        self.assertEqual(self.globals_before, {name: getattr(self.caller, name) for name in PATH_NAMES})

    def selected(self, run_id):
        return self.caller.CompileOnce(run_id=run_id)

    def assert_paths(self, instance, run_id):
        suffix = '01' if run_id == 'compile01' else '02'
        self.assertEqual(run_id, instance.run_id)
        self.assertEqual(self.raw / ('native_compile' + suffix), Path(instance.output))
        manifest = 'compile_inputs.json' if suffix == '01' else 'compile_inputs02.json'
        self.assertEqual(self.raw / manifest, Path(instance.inputs_path))
        self.assertEqual(self.remote_parent / ('motor-fault-' + run_id), Path(instance.remote))
        self.assertEqual(Path(instance.remote) / 'motor_fault', Path(instance.sketch))
        self.assertFalse(Path(instance.output).exists())

    def test_pure_request_parser_accepts_only_the_two_exact_list_forms(self):
        constructor = mock.patch.object(self.caller, 'CompileOnce', side_effect=AssertionError('constructor called'))
        with constructor as create, mock.patch.object(Path, 'read_text', side_effect=AssertionError('file read')):
            self.assertEqual('compile01', self.caller.parse_request(['--execute']))
            self.assertEqual('compile02', self.caller.parse_request(['--execute', '--run', 'compile02']))
            invalid = (None, False, 0, '--execute', b'--execute', ('--execute',), {}, [],
                       ['--execute', '--run', 'compile01'], ['--run', 'compile02', '--execute'],
                       ['--execute', '--run'], ['--execute', '--run', 'compile03'],
                       ['--execute', '--run', 'compile02', 'extra'], ['--execute', '--execute'],
                       ['--execute '], ['--execute', '--run', None], ['--execute', '--run', 2])
            for arguments in invalid:
                with self.subTest(arguments=arguments), self.assertRaises((ValueError, RuntimeError)):
                    self.caller.parse_request(arguments)
            create.assert_not_called()
        self.native.assert_not_called()

    def test_constructor_rejects_other_values_before_any_manifest_read(self):
        self.assertEqual(inspect.Parameter.KEYWORD_ONLY,
                         inspect.signature(self.caller.CompileOnce).parameters['run_id'].kind)
        with mock.patch.object(Path, 'read_text', side_effect=AssertionError('file read')), \
             mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('file read')):
            for value in (None, False, 1, [], {}, b'compile02', '', 'compile2',
                          'compile03', '../compile02', 'compile02 ', 'COMPILE02'):
                with self.subTest(value=value), self.assertRaises((ValueError, RuntimeError)):
                    self.selected(value)
            with self.assertRaises(TypeError):
                self.caller.CompileOnce('compile02')
        self.native.assert_not_called()

    def test_default_and_explicit02_read_only_their_own_manifest_and_keep_default_paths(self):
        reads = []
        original_text = Path.read_text
        original_bytes = Path.read_bytes

        def text(path, *args, **kwargs):
            reads.append(Path(path))
            return original_text(path, *args, **kwargs)

        def binary(path, *args, **kwargs):
            reads.append(Path(path))
            return original_bytes(path, *args, **kwargs)

        with mock.patch.object(Path, 'read_text', autospec=True, side_effect=text), \
             mock.patch.object(Path, 'read_bytes', autospec=True, side_effect=binary):
            first = self.caller.CompileOnce()
            self.assertIn(self.raw / 'compile_inputs.json', reads)
            self.assertNotIn(self.raw / 'compile_inputs02.json', reads)
            reads.clear()
            second = self.selected('compile02')
            self.assertIn(self.raw / 'compile_inputs02.json', reads)
            self.assertNotIn(self.raw / 'compile_inputs.json', reads)
        self.assert_paths(first, 'compile01')
        self.assert_paths(second, 'compile02')
        self.assert_globals_unchanged()
        self.native.assert_not_called()

    def test_interleaved_preambles_use_selected_remote_and_never_rebind_default_globals(self):
        first, second = self.selected('compile01'), self.selected('compile02')
        for active, other in ((first, second), (second, first), (first, second)):
            program = active.preamble()
            self.assertIn(str(active.remote), program)
            self.assertNotIn(str(other.remote), program)
            self.assert_paths(active, active.run_id)
            self.assert_globals_unchanged()
        self.native.assert_not_called()

    def test_transport_receipts_stay_in_selected_output_for_interleaved_attempts(self):
        first, second = self.selected('compile01'), self.selected('compile02')
        receipts = []
        completed = subprocess.CompletedProcess(['controlled-adb'], 0, stdout=b'fixture stdout', stderr=b'fixture stderr')
        with mock.patch.object(subprocess, 'run', return_value=completed) as controlled:
            for index, instance in enumerate((first, second, first)):
                Path(instance.output).mkdir(parents=True, exist_ok=True)
                with mock.patch.object(instance, 'local', return_value=None):
                    result, receipt = instance.transport(['version'], 1.0, 'fixture-' + str(index))
                self.assertEqual(completed.stdout, result.stdout)
                self.assertEqual(completed.stderr, result.stderr)
                self.assertTrue(Path(receipt).is_relative_to(Path(instance.output)))
                self.assertTrue(Path(receipt).is_dir())
                receipts.append(Path(receipt))
                self.assert_globals_unchanged()
            self.assertEqual(3, controlled.call_count)
        self.assertEqual(3, len(set(receipts)))

    def test_checked_command_raw_receipts_stay_with_interleaved_instances(self):
        first, second = self.selected('compile01'), self.selected('compile02')
        for index, (instance, other) in enumerate(((first, second), (second, first), (first, second))):
            folder = Path(instance.output) / 'commands' / ('fixture-' + str(index))
            folder.mkdir(parents=True)
            stdout, stderr = ('stdout-' + instance.run_id).encode(), b'fixture stderr\n'
            record = {'status': 'COMPLETED', 'execution': {'returncode': 0, 'timed_out': False, 'reaped': True},
                      'stdout_base64': base64.b64encode(stdout).decode(),
                      'stderr_base64': base64.b64encode(stderr).decode(),
                      'stdout_bytes': len(stdout), 'stderr_bytes': len(stderr)}
            result = subprocess.CompletedProcess(['controlled-direct'], 0,
                                                stdout=json.dumps(record).encode(), stderr=b'')
            with mock.patch.object(instance, 'local', return_value=None), \
                 mock.patch.object(instance, 'inventory', return_value={}), \
                 mock.patch.object(instance, 'sources', return_value=None), \
                 mock.patch.object(instance, 'prerequisites', return_value=None), \
                 mock.patch.object(instance, 'direct', return_value=(result, folder)) as direct:
                actual = instance.command_runner('2629958581', ['arduino-cli', 'version'], capture=True)
            self.assertEqual(stdout.decode(), actual.stdout)
            self.assertEqual(stderr.decode(), actual.stderr)
            direct.assert_called_once()
            self.assertEqual(record, json.loads((folder / 'remote_result.json').read_text()))
            self.assertEqual(stdout, (folder / 'child.stdout').read_bytes())
            self.assertEqual(stderr, (folder / 'child.stderr').read_bytes())
            self.assert_globals_unchanged()
        self.native.assert_not_called()

    def test_wrong_instance_cache_prefix_fails_local_admission_without_transport(self):
        first, second = self.selected('compile01'), self.selected('compile02')
        for active, other in ((first, second), (second, first)):
            with mock.patch.object(sys, 'dont_write_bytecode', True), \
                 mock.patch.object(sys, 'pycache_prefix', str(Path(other.output) / 'pycache')), \
                 self.assertRaises((ValueError, RuntimeError)):
                active.local()
        self.native.assert_not_called()
        self.assert_globals_unchanged()

    def test_run_rejects_invocation_selected_for_the_other_attempt_before_transport(self):
        for selected, arguments in (('compile01', ['--execute', '--run', 'compile02']),
                                    ('compile02', ['--execute'])):
            instance = self.selected(selected)
            with mock.patch.object(sys, 'argv', ['compile_motor_fault.py', *arguments]), \
                 mock.patch.object(sys, 'dont_write_bytecode', True), \
                 mock.patch.object(sys, 'pycache_prefix', str(Path(instance.output) / 'pycache')), \
                 self.assertRaises((ValueError, RuntimeError)):
                instance.run()
        self.native.assert_not_called()
        self.assert_globals_unchanged()

    def test_stage_pushes_each_mapped_source_into_the_selected_remote_sketch(self):
        sources = {'bench/motor_fault/motor_fault.ino': b'// fixture sketch\n',
                   'bench/motor_fault/src/motor_fault.h': b'// fixture diagnostic\n',
                   'src/config.h': b'// fixture config\n', 'src/core/fsm.h': b'// fixture core\n',
                   'src/hal/motors.h': b'// fixture HAL\n'}
        manifest = {name: hashlib.sha256(data).hexdigest() for name, data in sources.items()}
        staged = {name.removeprefix('bench/motor_fault/'): data for name, data in sources.items()}
        for name, data in sources.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        for run_id in ('compile01', 'compile02'):
            manifest_path = self.raw / ('compile_inputs.json' if run_id == 'compile01' else 'compile_inputs02.json')
            manifest_path.write_text(json.dumps(manifest))
            instance = self.selected(run_id)
            instance.claimed = True
            receipt = self.root / ('stage-receipt-' + run_id)
            receipt.mkdir()
            stage = Path(self.caller.STAGE)

            def prepare(sketch):
                self.assertEqual('bench/motor_fault', sketch)
                for name, data in staged.items():
                    path = stage / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                return stage

            board = mock.Mock()
            board.stage.side_effect = prepare
            response = (subprocess.CompletedProcess(['fixture-stage'], 0, stdout=b'', stderr=b''), receipt)
            with mock.patch.object(instance, 'local', return_value=None), \
                 mock.patch.object(instance, 'sources', return_value=None), \
                 mock.patch.object(instance, 'prerequisites', return_value=None), \
                 mock.patch.object(instance, 'direct', return_value=response), \
                 mock.patch.object(instance, 'transport', return_value=response) as transport:
                instance.stage(board)
            board.stage.assert_called_once_with('bench/motor_fault')
            expected = [mock.call(['push', str(stage / name), str(instance.sketch) + '/' + name], 60, 'push')
                        for name in sorted(staged)]
            self.assertCountEqual(expected, transport.call_args_list)
            self.assert_globals_unchanged()
            self.assertTrue(stage.resolve().is_relative_to(self.root.resolve()))
            shutil.rmtree(stage)
        self.native.assert_not_called()

    def test_final_policy_uses_selected_instance_executor_and_sketch(self):
        tools = self.root / 'tools'
        tools.mkdir()
        calls = self.root / 'policy-calls.jsonl'
        # Controlled policy records public arguments; real policy semantics are unchanged.
        script = ('import json\nfrom pathlib import Path\n'
                  f'RECEIPT = Path({str(calls)!r})\n'
                  'def note(value):\n'
                  '    with RECEIPT.open("a") as stream: stream.write(json.dumps(value) + "\\n")\n'
                  'def installed_pins(data):\n'
                  '    note(["installed", data]); return {"fixture-pin": "a" * 64}\n'
                  'def verify_hashes(runner, board, pins):\n'
                  '    note(["verify", runner.__self__.run_id, board]); return pins\n'
                  'def check_overrides(runner, board, data, user, sketch):\n'
                  '    note(["overrides", runner.__self__.run_id, board, str(sketch)])\n')
        policy = tools / 'app_build_policy.py'
        policy.write_text(script)
        digest = hashlib.sha256(policy.read_bytes()).hexdigest()
        for run_id in ('compile01', 'compile02', 'compile01'):
            path = self.raw / ('compile_inputs.json' if run_id == 'compile01' else 'compile_inputs02.json')
            path.write_text(json.dumps({'tools/app_build_policy.py': digest}))
            instance = self.selected(run_id)
            with mock.patch.object(instance, 'local', return_value=None):
                instance.final_policy(overrides=True)
            self.assert_globals_unchanged()
        records = [json.loads(line) for line in calls.read_text().splitlines()]
        self.assertEqual(['compile01', 'compile02', 'compile01'],
                         [row[1] for row in records if row[0] == 'verify'])
        self.assertEqual([(name, str(self.remote_parent / ('motor-fault-' + name) / 'motor_fault'))
                          for name in ('compile01', 'compile02', 'compile01')],
                         [(row[1], row[3]) for row in records if row[0] == 'overrides'])
        self.native.assert_not_called()

    def test_positive_run_routes_checked_compile_and_final_check_to_selected_instance(self):
        tools = self.root / 'tools'
        tools.mkdir()
        calls = self.root / 'compile-routing.jsonl'
        # Pure routing substitute supplies completion counts; it executes no compiler.
        script = ('import json\nfrom pathlib import Path\n'
                  f'RECEIPT = Path({str(calls)!r})\n'
                  'def source_hash(stage): return "d" * 64\n'
                  'def compile_app(*args, project, command_runner):\n'
                  '    owner = command_runner.__self__\n'
                  '    owner.query_calls = 1; owner.compiler_calls = 1\n'
                  '    with RECEIPT.open("a") as stream:\n'
                  '        stream.write(json.dumps({"args": list(args), "project": project, '
                  '"owner": owner.run_id}, default=str) + "\\n")\n'
                  '    return str(owner.remote) + "/fixture-artifacts"\n')
        (tools / 'board_tool.py').write_text(script)
        board_digest = hashlib.sha256((tools / 'board_tool.py').read_bytes()).hexdigest()
        for run_id in ('compile01', 'compile02'):
            manifest = self.raw / ('compile_inputs.json' if run_id == 'compile01' else 'compile_inputs02.json')
            manifest.write_text(json.dumps({'tools/board_tool.py': board_digest}))
            instance = self.selected(run_id)
            receipt = self.root / ('run-receipt-' + run_id)
            receipt.mkdir()
            response = (subprocess.CompletedProcess(['fixture-claim'], 0, stdout=b'{}', stderr=b''), receipt)
            identity = {'uid': 1000, 'user': 'arduino', 'boot_id': self.caller.BOOT,
                        'cli_sha256': self.caller.CLI_SHA, 'free_bytes': 2 ** 31, 'conflicts': []}

            def stage(board):
                instance.claimed = True
                instance.stage_hashes = {'fixture.cpp': 'a' * 64}

            arguments = ['--execute'] if run_id == 'compile01' else ['--execute', '--run', 'compile02']
            with mock.patch.object(sys, 'argv', ['compile_motor_fault.py', *arguments]), \
                 mock.patch.object(sys, 'dont_write_bytecode', True), \
                 mock.patch.object(sys, 'pycache_prefix', str(Path(instance.output) / 'pycache')), \
                 mock.patch.object(instance, 'local', return_value=None), \
                 mock.patch.object(instance, 'inventory', return_value=identity), \
                 mock.patch.object(instance, 'prerequisites', return_value=None), \
                 mock.patch.object(instance, 'sources', return_value=None), \
                 mock.patch.object(instance, 'direct', return_value=response), \
                 mock.patch.object(instance, 'stage', side_effect=stage), \
                 mock.patch.object(instance, 'final_policy', return_value=None) as final_policy:
                self.assertEqual(0, instance.run())
            self.assertTrue(final_policy.called)
            self.assertEqual('COMPILE_CHECKED', instance.report['status'])
            self.assertEqual(str(instance.remote) + '/fixture-artifacts', instance.report['artifacts'])
            self.assert_globals_unchanged()
        records = [json.loads(line) for line in calls.read_text().splitlines()]
        self.assertEqual(2, len(records))
        for record, run_id in zip(records, ('compile01', 'compile02')):
            remote = str(self.remote_parent / ('motor-fault-' + run_id))
            self.assertEqual(run_id, record['owner'])
            self.assertEqual('motor_fault.ino', record['project'])
            self.assertEqual(['2629958581', 'd' * 64, remote + '/motor_fault', remote,
                              'arduino:zephyr:unoq', '-DMATCH=0 -DMOTORS_ALLOWED=0', 'default'], record['args'])
        self.native.assert_not_called()

    def test_child_machinery_hashes_and_original_manifest_remain_exactly_preserved(self):
        for name in ('IDENTITY', 'REMOTE_CHILD'):
            self.assertEqual(PRESERVED[name], hashlib.sha256(getattr(self.caller, name).encode()).hexdigest())
        encoded_env = json.dumps(self.caller.ENV, sort_keys=True, separators=(',', ':')).encode()
        self.assertEqual(PRESERVED['ENV'], hashlib.sha256(encoded_env).hexdigest())
        source = CALLER.read_bytes().decode('utf-8')
        node = next(item for item in ast.parse(source).body
                    if isinstance(item, ast.FunctionDef) and item.name == 'extracted_wait')
        segment = ast.get_source_segment(source, node).encode()
        self.assertEqual(PRESERVED['extracted_wait'], hashlib.sha256(segment).hexdigest())
        self.assertEqual(PRESERVED['original_manifest_sha256'],
                         hashlib.sha256((RAW / 'compile_inputs.json').read_bytes()).hexdigest())
        self.native.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
