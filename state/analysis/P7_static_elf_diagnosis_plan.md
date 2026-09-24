# D145 proposed read-only diagnosis of D144's rejected ELF

No execution authority from this draft. D144 is terminal and its compiler GO is
consumed. Reuse the unchanged,80-method-tested D143 reader for exactly one read of
the170616-byte final ELF. Keep the old run/receipts, frozen parser and tests intact.
The new local directory is diagnosis-v1, not the existing run directory. No
inventory/query/compiler/remote claim/layout/upload/reset/delete action is called.

The following one-shot Python composition is executed with -B from the repository
only after separate inspection and coordinator GO. It loads captured hash-pinned
runner source, verifies its17 inputs, restores main's exact ADB checks and
run_probe's fresh-path admission, and constructs Probe without executing its
compile workflow. Historical identity/Claim/FileRecords are taken only from the
three literal-hash receipts below. The existing helper verifies current boot,
directory identities and stable file metadata; read_elf validates the complete
response, file identity, bytes and hash. Local pins/stage checks run afterward
even on read failure. Only an accepted byte stream is saved, exclusively.

This is a literal composition of already tested functions, not a new general
transport tool. Separate inspection precedes execution; the native read itself
supplies the actual byte-identity evidence. No new parser expectation is introduced.

```python
from pathlib import Path
import hashlib
import os
import sys
import types

root = Path.cwd().resolve()
if str(root).casefold() != r'C:\Users\narut\OneDrive\Desktop\Project\techbots_Sumo_Robots'.casefold():
    raise ValueError('Wrong repository')
if not sys.dont_write_bytecode:
    raise ValueError('Python -B required')
rawdir = root / 'state/analysis/P7_static_link_probe_raw'
runner_path = rawdir / 'run_static_probe.py'
runner_hash = '983e86d7eb68f437c50b4b790e96ca4520e092abe53e4d29e8ffe1a97502b208'
source = runner_path.read_bytes()
if hashlib.sha256(source).hexdigest() != runner_hash:
    raise ValueError('Runner source drift before load')
r = types.ModuleType('fixed_d145_reader')
r.__file__ = str(runner_path)
exec(compile(source, str(runner_path), 'exec'), r.__dict__)
r.safe_path(runner_path, 'file')
inputs = r.verify_inputs()
os.environ.update(SUMO_TRANSPORT='adb', SUMO_ADB_SERIAL=r.BOARD, SUMO_ADB_EXECUTABLE=r.ADB)
r.require(os.environ['SUMO_TRANSPORT'] == 'adb' and os.environ['SUMO_ADB_SERIAL'] == '2629958581', 'Wrong target')
r.safe_path(Path(r.ADB), 'file')
r.require(r.sha(Path(r.ADB).read_bytes()) == r.ADB_SHA, 'ADB executable drift')
board = r.load_module('fixed_d145_board', 'tools/board_tool.py', inputs)
run_id = 'f0220228320c4b2aa20c3e5e8264c813'
out = rawdir / 'diagnosis-v1'
r.validate_request(True, run_id, out, board.remote)
probe = r.Probe(run_id, out, board.remote, inputs)
receipt_hashes = {
    '0001': '534da2e8de0d846d850288c956f3c5a51b13f641b3329c6475dc5857930f32a7',
    '0009': '3f57a292649a0d20ddf88daf3f80a8b3d75a90e18460f3c7208c1eb17c6b45d4',
    '0021': 'c44e85bcb22dcb69c405b1bddeea74f7c30e4c9e3f1444370995f806162e3127',
}
observed = {}
for number, expected in receipt_hashes.items():
    path = rawdir / 'runs' / run_id / (number + '.json')
    r.safe_path(path, 'file')
    data = path.read_bytes()
    r.require(r.sha(data) == expected, 'Historical receipt changed')
    observed[number] = r.decode(r.decode(data)['stdout'])['data']
probe.check_inventory(observed['0001'])
probe.check_claim(observed['0009']['claim'])
probe.claim = observed['0009']['claim']
r.checked_files(observed['0021']['files'])
probe.check_claim(observed['0021']['claim'])
probe.files = observed['0021']['files']
expected_file = probe.files['build/app.ino.elf']
r.require(expected_file['identity']['bytes'] == 170616 and expected_file['sha256'] ==
          '5cc2dfdec597f1421d6250936569bc113542723c362786f23be62834b5ba0386', 'Wrong ELF baseline')
out.mkdir(mode=0o700)
r.write_json(out / 'inputs.json', dict(runner_sha256=runner_hash, pins=r.PINS,
             receipt_sha256=receipt_hashes, file=expected_file, claim=probe.claim), exclusive=True)
failure = None
payload = None
try:
    payload = probe.read_elf()
except Exception as error:
    failure = (error, probe.phase)
post = probe.postchecks(local_only=True)
failure = failure or post
try:
    r.safe_path(runner_path, 'file')
    r.require(r.sha(runner_path.read_bytes()) == runner_hash, 'Runner changed after read')
except Exception as error:
    probe.postcheck_errors.append(dict(check='runner_source', **r.error_record(error)))
    failure = failure or (error, 'runner_source')
if failure is not None:
    try:
        r.write_json(out / 'result.json', dict(status='READ_FAILED', phase=failure[1],
                     error=r.error_record(failure[0]), postcheck_errors=probe.postcheck_errors), exclusive=True)
    except OSError:
        pass
    raise failure[0]
r.require(probe.sequence == 1 and probe.query_attempts == 0 and probe.compile_attempts == 0, 'Unexpected dispatch count')
with (out / 'app.ino.elf').open('xb') as stream:
    stream.write(payload)
r.write_json(out / 'result.json', dict(status='DIAGNOSTIC_ELF_COLLECTED', source_sha256=r.SOURCE,
             run_id=run_id, file=expected_file, read_attempts=probe.sequence,
             query_attempts=0, compile_attempts=0, postcheck_errors=[]), exclusive=True)
```

The three environment settings exist only in this new Python process; they do not
alter the invoking shell or persistent configuration. The original numbered
read receipt retains actual argv/timeout/return code/stdout/stderr. No automatic
retry follows any failure. Post-hash/read/persistence failures cannot produce an
accepted diagnostic artifact result. Missing hardware is a real failure.

After collection, use existing local readelf/nm/Arm objdump read-only. Identify
the exact symbols violating D142's explicit bind/type/visibility rule; retain
compact source-bound output and primary ABI/toolchain evidence. Do not assume
that symbol compatibility establishes layout, packaging, entry/ABI or runtime.
Any changed admission requires a separately reviewed scope and independent tests;
this diagnostic never reruns the compiler or edits a frozen validator.
