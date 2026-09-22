# Checks the documented P0 shell contract using isolated synthetic projects.
# Keeps safety assertions independent of the tools implementation and real hardware.
# Run with Python unittest under WSL; passing tests are not target-build evidence.
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
FAKE = Path(__file__).with_name('fake_command.py')
BASH = shutil.which('bash')
SKETCH = '''#include "src/config.h"
#include "local.h"
#include "detail/extra.h"
#include "src/core/value.h"
#include "src/hal/value.h"
static_assert(FIXTURE_VALUE + LOCAL_VALUE + EXTRA_VALUE == 42);
void setup() { (void) coreValue(); (void) halValue(); }
void loop() {}
'''


class ToolContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sumo-tools-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Tools are copied as opaque executables; expectations come from README/P0.
        shutil.copytree(PROJECT / 'tools', self.root / 'tools')
        self.bin = self.root / 'bin'
        self.remote_bin = self.root / 'remote-bin'
        for directory, commands in ((self.bin, ('ssh', 'rsync')),
                                    (self.remote_bin, ('arduino-cli', 'python3'))):
            directory.mkdir()
            for command in commands:
                shutil.copyfile(FAKE, directory / command)
                (directory / command).chmod(0o755)
        self.trace = self.root / 'trace.jsonl'
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(('SUMO_', 'FAKE_'))}
        self.env.update(PATH=str(self.bin) + os.pathsep + self.env['PATH'],
                        SUMO_SSH_TARGET='fixture@board.invalid',
                        SUMO_REMOTE_ROOT=str(self.root / 'remote'),
                        FAKE_TRACE=str(self.trace), FAKE_TEMP_ROOT=str(self.root),
                        FAKE_REMOTE_BIN=str(self.remote_bin))
        self.make_fixture()

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def make_fixture(self):
        self.write('src/config.h', '#pragma once\n#define FIXTURE_VALUE 20\n')
        for module in ('core', 'hal'):
            self.write(f'src/{module}/value.h',
                       f'#pragma once\nint {module}Value();\n')
            self.write(f'src/{module}/value.cpp',
                       '#include "../config.h"\n#include "value.h"\n'
                       f'int {module}Value() {{ return FIXTURE_VALUE; }}\n')
        for relative in ('bench/p0_matrix', 'bench/p0_timing', 'bench/other', 'src/app'):
            self.write(f'{relative}/{Path(relative).name}.ino', SKETCH)
            self.write(f'{relative}/local.h', '#pragma once\n#define LOCAL_VALUE 10\n')
            self.write(f'{relative}/detail/extra.h', '#pragma once\n#define EXTRA_VALUE 12\n')

    def use_reviewed_sources(self):
        # Upload tests exercise the actual inert snapshot, with fake transports.
        for relative in ('src', 'bench/p0_matrix', 'bench/p0_timing'):
            destination = (self.root / relative).resolve()
            self.assertTrue(destination.is_relative_to(self.root.resolve()))
            shutil.rmtree(destination)
            shutil.copytree(PROJECT / relative, destination)

    def run_tool(self, *args, tool='flash.sh', changes=None):
        self.trace.unlink(missing_ok=True)
        env = self.env.copy()
        for key, value in (changes or {}).items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = value
        result = subprocess.run([BASH, str(self.root / 'tools' / tool), *args],
                                cwd=self.root, env=env, text=True,
                                input='UNTRUSTED KEYBOARD INPUT\n',
                                capture_output=True, timeout=15, check=False)
        self.events = ([json.loads(line) for line in self.trace.read_text().splitlines()]
                       if self.trace.exists() else [])
        self.assertNotIn('rejected_remote', [event['kind'] for event in self.events],
                         'Test transport does not recognize a public remote command')
        return result

    def commands(self, command):
        return [event['args'] for event in self.events
                if event['kind'] == 'arduino' and event['args'][0] == command]

    def assert_failed(self, result):
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertTrue((result.stdout + result.stderr).strip(), 'Failure needs a diagnostic')

    def assert_no_motion_command(self):
        self.assertEqual([], self.commands('upload'))
        for event in self.events:
            if event['kind'] == 'ssh':
                tokens = shlex.split(' '.join(event['args']))
                self.assertFalse({'upload', 'reset', 'start', 'monitor', 'reboot'} & set(tokens))
        self.assertFalse(any(event['kind'] == 'remote_python' for event in self.events))

    def test_compile_only_all_argument_orders_and_build_configurations(self):
        for target in ('app', 'bench/p0_matrix'):
            for match in (False, True):
                args = [target, '--compile-only'] + (['--match'] if match else [])
                for order in itertools.permutations(args):
                    with self.subTest(order=order):
                        result = self.run_tool(*order)
                        self.assertEqual(0, result.returncode, result.stderr)
                        self.assert_no_motion_command()
                        compile_args, = self.commands('compile')
                        fqbn = compile_args[compile_args.index('--fqbn') + 1]
                        expected = 'arduino:zephyr:unoq' + (':wait_linux_boot=no' if match else '')
                        self.assertEqual(expected, fqbn)
                        properties = ' '.join(compile_args)
                        self.assertRegex(properties, rf'-DMATCH={int(match)}(?:\s|$)')
                        self.assertRegex(properties, rf'-DMOTORS_ALLOWED={int(match)}(?:\s|$)')

    def test_staging_preserves_project_and_sketch_local_includes(self):
        result = self.run_tool('bench/p0_matrix', '--compile-only')
        self.assertEqual(0, result.returncode, result.stderr)
        stage = self.root / 'build/stage/p0_matrix'
        expected = ['p0_matrix.ino', 'local.h', 'detail/extra.h', 'src/config.h']
        expected += [f'src/{module}/value.{suffix}'
                     for module in ('core', 'hal') for suffix in ('h', 'cpp')]
        for name in expected:
            self.assertTrue((stage / name).is_file(), name)
        self.assertEqual(SKETCH, (stage / 'p0_matrix.ino').read_text())
        self.assertEqual((self.root / 'src/config.h').read_bytes(),
                         (stage / 'src/config.h').read_bytes())
        result = subprocess.run(['g++', '-std=c++17', '-fsyntax-only', '-x', 'c++',
                                 str(stage / 'p0_matrix.ino'),
                                 str(stage / 'src/core/value.cpp'),
                                 str(stage / 'src/hal/value.cpp')],
                                text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_bench_startup_modes_keep_motors_disabled_and_artifacts_separate(self):
        destinations = []
        for startup in ('default', 'immediate'):
            for args in (('bench/p0_matrix', '--compile-only', '--startup', startup),
                         ('--startup', startup, '--compile-only', 'bench/p0_matrix')):
                with self.subTest(args=args):
                    result = self.run_tool(*args)
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assert_no_motion_command()
                    command, = self.commands('compile')
                    fqbn = command[command.index('--fqbn') + 1]
                    suffix = ':wait_linux_boot=no' if startup == 'immediate' else ''
                    self.assertEqual('arduino:zephyr:unoq' + suffix, fqbn)
                    self.assertIn('-DMATCH=0 -DMOTORS_ALLOWED=0', ' '.join(command))
                    destinations.append(command[command.index('--output-dir') + 1])
        self.assertEqual(destinations[0], destinations[1])
        self.assertEqual(destinations[2], destinations[3])
        self.assertNotEqual(destinations[0], destinations[2])

    def test_reviewed_inert_immediate_upload_uses_same_artifact_and_zero_motor_macro(self):
        self.use_reviewed_sources()
        for sketch in ('bench/p0_timing',):
            result = self.run_tool(sketch, '--startup', 'immediate')
            self.assertEqual(0, result.returncode, result.stderr)
            compile_args, = self.commands('compile')
            upload_args, = self.commands('upload')
            self.assertIn('-DMATCH=0 -DMOTORS_ALLOWED=0', ' '.join(compile_args))
            for args in (compile_args, upload_args):
                self.assertEqual('arduino:zephyr:unoq:wait_linux_boot=no',
                                 args[args.index('--fqbn') + 1])
            self.assertEqual(compile_args[compile_args.index('--output-dir') + 1],
                             upload_args[upload_args.index('--input-dir') + 1])

    def test_immediate_matrix_upload_waits_for_loader_ownership_verification(self):
        self.use_reviewed_sources()
        result = self.run_tool('bench/p0_matrix', '--startup', 'immediate')
        self.assert_failed(result)
        self.assertIn('matrix', result.stderr)
        self.assertEqual([], self.events)
        result = self.run_tool('bench/p0_matrix', '--startup', 'immediate', '--compile-only')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assert_no_motion_command()

    def test_startup_selection_cannot_bypass_upload_or_configuration_guards(self):
        for args in (('app', '--match', '--startup', 'immediate'),
                     ('app', '--match', '--compile-only', '--startup', 'default'),
                     ('bench/p0_matrix', '--compile-only', '--startup', 'unknown'),
                     ('bench/p0_matrix', '--startup', 'immediate')):
            with self.subTest(args=args):
                # The final case still contains the unreviewed synthetic sketch.
                self.assert_failed(self.run_tool(*args))
                self.assertEqual([], self.events)

    def test_transport_is_strict_and_content_addressed_without_deletion(self):
        result = self.run_tool('bench/p0_matrix', '--compile-only')
        self.assertEqual(0, result.returncode, result.stderr)
        for event in self.events:
            if event['kind'] in ('ssh', 'rsync'):
                joined = ' '.join(event['args'])
                self.assertIn('StrictHostKeyChecking=yes', joined)
                self.assertIn('BatchMode=yes', joined)
                self.assertNotIn('--delete', joined)
                self.assertNotIn('rm ', joined)
        sync, = [event for event in self.events if event['kind'] == 'rsync']
        first_destination = sync['args'][-1]
        self.assertRegex(first_destination, r'[a-f0-9]{64}')
        self.write('bench/p0_matrix/local.h', '#define LOCAL_VALUE 11\n')
        self.assertEqual(0, self.run_tool('bench/p0_matrix', '--compile-only').returncode)
        second_sync, = [event for event in self.events if event['kind'] == 'rsync']
        self.assertNotEqual(first_destination, second_sync['args'][-1])

    def test_only_allowlisted_inert_sketches_upload_after_compile_without_port(self):
        self.use_reviewed_sources()
        for target in ('bench/p0_matrix', 'bench/p0_timing'):
            with self.subTest(target=target):
                result = self.run_tool(target)
                self.assertEqual(0, result.returncode, result.stderr)
                compile_args, = self.commands('compile')
                upload_args, = self.commands('upload')
                self.assertIn('-DMOTORS_ALLOWED=0', ' '.join(compile_args))
                self.assertLess(self.events.index(next(e for e in self.events
                                    if e.get('args') == compile_args)),
                                self.events.index(next(e for e in self.events
                                    if e.get('args') == upload_args)))
                self.assertEqual('arduino:zephyr:unoq',
                                 upload_args[upload_args.index('--fqbn') + 1])
                self.assertNotIn('--port', upload_args)
                self.assertNotIn('-p', upload_args)
                self.assertNotIn('/dev/ttyHS1', ' '.join(upload_args))

    def test_match_is_not_upload_permission_and_other_targets_stay_blocked(self):
        cases = [('app',), ('bench/other',)]
        for target in ('app', 'bench/p0_matrix', 'bench/p0_timing'):
            cases.extend(itertools.permutations((target, '--match')))
        for args in cases:
            with self.subTest(args=args):
                self.assert_failed(self.run_tool(*args))
                self.assert_no_motion_command()

    def test_failure_propagation_stops_later_stages(self):
        self.use_reviewed_sources()
        for failure in ('ssh', 'sync', 'compile', 'upload'):
            with self.subTest(failure=failure):
                self.assert_failed(self.run_tool('bench/p0_matrix',
                                                changes={'FAKE_FAIL': failure}))
                if failure != 'upload':
                    self.assertEqual([], self.commands('upload'))
                if failure in ('ssh', 'sync'):
                    self.assertEqual([], self.commands('compile'))

    def test_missing_or_wrong_core_prevents_compile_and_upload(self):
        self.use_reviewed_sources()
        for version in ('', '0.9.0', '1.0.1'):
            with self.subTest(version=version):
                self.assert_failed(self.run_tool('bench/p0_matrix',
                                                changes={'FAKE_CORE_VERSION': version}))
                self.assertEqual([], self.commands('compile'))
                self.assertEqual([], self.commands('upload'))

    def test_missing_connection_configuration_fails_before_transport(self):
        for key in ('SUMO_SSH_TARGET', 'SUMO_REMOTE_ROOT'):
            with self.subTest(key=key):
                self.assert_failed(self.run_tool('app', '--compile-only', changes={key: None}))
                self.assertEqual([], self.events)

    def test_invalid_arguments_and_unsafe_paths_fail_before_transport(self):
        for args in ((), ('--unknown',), ('app', '--unknown'), ('app', 'extra'),
                     ('../outside', '--compile-only'), ('/tmp/outside', '--compile-only'),
                     ('bench/../../outside', '--compile-only')):
            with self.subTest(args=args):
                self.assert_failed(self.run_tool(*args))
                self.assertEqual([], self.events)
        for key, value in (('SUMO_REMOTE_ROOT', '/'), ('SUMO_REMOTE_ROOT', '../outside'),
                           ('SUMO_REMOTE_ROOT', '/tmp/$(touch injected)'),
                           ('SUMO_SSH_TARGET', '-oProxyCommand=bad')):
            with self.subTest(key=key, value=value):
                self.assert_failed(self.run_tool('app', '--compile-only', changes={key: value}))
                self.assertEqual([], self.events)

    def test_missing_source_or_config_fails_before_transport(self):
        self.assert_failed(self.run_tool('bench/missing', '--compile-only'))
        self.assertEqual([], self.events)
        (self.root / 'src/config.h').unlink()
        self.assert_failed(self.run_tool('app', '--compile-only'))
        self.assertEqual([], self.events)

    def test_missing_rsync_fails_before_transport(self):
        (self.bin / 'rsync').unlink()
        for name in ('bash', 'python3', 'dirname'):
            (self.bin / name).symlink_to(shutil.which(name))
        result = self.run_tool('app', '--compile-only', changes={'PATH': str(self.bin)})
        self.assert_failed(result)
        self.assertIn('rsync', result.stdout + result.stderr)
        self.assertEqual([], self.events)

    def test_source_symlinks_are_rejected_before_transport(self):
        outside = self.root / 'outside.h'
        outside.write_text('#error outside\n')
        for relative in ('bench/p0_matrix/linked.h', 'src/core/linked.h'):
            link = self.root / relative
            link.symlink_to(outside)
            with self.subTest(relative=relative):
                self.assert_failed(self.run_tool('bench/p0_matrix', '--compile-only'))
                self.assertEqual([], self.events)
            link.unlink()

    def test_source_ancestor_symlink_is_rejected_before_transport(self):
        bench = self.root / 'bench'
        moved = self.root / 'moved_bench'
        bench.rename(moved)
        bench.symlink_to(moved, target_is_directory=True)
        self.assert_failed(self.run_tool('bench/p0_matrix', '--compile-only'))
        self.assertEqual([], self.events)

    def test_sketch_local_src_is_preserved_and_compiles(self):
        self.write('bench/p0_matrix/src/local_probe.h', '#define LOCAL_PROBE 17\n')
        self.write('bench/p0_matrix/src/local_probe.cpp',
                   '#include "local_probe.h"\nstatic_assert(LOCAL_PROBE == 17);\n')
        self.assertEqual(0, self.run_tool('bench/p0_matrix', '--compile-only').returncode)
        folder = self.root / 'build/stage/p0_matrix/src'
        self.assertTrue((folder / 'local_probe.h').is_file())
        result = subprocess.run(['g++', '-std=c++17', '-fsyntax-only',
                                 str(folder / 'local_probe.cpp')],
                                text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_sketch_local_project_collisions_fail_before_transport(self):
        for reserved in ('config.h', 'core/local.h', 'hal/local.h'):
            with self.subTest(reserved=reserved):
                self.write(f'bench/p0_matrix/src/{reserved}', '// conflicting source\n')
                self.assert_failed(self.run_tool('bench/p0_matrix', '--compile-only'))
                self.assertEqual([], self.events)
                (self.root / f'bench/p0_matrix/src/{reserved}').unlink()
                if '/' in reserved:
                    (self.root / 'bench/p0_matrix/src' / reserved.split('/')[0]).rmdir()

    def test_upload_rejects_changed_or_added_source_before_transport(self):
        self.use_reviewed_sources()
        for relative in ('bench/p0_matrix/p0_matrix.ino', 'src/config.h',
                         'bench/p0_matrix/extra.cpp', 'src/core/extra.cpp', 'src/hal/extra.cpp'):
            with self.subTest(relative=relative):
                path = self.root / relative
                original = path.read_bytes() if path.exists() else None
                path.write_bytes((original or b'') + b'\n// unreviewed source change\n')
                self.assert_failed(self.run_tool('bench/p0_matrix'))
                self.assertEqual([], self.events)
                if original is None:
                    path.unlink()
                else:
                    path.write_bytes(original)

    def test_upload_requires_readable_reviewed_snapshot(self):
        self.use_reviewed_sources()
        manifest = self.root / 'tools/p0_inert_sources.json'
        for contents in ('{}', '{invalid JSON'):
            manifest.write_text(contents)
            self.assert_failed(self.run_tool('bench/p0_matrix'))
            self.assertEqual([], self.events)
        manifest.unlink()
        self.assert_failed(self.run_tool('bench/p0_matrix'))
        self.assertEqual([], self.events)

    def test_reviewed_snapshot_survives_lf_checkout(self):
        self.use_reviewed_sources()
        # .gitattributes defines LF for all staged source types on a fresh clone.
        for folder in (self.root / 'src', self.root / 'bench'):
            for path in folder.rglob('*'):
                if path.is_file() and path.suffix in ('.h', '.cpp', '.ino'):
                    path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n'))
        for sketch in ('bench/p0_matrix', 'bench/p0_timing'):
            with self.subTest(sketch=sketch):
                result = self.run_tool(sketch)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(1, len(self.commands('upload')))

    def test_logs_execute_receive_only_request_and_report_disconnect(self):
        result = self.run_tool(tool='logs.sh')
        self.assert_failed(result)
        self.assertIn('fixture monitor counter=7', result.stdout)
        connections = [event['endpoint'] for event in self.events
                       if event['kind'] == 'socket_connect']
        self.assertEqual([['127.0.0.1', 7500]], connections)
        self.assertTrue(any(event['kind'] == 'socket_recv' for event in self.events))
        self.assertFalse({'socket_send', 'stdin_read'} & {event['kind'] for event in self.events})
        self.assertEqual([], self.commands('compile'))
        self.assertEqual([], self.commands('upload'))

    def test_logs_propagate_ssh_failure_and_reject_arguments(self):
        self.assert_failed(self.run_tool(tool='logs.sh', changes={'FAKE_FAIL': 'ssh'}))
        self.assert_failed(self.run_tool('--send', tool='logs.sh'))
        self.assertEqual([], self.events)

    def test_real_diagnostics_host_syntax_and_inert_guard(self):
        self.write('stubs/Arduino.h', '#pragma once\n#include <cstdint>\n'
                   'inline std::uint32_t millis() { return 0; }\n'
                   'inline std::uint32_t micros() { return 0; }\n')
        self.write('stubs/Arduino_LED_Matrix.h', '#pragma once\n#include "Arduino.h"\n'
                   'struct Arduino_LED_Matrix { void begin() {}\n'
                   'void setGrayscaleBits(int) {} void draw(std::uint8_t*) {} };\n')
        shutil.copyfile(PROJECT / 'src/config.h', self.root / 'src/config.h')
        for name in ('p0_matrix', 'p0_timing'):
            shutil.copyfile(PROJECT / f'bench/{name}/{name}.ino',
                            self.root / f'bench/{name}/{name}.ino')
            local_source = PROJECT / f'bench/{name}/src'
            if local_source.is_dir():
                shutil.copytree(local_source, self.root / f'bench/{name}/src')
            self.assertEqual(0, self.run_tool(f'bench/{name}', '--compile-only').returncode)
            sketch = self.root / f'build/stage/{name}/{name}.ino'
            for motors in (0, 1):
                with self.subTest(sketch=name, motors=motors):
                    result = subprocess.run(['g++', '-std=c++17', '-fsyntax-only',
                                             '-I', str(self.root / 'stubs'), '-include', 'Arduino.h',
                                             f'-DMOTORS_ALLOWED={motors}', '-x', 'c++', str(sketch)],
                                            capture_output=True, text=True, check=False)
                    if motors == 0:
                        self.assertEqual(0, result.returncode, result.stderr)
                    else:
                        self.assertNotEqual(0, result.returncode)
                        self.assertIn('static assertion failed', result.stderr)


if __name__ == '__main__':
    unittest.main()
