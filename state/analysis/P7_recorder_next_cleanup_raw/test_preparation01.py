# Checks the data-only recorder cleanup derivative without any native invocation.
# Uses exact reverse proofs and controlled process entries to preserve fail-closed guards.
# No cleanup main, credential operation, board command or filesystem deletion is called.
import ast
import base64
import bz2
import hashlib
import json
from pathlib import Path
import shlex
import types
import unittest
from unittest import mock

RAW = Path(__file__).resolve().parent
MAIN = Path(__file__).absolute().parents[3]
STAGE = '/home/arduino/sumox26_codex_build/cleanup-recorder-next-root01'


def read(name):
    return (RAW / name).read_bytes()


def pin(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def module(name):
    value = types.ModuleType('fixture_' + name)
    exec(compile(read(name), str(RAW / name), 'exec'), value.__dict__)
    return value


def reverse(raw, steps):
    for step in reversed(steps):
        assert pin(raw) == step['after']
        assert raw.count(step['new'].encode()) == step['count']
        raw = raw.replace(step['new'].encode(), step['old'].encode())
        assert pin(raw) == step['before']
    return raw


class PreparationTests(unittest.TestCase):
    def test_new_observation_literals_and_embedded_sources_match_exactly(self):
        self.assertEqual(pin(read('admission01.json'))['sha256'],
                         '17cfc318c40cbe01b95f824bea001a7aa03359b94bbae54119fa21830f627b99')
        observed = json.loads(json.loads(read('admission01.json'))['stdout'])
        self.assertEqual((observed['directory_before']['dev'], observed['directory_before']['ino']), (34, 6292))
        self.assertEqual(sum(row['bytes'] for row in observed['files'].values()), 2359512)
        self.assertEqual(set(observed['files']), {'recorder.ino.bin-zsk.bin', 'flash_sketch.cfg',
                                                'zephyr-arduino_uno_q_stm32u585xx.elf'})
        for kind in ('absence', 'stage', 'verify', 'retrieve'):
            source = read(kind + '_program01.py').decode()
            assignments = {node.targets[0].id: node.value for node in ast.parse(source).body
                          if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)}
            self.assertEqual(ast.literal_eval(assignments['stage']), STAGE)
            tokens = [n.value for n in ast.walk(assignments['packet']) if isinstance(n, ast.Constant)
                      and isinstance(n.value, str) and len(n.value) > 1000]
            self.assertEqual(len(tokens), 1)
            packet = json.loads(bz2.decompress(base64.b64decode(tokens[0])))
            expected = {'cleanup_root01.py': read('cleanup_root01.py').decode(),
                        'cleanup_remoteocd01.py': read('cleanup_remoteocd01.py').decode(),
                        'static_remote.py': (MAIN/'state/analysis/P7_static_link_probe_raw/static_remote.py').read_bytes().decode()}
            self.assertEqual(packet, expected)
            self.assertEqual(ast.literal_eval(assignments['pins']), {name: pin(raw.encode()) for name, raw in expected.items()})
            if kind == 'verify':
                self.assertEqual(ast.literal_eval(assignments['expected_scratch']), observed['directory_before'])
                self.assertEqual(ast.literal_eval(assignments['expected_copies']),
                                 {name: {k: row[k] for k in ('identity', 'sha256')} for name, row in observed['files'].items()})
            if kind in ('verify', 'retrieve'):
                self.assertEqual(ast.literal_eval(assignments['expected_originals']), observed['originals'])
        dispatcher = read('native_dispatch_template01.py')
        for name in (b'__PREPARATION_MANIFEST_SHA256__', b'__PREPARATION_REVIEW_SHA256__'):
            self.assertEqual(dispatcher.count(name), 1)
        self.assertIn(b'P7_recorder_next_cleanup_raw', dispatcher)
        self.assertIn(b'P7_recorder_next_cleanup_review.md', dispatcher)
        self.assertIn(MAIN.as_posix().encode(), dispatcher)
        self.assertNotIn(b'OneDrive/Desktop/Project/techbots_Sumo_Robots', dispatcher)

    def test_complete_reverse_proof_for_recipe_wrapper_and_four_programs(self):
        record = json.loads(read('cleanup_derivation01.json'))
        for kind, name in [('recipe', 'cleanup_remoteocd01.py'), ('wrapper', 'cleanup_root01.py'), ('dispatcher', 'native_dispatch_template01.py')]:
            item = record[kind]
            original = (MAIN / item['template']['path']).read_bytes()
            self.assertEqual(pin(original), item['before'])
            self.assertEqual(pin(read(name)), item['after'])
            self.assertEqual(reverse(read(name), item['steps']), original)
        for kind, item in record['program_derivations'].items():
            source = (MAIN / item['template']['path']).read_bytes()
            self.assertEqual(pin(source), item['template']['pin'])
            original = source
            self.assertEqual(reverse(read(kind + '_program01.py'), item['steps']), original)

    def test_load_projection_pins_and_exact_three_current_originals(self):
        wrapper = module('cleanup_root01.py')
        helper = (MAIN / 'state/analysis/P7_static_link_probe_raw/static_remote.py').read_bytes()
        sources = {'cleanup_remoteocd01.py': read('cleanup_remoteocd01.py'), 'static_remote.py': helper}
        for name, raw in sources.items():
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), wrapper.PINS[name])
        with mock.patch.object(wrapper, 'read_source', side_effect=sources.__getitem__):
            recipe, actual_helper = wrapper.load_cleanup()
        self.assertEqual(actual_helper, helper)
        self.assertEqual(wrapper.STAGE, STAGE)
        admission = json.loads(json.loads(read('admission01.json'))['stdout'])
        self.assertEqual(set(recipe.PINS), set(admission['files']))
        for name, value in recipe.PINS.items():
            self.assertEqual(value, (admission['originals'][name]['bytes'],
                                    admission['originals'][name]['sha256'],
                                    admission['originals'][name]['path']))
        with mock.patch.object(wrapper, 'read_source', side_effect=lambda n: sources[n] + b'\n'):
            with self.assertRaisesRegex(ValueError, 'Process projection changed'):
                wrapper.load_cleanup()

    def test_active_compiler_refuses_before_any_descriptor_inspection(self):
        recipe = module('cleanup_remoteocd01.py')
        class Process:
            name = '987654'
            def __truediv__(self, name):
                if name != 'comm':
                    raise AssertionError('Continued after active compiler')
                return types.SimpleNamespace(read_text=lambda: 'arduino-cli\n')
            def stat(self):
                raise AssertionError('Continued after active compiler')
        proc = types.SimpleNamespace(iterdir=lambda: [Process()])
        with mock.patch.object(recipe, 'Path', return_value=proc):
            with self.assertRaisesRegex(ValueError, 'Native process is active'):
                recipe.processes()

    def test_projected_disappearing_handle_is_not_silently_skipped(self):
        wrapper = module('cleanup_root01.py')
        raw = read('cleanup_remoteocd01.py').replace(wrapper.PROJECTION_OLD, wrapper.PROJECTION_NEW)
        recipe = types.ModuleType('projected_recipe_fixture')
        exec(compile(raw, '<projected-fixture>', 'exec'), recipe.__dict__)
        class Process:
            name = '987654'
            def __truediv__(self, name):
                return types.SimpleNamespace(read_text=lambda: 'python3\n', iterdir=lambda: [])
            def stat(self):
                return types.SimpleNamespace(st_uid=1000)
        proc = types.SimpleNamespace(iterdir=lambda: [Process()])
        with mock.patch.object(recipe, 'Path', return_value=proc), \
             mock.patch.object(recipe.os, 'readlink', side_effect=FileNotFoundError('controlled missing handle')):
            with self.assertRaisesRegex(FileNotFoundError, 'controlled missing handle'):
                recipe.processes()

    def test_intents_keep_staging_separate_from_authentication_and_deletion(self):
        for kind in ('absence', 'stage', 'verify', 'retrieve'):
            intent = json.loads(read('cleanup_' + kind + '_intent01.json'))
            program = read(kind + '_program01.py')
            self.assertEqual(pin(program), intent['program'])
            self.assertEqual(intent['stage'], STAGE)
            self.assertEqual(intent['timeout_seconds'], 70)
            tree = ast.parse(program)
            calls = {node.func.attr for node in ast.walk(tree)
                     if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
            self.assertFalse(calls & {'unlink', 'rmdir', 'setuid', 'seteuid', 'setresuid', 'setresgid', 'Popen', 'run'})
            if kind != 'stage':
                self.assertNotIn('mkdir', calls)
            if kind in ('absence', 'stage'):
                self.assertEqual(shlex.split(intent['argv'][-1])[-1].encode(), program)
                self.assertLess(intent['command_units'], 30000)
            else:
                self.assertNotIn('argv', intent)
                self.assertIn(b'__STAGE_IDENTITY_FROM_CHECKED_RECEIPT__', program)
        auth = json.loads(read('cleanup_authenticated_intent01.json'))
        self.assertEqual(shlex.split(auth['argv'][-1]), shlex.split("set -C; sudo -S -p '' -H /usr/bin/python3 -I -B " +
                         STAGE + '/cleanup_root01.py > ' + STAGE + '/result_root01.json'))
        self.assertEqual(auth['timeout_seconds'], 70)
        self.assertIn('STDIN only', auth['credential_transport'])
        self.assertIn('no retry', auth['single_use'])


if __name__ == '__main__':
    unittest.main()
