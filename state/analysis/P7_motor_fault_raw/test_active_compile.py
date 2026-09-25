# Tests D171's exact active compile selection and isolated attempt ownership.
# Protects retained legacy stages and compile routes without native operations.
# Uses the public D167 RAM fixture, opaque caller import and controlled substitutes.
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest import mock

import test_compile02 as legacy


class ActiveCompileTests(unittest.TestCase):
    setUpClass = classmethod(legacy.Compile02Tests.setUpClass.__func__)
    selected = legacy.Compile02Tests.selected
    assert_globals_unchanged = legacy.Compile02Tests.assert_globals_unchanged

    def setUp(self):
        legacy.Compile02Tests.setUp(self)
        self.manifest('active01', {'active.txt': 'a' * 64})
        guard = mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('native child forbidden'))
        self.children = guard.start()
        self.addCleanup(guard.stop)

    def manifest(self, run_id, entries):
        names = {'compile01': 'compile_inputs.json', 'compile02': 'compile_inputs02.json',
                 'active01': 'compile_inputs_active01.json'}
        path = self.raw / names[run_id]
        path.write_text(json.dumps(entries), encoding='utf-8')
        return path

    def prepare_stage(self, run_id='active01', defect=None):
        inputs = {'bench/motor_fault/motor_fault.ino': b'// sketch\n',
                  'bench/motor_fault/src/probe.h': b'// diagnostic\n',
                  'src/config.h': b'// configuration\n', 'src/core/fsm.h': b'// core\n',
                  'src/hal/motors.h': b'// HAL\n', 'src/app/service.cpp': b'// app support\n'}
        self.manifest(run_id, {name: hashlib.sha256(data).hexdigest() for name, data in inputs.items()})
        instance = self.selected(run_id)
        instance.claimed = True
        Path(instance.output).mkdir(parents=True)
        mapped = {name.removeprefix('bench/motor_fault/'): data for name, data in inputs.items()}
        for name, data in inputs.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

        def stage(sketch, **kwargs):
            self.assertEqual('bench/motor_fault', sketch)
            expected = {'attempt': 'motor-fault-active01'} if run_id == 'active01' else {}
            self.assertEqual(expected, kwargs)
            for name, data in mapped.items():
                path = Path(instance.stage_path) / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            if defect == 'missing':
                (Path(instance.stage_path) / 'src/config.h').unlink()
            elif defect == 'extra':
                (Path(instance.stage_path) / 'unreviewed.h').write_bytes(b'extra')
            elif defect == 'changed':
                (Path(instance.stage_path) / 'src/config.h').write_bytes(b'changed')
            return Path(instance.stage_path).parent if defect == 'wrong-return' else Path(instance.stage_path)

        board = mock.Mock()
        board.stage.side_effect = stage
        return instance, board, mapped

    def call_stage(self, instance, board):
        receipt = Path(instance.output) / 'fixture-stage'
        receipt.mkdir()
        response = (subprocess.CompletedProcess(['controlled-stage'], 0, stdout=b'', stderr=b''), receipt)
        with mock.patch.object(instance, 'local', return_value=None), \
             mock.patch.object(instance, 'sources', return_value=None), \
             mock.patch.object(instance, 'prerequisites', return_value=None), \
             mock.patch.object(instance, 'direct', return_value=response) as direct, \
             mock.patch.object(instance, 'transport', return_value=response) as transport:
            if board.stage.side_effect is None:
                raise AssertionError('fixture must retain its stage substitute')
            try:
                instance.stage(board)
            except (RuntimeError, ValueError):
                direct.assert_not_called()
                transport.assert_not_called()
                raise
        return transport.call_args_list

    def test_parser_extends_only_the_exact_active_form_without_construction(self):
        with mock.patch.object(self.caller, 'CompileOnce', side_effect=AssertionError('constructed')) as create, \
             mock.patch.object(Path, 'read_text', side_effect=AssertionError('read')):
            for argv, selected in ((['--execute'], 'compile01'),
                                   (['--execute', '--run', 'compile02'], 'compile02'),
                                   (['--execute', '--run', 'active01'], 'active01')):
                self.assertEqual(selected, self.caller.parse_request(argv))
            for argv in (None, 'active01', ('--execute', '--run', 'active01'), [],
                         ['--execute', '--run', 'compile01'], ['--run', 'active01', '--execute'],
                         ['--execute', '--run', 'ACTIVE01'], ['--execute', '--run', 'active1'],
                         ['--execute', '--run', 'active01 '], ['--execute', '--run', b'active01'],
                         ['--execute', '--run', 'active01', '--flags'], ['--execute', '--run', None]):
                with self.subTest(argv=argv), self.assertRaises((RuntimeError, ValueError)):
                    self.caller.parse_request(argv)
            create.assert_not_called()
        self.native.assert_not_called()

    def test_constructor_has_closed_keyword_only_selector(self):
        parameter = inspect.signature(self.caller.CompileOnce).parameters['run_id']
        self.assertEqual(inspect.Parameter.KEYWORD_ONLY, parameter.kind)
        self.assertEqual('compile01', parameter.default)
        with mock.patch.object(Path, 'read_text', side_effect=AssertionError('read')), \
             mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('read')):
            for value in (None, False, 1, [], {}, b'active01', '', 'active1', 'active02',
                          '../active01', 'active01 ', 'ACTIVE01'):
                with self.subTest(value=value), self.assertRaises((RuntimeError, ValueError)):
                    self.selected(value)
            with self.assertRaises(TypeError):
                self.caller.CompileOnce('active01')
        self.native.assert_not_called()

    def test_paths_flags_manifest_reads_and_interleaving_are_instance_specific(self):
        original = Path.read_text
        read_paths = []

        def read(path, *args, **kwargs):
            read_paths.append(Path(path))
            return original(path, *args, **kwargs)

        for run_id in ('active01', 'compile01', 'compile02', 'active01'):
            read_paths.clear()
            with mock.patch.object(Path, 'read_text', autospec=True, side_effect=read):
                instance = self.selected(run_id)
            active = run_id == 'active01'
            filename = {'compile01': 'compile_inputs.json', 'compile02': 'compile_inputs02.json',
                        'active01': 'compile_inputs_active01.json'}[run_id]
            self.assertEqual([self.raw / filename], [p for p in read_paths if p.name.startswith('compile_inputs')])
            self.assertEqual(self.raw / ('native_' + run_id), Path(instance.output))
            self.assertEqual(self.raw / filename, Path(instance.inputs_path))
            self.assertEqual(self.remote_parent / ('motor-fault-' + run_id), Path(instance.remote))
            self.assertEqual(Path(instance.remote) / 'motor_fault', Path(instance.sketch))
            expected = self.root / 'build/stage/motor-fault-active01/motor_fault' if active else Path(self.caller.STAGE)
            self.assertEqual(expected, Path(instance.stage_path))
            self.assertEqual(expected.parent if active else expected, Path(instance.stage_owner))
            self.assertEqual('motor-fault-active01' if active else None, instance.stage_attempt)
            flags = '-DMATCH=0 -DMOTORS_ALLOWED=0' + (' -DSUMOX_MOTOR_FAULT_PROBE=1' if active else '')
            self.assertEqual(flags, instance.flags)
            self.assertIn(str(instance.remote), instance.preamble())
            self.assertFalse(Path(instance.output).exists())
            self.assert_globals_unchanged()
        self.native.assert_not_called()

    def test_interleaved_receipts_are_owned_by_selected_output(self):
        instances = [self.selected(name) for name in ('active01', 'compile02', 'compile01')]
        completed = subprocess.CompletedProcess(['controlled'], 0, stdout=b'fixture', stderr=b'')
        with mock.patch.object(subprocess, 'run', return_value=completed) as controlled:
            for instance in instances + instances[:1]:
                Path(instance.output).mkdir(parents=True, exist_ok=True)
                with mock.patch.object(instance, 'local', return_value=None):
                    result, receipt = instance.transport(['version'], 1, 'fixture')
                self.assertEqual(b'fixture', result.stdout)
                self.assertTrue(Path(receipt).is_relative_to(Path(instance.output)))
                self.assert_globals_unchanged()
            self.assertEqual(4, controlled.call_count)

    def test_selected_cache_and_invocation_reject_other_attempt(self):
        for selected, other in (('active01', 'compile02'), ('compile01', 'active01')):
            instance = self.selected(selected)
            with mock.patch.object(sys, 'dont_write_bytecode', True), \
                 mock.patch.object(sys, 'pycache_prefix', str(self.raw / ('native_' + other) / 'pycache')), \
                 self.assertRaises((RuntimeError, ValueError)):
                instance.local()
            args = ['--execute', '--run', other]
            with mock.patch.object(sys, 'argv', ['compile_motor_fault.py', *args]), \
                 self.assertRaises((RuntimeError, ValueError)):
                instance.run()
            self.assertFalse(Path(instance.output).exists())
        self.native.assert_not_called()

    def test_existing_active_owner_refused_before_run_outputs_or_contact(self):
        instance = self.selected('active01')
        owner = Path(instance.stage_owner)
        owner.parent.mkdir(parents=True)
        for kind in ('directory', 'file', 'live-link', 'dangling-link'):
            with self.subTest(kind=kind):
                target = self.root / 'link-target'
                target.mkdir(exist_ok=True)
                if kind == 'directory':
                    owner.mkdir()
                elif kind == 'file':
                    owner.write_bytes(b'retained')
                else:
                    owner.symlink_to(target if kind == 'live-link' else self.root / 'absent-target', target_is_directory=True)
                with mock.patch.object(sys, 'argv', ['compile_motor_fault.py', '--execute', '--run', 'active01']), \
                     mock.patch.object(instance, 'local', return_value=None), \
                     mock.patch.object(instance, 'inventory', side_effect=AssertionError('board contact')):
                    try:
                        code = instance.run()
                    except (RuntimeError, ValueError):
                        code = 1
                self.assertNotEqual(0, code)
                self.assertFalse(Path(instance.output).exists())
                self.assertTrue(owner.exists() or owner.is_symlink())
                self.assertFalse(Path(instance.stage_path).exists())
                owner.rmdir() if kind == 'directory' else owner.unlink()
        self.native.assert_not_called()

    def test_stage_rechecks_existing_owner_before_copy_or_transport(self):
        instance = self.selected('active01')
        Path(instance.stage_owner).mkdir(parents=True)
        board = mock.Mock()
        with mock.patch.object(instance, 'local', return_value=None), \
             mock.patch.object(instance, 'direct', side_effect=AssertionError('native direct')), \
             mock.patch.object(instance, 'transport', side_effect=AssertionError('native transport')), \
             self.assertRaises((RuntimeError, ValueError)):
            instance.stage(board)
        board.stage.assert_not_called()
        self.assertFalse(Path(instance.output).exists())
        self.assertTrue(Path(instance.stage_owner).is_dir())
        self.native.assert_not_called()

    def test_active_stage_uses_attempt_exact_map_and_push_paths_preserving_legacy(self):
        legacy_stage = Path(self.caller.STAGE)
        legacy_stage.mkdir(parents=True)
        sentinel = legacy_stage / 'retained.txt'
        sentinel.write_bytes(b'earlier failed or completed attempt')
        before = (sentinel.read_bytes(), sentinel.stat().st_mtime_ns)
        instance, board, mapped = self.prepare_stage()
        calls = self.call_stage(instance, board)
        board.stage.assert_called_once_with('bench/motor_fault', attempt='motor-fault-active01')
        self.assertCountEqual([mock.call(['push', str(Path(instance.stage_path) / name),
                                         str(instance.sketch) + '/' + name], 60, 'push')
                               for name in sorted(mapped)], calls)
        self.assertEqual({name: hashlib.sha256(data).hexdigest() for name, data in mapped.items()}, instance.stage_hashes)
        self.assertEqual(before, (sentinel.read_bytes(), sentinel.stat().st_mtime_ns))
        self.assert_globals_unchanged()
        self.native.assert_not_called()

    def test_legacy_stage_retains_one_argument_route_and_flags(self):
        instance, board, mapped = self.prepare_stage('compile02')
        calls = self.call_stage(instance, board)
        board.stage.assert_called_once_with('bench/motor_fault')
        self.assertEqual('-DMATCH=0 -DMOTORS_ALLOWED=0', instance.flags)
        self.assertEqual(len(mapped), len(calls))
        self.assertTrue(all(call.args[0][1].startswith(str(self.caller.STAGE) + '/') for call in calls))
        self.assert_globals_unchanged()

    def test_wrong_returned_stage_is_refused_before_transport_and_retained(self):
        instance, board, _ = self.prepare_stage(defect='wrong-return')
        with self.assertRaises((RuntimeError, ValueError)):
            self.call_stage(instance, board)
        self.assertTrue(Path(instance.stage_owner).is_dir())
        self.native.assert_not_called()

    def test_incomplete_extra_or_changed_stage_map_is_refused_before_transport(self):
        for defect in ('missing', 'extra', 'changed'):
            with self.subTest(defect=defect):
                instance, board, _ = self.prepare_stage(defect=defect)
                with self.assertRaises((RuntimeError, ValueError)):
                    self.call_stage(instance, board)
                self.assertTrue(Path(instance.stage_owner).is_dir())
                # Only this test's synthetic RAM owner and output are disposable.
                for path in (Path(instance.stage_owner), Path(instance.output)):
                    self.assertTrue(path.resolve().is_relative_to(self.root.resolve()))
                    shutil.rmtree(path)
        self.native.assert_not_called()

    def test_local_hash_checks_active_stage_and_selected_manifest_with_valid_control(self):
        caller_path = self.raw / 'compile_motor_fault.py'
        shutil.copyfile(legacy.CALLER, caller_path)  # Opaque identity bytes only.
        old_manifest = json.loads((legacy.RAW / 'compile_inputs02.json').read_text())
        files = [name for name in old_manifest if not name.startswith(('src/', 'bench/'))]
        files += ['src/config.h', 'bench/motor_fault/motor_fault.ino']
        for name in files:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_bytes(b'// controlled local identity bytes\n')
        inputs = {name: hashlib.sha256((self.root / name).read_bytes()).hexdigest() for name in files}
        manifest = self.manifest('active01', inputs)
        instance = self.selected('active01')
        active = Path(instance.stage_path) / 'motor_fault.ino'
        active.parent.mkdir(parents=True)
        active.write_bytes(b'active fixture\n')
        instance.stage_hashes = {'motor_fault.ino': hashlib.sha256(active.read_bytes()).hexdigest()}
        legacy_stage = Path(self.caller.STAGE)
        legacy_stage.mkdir(parents=True)
        (legacy_stage / 'unrelated.txt').write_bytes(b'legacy retained')
        with mock.patch.object(self.caller, '__file__', str(caller_path)), \
             mock.patch.object(sys, 'dont_write_bytecode', True), \
             mock.patch.object(sys, 'pycache_prefix', str(Path(instance.output) / 'pycache')):
            instance.local()
            active.write_bytes(b'changed active fixture\n')
            with self.assertRaises((RuntimeError, ValueError)):
                instance.local()
            active.write_bytes(b'active fixture\n')
            instance.local()
            original = manifest.read_bytes()
            manifest.write_bytes(original + b'\n')
            with self.assertRaises((RuntimeError, ValueError)):
                instance.local()
            manifest.write_bytes(original)
            instance.local()
        self.assertEqual(b'legacy retained', (legacy_stage / 'unrelated.txt').read_bytes())
        self.native.assert_not_called()

    def exercise_run(self, fail_compile=False, fail_final=False):
        tools = self.root / 'tools'
        tools.mkdir()
        calls = self.root / 'routing.jsonl'
        script = ('import json\nfrom pathlib import Path\n'
                  f'LOG = Path({str(calls)!r})\n'
                  'def note(value):\n'
                  '    with LOG.open("a") as out: out.write(json.dumps(value, default=str) + "\\n")\n'
                  'def source_hash(stage):\n'
                  '    note({"stage": stage}); return "d" * 64\n'
                  'def compile_app(*args, project, command_runner):\n'
                  '    owner = command_runner.__self__\n'
                  '    owner.query_calls = 1; owner.compiler_calls = 1\n'
                  '    note({"args": args, "project": project, "owner": owner.run_id})\n'
                  + ('    raise RuntimeError("controlled compile failure")\n' if fail_compile else
                     '    return str(owner.remote) + "/fixture-artifacts"\n'))
        board_path = tools / 'board_tool.py'
        board_path.write_text(script)
        self.manifest('active01', {'tools/board_tool.py': hashlib.sha256(board_path.read_bytes()).hexdigest()})
        instance = self.selected('active01')
        receipt = self.root / 'run-receipt'
        receipt.mkdir()
        response = (subprocess.CompletedProcess(['controlled-claim'], 0, stdout=b'{}', stderr=b''), receipt)
        identity = {'uid': 1000, 'user': 'arduino', 'boot_id': self.caller.BOOT,
                    'cli_sha256': self.caller.CLI_SHA, 'free_bytes': 2 ** 31, 'conflicts': []}

        def stage(board):
            instance.claimed = True
            instance.stage_hashes = {'fixture.cpp': 'a' * 64}

        def local():
            if fail_final and instance.compiler_calls == 1:
                raise RuntimeError('controlled final local failure')

        with mock.patch.object(sys, 'argv', ['compile_motor_fault.py', '--execute', '--run', 'active01']), \
             mock.patch.object(sys, 'dont_write_bytecode', True), \
             mock.patch.object(sys, 'pycache_prefix', str(Path(instance.output) / 'pycache')), \
             mock.patch.object(instance, 'local', side_effect=local), \
             mock.patch.object(instance, 'inventory', return_value=identity), \
             mock.patch.object(instance, 'prerequisites', return_value=None), \
             mock.patch.object(instance, 'sources', return_value=None), \
             mock.patch.object(instance, 'direct', return_value=response), \
             mock.patch.object(instance, 'stage', side_effect=stage), \
             mock.patch.object(instance, 'final_policy', return_value=None) as final_policy:
            code = instance.run()
        self.assertEqual(2, final_policy.call_count)
        records = [json.loads(line) for line in calls.read_text().splitlines()]
        self.assertEqual([{'stage': str(instance.stage_path)},
                          {'args': ['2629958581', 'd' * 64, str(instance.sketch), str(instance.remote),
                                    'arduino:zephyr:unoq', '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1',
                                    'default'], 'project': 'motor_fault.ino', 'owner': 'active01'}], records)
        self.assertEqual((1, 1), (instance.query_calls, instance.compiler_calls))
        self.assert_globals_unchanged()
        self.native.assert_not_called()
        self.children.assert_not_called()
        return instance, code

    def test_checked_compile_routes_source_hash_flags_executor_and_artifacts(self):
        instance, code = self.exercise_run()
        self.assertEqual(0, code)
        self.assertEqual('COMPILE_CHECKED', instance.report['status'])
        self.assertEqual(str(instance.remote) + '/fixture-artifacts', instance.report['artifacts'])
        self.assertEqual('d' * 64, instance.report['source_sha256'])

    def test_failed_compile_still_runs_all_seven_independent_final_checks(self):
        instance, code = self.exercise_run(fail_compile=True)
        self.assertNotEqual(0, code)
        self.assertNotEqual('COMPILE_CHECKED', instance.report['status'])
        self.assertIn('controlled compile failure', instance.report['first_error'])
        self.assertEqual(['local', 'identity', 'cli_initialization_inventory', 'cli_builtin_files_inventory',
                          'remote_sources', 'installed_pins', 'overrides'],
                         [item['name'] for item in instance.report['final_checks']])
        self.assertTrue(all(item['status'] == 'PASS' for item in instance.report['final_checks']))
        self.assertTrue(Path(instance.output).is_dir())

    def test_failure_of_one_final_check_does_not_skip_later_checks_or_replace_first_error(self):
        instance, code = self.exercise_run(fail_compile=True, fail_final=True)
        self.assertNotEqual(0, code)
        self.assertIn('controlled compile failure', instance.report['first_error'])
        checks = instance.report['final_checks']
        self.assertEqual(['local', 'identity', 'cli_initialization_inventory', 'cli_builtin_files_inventory',
                          'remote_sources', 'installed_pins', 'overrides'], [item['name'] for item in checks])
        self.assertNotEqual('PASS', checks[0]['status'])
        self.assertIn('controlled final local failure', checks[0]['error'])
        self.assertTrue(all(item['status'] == 'PASS' for item in checks[1:]))


if __name__ == '__main__':
    unittest.main(verbosity=2)
