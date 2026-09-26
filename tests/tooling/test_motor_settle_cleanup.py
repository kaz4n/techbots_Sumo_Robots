# Tests D200 exact cleanup derivatives using independently pinned historical fixtures.
# Retains37 credential/descriptor methods and10 metadata methods plus2 refusals.
# Freeze before subject inspection; no actual credentials, processes, or deletion.
import ast
import hashlib
from pathlib import Path
import sys
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
OLD = 'state/analysis/P7_app_motor_fault_run_raw/'
PRIOR = 'state/analysis/P7_app_motor_observe_run_raw/'
NEW = 'state/analysis/P7_motor_settle_cleanup_raw/'
CONTRACT = 'state/analysis/P7_motor_settle_cleanup_contract.md'
CONTRACT_PIN = (16277, '6cb02590369cdce1edd748987df363f99f336c9736dfd06e72906c4578457f47')
CORE = OLD + 'test_cleanup_root02.py'
CORE_PIN = (37221, '225ef637e85dfe4ce1598e6744c781720b900905ea0c9c3bf0737d58b49e1559')
DELTA = 'tests/tooling/test_app_motor_observe_cleanup.py'
DELTA_PIN = (14429, '18b150d239ba34aca30ce8b436036532a15e2c5aacb53ccf1166f51a68a831c0')
RECIPE_SHA = '6afeea1b9733670cdf315b2bf29b3e6e9c24016a2ba9217013e67496ec088f4d'
PROJECTED_SHA = '96d1197ec296906958f71c772102fdd34f7979525cde3e41222ee611025274c4'
WRAPPER_SHA = '13f33327c5474d7c4dee56657a9d93b50e6fcdaee864e1855c916417a53c6290'
PRIOR_RECIPE_SHA = '1834edd39d628dccda0516f35cbc35434fd659c28392df6600cfdcf882e8ec9a'
PRIOR_PROJECTED_SHA = 'b4bdb4dd7cbe6ed2ff534a033507ad2c080c5b789dc02716f4189f557a34c0c1'
OLD_RECIPE_SHA = '23ef85ae3c386cc76751eea0fb18a90148a6fe513e3e8c753d527c06efcbbe95'
OLD_PROJECTED_SHA = '51286ad414794e82f3161bed16cbb47dca421e831316e053a7eab967469f602e'
PAYLOAD_NAME = 'app_motor_observe.ino.bin-zsk.bin'
PAYLOAD_PATH = '/home/arduino/sumox26_codex_build/app-motor-observe-static01/build/' + PAYLOAD_NAME
PAYLOAD_SHA = '85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c'
PRIOR_PAYLOAD_SHA = 'deb40317e5c444af26e65da4b6f1d0e577d9897d59dbddff3bce03a7bc14335c'
FUTURE_PAYLOAD_SHA = 'e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0'
PINS = {
    CONTRACT: CONTRACT_PIN, CORE: CORE_PIN, DELTA: DELTA_PIN,
    PRIOR + 'cleanup_remoteocd02.py': (7735, PRIOR_RECIPE_SHA),
    PRIOR + 'cleanup_root03.py': (9606, 'a089cc3bac9d8df3ffe53947e22b1bb4ffa139a733c7ebb1f5ba62e6d5bd804f'),
    'state/analysis/P7_app_motor_observe_cleanup_contract.md': (12460, '7258230a63f48e09401186b8ad3bed09f958006909610cea835926427a3609f6'),
    'state/analysis/P7_static_link_probe_raw/static_remote.py': (33321, '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8'),
    NEW + 'observe_admission01.py': (9770, 'e4db653bf71bb2201549ea0ade3d637521520d6e2e9747473cf52fd6688aaa83'),
    NEW + 'admission01.json': (24558, 'e95ebed4ee3d6441abccced02adbcc4857fe5f10418d94e158b009d3edecf922'),
    'state/analysis/P7_app_motor_observe_compile_raw/native_static01/artifacts.json': (9651, '5ceba77dde7c493d66398bfd6d8e0e27e56345612290cb8fef9328f24b87625b'),
    'state/analysis/P7_motor_settle_compile_raw/native_static01/artifacts.json': (9648, 'e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10'),
    NEW + 'cleanup_remoteocd03.py': (7740, RECIPE_SHA),
    NEW + 'cleanup_root04.py': (9603, WRAPPER_SHA),
}
OLD_PAYLOAD = (
    "    'app_motor_fault.ino.bin-zsk.bin': (95328, '" + PRIOR_PAYLOAD_SHA + "',\n"
    "        '/home/arduino/sumox26_codex_build/app-motor-fault-static01/build/app_motor_fault.ino.bin-zsk.bin'),\n")
NEW_PAYLOAD = "    '" + PAYLOAD_NAME + "': (95360, '" + PAYLOAD_SHA + "',\n        '" + PAYLOAD_PATH + "'),\n"
CORE_CHANGES = (
    ('cleanup-app-inert-root02', 'cleanup-app-settle-root04', 1),
    ('cleanup_remoteocd01.py', 'cleanup_remoteocd03.py', 5),
    ('cleanup_root02.py', 'cleanup_root04.py', 2),
    ('_independent_cleanup_root02', '_independent_cleanup_root04', 1),
    ('7873', '7740', 1), ('7870', '7737', 1),
    (OLD_RECIPE_SHA, RECIPE_SHA, 1), (OLD_PROJECTED_SHA, PROJECTED_SHA, 1),
    ('d190-exact-scratch-cleanup-v1', 'd200-exact-settle-scratch-cleanup-v1', 3),
    ('d190-human-root-cleanup-v2', 'd200-authenticated-settle-cleanup-v1', 1),
    ("fs.records['/tmp/remoteocd'].st_ino = 33", "fs.records['/tmp/remoteocd'].st_ino = 1172", 1),
)
DELTA_CHANGES = (
    ('cleanup_remoteocd02.py', 'cleanup_remoteocd03.py', 7),
    ('cleanup_root03.py', 'cleanup_root04.py', 2),
    ('cleanup-app-observe-root03', 'cleanup-app-settle-root04', 1),
    ('7732', '7737', 1), ('7735', '7740', 1),
    ('result_root03.json', 'result_root04.json', 1),
    ('create\\nit exclusively, never overwrite it',
     'Create it\\nexclusively with no-clobber behavior; never overwrite a prior result', 1),
    ('(95328, PAYLOAD_SHA', '(95360, PAYLOAD_SHA', 1), ('2399736', '2399768', 1),
    ("'motor_fault.ino.elf-zsk.bin', 'flash_sketch.cfg'", "'app_motor_fault.ino.bin-zsk.bin', 'flash_sketch.cfg'", 1),
    ("(b'x' * 29836, b'x' * 95328, b'x' * 95329)", "(b'x' * 95328, b'x' * 95360, b'x' * 95361)", 1),
    ('b4416792a5bc228f34712fad9199a07c3c480aace979faa88aa12b50288b0a79', PRIOR_PAYLOAD_SHA, 1),
    ("recipe.checked_bytes(b'x' * 95328, pin)", "recipe.checked_bytes(b'x' * 95360, pin)", 1),
    ('(33, 869)', '(869, 1172)', 1), ('if inode == 33 else', 'if inode == 869 else', 1),
    ('int(inode == 869)', 'int(inode == 1172)', 1),
    ('self.directory_fixture(recipe, 869)', 'self.directory_fixture(recipe, 1172)', 1),
    ("'motor-fault-active01'", "'app-motor-fault-static01'", 1),
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(name):
    raw = (ROOT / name).read_bytes()
    if (len(raw), sha(raw)) != PINS[name]:
        raise AssertionError('Frozen input differs: ' + name)
    return raw


def replace_checked(raw, changes):
    for before, after, count in changes:
        before, after = before.encode(), after.encode()
        if raw.count(before) != count: raise AssertionError('Independent occurrence: ' + repr(before))
        raw = raw.replace(before, after)
    return raw


def module(raw, path, name):
    value = types.ModuleType(name); value.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), value.__dict__)
    return value


def recipe_projection():
    raw = replace_checked(checked(PRIOR + 'cleanup_remoteocd02.py'), (
        ('D190', 'D195', 1), (OLD_PAYLOAD, NEW_PAYLOAD, 1),
        ('info.st_ino == 869', 'info.st_ino == 1172', 1),
        ('d196-exact-observer-scratch-cleanup-v1', 'd200-exact-settle-scratch-cleanup-v1', 1)))
    if (len(raw), sha(raw)) != PINS[NEW + 'cleanup_remoteocd03.py']:
        raise AssertionError('Independent recipe identity')
    return raw


def wrapper_projection():
    raw = replace_checked(checked(PRIOR + 'cleanup_root03.py'), (
        ('cleanup-app-observe-root03', 'cleanup-app-settle-root04', 1),
        ('cleanup_remoteocd02.py', 'cleanup_remoteocd03.py', 4), ('7735', '7740', 1),
        (PRIOR_RECIPE_SHA, RECIPE_SHA, 1), (PRIOR_PROJECTED_SHA, PROJECTED_SHA, 1),
        ('d196-authenticated-observer-cleanup-v1', 'd200-authenticated-settle-cleanup-v1', 1)))
    if (len(raw), sha(raw)) != PINS[NEW + 'cleanup_root04.py']:
        raise AssertionError('Independent wrapper identity')
    return raw


def inherited_core():
    raw = replace_checked(checked(CORE), CORE_CHANGES)
    if (len(raw), sha(raw)) != (37255, '4109c339f8d6a8faa195b671a8b20ce778810bd895e04846b84784f58610a33f'):
        raise AssertionError('Private core fixture identity')
    return module(raw, ROOT / NEW / '_private_oracle.py', '_d200_private_core')


def private_oracle():
    raw = checked(DELTA); lines = raw.splitlines(keepends=True)
    node = next(item for item in ast.parse(raw).body if isinstance(item, ast.ClassDef) and item.name == 'MetadataContract')
    before = b''.join(lines[node.lineno-1:node.end_lineno])
    if raw.count(before) != 1: raise AssertionError('Unique historical metadata fixture class')
    raw = raw.replace(before, replace_checked(before, DELTA_CHANGES))
    if (len(raw), sha(raw)) != (14478, 'fc1ce156a78519c041a8836191583f4548fc7846d5c229060818dfbc9a33f0a2'):
        raise AssertionError('Private metadata oracle identity')
    oracle = module(raw, ROOT / DELTA, '_d200_private_delta')
    oracle.NEW, oracle.CONTRACT = NEW, CONTRACT
    oracle.RECIPE_SHA, oracle.PROJECTED_SHA, oracle.WRAPPER_SHA = RECIPE_SHA, PROJECTED_SHA, WRAPPER_SHA
    oracle.PAYLOAD_NAME, oracle.PAYLOAD_PATH, oracle.PAYLOAD_SHA = PAYLOAD_NAME, PAYLOAD_PATH, PAYLOAD_SHA
    oracle.PINS = {**oracle.PINS, **PINS}
    oracle.recipe_projection, oracle.wrapper_projection = recipe_projection, wrapper_projection
    oracle.inherited_oracle = inherited_core
    return oracle


def focused_cases(oracle):
    class CurrentCopyRefusals(unittest.TestCase):
        def test_D190_and_D198_package_bytes_cannot_replace_the_current_D193_copy(self):
            recipe = oracle.definitions('cleanup_remoteocd03.py')
            before = dict(recipe.PINS); pin = recipe.PINS[PAYLOAD_NAME]
            self.assertEqual(pin, (95360, PAYLOAD_SHA, PAYLOAD_PATH))
            for wrong_size in (95328, 95520):
                with self.subTest(size=wrong_size), self.assertRaisesRegex(ValueError, 'Copy or original differs'):
                    recipe.checked_bytes(b'x' * wrong_size, pin)
            for wrong_digest in (PRIOR_PAYLOAD_SHA, FUTURE_PAYLOAD_SHA):
                digest = mock.Mock(return_value=types.SimpleNamespace(hexdigest=lambda: wrong_digest))
                recipe.hashlib = types.SimpleNamespace(sha256=digest)
                with self.subTest(digest=wrong_digest), self.assertRaisesRegex(ValueError, 'Copy or original differs'):
                    recipe.checked_bytes(b'x' * 95360, pin)
                digest.assert_called_once()
            self.assertEqual(recipe.PINS, before)

        def test_previous_source_names_and_stage_schema_source_drift_fail_before_execution(self):
            wrapper = oracle.definitions('cleanup_root04.py')
            wrapper.os = types.SimpleNamespace(open=mock.Mock(side_effect=AssertionError('Unknown source opened')))
            for name in ('cleanup_remoteocd01.py', 'cleanup_remoteocd02.py', 'cleanup_root03.py'):
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Unknown source basename'):
                    wrapper.read_source(name)
            wrapper.os.open.assert_not_called()
            name = NEW + 'cleanup_root04.py'; current = checked(name)
            # These are rejected SOURCE substitutions, not a new JSON schema predicate.
            for before, after in (
                    (b'cleanup-app-settle-root04', b'cleanup-app-observe-root03'),
                    (b'd200-authenticated-settle-cleanup-v1', b'd196-authenticated-observer-cleanup-v1')):
                self.assertEqual(current.count(before), 1)
                wrong = current.replace(before, after); read = Path.read_bytes
                def observed(path):
                    return wrong if path == ROOT / name else read(path)
                with mock.patch.object(Path, 'read_bytes', observed), self.assertRaisesRegex(AssertionError, 'Frozen input changed'):
                    oracle.definitions('cleanup_root04.py')

    return CurrentCopyRefusals


def load_tests(loader, standard, pattern):
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Independent D200 tests require Python -I -B')
    oracle = private_oracle(); core = inherited_core()
    core.Contract = unittest.skipUnless(sys.platform.startswith('linux'),
        'Historical credential/proc fixtures require Linux Python -I -B')(core.Contract)
    inherited = loader.loadTestsFromTestCase(core.Contract)
    delta = loader.loadTestsFromTestCase(oracle.MetadataContract)
    focused = loader.loadTestsFromTestCase(focused_cases(oracle))
    if (inherited.countTestCases(), delta.countTestCases(), focused.countTestCases()) != (37, 10, 2):
        raise AssertionError('Expected37 core+10 metadata+2 focused methods')
    return unittest.TestSuite([standard, inherited, delta, focused])


if __name__ == '__main__':
    unittest.main(verbosity=2)
