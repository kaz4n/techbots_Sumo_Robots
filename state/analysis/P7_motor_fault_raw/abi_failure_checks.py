# Exercises the reviewed file-only reader's failure-evidence requirements in memory.
# No board command, firmware operation or temporary filesystem output is allowed.
# Root-authored controlled checks supplement the separate source review, not a gate.
import ast
import base64
import copy
import hashlib
import io
import json
from pathlib import Path
import types

RAW = Path(__file__).resolve().parent
READER = RAW / 'inspect_active_abi.py'
ns = {'__file__': str(READER), '__name__': 'controlled_reader'}
exec(compile(READER.read_bytes(), str(READER), 'exec'), ns)
checks = []


def closure_case(name, reply, error=None, drift=False):
    written = {}
    def transport(*args):
        if error is not None:
            raise error
        return types.SimpleNamespace(stdout=reply, stderr=b''), None
    fake = types.SimpleNamespace(CompileOnce=types.SimpleNamespace(transport=transport),
        decode=json.loads, write=lambda path, value: written.update({path.name: copy.deepcopy(value)}),
        sha=lambda raw: 'changed' if drift and raw == b'B' else hashlib.sha256(raw).hexdigest())
    class MemoryRoot:
        def __truediv__(self, name):
            return types.SimpleNamespace(read_bytes=lambda: name.encode())
    globals_ = {**ns, 'ROOT': MemoryRoot()}
    observe = types.FunctionType(ns['observe'].__code__, globals_)
    caught = None
    try:
        observe(fake, None, ['file-only'], {k: hashlib.sha256(k.encode()).hexdigest() for k in 'ABC'})
    except Exception as exception:
        caught = exception
    closure = written['local_result.json']
    assert len(closure['final_checks']) == 3
    failed = error is not None or reply == b'{' or b'FAILED' in reply or drift
    assert (closure['status'] == 'FAILED') == failed
    assert (caught is not None) == failed
    if error is not None:
        assert caught is error and closure['first_error']['message'] == str(error)
    if drift:
        assert closure['final_checks'][1]['status'] == 'FAILED'
        assert closure['final_checks'][2]['status'] == 'PASS'
    if b'FAILED' in reply:
        assert written['result.json']['status'] == 'FAILED'
    checks.append(name)


def stream_case(name, broken_seek=False, broken_read=False, execution_error=False):
    outputs = [b'\xffstdout', b'\xfestderr']
    class Stream(io.BytesIO):
        def __init__(self):
            self.index = 2 - len(outputs)
            super().__init__(outputs.pop(0))
        def seek(self, *args):
            if self.index == 0 and broken_seek:
                raise OSError('stdout seek failed')
            return super().seek(*args)
        def read(self, *args):
            if self.index == 0 and broken_read:
                raise OSError('stdout read failed')
            return super().read(*args)
    original = RuntimeError('original execution failure')
    def wait(*args):
        if execution_error:
            raise original
        return {'returncode': 0, 'reaped': True, 'timed_out': False}
    tree = ast.parse(ns['REMOTE_READ'])
    funcs = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'command'], type_ignores=[])
    env = {'tempfile': types.SimpleNamespace(TemporaryFile=Stream), 'time': types.SimpleNamespace(time=lambda: 0),
           'subprocess': types.SimpleNamespace(DEVNULL=None, Popen=lambda *a, **kw: object()),
           'ENV': {}, 'output_limit': lambda: None, 'wait_child': wait, 'base64': base64,
           'result': {'commands': []}}
    exec(compile(funcs, '<controlled-command>', 'exec'), env)
    caught = None
    try:
        env['command'](['file-only'])
    except Exception as exception:
        caught = exception
    record = env['result']['commands'][0]
    assert base64.b64decode(record['stderr_base64']) == b'\xfestderr'
    if broken_seek or broken_read:
        assert record['stream_errors'][0]['stream'] == 'stdout'
    else:
        assert base64.b64decode(record['stdout_base64']) == b'\xffstdout'
    if execution_error:
        assert caught is original and record['error']['message'] == str(original)
    assert caught is not None  # Nonempty stderr is an explicit failed observation.
    checks.append(name)


success = json.dumps({'status': 'OBSERVED', 'commands': [None] * 5}).encode()
closure_case('successful closure', success)
closure_case('transport error still closes all inputs', b'', RuntimeError('transport'))
closure_case('malformed JSON still closes all inputs', b'{')
closure_case('failed remote packet retained before closure', b'{"status":"FAILED","commands":[]}')
closure_case('local drift fails and continues later checks', success, drift=True)
closure_case('transport error retained through later drift', b'', RuntimeError('first'), drift=True)
stream_case('non-UTF8 preserves both exact streams')
stream_case('stdout seek failure preserves stderr and execution error', broken_seek=True, execution_error=True)
stream_case('stdout read failure preserves stderr and execution error', broken_read=True, execution_error=True)
print(json.dumps({'status': 'PASS', 'checks': checks, 'native_calls': 0,
                  'reader_sha256': hashlib.sha256(READER.read_bytes()).hexdigest()}, indent=2))
