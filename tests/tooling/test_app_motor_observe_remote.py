# Tests the fixed observer capture contract independently of its implementation.
# Retains all 26 historical methods and adds bounded wait and partial-evidence cases.
# Native operations and sleeping are controlled; freeze before first subject load.
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / 'state/analysis'
SUBJECT = ANALYSIS / 'P7_app_motor_observe_run_raw/remote.py'
HISTORICAL = ANALYSIS / 'P7_app_motor_fault_run_raw/test_remote.py'
ORIGINAL = ANALYSIS / 'P7_app_motor_fault_run_raw/remote_run02.py'
ORACLE_SHA = '44f7651b70ffc06697fb2932f4bab01a8ecc8c47d2b31fe779af356596d73bb2'
ORIGINAL_SHA = 'a77fb7d458ceb88f939ce785250d7c49727c56db231a9688890bef808c0c9162'
SOURCE = '3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0'
RUN = 'app-motor-observe-3a08ddeb-run01'
RAW_SHA = 'f1df5e7f4e094021e96947c53a204b6fac32c12ef35caba76eae61f2bfcdc3cc'
PACKAGE_SHA = '85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c'
BASELINE_SHA = 'e0bb7868e54a640499718d5c0d3df4ce6c6b4ef72a49f0bda9df64bbb60530f5'
OLD_SOURCE = '21df6ae82cca4b09dc6b1e0de5bc719cf98ec6887800d5ce8297522e491a7950'
OLD_RAW = '18598e13f2b5601db504f5272826b0952b95477dd2b1b8d397d20bd2ff899144'
OLD_PACKAGE = 'deb40317e5c444af26e65da4b6f1d0e577d9897d59dbddff3bce03a7bc14335c'
ORACLE = None
STUBS = {}


def checked(path, expected):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise AssertionError('Independent input changed: ' + str(path))
    return raw


def replace_exact(raw, old, new, count):
    old, new = old.encode(), new.encode()
    if raw.count(old) != count:
        raise AssertionError('Independent replacement count differs: ' + repr(old))
    return raw.replace(old, new)


def baseline():
    raw = checked(ORIGINAL, ORIGINAL_SHA)
    replacements = (
        (OLD_SOURCE, SOURCE, 1), ('app-motor-fault-21df6ae8-run02', RUN, 1),
        ('app-motor-fault', 'app-motor-observe', 8),
        ('app_motor_fault', 'app_motor_observe', 4),
        ('AppMotorFaultCapture', 'AppMotorObserveCapture', 2),
        ('95312', '95344', 1), (OLD_RAW, RAW_SHA, 1),
        ('95328', '95360', 2), (OLD_PACKAGE, PACKAGE_SHA, 1),
        ('727088', '727152', 1))
    for entry in replacements:
        raw = replace_exact(raw, *entry)
    if len(raw) != 10548 or hashlib.sha256(raw).hexdigest() != BASELINE_SHA:
        raise AssertionError('Contract baseline differs')
    return raw


def method_names(raw):
    return sorted((node.name, method.name) for node in ast.parse(raw).body
                  if isinstance(node, ast.ClassDef) for method in node.body
                  if isinstance(method, ast.FunctionDef) and method.name.startswith('test_'))


def historical_oracle():
    raw = checked(HISTORICAL, ORACLE_SHA)
    before = method_names(raw)
    replacements = (
        (OLD_SOURCE, SOURCE, 1), ('app-motor-fault-21df6ae8-run01', RUN, 1),
        ('app-motor-fault', 'app-motor-observe', 6),
        ('app_motor_fault', 'app_motor_observe', 3),
        ('95312', '95344', 1), (OLD_RAW, RAW_SHA, 1),
        ('95328', '95360', 1), (OLD_PACKAGE, PACKAGE_SHA, 1),
        ('29792', '29824', 1), ('(26, 727088)', '(26, 727152)', 1),
        ("'requested_bytes': 727088", "'requested_bytes': 727152", 1),
        ("HERE / 'remote.py'", 'SUBJECT', 3),
        ("side_effect=AssertionError('Native action forbidden'))",
         "side_effect=AssertionError('Native action forbidden'), create=True)", 2),
        ('self.assertEqual(self.clock.sleeps, [2])',
         'self.assertEqual(self.clock.sleeps, [30, 2])', 1),
        ('            self.assertEqual(len(self.calls), 13)\n            self.clock.sleep(seconds)',
         '            self.assertIn(seconds, (30, 2))\n'
         '            self.assertEqual(len(self.calls), 7 if seconds == 30 else 13)\n'
         '            self.clock.sleep(seconds)', 1),
        ('                def sleep(seconds):\n                    case.assertEqual(len(case.calls), 13)\n'
         '                    case.clock.now += elapsed',
         '                def sleep(seconds):\n'
         '                    if seconds == 30:\n'
         '                        case.assertEqual(len(case.calls), 7)\n'
         '                        case.clock.sleep(seconds)\n'
         '                        return\n'
         '                    case.assertEqual(seconds, 2)\n'
         '                    case.assertEqual(len(case.calls), 13)\n'
         '                    case.clock.now += elapsed', 1))
    for entry in replacements:
        raw = replace_exact(raw, *entry)
    if method_names(raw) != before or len(before) != 26:
        raise AssertionError('Historical method inventory changed')
    module = ModuleType('_d195_remote_historical_oracle')
    module.__file__ = str(HISTORICAL)
    module.SUBJECT = SUBJECT
    exec(compile(raw, str(HISTORICAL) + '<D195-fixture>', 'exec'), module.__dict__)
    # Metadata cases need no Linux descriptors. Linux-only lifecycle retains its skip.
    module.Contract.__unittest_skip__ = False
    return module


def forbidden(*args, **kwargs):
    raise AssertionError('Native action forbidden')


def setUpModule():
    if sys.platform.startswith('linux'):
        return
    # Only missing Linux imports receive inert stubs; restore these exact keys only.
    for name in ('resource', 'pwd'):
        if name not in sys.modules:
            module = ModuleType(name)
            module.RLIMIT_FSIZE = 1
            module.setrlimit = forbidden
            module.getpwuid = forbidden
            STUBS[name] = module
            sys.modules[name] = module


def tearDownModule():
    for name, module in STUBS.items():
        if sys.modules.get(name) is module:
            del sys.modules[name]
    STUBS.clear()


class WaitContract(unittest.TestCase):
    def setUp(self):
        for owner, name in ((subprocess, 'Popen'), (os, 'killpg'), (os, 'system')):
            guard = mock.patch.object(owner, name, side_effect=forbidden, create=True)
            guard.start()
            self.addCleanup(guard.stop)
        self.subject = ORACLE.load(SUBJECT, '_d195_wait_subject')
        self.deps = self.subject.load_dependencies(ORACLE.dependency_sources())
        self.clock = ORACLE.Clock()

    def capture(self, sleeper=None):
        result = self.subject._capture_type(self.deps)(
            None, None, b'', Path('/'), forbidden, self.clock,
            sleeper or self.clock.sleep, None, RUN)
        result.prepare_plan()
        return result

    def gathered(self, sleeper=None):
        capture = self.capture(sleeper)
        events = []
        capture.loader, capture.sketch = b'loader', b'sketch'
        def read(index, item):
            events.append(('read', index))
            capture.report['reads'].append({'name': item[0]})
            counts = capture.report['counts']
            counts['commands'] += 1
            counts['reads'] += 1
            counts['requested_bytes'] += item[2]
        def check(label, begin, end, reference):
            events.append(('flash', label, begin, end))
            capture.report['analysis']['flash'][label] = True
        capture.one_read, capture.check_image = read, check
        return capture, events

    def test_baseline_and_only_authorized_function_changes(self):
        old, new = ast.parse(baseline()), ast.parse(SUBJECT.read_bytes())
        old_functions = {n.name: n for n in old.body if isinstance(n, ast.FunctionDef)}
        new_functions = {n.name: n for n in new.body if isinstance(n, ast.FunctionDef)}
        self.assertEqual(set(old_functions), set(new_functions))
        for name in old_functions.keys() - {'_capture_type'}:
            self.assertEqual(ast.dump(old_functions[name]), ast.dump(new_functions[name]), name)
        def methods(function):
            cls = next(n for n in function.body if isinstance(n, ast.ClassDef))
            return {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
        before, after = methods(old_functions['_capture_type']), methods(new_functions['_capture_type'])
        self.assertEqual(set(after), set(before) | {'pre_sample_pause'})
        for name in ('profile_bindings', 'check_image'):
            self.assertEqual(ast.dump(before[name]), ast.dump(after[name]), name)

    def test_initial_wait_fields_and_success_preserve_capture_origin(self):
        capture = self.capture()
        self.assertIsNone(capture.report['analysis']['pre_sample_wait'])
        self.assertIsNone(capture.report['wait'])
        capture.pre_sample_pause()
        self.assertEqual(capture.report['analysis']['pre_sample_wait'],
                         {'requested_seconds': 30, 'before': 100.0, 'after': 130.0})
        self.assertIs(type(capture.report['analysis']['pre_sample_wait']['requested_seconds']), int)
        self.assertEqual(self.clock.sleeps, [30])
        self.assertEqual(capture.started, 100.0)
        self.assertEqual(capture.budget(), 570)
        self.assertIsNone(capture.report['wait'])

    def test_equal_or_insufficient_budget_refuses_before_record_or_sleep(self):
        for remaining in (30, 29, 0, -1):
            with self.subTest(remaining=remaining):
                self.clock = ORACLE.Clock()
                capture = self.capture()
                self.clock.now = 700 - remaining
                with self.assertRaises(Exception):
                    capture.pre_sample_pause()
                self.assertIsNone(capture.report['analysis']['pre_sample_wait'])
                self.assertEqual(self.clock.sleeps, [])

    def test_just_over_thirty_seconds_remaining_is_admitted(self):
        capture = self.capture()
        self.clock.now = 669.5
        capture.pre_sample_pause()
        self.assertEqual(capture.budget(), 0.5)
        self.assertEqual(self.clock.sleeps, [30])

    def test_short_sleep_retains_observed_after(self):
        def short(seconds):
            self.assertEqual(seconds, 30)
            self.clock.now += 29.999
        capture = self.capture(short)
        with self.assertRaises(Exception):
            capture.pre_sample_pause()
        self.assertEqual(capture.report['analysis']['pre_sample_wait'],
                         {'requested_seconds': 30, 'before': 100.0, 'after': 129.999})

    def test_throwing_sleeper_retains_before_and_original_exception(self):
        failure = RuntimeError('first sleeper error')
        def throwing(seconds):
            self.assertEqual(seconds, 30)
            raise failure
        capture = self.capture(throwing)
        with self.assertRaises(RuntimeError) as caught:
            capture.pre_sample_pause()
        self.assertIs(caught.exception, failure)
        self.assertEqual(capture.report['analysis']['pre_sample_wait'],
                         {'requested_seconds': 30, 'before': 100.0, 'after': None})

    def test_invalid_or_backward_clock_before_record_cannot_sleep(self):
        for value in (True, None, float('nan'), float('inf'), 99.0):
            with self.subTest(value=value):
                self.clock = ORACLE.Clock()
                capture = self.capture()
                self.clock.now = value
                with self.assertRaises(Exception):
                    capture.pre_sample_pause()
                self.assertIsNone(capture.report['analysis']['pre_sample_wait'])
                self.assertEqual(self.clock.sleeps, [])

    def test_invalid_or_backward_after_clock_keeps_partial_wait(self):
        for value in (True, None, float('nan'), float('inf'), 99.0):
            with self.subTest(value=value):
                self.clock = ORACLE.Clock()
                capture = self.capture(lambda seconds: setattr(self.clock, 'now', value))
                with self.assertRaises(Exception):
                    capture.pre_sample_pause()
                self.assertEqual(capture.report['analysis']['pre_sample_wait'],
                                 {'requested_seconds': 30, 'before': 100.0, 'after': None})

    def test_final_budget_oversleep_does_not_reset_origin(self):
        capture = self.capture(lambda seconds: setattr(self.clock, 'now', 700.0))
        with self.assertRaises(Exception):
            capture.pre_sample_pause()
        self.assertEqual(capture.report['analysis']['pre_sample_wait']['after'], 700.0)
        self.assertEqual(capture.started, 100.0)

    def test_gather_exact_wait_positions_flash_brackets_and_complete(self):
        capture, events = self.gathered()
        def sleep(seconds):
            events.append(('sleep', seconds))
            self.clock.sleep(seconds)
        capture.sleeper = sleep
        capture.gather()
        expected = []
        checks = {4: ('before_loader', 0, 5), 6: ('before_sketch', 5, 7),
                  20: ('after_sketch', 19, 21), 25: ('after_loader', 21, 26)}
        for index in range(26):
            if index in (7, 13):
                expected.append(('sleep', 30 if index == 7 else 2))
            expected.append(('read', index))
            if index in checks:
                expected.append(('flash', *checks[index]))
        self.assertEqual(events, expected)
        self.assertEqual(capture.report['counts'],
                         {'commands': 26, 'reads': 26, 'requested_bytes': 727152})
        self.assertTrue(capture.complete())
        self.assertEqual(capture.report['analysis']['coherence'], 'UNPROVEN')
        self.assertEqual(capture.report['wait'],
                         {'requested_seconds': 2, 'before': 130.0, 'after': 132.0})

    def test_gather_wait_failure_stops_after_seven_reads(self):
        for elapsed in (29, 600):
            with self.subTest(elapsed=elapsed):
                self.clock = ORACLE.Clock()
                capture, events = self.gathered(lambda seconds: setattr(self.clock, 'now', 100 + elapsed))
                with self.assertRaises(Exception):
                    capture.gather()
                self.assertEqual([e[1] for e in events if e[0] == 'read'], list(range(7)))
                self.assertEqual(capture.report['analysis']['snapshots'], [])
                self.assertIsNone(capture.report['wait'])
                self.assertFalse(capture.complete())

    def test_complete_requires_all_original_evidence_and_valid_wait(self):
        capture, _ = self.gathered()
        capture.gather()
        original = copy.deepcopy(capture.report)
        def reject(change):
            capture.report = copy.deepcopy(original)
            change(capture.report)
            self.assertFalse(capture.complete())
        reject(lambda r: r.update(analysis=None))
        reject(lambda r: r['analysis'].update(pre_sample_wait=None))
        reject(lambda r: r['analysis']['pre_sample_wait'].update(after=None))
        reject(lambda r: r['analysis']['pre_sample_wait'].update(after=129.99))
        reject(lambda r: r['analysis']['snapshots'].pop())
        for name in original['analysis']['flash']:
            reject(lambda r, name=name: r['analysis']['flash'].update({name: False}))
        for name in original['counts']:
            reject(lambda r, name=name: r['counts'].update({name: r['counts'][name] - 1}))

    def test_final_close_exception_leaves_first_wait_error_in_written_result(self):
        capture, _ = self.gathered(lambda seconds: (_ for _ in ()).throw(RuntimeError('first wait error')))
        saved = []
        capture.admit = lambda: None
        capture.claim = lambda: setattr(capture, 'claimed', True)
        capture.check_file = lambda name: None
        capture.check_identity = capture.check_directory = lambda: None
        capture.write_record = lambda name, value, **kwargs: saved.append((name, copy.deepcopy(value)))
        capture.close = lambda: (_ for _ in ()).throw(OSError('terminal descriptor close error'))
        with self.assertRaisesRegex(OSError, 'terminal descriptor close error'):
            self.deps.capture._collect(capture)
        self.assertEqual(saved[-1][0], 'capture_result.json')
        self.assertEqual(saved[-1][1]['first_error']['message'], 'first wait error')
        self.assertEqual(saved[-1][1]['status'], 'FAILED')
        self.assertEqual(saved[-1][1]['counts']['reads'], 7)


@unittest.skipUnless(sys.platform.startswith('linux'), 'Linux descriptor contract')
class PublicWaitLifecycle(unittest.TestCase):
    def case(self, exercise):
        case = ORACLE.Lifecycle('test_upload_success_exact_one_shot_and_all_closing_pins')
        try:
            case.setUp()
            exercise(case)
        finally:
            case.doCleanups()

    def test_public_collect_retains_wait_and_separate_sample_gap(self):
        def exercise(case):
            report = case.assert_report(case.run_mode('capture'), 'capture', 'COLLECTED')
            analysis = report['analysis']
            self.assertEqual(analysis['pre_sample_wait'],
                             {'requested_seconds': 30, 'before': 100.0, 'after': 130.0})
            self.assertEqual(report['wait'],
                             {'requested_seconds': 2, 'before': 130.0, 'after': 132.0})
            self.assertEqual(set(analysis), {'schema', 'flash', 'snapshots', 'coherence', 'pre_sample_wait'})
            self.assertEqual(report['counts']['requested_bytes'], 727152)
            self.assertEqual(len(case.calls), 26)
        self.case(exercise)

    def test_public_collect_wait_failures_keep_seven_reads_and_flash_evidence(self):
        for kind in ('short', 'throw', 'backward', 'oversleep', 'budget'):
            def exercise(case):
                def sleep(seconds):
                    self.assertEqual(seconds, 30)
                    self.assertEqual(len(case.calls), 7)
                    if kind == 'throw':
                        raise RuntimeError('first controlled wait failure')
                    case.clock.now += {'short': 29, 'backward': -1, 'oversleep': 600}[kind]
                if kind == 'budget':
                    case.after_execute = lambda index: setattr(case.clock, 'now', 670.0) if index == 6 else None
                report = case.assert_report(case.run_mode('capture', sleeper=sleep), 'capture', 'FAILED')
                self.assertEqual(len(case.calls), 7)
                self.assertEqual(report['counts']['reads'], 7)
                self.assertIsNone(report['wait'])
                self.assertEqual(report['analysis']['snapshots'], [])
                self.assertEqual(report['analysis']['flash'],
                                 {'before_loader': True, 'before_sketch': True,
                                  'after_loader': False, 'after_sketch': False})
                wait = report['analysis']['pre_sample_wait']
                if kind == 'budget':
                    self.assertIsNone(wait)
                else:
                    self.assertEqual(wait['before'], 100.0)
                    self.assertEqual(wait['requested_seconds'], 30)
                    self.assertEqual(wait['after'], None if kind in ('throw', 'backward') else
                                     129.0 if kind == 'short' else 700.0)
                if kind == 'throw':
                    self.assertEqual(report['first_error']['message'], 'first controlled wait failure')
            with self.subTest(kind=kind):
                self.case(exercise)

    def test_first_wait_error_survives_failing_closing_pins_identity_and_clock(self):
        def exercise(case):
            def sleep(seconds):
                for pin in case.capture_binding['files'].values():
                    case.logical(pin['path']).write_bytes(b'changed after first error')
                case.identity_value['boot_id'] = '00000000-0000-0000-0000-000000000000'
                case.clock.now = 99.0
                raise RuntimeError('first controlled wait failure')
            report = case.assert_report(case.run_mode('capture', sleeper=sleep), 'capture', 'FAILED')
            self.assertEqual(report['first_error']['message'], 'first controlled wait failure')
            self.assertGreaterEqual(len(report['postcheck_errors']), 7)
            self.assertEqual(report['analysis']['pre_sample_wait'],
                             {'requested_seconds': 30, 'before': 100.0, 'after': None})
            self.assertEqual(len(case.calls), 7)
        self.case(exercise)


def load_tests(loader, tests, pattern):
    global ORACLE
    ORACLE = historical_oracle()
    # Historical classes use this module's fixture-level platform setup/teardown.
    ORACLE.Contract.__module__ = __name__
    ORACLE.Lifecycle.__module__ = __name__
    result = unittest.TestSuite()
    for cls in (ORACLE.Contract, ORACLE.Lifecycle, WaitContract, PublicWaitLifecycle):
        result.addTests(loader.loadTestsFromTestCase(cls))
    return result


if __name__ == '__main__':
    unittest.main(verbosity=2)
