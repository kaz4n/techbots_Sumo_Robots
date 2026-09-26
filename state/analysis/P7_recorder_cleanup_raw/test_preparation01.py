# Checks the data-only recorder cleanup derivative without any native invocation.
# Uses exact reverse proofs and controlled process entries to preserve fail-closed guards.
# No cleanup main, credential operation, board command or filesystem deletion is called.
import ast
import hashlib
import json
from pathlib import Path
import shlex
import types
import unittest
from unittest import mock

RAW = Path(__file__).resolve().parent
MAIN = Path('C:/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots')
STAGE = '/home/arduino/sumox26_codex_build/cleanup-recorder-root01'


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
    def test_complete_reverse_proof_for_recipe_wrapper_and_four_programs(self):
        record = json.loads(read('cleanup_derivation01.json'))
        for kind, name in [('recipe', 'cleanup_remoteocd01.py'), ('wrapper', 'cleanup_root01.py')]:
            item = record[kind]
            original = (MAIN / item['template']).read_bytes()
            self.assertEqual(pin(original), item['before'])
            self.assertEqual(pin(read(name)), item['after'])
            self.assertEqual(reverse(read(name), item['steps']), original)
        for kind, item in record['program_derivations'].items():
            source = (MAIN / item['template']['path']).read_bytes()
            self.assertEqual(pin(source), item['template']['pin'])
            original = shlex.split(json.loads(source)['argv'][-1])[-1].encode()
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
