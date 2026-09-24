# Checks the one existing D144 packet through the separately tested D147 interface.
# Keeps structural evidence distinct from production admission and MCU execution.
# Reviewed as a fixed read-only composition before its single recorded invocation.
from pathlib import Path
import hashlib
import os
import subprocess
import sys
import types

ROOT = Path.cwd().resolve()
RAW = ROOT / 'state/analysis/P7_static_link_probe_raw'
RUN = 'f0220228320c4b2aa20c3e5e8264c813'
RUNNER_SHA = '983e86d7eb68f437c50b4b790e96ca4520e092abe53e4d29e8ffe1a97502b208'
REMOTE_SHA = 'c6099f6d29ebdc400df5280032a8b5b0d229a003c594033a920f459316e2b8e7'
NATIVE_SHA = 'cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0'
BASE_SHA = 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368'
TLS_SHA = '68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70'
LOADER_SHA = '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
RECEIPTS = {
    '0001': '534da2e8de0d846d850288c956f3c5a51b13f641b3329c6475dc5857930f32a7',
    '0009': '3f57a292649a0d20ddf88daf3f80a8b3d75a90e18460f3c7208c1eb17c6b45d4',
    '0021': 'c44e85bcb22dcb69c405b1bddeea74f7c30e4c9e3f1444370995f806162e3127',
}


def prepare():
    if str(ROOT).casefold() != r'C:\Users\narut\OneDrive\Desktop\Project\techbots_Sumo_Robots'.casefold():
        raise ValueError('Wrong repository')
    if not sys.dont_write_bytecode:
        raise ValueError('Python -B required')
    path = RAW / 'run_static_probe.py'
    source = path.read_bytes()
    if hashlib.sha256(source).hexdigest() != RUNNER_SHA:
        raise ValueError('Runner changed before load')
    r = types.ModuleType('fixed_d148_runner')
    r.__file__ = str(path)
    exec(compile(source, str(path), 'exec'), r.__dict__)
    r.safe_path(path, 'file')
    inputs = r.verify_inputs()
    os.environ.update(SUMO_TRANSPORT='adb', SUMO_ADB_SERIAL=r.BOARD, SUMO_ADB_EXECUTABLE=r.ADB)
    r.safe_path(Path(r.ADB), 'file')
    r.require(r.sha(Path(r.ADB).read_bytes()) == r.ADB_SHA, 'ADB changed')
    board = r.load_module('fixed_d148_board', 'tools/board_tool.py', inputs)
    out = RAW / 'native_actual'
    r.validate_request(True, RUN, out, board.remote)
    probe = r.Probe(RUN, out, board.remote, inputs)
    old = {}
    for number, digest in RECEIPTS.items():
        path = RAW / 'runs' / RUN / (number + '.json')
        r.safe_path(path, 'file')
        data = path.read_bytes()
        r.require(r.sha(data) == digest, 'Historical receipt changed')
        old[number] = r.decode(r.decode(data)['stdout'])['data']
    probe.check_inventory(old['0001'])
    probe.check_claim(old['0009']['claim'])
    probe.claim = old['0009']['claim']
    r.checked_files(old['0021']['files'])
    probe.check_claim(old['0021']['claim'])
    probe.files = old['0021']['files']
    return r, probe, inputs, out


def captured(r):
    hashes = {'run_static_probe.py': RUNNER_SHA, 'read_native_actual.py': REMOTE_SHA,
              'static_native_artifacts.py': NATIVE_SHA, 'static_artifacts.py': BASE_SHA}
    data = {}
    for name, digest in hashes.items():
        path = RAW / name
        r.safe_path(path, 'file')
        data[name] = path.read_bytes()
        r.require(r.sha(data[name]) == digest, 'Scoped source drift: ' + name)
    return hashes, data


def check_packet(r, probe, packet):
    r.keys(packet, 'scope identity claim loader tls_source validator_sha256 base_sha256 files report error postcheck_errors')
    r.require(packet['scope'] == 'READ_ONLY_NATIVE_TLS_VALIDATION', 'Wrong scope')
    r.identity(packet['identity'])
    r.require(packet['identity'] == probe.first_identity, 'Board identity drift')
    probe.check_claim(packet['claim'])
    r.checked_files(packet['files'])
    r.require(packet['files'] == probe.files, 'Artifact drift')
    for name, limit, digest in [('loader', 16777216, LOADER_SHA), ('tls_source', 65536, TLS_SHA)]:
        r.checked_file(packet[name], limit)
        r.require(packet[name]['sha256'] == digest, 'Installed native input drift')
    r.require(packet['validator_sha256'] == NATIVE_SHA and packet['base_sha256'] == BASE_SHA,
              'Wrong validator sources')
    r.require(packet['error'] is None and packet['postcheck_errors'] == [],
              'Native validator or remote postcheck rejected actual artifacts')
    report = packet['report']
    r.keys(report, 'status entry flash ram data_copy bss_zero sections weak_undefined artifacts native_tls')
    r.require(report['status'] == 'STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS', 'Wrong native status')
    values = {'_TLS_MODULE_BASE_': 8, '_rand_next': 8, 'z_tls_current': 16,
              'errno': 20, '_strtok_last': 24, '_localtime_buf': 28}
    expected = dict(source_sha256=TLS_SHA, loader_sha256=LOADER_SHA,
                    symbols=[dict(name=name, value=values[name], size=0, bind=1, type=6,
                                  other=0, section=65521) for name in sorted(values)])
    r.require(report['native_tls'] == expected, 'Unexpected native TLS report')
    # This local projection only reuses the frozen schema/bounds check. It is never
    # saved, returned to a production consumer, or treated as old admission status.
    common = {key: value for key, value in report.items() if key != 'native_tls'}
    common['status'] = 'STATIC_LAYOUT_PACKAGE_PASS'
    r.checked_layout(common, probe.files)


def main():
    r, probe, inputs, out = prepare()
    hashes, data = captured(r)
    boot = inputs[r.RAW + 'static_bootstrap.txt'].decode().replace('@HELPER_SHA256@', REMOTE_SHA)
    token = lambda value: r.encoded(r.canonical(value))
    argv = ['python3', '-I', '-B', '-c', boot, r.encoded(data['read_native_actual.py'], True),
            probe.helper_encoded, token(probe.claim), token(probe.files),
            r.encoded(data['static_native_artifacts.py'], True), r.encoded(data['static_artifacts.py'], True)]
    line = subprocess.list2cmdline([r.ADB, '-s', r.BOARD, 'shell', '-T', r.shlex.join(argv)])
    units = len(line.encode('utf-16-le')) // 2 + 1
    r.require(units <= 30000, 'Read composition exceeds Windows command limit')
    out.mkdir(mode=0o700)
    r.write_json(out / 'inputs.json', dict(pins=r.PINS, scoped_sources=hashes, receipts=RECEIPTS,
                 files=probe.files, claim=probe.claim, command_utf16_units=units), exclusive=True)
    failure, packet = None, None
    try:
        probe.installed_pins()
        probe.source()
        probe.phase = 'native_validation'
        reply = probe.dispatch(r.BOARD, argv, capture=True, timeout=60)
        r.require(not reply.stderr and len(reply.stdout.encode()) <= 1048576, 'Invalid native output')
        packet = r.decode(reply.stdout)
        check_packet(r, probe, packet)
    except Exception as error:
        failure = (error, probe.phase)
    # Every available final check runs independently, including after rejection.
    for method in (probe.installed_pins, probe.source):
        try:
            method()
        except Exception as error:
            probe.postcheck_errors.append(dict(check=method.__name__, **r.error_record(error)))
            failure = failure or (error, probe.phase)
    post = probe.postchecks(local_only=True)
    failure = failure or post
    try:
        captured(r)
    except Exception as error:
        probe.postcheck_errors.append(dict(check='scoped_sources', **r.error_record(error)))
        failure = failure or (error, 'scoped_sources')
    result = dict(status='NATIVE_STRUCTURE_FAILED' if failure else 'NATIVE_STRUCTURE_VALIDATED',
                  source_sha256=r.SOURCE, run_id=RUN, query_attempts=probe.query_attempts,
                  compile_attempts=probe.compile_attempts, read_commands=probe.sequence,
                  packet=packet, postcheck_errors=probe.postcheck_errors)
    if failure:
        result.update(phase=failure[1], error=r.error_record(failure[0]))
    r.write_json(out / 'result.json', result, exclusive=True)
    if failure:
        raise failure[0]
    r.require(probe.sequence == 5 and probe.query_attempts == probe.compile_attempts == 0,
              'Unexpected command counts')
    print('NATIVE_STRUCTURE_VALIDATED; original D144 rejection and production policy unchanged')


if __name__ == '__main__':
    main()
