# Builds synthetic D136 cohorts using the established independent D073 CSV bytes.
# Binds each attempt to explicit historical configuration without consulting live config.
# Deferred public API tests keep logical wire evidence separate from physical trials.
from contextlib import ExitStack
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType
import unittest
from unittest import mock

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / 'AGENTS.md').is_file())
FIXTURES = str(ROOT / 'tests/tooling')
if FIXTURES not in sys.path:
    sys.path.insert(0, FIXTURES)
from countdown_analysis_fixture import BoundedReader, Bundle as CsvBundle, CLEAN_FRAME, U32, wire

TOOL = ROOT / 'tools/analyze_opener_abort.py'
VALUES = dict(TICK_US=1000, ATTACK_ENTER_TICKS=3, MODE_ARC_ENABLED=1,
              MODE_WAIT_ENABLED=1, LOG_HZ=25, LOG_EVENT_CAPACITY=4096,
              LOG_FRAME_WINDOW_MS=200000)
REPORT_KEYS = set(('schema_version input_status evidence_status timing_status mode source '
    'required_attempts qualified_attempts passing_attempts logical_failures minimum_elapsed_us '
    'maximum_elapsed_us attempts errors declared_physical_trials_status hardware_acceptance '
    'transport_verified common_attempt_verified producer_semantics_verified').split())
ATTEMPT_KEYS = set(('id qualification trace_status motors_allowed binding_status read_start_us '
    'read_end_us qualified_us handover_us applied_us elapsed_us cue handover_state '
    'logical_status timing_status terminal_detail terminal_value errors validation').split())
SOURCE_KEYS = set(('firmware_revision source_sha256 config config_sha256 flags '
                   'config_values binding_status').split())
ENDPOINTS = ('read_start_us', 'read_end_us', 'qualified_us', 'handover_us', 'applied_us', 'elapsed_us')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def packed(mode, phase=0, cause=1, mask=2, snapshot=False):
    return mode | phase << 3 | cause << 6 | mask << 8 | int(snapshot) << 15


def expected_cue(value):
    mode, phase, cause = value & 7, value >> 3 & 7, value >> 6 & 3
    mask, snapshot = value >> 8 & 127, bool(value & 32768)
    front, side = bool(mask & 7), bool(mask & 120)
    valid = False
    if mode == 3 and phase == 0:
        valid = cause == 1 and front or cause == 2 and not front and side and not snapshot
    elif not snapshot and mode in (1, 2, 6) and phase in (1, 2, 3):
        outer = bool(mask & (40 if mode == 2 else 80))
        valid = cause == 1 and phase != 1 and front or cause == 2 and outer and (phase == 1 or not front)
    elif not snapshot and mode in (4, 5) and phase in (2, 3):
        valid = cause == 1 and front
    elif not snapshot and mode == 6 and phase == 4:
        valid = cause == 2 and side
    if not valid:
        return None
    return dict(mode=mode, phase=phase, cause=cause, effective_mask=mask,
                snapshot_front_present=snapshot)


class Source:
    def __init__(self, directory, motors=True, **changes):
        self.path = Path(directory) / 'historical_config.h'
        self.values = dict(VALUES, **changes)
        self.motors = motors
        self.write()

    def canonical(self):
        declarations = ''.join('inline constexpr std::uint32_t ' + name + ' = ' + str(value) + 'U;\n'
                               for name, value in self.values.items())
        return ('#pragma once\n#include <cstdint>\nnamespace config {\n' + declarations + '}\n').encode()

    def write(self, raw=None):
        self.path.write_bytes(self.canonical() if raw is None else raw)
        return self

    def descriptor(self):
        return dict(firmware_revision='a' * 40, source_sha256='b' * 64,
                    config=self.path.name, config_sha256=sha(self.path.read_bytes()),
                    flags='-DMATCH=0 -DMOTORS_ALLOWED=' + str(int(self.motors)) + ' -DSUMOX_P5_ABORT_TIMING=1')


class Bundle(CsvBundle):
    def __init__(self, directory, source, index=0, mode=3, elapsed=1000, release=None):
        super().__init__(directory, index, release=release, mode=mode)
        self.motors = source.motors
        self.declarations.update({key: value for key, value in source.descriptor().items()
                                  if key in ('firmware_revision', 'source_sha256', 'config_sha256')})
        self.times = {0: self.summary['release_us'], 16: self.absolute(5200000),
                      17: self.absolute(5200010), 18: self.absolute(5200100),
                      19: self.absolute(5200100), 20: self.absolute(5200100 + elapsed)}
        phase = {1: 2, 2: 2, 3: 0, 4: 2, 5: 2, 6: 4}[mode]
        self.cue_value = packed(mode, phase, 2 if mode == 6 else 1, 16 if mode == 6 else 2)
        self.handover = 7 if mode == 6 else 6 if source.values['ATTACK_ENTER_TICKS'] == 1 else 5
        self.set_trace([0, 16, 17, 18, 19, 20]).write()

    def absolute(self, offset):
        return (self.summary['release_us'] + offset) & U32

    def timing_record(self, detail, time=None, value=None):
        if time is None:
            time = self.times.get(detail, self.times[18])
        if value is None:
            value = {0: 0x0205 if self.motors else 0x0201, 18: self.cue_value,
                     19: self.handover, 25: 5}.get(detail, 1)
        return dict(t_us=time, ordinal=0, kind=10, detail=detail, value=value)

    def set_trace(self, details):
        self.events = [dict(t_us=self.summary['release_us'], ordinal=0, kind=0,
                            detail=self.summary['mode'], value=0)]
        remaining = list(details)
        if remaining and remaining[0] == 0:
            self.events.append(self.timing_record(remaining.pop(0)))
        self.events.append(dict(t_us=self.absolute(5100000), ordinal=0, kind=1,
                                detail=self.summary['mode'], value=0))
        self.events.extend(self.timing_record(detail) for detail in remaining)
        return self.renumber()

    def renumber(self):
        for ordinal, event in enumerate(self.events):
            event['ordinal'] = ordinal
        return self

    def marker(self, detail):
        return next(event for event in self.events if event['kind'] == 10 and event['detail'] == detail)

    def ordinary(self, kind):
        return next(event for event in self.events if event['kind'] == kind)


def load_analyzer():
    spec = importlib.util.spec_from_file_location('d136_independent_public', TOOL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AbortAnalysisCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tools = str(ROOT / 'tools')
        sys.path.insert(0, tools)
        cls.addClassCleanup(lambda: sys.path.remove(tools))
        cls.validator = importlib.import_module('validate_csv_bundle')
        cls.module = load_analyzer()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='sumo-d136-synthetic-')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.path = self.directory / 'cohort.json'
        self.source = Source(self.directory)

    def document(self, bundles=(), mode=3):
        return dict(schema_version=1, mode=mode, source=self.source.descriptor(),
                    attempts=[bundle.entry() for bundle in bundles])

    def write_cohort(self, bundles=(), mode=3, document=None):
        value = self.document(bundles, mode) if document is None else document
        self.path.write_text(json.dumps(value), encoding='ascii')
        return self.path

    def analyze(self, bundles=None, mode=3, document=None, module=None):
        if bundles is not None or document is not None:
            self.write_cohort(() if bundles is None else bundles, mode, document)
        report = (module or self.module).analyze_cohort(self.path)
        self.assert_report(report)
        return report

    def assert_report(self, report):
        self.assertEqual(set(report), REPORT_KEYS)
        self.assertEqual(report['schema_version'], 1)
        self.assertEqual(report['required_attempts'], 10)
        self.assertIn(report['input_status'], ('VALID', 'INVALID'))
        self.assertIn(report['evidence_status'], ('COMPLETE', 'INCOMPLETE', 'INVALID'))
        self.assertIn(report['timing_status'], ('PASS', 'FAIL', 'NOT_QUALIFIED'))
        self.assertIn(report['declared_physical_trials_status'], ('ELIGIBLE', 'NOT_QUALIFIED'))
        for key in ('hardware_acceptance', 'transport_verified', 'common_attempt_verified', 'producer_semantics_verified'):
            self.assertIs(report[key], False)
        if report['source'] is not None:
            self.assertEqual(set(report['source']), SOURCE_KEYS)
            if report['source']['config_values'] is not None:
                self.assertEqual(set(report['source']['config_values']), set(VALUES))
        for attempt in report['attempts']:
            self.assertEqual(set(attempt), ATTEMPT_KEYS)
            self.assertTrue(attempt['motors_allowed'] is None or type(attempt['motors_allowed']) is bool)
            if attempt['cue'] is not None:
                self.assertEqual(set(attempt['cue']), {'mode', 'phase', 'cause', 'effective_mask', 'snapshot_front_present'})
        for errors in [report['errors']] + [a['errors'] for a in report['attempts']]:
            for error in errors:
                self.assertTrue({'code', 'message'} <= set(error))
                self.assertTrue(error['code'])
                self.assertTrue(error['message'].strip())

    def one(self, bundle, qualification='QUALIFIED', trace='COMPLETE'):
        report = self.analyze([bundle], bundle.summary['mode'])
        self.assertEqual(report['input_status'], 'VALID', report)
        self.assertEqual(len(report['attempts']), 1)
        attempt = report['attempts'][0]
        self.assertEqual((attempt['qualification'], attempt['trace_status']), (qualification, trace), attempt)
        self.assertEqual(report['qualified_attempts'], int(qualification == 'QUALIFIED'))
        self.assertEqual(report['evidence_status'], 'INVALID' if qualification == 'INVALID' else 'INCOMPLETE')
        self.assertEqual(report['timing_status'], 'NOT_QUALIFIED')
        return report, attempt

    def invalid_attempt(self, bundle, trace='INVALID'):
        report, attempt = self.one(bundle, 'INVALID', trace)
        for key in ENDPOINTS:
            self.assertIsNone(attempt[key], key)
        self.assertEqual(attempt['logical_status'], 'NOT_EVALUATED')
        self.assertEqual(attempt['timing_status'], 'NOT_EVALUATED')
        self.assertTrue(attempt['errors'])
        return report, attempt

    def invalid_input(self, document=None):
        report = self.analyze(document=document) if document is not None else self.analyze()
        self.assertEqual((report['input_status'], report['evidence_status'], report['timing_status']),
                         ('INVALID', 'INVALID', 'NOT_QUALIFIED'), report)
        self.assertIsNone(report['mode'])
        self.assertIsNone(report['source'])
        self.assertEqual(report['attempts'], [])
        for key in ('qualified_attempts', 'passing_attempts', 'logical_failures'):
            self.assertEqual(report[key], 0)
        for key in ('minimum_elapsed_us', 'maximum_elapsed_us'):
            self.assertIsNone(report[key])
        self.assertEqual(report['declared_physical_trials_status'], 'NOT_QUALIFIED')
        self.assertTrue(report['errors'])
        return report

    def ten(self, mode=3, elapsed=1000):
        return [Bundle(self.directory, self.source, index, mode, elapsed) for index in range(10)]

    def validated_then(self, action, expected_calls=1):
        module = load_analyzer()
        path = (ROOT / 'tools/validate_csv_bundle.py').resolve()
        dependencies = []
        for name, value in vars(module).items():
            if (isinstance(value, ModuleType) and callable(getattr(value, 'validate_bundle', None))
                    and isinstance(getattr(value, '__file__', None), str) and Path(value.__file__).resolve() == path):
                dependencies.append((value, 'validate_bundle'))
            elif (callable(value) and getattr(value, '__name__', None) == 'validate_bundle'
                  and getattr(value, '__code__', None) is not None and Path(value.__code__.co_filename).resolve() == path):
                dependencies.append((module, name))
        self.assertEqual(len(dependencies), 1, 'One unchanged public validator dependency')
        owner, name = dependencies[0]
        original, accepted_reports = getattr(owner, name), []

        def boundary(*args, **kwargs):
            accepted = original(*args, **kwargs)
            accepted_reports.append(accepted)
            action(accepted)
            return accepted

        with mock.patch.object(owner, name, boundary):
            report = self.analyze(module=module)
        self.assertEqual(len(accepted_reports), expected_calls)
        self.assertEqual([a['validation'] for a in report['attempts']], accepted_reports)
        return report
