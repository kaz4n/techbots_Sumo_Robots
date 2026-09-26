# Observes one unchanged inherited Windows private-loading test without repairs.
# Captures original read-handle locals in memory to distinguish stamp predicates.
# Frozen single execution, preserved verdict, no altered guards or device calls.
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
FREEZE = RAW / 'windows_stamp_diagnostic_freeze01.json'
OWNER = RAW / 'windows_stamp_diagnostic01'
ORACLE = 'tests/tooling/test_motor_const_compile.py'
SUBJECT = 'tools/compile_motor_const.py'
METHOD = 'test_private_loading_preserves_modules_defaults_original_paths_and_hard_pins'
STAMP_FIELDS = ('dev', 'ino', 'mode', 'nlink', 'size', 'mtime_ns', 'file_attributes', 'ctime_ns')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify_inputs(freeze):
    changed = []
    for name, pin in freeze['files'].items():
        raw = (ROOT / name).read_bytes()
        if {'bytes': len(raw), 'sha256': sha(raw)} != pin:
            changed.append(name)
    return changed


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def selected_test():
    module = types.ModuleType('_d203_stamp_diagnostic_oracle')
    module.__file__ = str(ROOT / ORACLE)
    exec(compile((ROOT / ORACLE).read_bytes(), module.__file__, 'exec'), module.__dict__)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    cases = list(flatten(suite))
    if len(cases) != 69 or suite.countTestCases() != 69:
        raise AssertionError('Expected the unchanged complete 69-method caller suite')
    selected = [case for case in cases if case._testMethodName == METHOD]
    if len(selected) != 1:
        raise AssertionError('Expected exactly one unchanged inherited method')
    case = selected[0]
    code = getattr(type(case), METHOD).__code__
    if code.co_name != METHOD or Path(code.co_filename) != ROOT / 'tests/tooling/test_app_motor_observe_compile.py':
        raise AssertionError('Selected method is not the unchanged inherited code')
    return case, {'id': case.id(), 'file': code.co_filename, 'first_line': code.co_firstlineno,
                  'suite_count': len(cases), 'selected_count': len(selected)}


def labelled_stamps(path, values):
    if values is None:
        return None
    names = [str(item) for item in (*reversed(path.parents), path)]
    return [{'path': names[index] if index < len(names) else None, 'stamp': list(stamp)}
            for index, stamp in enumerate(values)]


def snapshot(frame):
    local = frame.f_locals
    path = local.get('path')
    result = {'line': frame.f_lineno, 'relative': local.get('relative'), 'path': str(path)}
    for name in ('before', 'after'):
        if name in local:
            result[name] = labelled_stamps(path, local[name])
    for name in ('opened', 'closed', 'path_identity', 'handle_identity'):
        if name in local:
            result[name] = list(local[name])
    raw = local.get('raw')
    if isinstance(raw, bytes):
        result['raw_bytes'] = len(raw)
        result['raw_sha256'] = sha(raw)
    return result


class ReadTrace:
    def __init__(self):
        self.target = os.path.normcase(str(ROOT / SUBJECT))
        self.reads = []
        self.frames = {}
        self.errors = []

    def error(self, error):
        if not self.errors:
            self.errors.append({'type': type(error).__name__, 'message': str(error)[:2048]})

    def global_trace(self, frame, event, arg):
        try:
            if event == 'call' and frame.f_code.co_name == '_read_handle' and os.path.normcase(frame.f_code.co_filename) == self.target:
                if len(self.reads) >= 24:
                    raise RuntimeError('Diagnostic read count exceeds its fixed bound')
                record = {'call': snapshot(frame), 'exceptions': []}
                self.reads.append(record)
                self.frames[id(frame)] = record
                return self.local_trace
        except BaseException as error:
            self.error(error)
        return None

    def local_trace(self, frame, event, arg):
        try:
            record = self.frames.get(id(frame))
            if record is None:
                return None
            if event == 'exception':
                if len(record['exceptions']) >= 8:
                    raise RuntimeError('Diagnostic exception count exceeds its fixed bound')
                kind, value, unused_traceback = arg
                record['exceptions'].append({'type': kind.__name__, 'message': str(value)[:2048],
                                             'locals': snapshot(frame)})
            elif event == 'return':
                record['return'] = snapshot(frame)
                record['returned_bytes'] = isinstance(arg, bytes)
                record['return_bytes'] = len(arg) if isinstance(arg, bytes) else None
                self.frames.pop(id(frame), None)
        except BaseException as error:
            self.error(error)
        return self.local_trace


def predicate_summary(observation):
    before, after = observation.get('before'), observation.get('after')
    opened, closed = observation.get('opened'), observation.get('closed')
    path, handle = observation.get('path_identity'), observation.get('handle_identity')
    size = observation.get('raw_bytes')
    return {
        'before_equals_after': before == after if before is not None and after is not None else None,
        'opened_equals_closed': opened == closed if opened is not None and closed is not None else None,
        'path_identity_equals_handle_identity': path == handle if path is not None and handle is not None else None,
        'raw_length_equals_before_size': size == before[-1]['stamp'][4] if size is not None and before else None,
        'raw_length_at_most_65536': size <= 65536 if size is not None else None,
    }


def save_json(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def main():
    if os.name != 'nt' or not sys.dont_write_bytecode or not sys.flags.isolated or len(sys.argv) != 1:
        raise RuntimeError('Run exactly once on Windows with Python -I -B and no arguments')
    if sys.gettrace() is not None:
        raise RuntimeError('Existing tracing must not be replaced')
    freeze = json.loads(FREEZE.read_bytes())
    if verify_inputs(freeze):
        raise AssertionError('Frozen diagnostic input changed before selection')
    case, selection = selected_test()
    OWNER.mkdir(exist_ok=False)
    observer = ReadTrace()
    output = io.StringIO()
    runner = unittest.TextTestRunner(stream=output, verbosity=2)
    sys.settrace(observer.global_trace)
    try:
        result = runner.run(unittest.TestSuite([case]))
    finally:
        sys.settrace(None)
    # The single test's class and instance cleanups have completed before writes.
    changed = verify_inputs(freeze)
    coverage_errors = []
    if not observer.reads:
        coverage_errors.append('No original read-handle call was observed')
    if result.wasSuccessful() and len(observer.reads) != 6:
        coverage_errors.append('Successful two-load test must observe exactly six original reads')
    for record in observer.reads:
        for item in record['exceptions']:
            item['original_guard_predicates'] = predicate_summary(item['locals'])
        if 'return' in record:
            record['return_guard_predicates'] = predicate_summary(record['return'])
    report = {
        'schema': 'd203-unchanged-windows-stamp-diagnostic-v1',
        'selection': selection, 'tests_run': result.testsRun,
        'was_successful': result.wasSuccessful(),
        'failures': [{'id': item.id(), 'traceback': trace} for item, trace in result.failures],
        'errors': [{'id': item.id(), 'traceback': trace} for item, trace in result.errors],
        'skipped': [{'id': item.id(), 'reason': reason} for item, reason in result.skipped],
        'stamp_fields': STAMP_FIELDS, 'reads': observer.reads, 'observer_errors': observer.errors,
        'coverage_errors': coverage_errors,
        'unclosed_observed_frames': len(observer.frames), 'changed_inputs': changed,
        'first_failure': freeze['first_failure'],
        'limitations': ['No original guard, return, test assertion or method body was changed.',
                       'Trace observation changes timing; success is non-reproduction, not a cause attribution.',
                       'Original first failure remains authoritative evidence and is not relabelled.'],
    }
    evidence = output.getvalue().encode('utf-8')
    with (OWNER / 'unittest.txt').open('xb') as stream:
        stream.write(evidence)
    report['unittest_bytes'] = len(evidence)
    report['unittest_sha256'] = sha(evidence)
    save_json(OWNER / 'observation.json', report)
    print(json.dumps({'tests_run': result.testsRun, 'was_successful': result.wasSuccessful(),
                      'observed_reads': len(observer.reads), 'observer_errors': observer.errors,
                      'coverage_errors': coverage_errors, 'changed_inputs': changed, 'owner': str(OWNER)}))
    if observer.errors or observer.frames or coverage_errors or changed or result.testsRun != 1 or result.skipped:
        return 2
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
