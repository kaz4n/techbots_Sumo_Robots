# Compares existing static DWARF with the exact current dynamic ABI query baseline.
# Keeps file-only GDB evidence separate from firmware execution and runtime proof.
# Inspected before one-shot execution; existing source/tests/consumers stay fixed.
from pathlib import Path
import hashlib
import json
import os
import re
import sys
import types

ROOT = Path.cwd().resolve()
RAW = ROOT / 'state/analysis/P7_static_link_probe_raw'
RUN = 'f0220228320c4b2aa20c3e5e8264c813'
RUNNER_SHA = '983e86d7eb68f437c50b4b790e96ca4520e092abe53e4d29e8ffe1a97502b208'
RECEIPTS = {
    '0001': '534da2e8de0d846d850288c956f3c5a51b13f641b3329c6475dc5857930f32a7',
    '0009': '3f57a292649a0d20ddf88daf3f80a8b3d75a90e18460f3c7208c1eb17c6b45d4',
    '0021': 'c44e85bcb22dcb69c405b1bddeea74f7c30e4c9e3f1444370995f806162e3127',
}
BASE = ROOT / 'state/analysis/P7_default_qualification_raw'
BASE_PINS = {
    'current_default_abi/receipt.json': '7a3e3fb9c67f023acae1c4efd5e2ee680123743f1f339edbed367d957728eb4f',
    'abi_comparison.json': 'fe13798520a1d5688e7d3f7fe56a19f6d2df1e22af8162dc862109728efbd47c',
}
GDB = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-gdb'
GDB_SHA = '8e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778'


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
    out = RAW / 'native_abi'
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


def baseline(r, probe):
    raw = {}
    for name, digest in BASE_PINS.items():
        path = BASE / name
        r.safe_path(path, 'file')
        raw[name] = path.read_bytes()
        r.require(r.sha(raw[name]) == digest, 'ABI baseline drift')
    old = r.decode(raw['current_default_abi/receipt.json'])
    argv = old['argv'].copy()
    r.require(old['returncode'] == 0 and argv[:4] == [GDB, '-nx', '-nh', '-batch'],
              'Unexpected historical GDB command')
    r.require(probe.pins.get(GDB) == GDB_SHA, 'GDB pin missing')
    r.require(len(argv) == 465 and all(type(x) is str for x in argv), 'Wrong query list')
    r.require(all(argv[i] == '-ex' for i in range(5, len(argv), 2)), 'Unexpected GDB option')
    argv[4] = probe.build + '/app.ino_debug.elf'
    # -nx disables init files; independently disable object-associated scripts
    # before GDB opens the ELF, while retaining every baseline query verbatim.
    argv[4:4] = ['-iex', 'set auto-load no']
    expected = r.decode(raw['abi_comparison.json'])['current_default']
    r.require(set(expected) == {'types', 'member_offsets'} and len(expected['types']) == 16
              and len(expected['member_offsets']) == 82, 'Wrong baseline cardinality')
    return argv, expected


def parse(r, stdout, expected):
    sizes = re.findall(r'TYPE (\S+)\s+\$\d+ = (\d+)\s+\$\d+ = (\d+)', stdout)
    members = re.findall(r'MEMBER (\S+) (\S+)\s+\$\d+ = (\d+)', stdout)
    r.require(len(sizes) == 16 and len(members) == 82, 'Incomplete ABI output')
    actual = dict(types={name: dict(sizeof=int(size), alignof=int(align)) for name, size, align in sizes},
                  member_offsets={name + '::' + field: int(value) for name, field, value in members})
    r.require(actual['types'].keys() == expected['types'].keys() and
              actual['member_offsets'].keys() == expected['member_offsets'].keys(), 'Wrong ABI result keys')
    return actual


def finish(r, probe, out, actual, expected, failure):
    equal = actual == expected if actual is not None else False
    if failure is None and not equal:
        failure = (ValueError('Static/current-default ABI differs'), 'abi_compare')
    if failure is None and not (probe.sequence == 5 and probe.query_attempts == probe.compile_attempts == 0):
        failure = (ValueError('Unexpected read-command counts'), 'command_counts')
    result = dict(status='STATIC_ABI_FAILED' if failure else 'STATIC_ABI_MATCH',
                  source_sha256=r.SOURCE, run_id=RUN, actual=actual, matches_current_default=equal,
                  read_commands=probe.sequence, query_attempts=probe.query_attempts,
                  compile_attempts=probe.compile_attempts, postcheck_errors=probe.postcheck_errors)
    if failure:
        result.update(phase=failure[1], error=r.error_record(failure[0]))
    try:
        r.write_json(out / 'result.json', result, exclusive=True)
    except Exception:
        if failure:
            raise failure[0]
        raise
    if failure:
        raise failure[0]
    print('STATIC_ABI_MATCH: 16 type size/alignment pairs and 82 member offsets; no target/inferior')


def main():
    r, probe, inputs, out = prepare()
    argv, expected = baseline(r, probe)
    out.mkdir(mode=0o700)
    r.write_json(out / 'inputs.json', dict(pins=r.PINS, baseline_pins=BASE_PINS, receipts=RECEIPTS,
                 files=probe.files, claim=probe.claim, argv=argv), exclusive=True)
    failure, actual = None, None
    try:
        probe.remote_postcheck()
        probe.installed_pins()
        probe.phase = 'file_only_gdb'
        reply = probe.dispatch(r.BOARD, argv, capture=True, timeout=60)
        r.require(not reply.stderr and len(reply.stdout.encode()) <= 1048576, 'Invalid GDB output')
        actual = parse(r, reply.stdout, expected)
    except Exception as error:
        failure = (error, probe.phase)
    for method in (probe.remote_postcheck, probe.installed_pins):
        try:
            method()
        except Exception as error:
            probe.postcheck_errors.append(dict(check=method.__name__, **r.error_record(error)))
            failure = failure or (error, probe.phase)
    post = probe.postchecks(local_only=True)
    failure = failure or post
    try:
        baseline(r, probe)
    except Exception as error:
        probe.postcheck_errors.append(dict(check='baseline', **r.error_record(error)))
        failure = failure or (error, 'baseline')
    finish(r, probe, out, actual, expected, failure)


if __name__ == '__main__':
    main()
