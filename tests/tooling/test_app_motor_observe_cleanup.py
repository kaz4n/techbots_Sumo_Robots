# Checks D196 metadata-only cleanup against its independently frozen contract.
# Retains the complete historical credential/descriptor oracle in a private module.
# Uses host-only fixtures; never authenticates, scans real processes, or deletes files.
import contextlib
import hashlib
from pathlib import Path
import stat
import sys
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
OLD = 'state/analysis/P7_app_motor_fault_run_raw/'
NEW = 'state/analysis/P7_app_motor_observe_run_raw/'
CONTRACT = 'state/analysis/P7_app_motor_observe_cleanup_contract.md'
OLD_RECIPE_SHA = '23ef85ae3c386cc76751eea0fb18a90148a6fe513e3e8c753d527c06efcbbe95'
RECIPE_SHA = '1834edd39d628dccda0516f35cbc35434fd659c28392df6600cfdcf882e8ec9a'
OLD_PROJECTED_SHA = '51286ad414794e82f3161bed16cbb47dca421e831316e053a7eab967469f602e'
PROJECTED_SHA = 'b4bdb4dd7cbe6ed2ff534a033507ad2c080c5b789dc02716f4189f557a34c0c1'
WRAPPER_SHA = 'a089cc3bac9d8df3ffe53947e22b1bb4ffa139a733c7ebb1f5ba62e6d5bd804f'
PINS = {
    CONTRACT: (12460, '7258230a63f48e09401186b8ad3bed09f958006909610cea835926427a3609f6'),
    OLD + 'cleanup_remoteocd01.py': (7873, OLD_RECIPE_SHA),
    OLD + 'cleanup_root02.py': (9592, '4192f23ea49705a0af691953e6aec3c1f9da66c7cc1897ca3f5d49fba9fc5388'),
    OLD + 'test_cleanup_root02.py': (37221, '225ef637e85dfe4ce1598e6744c781720b900905ea0c9c3bf0737d58b49e1559'),
    OLD + 'cleanup_root02_actual_result.json': (6306, 'c0e45b308cd3bc73fa4a3b537471e7f753b5bb256270126c9f492da0d1af2700'),
    'state/analysis/P7_static_link_probe_raw/static_remote.py': (33321, '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8'),
    'state/analysis/P7_app_motor_observe_abi_raw/upload_scratch_inventory01.json': (3216, '20db3c251a907d6b143afc11a05c44780ba3a09d85e3202ad05878225f4a06f2'),
    'state/analysis/P7_app_motor_fault_compile_raw/native_static01/artifacts.json': (9597, '57b98c00db1ed5d90394812fcbb3fb28effedd4381f6e2fc03a6e7c04b45a6ce'),
    NEW + 'cleanup_remoteocd02.py': (7735, RECIPE_SHA),
    NEW + 'cleanup_root03.py': (9606, WRAPPER_SHA),
}
OLD_PAYLOAD = (
    "    'motor_fault.ino.elf-zsk.bin': (29836, 'b4416792a5bc228f34712fad9199a07c3c480aace979faa88aa12b50288b0a79',\n"
    "        '/home/arduino/sumox26_codex_build/motor-fault-active01/_app_builds/native-app-v1/'\n"
    "        '8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36/bench-default/'\n"
    "        '3aafdd0129f64799b4db51efe78e5c44/build/motor_fault.ino.elf-zsk.bin'),\n"
)
PAYLOAD_NAME = 'app_motor_fault.ino.bin-zsk.bin'
PAYLOAD_PATH = '/home/arduino/sumox26_codex_build/app-motor-fault-static01/build/' + PAYLOAD_NAME
PAYLOAD_SHA = 'deb40317e5c444af26e65da4b6f1d0e577d9897d59dbddff3bce03a7bc14335c'
NEW_PAYLOAD = "    '" + PAYLOAD_NAME + "': (95328, '" + PAYLOAD_SHA + "',\n        '" + PAYLOAD_PATH + "'),\n"
SCAN_OLD = '                except FileNotFoundError:\n                    continue\n'
SCAN_NEW = '                except FileNotFoundError:\n                    raise\n'


def checked(path):
    raw = (ROOT / path).read_bytes()
    size, digest = PINS[path]
    if (len(raw), hashlib.sha256(raw).hexdigest()) != (size, digest):
        raise AssertionError('Frozen input changed: ' + path)
    return raw


def replace_checked(raw, replacements):
    for before, after, count in replacements:
        before, after = before.encode(), after.encode()
        if raw.count(before) != count:
            raise AssertionError('Projection count differs: ' + repr(before))
        raw = raw.replace(before, after)
    return raw


def recipe_projection():
    return replace_checked(checked(OLD + 'cleanup_remoteocd01.py'), [
        ('D184', 'D190', 1), (OLD_PAYLOAD, NEW_PAYLOAD, 1),
        ('info.st_ino == 33', 'info.st_ino == 869', 1),
        ('d190-exact-scratch-cleanup-v1', 'd196-exact-observer-scratch-cleanup-v1', 1),
    ])


def wrapper_projection():
    return replace_checked(checked(OLD + 'cleanup_root02.py'), [
        ('# Runs the pinned exact cleanup only after a human starts this wrapper with sudo.',
         '# Runs the pinned exact cleanup only through task-authorized sudo authentication.', 1),
        ('cleanup-app-inert-root02', 'cleanup-app-observe-root03', 1),
        ('cleanup_remoteocd01.py', 'cleanup_remoteocd02.py', 4), ('7873', '7735', 1),
        (OLD_RECIPE_SHA, RECIPE_SHA, 1), (OLD_PROJECTED_SHA, PROJECTED_SHA, 1),
        ('d190-human-root-cleanup-v2', 'd196-authenticated-observer-cleanup-v1', 1),
    ])


def inherited_oracle():
    raw = replace_checked(checked(OLD + 'test_cleanup_root02.py'), [
        ('cleanup-app-inert-root02', 'cleanup-app-observe-root03', 1),
        ('cleanup_remoteocd01.py', 'cleanup_remoteocd02.py', 5),
        ('cleanup_root02.py', 'cleanup_root03.py', 2),
        ('_independent_cleanup_root02', '_independent_cleanup_root03', 1),
        ('7873', '7735', 1), ('7870', '7732', 1),
        (OLD_RECIPE_SHA, RECIPE_SHA, 1), (OLD_PROJECTED_SHA, PROJECTED_SHA, 1),
        ('d190-exact-scratch-cleanup-v1', 'd196-exact-observer-scratch-cleanup-v1', 3),
        ('d190-human-root-cleanup-v2', 'd196-authenticated-observer-cleanup-v1', 1),
        ("fs.records['/tmp/remoteocd'].st_ino = 33", "fs.records['/tmp/remoteocd'].st_ino = 869", 1),
    ])
    module = types.ModuleType('_d196_inherited_oracle')
    module.__file__ = str(ROOT / NEW / '_private_oracle.py')
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def definitions(name):
    raw = checked(NEW + name)
    module = types.ModuleType('_d196_definitions_' + name[:-3])
    # Definitions-only import must not perform credentials, process or filesystem work.
    with contextlib.ExitStack() as stack:
        for target in ('os.setresuid', 'os.setresgid', 'os.seteuid', 'os.setgroups',
                       'os.unlink', 'os.rmdir', 'os.system', 'os.open', 'os.listdir',
                       'subprocess.run', 'subprocess.Popen'):
            stack.enter_context(mock.patch(target, create=True,
                side_effect=AssertionError('Import attempted operation: ' + target)))
        exec(compile(raw, '<fixed cleanup definitions>', 'exec'), module.__dict__)
    return module


class MetadataContract(unittest.TestCase):
    def test_all_frozen_inputs_and_consumed_success_are_preserved(self):
        for path in PINS:
            with self.subTest(path=path):
                checked(path)

    def test_exact_recipe_metadata_diff_and_private_observer_projection(self):
        raw = recipe_projection()
        self.assertEqual(raw, checked(NEW + 'cleanup_remoteocd02.py'))
        projected = replace_checked(raw, [(SCAN_OLD, SCAN_NEW, 1)])
        self.assertEqual(len(projected), 7732)
        self.assertEqual(hashlib.sha256(projected).hexdigest(), PROJECTED_SHA)

    def test_exact_wrapper_metadata_diff_preserves_all_operational_bytes(self):
        self.assertEqual(wrapper_projection(), checked(NEW + 'cleanup_root03.py'))

    def test_inherited_oracle_retains_all_37_methods_and_assertions(self):
        import ast
        before = ast.parse(checked(OLD + 'test_cleanup_root02.py'))
        old_class = next(node for node in before.body if isinstance(node, ast.ClassDef) and node.name == 'Contract')
        methods = [node.name for node in old_class.body if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
        projected = inherited_oracle()
        self.assertEqual(len(methods), 37)
        self.assertEqual(sorted(methods), sorted(name for name in vars(projected.Contract) if name.startswith('test_')))
        # The checked literal projection changes metadata only; all assertion statements survive.
        self.assertGreater(sum(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                               and node.func.attr.startswith('assert') for node in ast.walk(old_class)), 100)

    def test_fresh_stage_dependencies_and_old_basename_refusal(self):
        wrapper = definitions('cleanup_root03.py')
        self.assertEqual(wrapper.STAGE, '/home/arduino/sumox26_codex_build/cleanup-app-observe-root03')
        self.assertEqual(wrapper.PINS, {
            'cleanup_remoteocd02.py': (7735, RECIPE_SHA),
            'static_remote.py': PINS['state/analysis/P7_static_link_probe_raw/static_remote.py']})
        self.assertEqual(wrapper.PROJECTION_SHA, PROJECTED_SHA)
        wrapper.os = types.SimpleNamespace(open=mock.Mock(side_effect=AssertionError('Forbidden source open')))
        with self.assertRaisesRegex(ValueError, 'Unknown source basename'):
            wrapper.read_source('cleanup_remoteocd01.py')
        wrapper.os.open.assert_not_called()
        contract = checked(CONTRACT).decode()
        self.assertIn('result_root03.json', contract)
        self.assertIn('create\nit exclusively, never overwrite it', contract)

    def test_exact_new_payload_pin_and_retained_originals(self):
        recipe = definitions('cleanup_remoteocd02.py')
        self.assertEqual(recipe.PINS[PAYLOAD_NAME], (95328, PAYLOAD_SHA, PAYLOAD_PATH))
        self.assertEqual(set(recipe.PINS), {PAYLOAD_NAME, 'flash_sketch.cfg', 'zephyr-arduino_uno_q_stm32u585xx.elf'})
        self.assertEqual(sum(pin[0] for pin in recipe.PINS.values()), 2399736)
        original = types.ModuleType('_d196_old_recipe_definitions')
        exec(compile(checked(OLD + 'cleanup_remoteocd01.py'), '<old definitions>', 'exec'), original.__dict__)
        for name in ('flash_sketch.cfg', 'zephyr-arduino_uno_q_stm32u585xx.elf'):
            self.assertEqual(recipe.PINS[name], original.PINS[name])
        self.assertEqual(recipe.EXPECTED, original.EXPECTED)
        self.assertEqual(recipe.TARGET, original.TARGET)
        self.assertEqual(recipe.HELPER_SHA, original.HELPER_SHA)

    def test_old_scratch_basename_refuses_before_child_reads_or_mutations(self):
        recipe = definitions('cleanup_remoteocd02.py')
        recipe.os = types.SimpleNamespace(listdir=mock.Mock(return_value=[
            'motor_fault.ino.elf-zsk.bin', 'flash_sketch.cfg', 'zephyr-arduino_uno_q_stm32u585xx.elf']))
        helper = types.SimpleNamespace(read_file=mock.Mock(side_effect=AssertionError('Child must not be read')))
        with self.assertRaisesRegex(ValueError, 'Scratch child names changed'):
            recipe.inventory(helper, 42, recipe.PINS)
        helper.read_file.assert_not_called()

    def test_old_payload_length_and_digest_refuse_without_relaxing_new_pin(self):
        recipe = definitions('cleanup_remoteocd02.py')
        pin = recipe.PINS[PAYLOAD_NAME]
        for wrong in (b'x' * 29836, b'x' * 95328, b'x' * 95329):
            with self.subTest(length=len(wrong)), self.assertRaisesRegex(ValueError, 'Copy or original differs'):
                recipe.checked_bytes(wrong, pin)
        # Distinguishes digest comparison from length-only rejection using a controlled digest.
        digest = mock.Mock(return_value=types.SimpleNamespace(hexdigest=lambda:
            'b4416792a5bc228f34712fad9199a07c3c480aace979faa88aa12b50288b0a79'))
        recipe.hashlib = types.SimpleNamespace(sha256=digest)
        with self.assertRaisesRegex(ValueError, 'Copy or original differs'):
            recipe.checked_bytes(b'x' * 95328, pin)
        digest.assert_called_once()

    def directory_fixture(self, recipe, inode):
        reads = []
        def logical_read(root, path, limit):
            reads.append((path, limit))
            return b'isolated path-selection fixture'
        helper = types.SimpleNamespace(identity=lambda root: dict(recipe.EXPECTED),
            logical_read=logical_read, directory=lambda root, path: contextlib.nullcontext(41),
            child_directory=lambda parent, name, path: contextlib.nullcontext(42))
        info = types.SimpleNamespace(st_dev=34, st_ino=inode, st_uid=1000, st_gid=1000,
            st_mode=stat.S_IFDIR | 0o755, st_nlink=2, st_size=4096, st_mtime_ns=1, st_ctime_ns=1)
        recipe.os = types.SimpleNamespace(fstat=lambda fd: info)
        # Content behavior is tested independently; this seam isolates path/inode admission.
        recipe.checked_bytes = mock.Mock()
        recipe.inventory = mock.Mock(side_effect=RuntimeError('admitted inventory boundary'))
        return helper, reads

    def test_old_inode_refuses_and_new_inode_reaches_inventory_without_deleting(self):
        for inode in (33, 869):
            with self.subTest(inode=inode):
                recipe = definitions('cleanup_remoteocd02.py')
                helper, reads = self.directory_fixture(recipe, inode)
                error, message = (ValueError, 'Scratch directory identity changed') if inode == 33 else (RuntimeError, 'admitted inventory boundary')
                with self.assertRaisesRegex(error, message):
                    recipe.cleanup(helper, 40, {'use_checks': [], 'removed': []})
                self.assertEqual(recipe.inventory.call_count, int(inode == 869))
                self.assertEqual(recipe.checked_bytes.call_count, 3)
                self.assertEqual(reads, [(pin[2], pin[0]) for pin in recipe.PINS.values()])

    def test_old_retained_payload_path_has_no_fallback(self):
        recipe = definitions('cleanup_remoteocd02.py')
        helper, reads = self.directory_fixture(recipe, 869)
        selected = []
        def only_old_payload_available(root, path, limit):
            selected.append(path)
            if path == PAYLOAD_PATH:
                raise FileNotFoundError('new retained payload missing')
            return b'isolated retained-path fixture'
        helper.logical_read = only_old_payload_available
        with self.assertRaisesRegex(FileNotFoundError, 'new retained payload missing'):
            recipe.cleanup(helper, 40, {'use_checks': [], 'removed': []})
        self.assertEqual(selected[-1], PAYLOAD_PATH)
        self.assertFalse(any('motor-fault-active01' in path for path in selected))
        recipe.inventory.assert_not_called()


def load_tests(loader, standard_tests, pattern):
    inherited = inherited_oracle()
    inherited.Contract = unittest.skipUnless(sys.platform.startswith('linux'),
        'Historical credential/proc fixtures require Linux Python -I -B')(inherited.Contract)
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(inherited.Contract))
    suite.addTests(loader.loadTestsFromTestCase(MetadataContract))
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)
