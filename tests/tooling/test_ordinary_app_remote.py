# Checks the ordinary native scope from frozen independent historical fixtures.
# Retains 42 remote guard/wait cases and adds five ordinary expectations.
# No native operation is allowed; subject inspection begins only after freeze.
import ast
import copy
import hashlib
import json
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
RAW = 'state/analysis/P7_ordinary_app_run_raw/'
FIXTURE = RAW + 'native_fixture_derivation01.json'
FIXTURE_PIN = {'bytes': 194972, 'sha256': '8cfd7f553c4e17334a899c575d2b4935cbcfd69c332b43c7fe0a84bfc1f95372'}
_PROVIDER = None


def identity(raw):
    return {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def checked(path, pin):
    raw = Path(path).read_bytes()
    expected = {'bytes': pin['bytes'], 'sha256': pin['sha256']}
    if identity(raw) != expected:
        raise AssertionError('Frozen D212 input differs: ' + str(path))
    return raw


def specification():
    return json.loads(checked(ROOT / FIXTURE, FIXTURE_PIN))


def project(raw, steps):
    for row in steps:
        old, new = row['old'].encode(), row['new'].encode()
        if identity(raw) != row['before'] or raw.count(old) != row['count']:
            raise AssertionError('D212 fixture input or occurrence differs')
        raw = raw.replace(old, new)
        if identity(raw) != row['after']:
            raise AssertionError('D212 fixture output differs')
    return raw


def triples(record):
    return tuple(tuple(row) for row in record['historical_changes']) + tuple(
        (row['old'], row['new'], row['count']) for row in record['steps'])


def provider_source(kind):
    spec = specification()
    record = spec['providers'][kind]
    old = record['input']
    oldraw = checked(ROOT / old['path'], old)
    ancestor = types.ModuleType('_d212_metadata_ancestor_' + kind)
    ancestor.__file__ = str(ROOT / old['path'])
    exec(compile(oldraw, ancestor.__file__, 'exec'), ancestor.__dict__)
    inherited = ancestor.fixture_projection(ancestor.checked(ROOT / ancestor.PRIOR, ancestor.PRIOR_SHA)
        if kind == 'remote' else ancestor.load_support().checked(ROOT / ancestor.PRIOR, ancestor.PRIOR_SHA)
        if kind == 'actions' else ancestor.load_support().load_support().checked(ROOT / ancestor.PRIOR, ancestor.PRIOR_SHA))
    if identity(inherited) != record['d207_projected']:
        raise AssertionError('Historical D207 provider projection changed')
    raw = project(inherited, record['d212_steps'])
    if identity(raw) != record['expected']:
        raise AssertionError('Ordinary provider projection changed')
    return raw, ancestor.PRIOR, spec


def make_provider(kind, injections=None):
    raw, oldpath, spec = provider_source(kind)
    module = types.ModuleType('_d212_private_' + kind)
    module.__file__ = str(ROOT / oldpath)
    module.D212_CORE_CHANGES = triples(spec['core'][kind])
    module.D212_BASELINE_CHANGES = triples(spec['baseline'])
    module.__dict__.update(injections or {})
    exec(compile(raw, module.__file__ + '<frozen D212>', 'exec'), module.__dict__)
    return module


def private_oracle():
    return make_provider('remote')


def historical_oracle():
    return private_oracle().historical_oracle()


def assert_recipe(case, kind, count):
    spec = specification()
    derivation = json.loads(checked(ROOT / spec['derivation']['path'], spec['derivation']))
    record = derivation['native_recipes'][kind + '.py']
    case.assertEqual(len(record['steps']), count)
    raw = checked(ROOT / record['input']['path'], record['input'])
    expected = raw
    for row in record['steps']:
        case.assertEqual(expected.count(row['old'].encode()), row['count'])
        expected = expected.replace(row['old'].encode(), row['new'].encode())
    actual = checked(ROOT / RAW / (kind + '.py'), record['expected'])
    case.assertEqual(actual, expected)
    case.assertEqual(identity(actual), record['expected'])


def setUpModule():
    _PROVIDER.setUpModule()


def tearDownModule():
    _PROVIDER.tearDownModule()


class OrdinaryRemote(unittest.TestCase):
    def setUp(self):
        case = _PROVIDER.WaitContract('test_initial_wait_fields_and_success_preserve_capture_origin')
        case.setUp(); self.addCleanup(case.doCleanups)
        self.subject, self.deps = case.subject, case.deps
        self.spec = specification()
        self.windows = tuple(tuple(row) for row in self.spec['windows'])

    def test_exact_seventeen_recipe_steps_preserve_all_other_bytes(self):
        assert_recipe(self, 'remote', 17)

    def test_seven_windows_twenty_eight_reads_and_all_flash_boundaries(self):
        self.assertEqual(tuple(self.subject.WINDOWS), self.windows)
        expected = tuple((row['name'], row['address'], row['bytes']) for row in self.spec['read_plan'])
        self.assertEqual(tuple(self.subject.read_plan()), expected)
        self.assertEqual((len(expected), sum(row[2] for row in expected)), (28, 715858))
        self.assertEqual(sum(row[2] for row in self.windows), 1305)
        self.assertEqual(expected[6], ('before.sketch.1', 0x08110000, 27408))
        self.assertEqual(expected[22], ('after.sketch.1', 0x08110000, 27408))
        for start, prefix in ((7, 'first'), (14, 'second')):
            self.assertEqual(expected[start:start+7],
                tuple((prefix+'.'+name, address, size) for name, address, size in self.windows))
        self.assertEqual(self.spec['geometry']['flash_completed_after_indices'],
                         {'before_loader': 4, 'before_sketch': 6, 'after_sketch': 22, 'after_loader': 27})
        self.assertEqual((self.subject.SOURCE, self.subject.RUN_ID), (self.spec['source'], self.spec['run']))

    def test_ordinary_artifact_paths_absences_and_raw_package_separation(self):
        for kind in ('upload', 'capture'):
            value = _PROVIDER.ORACLE.bindings(kind)
            self.assertEqual(value, self.spec['bindings'][kind])
            getattr(self.subject, 'checked_'+kind+'_bindings')(self.deps, value)
            self.assertEqual(value['files']['sketch']['bytes'], 92944)
            self.assertTrue(value['files']['sketch']['path'].endswith('/ordinary-app-static01/build/app.ino.bin-zsk.bin'))
            if kind == 'upload':
                self.assertEqual(value['files']['raw']['bytes'], 92928)
                self.assertEqual(len(value['absent']), 14)
                self.assertEqual(value['absent'][-3:], [
                    '/home/arduino/sumox26_codex_build/'+self.spec['source']+'/app/sketch.'+x for x in ('yaml','yml','json')])
                wrong = copy.deepcopy(value); wrong['files']['raw'] = dict(value['files']['sketch'])
                with self.assertRaises(Exception): self.subject.checked_upload_bindings(self.deps, wrong)
            wrong = copy.deepcopy(value); wrong['files']['sketch']['bytes'] = 92928
            before = copy.deepcopy(wrong)
            with self.assertRaises(Exception): getattr(self.subject, 'checked_'+kind+'_bindings')(self.deps, wrong)
            self.assertEqual(wrong, before)
        self.assertEqual(_PROVIDER.ORACLE.ARGV, ['/usr/bin/arduino-cli','--config-file','/dev/null','upload','--fqbn',
            'arduino:zephyr:unoq:link_mode=static','--input-file',
            '/home/arduino/sumox26_codex_build/ordinary-app-static01/build/app.ino.bin',
            '/home/arduino/sumox26_codex_build/'+self.spec['source']+'/app'])

    def test_D207_source_owners_and_diagnostic_images_are_refused(self):
        for kind in ('upload', 'capture'):
            positive = _PROVIDER.ORACLE.bindings(kind)
            cases = [dict(positive, source_sha256='4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2'),
                     dict(positive, run_id='app-motor-const-4bc3a2e6-run01')]
            for size, digest in ((95368,'f15c7ce1f0ff5fea2d44d0b60f0607f9adae22b83ba5043fe4de5e2b21fa26f7'),
                                 (95520,'e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0')):
                value = copy.deepcopy(positive); value['files']['sketch'].update(bytes=size,sha256=digest); cases.append(value)
            for value in cases:
                self.assertNotEqual(value, positive); before=copy.deepcopy(value)
                with self.subTest(kind=kind), self.assertRaises(Exception):
                    getattr(self.subject, 'checked_'+kind+'_bindings')(self.deps, value)
                self.assertEqual(value, before)

    def test_initial_and_sample_waits_keep_original_six_hundred_second_budget(self):
        case = _PROVIDER.WaitContract('test_initial_wait_fields_and_success_preserve_capture_origin')
        case.setUp(); self.addCleanup(case.doCleanups)
        capture, events = case.gathered()
        capture.gather()
        self.assertEqual(case.clock.sleeps, [30,2])
        self.assertEqual(capture.started, 100.0)
        self.assertEqual(capture.budget(), 568)
        self.assertEqual(capture.report['counts'], {'commands':28,'reads':28,'requested_bytes':715858})
        self.assertEqual(capture.report['analysis']['coherence'],'UNPROVEN')


def load_tests(loader, tests, pattern):
    global _PROVIDER
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('D212 oracles require Python -I -B')
    _PROVIDER = private_oracle(); _PROVIDER.ORACLE = _PROVIDER.historical_oracle()
    suite = unittest.TestSuite()
    for cls in (_PROVIDER.ORACLE.Contract, _PROVIDER.ORACLE.Lifecycle,
                _PROVIDER.WaitContract, _PROVIDER.PublicWaitLifecycle, OrdinaryRemote):
        cls.__module__ = __name__; suite.addTests(loader.loadTestsFromTestCase(cls))
    if suite.countTestCases()!=47: raise AssertionError('42 inherited and5 ordinary remote cases required')
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)

