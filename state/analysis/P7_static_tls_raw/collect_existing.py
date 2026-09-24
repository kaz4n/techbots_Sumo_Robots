# Collects fixed existing TLS provenance through a reviewed read-only composition.
# Preserves original failed admission while identifying its actual linked inputs.
# Independently inspected before execution; no reusable build or deployment path.
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
r = types.ModuleType('fixed_d146_reader')
r.__file__ = str(runner_path)
exec(compile(source, str(runner_path), 'exec'), r.__dict__)
r.safe_path(runner_path, 'file')
inputs = r.verify_inputs()
os.environ.update(SUMO_TRANSPORT='adb', SUMO_ADB_SERIAL=r.BOARD, SUMO_ADB_EXECUTABLE=r.ADB)
r.require(os.environ['SUMO_TRANSPORT'] == 'adb' and os.environ['SUMO_ADB_SERIAL'] == '2629958581', 'Wrong target')
r.safe_path(Path(r.ADB), 'file')
r.require(r.sha(Path(r.ADB).read_bytes()) == r.ADB_SHA, 'ADB executable drift')
board = r.load_module('fixed_d146_board', 'tools/board_tool.py', inputs)
run_id = 'f0220228320c4b2aa20c3e5e8264c813'
out = root / 'state/analysis/P7_static_tls_raw/observed'
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
remote_path = root / 'state/analysis/P7_static_tls_raw/read_existing.py'
remote_sha = '48ca3cdf0ef2eda317ceb58cd841ee53fa21ff92336abfd2212005cc6b4f8b6e'
r.safe_path(remote_path, 'file')
remote_source = remote_path.read_bytes()
r.require(r.sha(remote_source) == remote_sha, 'Diagnostic source drift')
boot = inputs[r.RAW + 'static_bootstrap.txt'].decode().replace('@HELPER_SHA256@', remote_sha)
import base64
import zlib
out.mkdir(mode=0o700)
r.write_json(out / 'inputs.json', dict(runner_sha256=runner_hash, pins=r.PINS,
             remote_sha256=remote_sha, receipt_sha256=receipt_hashes,
             files=probe.files, claim=probe.claim), exclusive=True)
failure = None
packet = None
try:
    probe.phase = 'read_tls_provenance'
    token = lambda value: r.encoded(r.canonical(value))
    argv = ['python3', '-I', '-B', '-c', boot, r.encoded(remote_source, True),
            probe.helper_encoded, token(probe.claim), token(probe.files)]
    result = probe.dispatch(r.BOARD, argv, capture=True, timeout=60)
    r.require(len(result.stdout.encode()) <= 2097152 and not result.stderr, 'Oversized output or diagnostic stderr')
    packet = r.decode(result.stdout)
    r.require(packet['scope'] == 'READ_ONLY_TLS_PROVENANCE', 'Wrong response scope')
    r.identity(packet['identity'])
    r.require(packet['identity'] == probe.first_identity, 'Remote identity drift')
    probe.check_claim(packet['claim'])
    r.checked_files(packet['artifact_postcheck'])
    r.require(packet['artifact_postcheck'] == probe.files, 'Artifact postcheck drift')
    r.checked_file(packet['loader'], 16777216)
    r.require(packet['loader']['sha256'] == '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd', 'Loader drift')
    names = {'tls-syms.S', 'app.ino.map', 'app.ino_debug.elf', 'app.ino_temp.elf'}
    if 'tls-syms.S.o' in packet['files']:
        names.add('tls-syms.S.o')
        r.require('object_unresolved' not in packet, 'Contradictory object status')
    else:
        r.require(packet.get('object_unresolved') == 'Fixed candidate not named in map; no alternative path read', 'Missing object status')
    r.require(set(packet['files']) == names, 'Wrong collected file set')
    decoded = {}
    for name, item in packet['files'].items():
        limit = 65536 if name == 'tls-syms.S' else (1048576 if name == 'tls-syms.S.o' else 16777216)
        r.checked_file(item['record'], limit)
        if name.startswith('app.ino'):
            r.require(item['record'] == probe.files['build/' + name], 'Original file drift')
        if name == 'app.ino_temp.elf':
            r.require(item.get('same_bytes_as') == 'app.ino_debug.elf' and
                      item['record']['sha256'] == packet['files']['app.ino_debug.elf']['record']['sha256'], 'False content alias')
            continue
        encoded = item['zlib_base64']
        compressed = base64.b64decode(encoded, validate=True)
        r.require(base64.b64encode(compressed).decode() == encoded, 'Noncanonical payload')
        decoder = zlib.decompressobj()
        data = decoder.decompress(compressed, limit + 1)
        r.require(len(data) <= limit and decoder.eof and not decoder.unused_data and
                  not decoder.unconsumed_tail, 'Invalid compressed payload')
        r.require(len(data) == item['record']['identity']['bytes'] and
                  r.sha(data) == item['record']['sha256'], 'Payload identity mismatch')
        decoded[name] = data
except Exception as error:
    failure = (error, probe.phase)
post = probe.postchecks(local_only=True)
failure = failure or post
for path, expected in ((runner_path, runner_hash), (remote_path, remote_sha)):
    try:
        r.safe_path(path, 'file')
        r.require(r.sha(path.read_bytes()) == expected, 'Diagnostic source changed after read')
    except Exception as error:
        probe.postcheck_errors.append(dict(check=str(path), **r.error_record(error)))
        failure = failure or (error, 'source_postcheck')
if failure is not None:
    try:
        r.write_json(out / 'result.json', dict(status='READ_FAILED', phase=failure[1],
                     error=r.error_record(failure[0]), postcheck_errors=probe.postcheck_errors), exclusive=True)
    except OSError:
        pass
    raise failure[0]
r.require(probe.sequence == 1 and probe.query_attempts == 0 and probe.compile_attempts == 0, 'Unexpected dispatch count')
for name, data in decoded.items():
    with (out / name).open('xb') as stream:
        stream.write(data)
r.write_json(out / 'result.json', dict(status='DIAGNOSTIC_TLS_FILES_COLLECTED',
             source_sha256=r.SOURCE, run_id=run_id, files={name: item['record'] for name, item in packet['files'].items()},
             object_unresolved=packet.get('object_unresolved'), read_attempts=probe.sequence,
             query_attempts=0, compile_attempts=0, postcheck_errors=[]), exclusive=True)
print('DIAGNOSTIC_TLS_FILES_COLLECTED; original validation rejection unchanged')
