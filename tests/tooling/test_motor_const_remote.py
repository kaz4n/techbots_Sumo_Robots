# Preserves all D201 capture assertions through checked D207 metadata fixtures.
# Adds exact derivative, six-window accounting and stale-binding refusals.
# Freeze before new source reads; all hardware, clocks and children are controlled.
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
PRIOR = 'tests/tooling/test_app_motor_observe_remote.py'
PRIOR_SHA = 'f45218ea3d9fb118adfe796c12fc5f4bab654c843cf33cc531e81d99a3f41fc6'
BINDING = 'state/analysis/P7_motor_const_run_raw/run_derivation01.json'
BINDING_SHA = 'c90961438062c153f9c99621eba0617b3fc26b0f3dbdd2c35859ec2e744b5bfb'
SUBJECT = ROOT / 'state/analysis/P7_motor_const_run_raw/remote.py'
SOURCE = '4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2'
RUN = 'app-motor-const-4bc3a2e6-run01'
WINDOWS = (('trace', 536951180, 2128), ('report', 537119696, 1168),
           ('runtime', 537117984, 600), ('transaction', 537115448, 504),
           ('settle', 537121768, 28), ('gate', 536953520, 88))
CHANGES = (('P7_app_motor_observe_run_raw', 'P7_motor_settle_run_raw', 1), ('3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0', '117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da', 1), ('app-motor-observe-3a08ddeb-run01', 'app-motor-settle-117cc0e7-run01', 1), ('app-motor-observe', 'app-motor-settle', 2), ('f1df5e7f4e094021e96947c53a204b6fac32c12ef35caba76eae61f2bfcdc3cc', 'd1033e627420e0de5d8ca90ebdf79c284228a23448f3d3e99130651d5afc65cc', 1), ('85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c', 'e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0', 1), ('AppMotorObserveCapture', 'AppMotorSettleCapture', 1), ('95344', '95504', 2), ('95360', '95520', 2), ('29824', '29984', 1), ('727152', '727432', 5), ('10548', '10534', 1), ('e0bb7868e54a640499718d5c0d3df4ce6c6b4ef72a49f0bda9df64bbb60530f5', 'a8aa4a7cb83ee734683ee3a4d2f089476e6705a916632049b148d9f5238492d6', 1))
_PROVIDER = None


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, expected):
    raw = Path(path).read_bytes()
    if sha(raw) != expected: raise AssertionError('Frozen input changed: ' + str(path))
    return raw


def replace(raw, changes):
    for before, after, count in changes:
        before, after = before.encode(), after.encode()
        if raw.count(before) != count: raise AssertionError('Fixture count differs: ' + repr(before))
        raw = raw.replace(before, after)
    return raw


def scoped(raw, name, changes):
    node = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == name)
    before = b''.join(raw.splitlines(keepends=True)[node.lineno-1:node.end_lineno])
    if raw.count(before) != 1: raise AssertionError('Unique fixture function')
    return raw.replace(before, replace(before, changes))


def fixture_projection(raw):
    raw = replace(raw, CHANGES)
    raw = scoped(raw, 'baseline', (("    replacements = (\n", "    replacements = (\n"
        "        (\"('previous', 537115952, 48)\", \"('settle', 537121768, 28)\", 1),\n", 1),
        ("('727088', '727432', 1))", "('727088', '727432', 1),\n"
         "        ('_app_motor_observe_private_', '_app_motor_settle_private_', 1))", 1)))
    raw = scoped(raw, 'historical_oracle', (("    replacements = (\n", "    replacements = (\n"
        "        (\"('previous', 537115952, 48)\", \"('settle', 537121768, 28)\", 1),\n"
        "        ('4536', '4516', 1),\n", 1),))
    if (len(raw), sha(raw)) != (21196, 'c96d981202c9e19ad3fb50f50c23a726867b8b5a49dcf795816a9289b206d4ae'):
        raise AssertionError('Projected remote fixture changed')
    raw = replace(raw, (('P7_motor_settle_run_raw', 'P7_motor_const_run_raw', 1), ('117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da', '4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2', 1), ('app-motor-settle-117cc0e7-run01', 'app-motor-const-4bc3a2e6-run01', 1), ('app-motor-settle', 'app-motor-const', 2), ('_app_motor_settle_private_', '_app_motor_const_private_', 1), ('AppMotorSettleCapture', 'AppMotorConstCapture', 1), ('d1033e627420e0de5d8ca90ebdf79c284228a23448f3d3e99130651d5afc65cc', '76d2846dfe99602b1a4dd680f19c8150a02af4dba3b4f3411fafd7c55e3824d3', 1), ('e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0', 'f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7', 1), ('95504', '95352', 2), ('95520', '95368', 2), ('29984', '29832', 1), ('727432', '727128', 5), ('10534', '10522', 1), ('a8aa4a7cb83ee734683ee3a4d2f089476e6705a916632049b148d9f5238492d6', '44d8edd3724ea78e673f35d07e2ab92736822faccfcbb28bc9b4fa8cc0d83a73', 1)))
    if (len(raw), hashlib.sha256(raw).hexdigest()) != (21190, 'fb90838accf91e6af276451b8418b74763257e699f403ebf7070f93097c222fd'):
        raise AssertionError('D207 projected fixture changed')
    return raw


def private_oracle():
    raw = fixture_projection(checked(ROOT / PRIOR, PRIOR_SHA))
    value = types.ModuleType('_d201_private_remote_oracle'); value.__file__ = str(ROOT / PRIOR)
    exec(compile(raw, str(ROOT / PRIOR) + '<fixed D201 metadata>', 'exec'), value.__dict__)
    return value


def historical_oracle():
    return private_oracle().historical_oracle()


def setUpModule():
    _PROVIDER.setUpModule()


def tearDownModule():
    _PROVIDER.tearDownModule()


class CurrentRemote(unittest.TestCase):
    def setUp(self):
        case = _PROVIDER.WaitContract('test_initial_wait_fields_and_success_preserve_capture_origin')
        case.setUp(); self.addCleanup(case.doCleanups)
        self.subject, self.deps = case.subject, case.deps

    def test_exact_eleven_metadata_changes_preserve_all_other_source_bytes(self):
        spec = json.loads(checked(ROOT / BINDING, BINDING_SHA))['metadata_derivatives']['remote']
        self.assertEqual(len(spec['steps']), 10)
        raw = checked(ROOT / 'state/analysis/P7_motor_settle_run_raw/remote.py', spec['input']['sha256'])
        self.assertEqual(len(raw), spec['input']['bytes'])
        expected = replace(raw, [(r['old'], r['new'], r['count']) for r in spec['steps']])
        actual = SUBJECT.read_bytes()
        self.assertEqual(actual, expected)
        self.assertEqual((len(actual), sha(actual)), (11331, spec['expected']['sha256']))

    def test_exact_current_six_windows_and_twenty_six_reads(self):
        self.assertEqual(tuple(self.subject.WINDOWS), WINDOWS)
        plan = self.subject.read_plan()
        self.assertEqual((len(plan), sum(row[2] for row in plan)), (26, 727128))
        self.assertEqual(sum(row[2] for row in WINDOWS), 4516)
        self.assertEqual(plan[6], ('before.sketch.1', 0x08110000, 29832))
        self.assertEqual(plan[20], ('after.sketch.1', 0x08110000, 29832))
        for start, prefix in ((7, 'first'), (13, 'second')):
            self.assertEqual(tuple(plan[start:start+6]),
                tuple((prefix + '.' + name, address, size) for name, address, size in WINDOWS))
        self.assertNotIn(('previous', 537115952, 48), self.subject.WINDOWS)
        self.assertEqual((self.subject.SOURCE, self.subject.RUN_ID), (SOURCE, RUN))

    def test_previous_source_and_D193_image_bindings_cannot_replace_current_inputs(self):
        fixture = _PROVIDER.ORACLE
        for kind in ('upload', 'capture'):
            original = fixture.bindings(kind)
            candidates = [dict(original, source_sha256='3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0')]
            value = copy.deepcopy(original)
            value['files']['sketch'].update(bytes=95360,
                sha256='85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c')
            candidates.append(value)
            check = getattr(self.subject, 'checked_' + kind + '_bindings')
            for candidate in candidates:
                before = copy.deepcopy(candidate)
                with self.subTest(kind=kind), self.assertRaises(Exception): check(self.deps, candidate)
                self.assertEqual(candidate, before)


    def test_D201_source_package_and_consumed_owner_bindings_are_rejected(self):
        for kind in ('upload', 'capture'):
            original = _PROVIDER.ORACLE.bindings(kind)
            candidates = [dict(original, source_sha256='117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da'),
                          dict(original, run_id='app-motor-settle-117cc0e7-run01')]
            value = copy.deepcopy(original)
            value['files']['sketch'].update(bytes=95520,
                sha256='e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0')
            candidates.append(value)
            for candidate in candidates:
                before = copy.deepcopy(candidate)
                with self.subTest(kind=kind, candidate=candidate), self.assertRaises(Exception):
                    getattr(self.subject, 'checked_' + kind + '_bindings')(self.deps, candidate)
                self.assertEqual(candidate, before)

    def test_current_profile_keeps_fixed_bounds_and_one_wait(self):
        capture = _PROVIDER.WaitContract('test_initial_wait_fields_and_success_preserve_capture_origin')
        capture.setUp(); self.addCleanup(capture.doCleanups)
        owner = capture.capture()
        owner.pre_sample_pause()
        self.assertEqual(capture.clock.sleeps, [30])
        self.assertEqual(owner.budget(), 570)
        self.assertEqual(tuple(capture.subject.WINDOWS), WINDOWS)


def load_tests(loader, tests, pattern):
    global _PROVIDER
    _PROVIDER = private_oracle(); _PROVIDER.ORACLE = _PROVIDER.historical_oracle()
    result = unittest.TestSuite()
    for cls in (_PROVIDER.ORACLE.Contract, _PROVIDER.ORACLE.Lifecycle,
                _PROVIDER.WaitContract, _PROVIDER.PublicWaitLifecycle, CurrentRemote):
        cls.__module__ = __name__; result.addTests(loader.loadTestsFromTestCase(cls))
    if result.countTestCases() != 47: raise AssertionError('Expected45 retained+2 D207 remote methods')
    return result


if __name__ == '__main__':
    unittest.main(verbosity=2)
