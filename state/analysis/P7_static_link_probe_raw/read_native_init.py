# Reads the exact 18-byte native device-init wrapper from the existing packaged ELF.
# Avoids the evidenced ambiguous by-name lookup; no native function executes.
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
GDB = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-gdb'
GDB_SHA = '8e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778'
LOADER = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
LOADER_SHA = '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'


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
    out = RAW / 'native_init'
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


def commands(probe):
    argv = [GDB, '-nx', '-nh', '-batch', '-iex', 'set auto-load no', LOADER,
            '-ex', 'echo D151_LOADER_00\\n',
            '-ex', 'disassemble /r 0x08019e5c,0x08019e6e',
            '-ex', 'echo D151_END\\n']
    return argv, [dict(label='D151_LOADER_00',
                      query='disassemble /r 0x08019e5c,0x08019e6e')]


def blocks(r, stdout, labels):
    expected = [item['label'] for item in labels] + ['D151_END']
    observed = re.findall(r'^D151_(?:APP_\d{2}|LOADER_\d{2}|END)$', stdout, flags=re.M)
    r.require(observed == expected, 'Incomplete or duplicate API query labels')
    result = {}
    for current, following in zip(expected, expected[1:]):
        part = stdout.split(current + '\n', 1)[1].split(following + '\n', 1)[0]
        r.require(part.strip(), 'Empty API query result')
        result[current] = part
    return result


def finalize(r, probe, out, queries, failure):
    if failure is None and not (probe.sequence == 5 and probe.query_attempts == probe.compile_attempts == 0):
        failure = (ValueError('Unexpected command counts'), 'command_counts')
    result = dict(status='NATIVE_INIT_READ_FAILED' if failure else 'NATIVE_INIT_QUERIES_COLLECTED',
                  source_sha256=r.SOURCE, run_id=RUN, query_count=len(queries) if queries is not None else 0,
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
    print('NATIVE_INIT_QUERIES_COLLECTED: file observations only; interpretation/review follows')


def main():
    r, probe, inputs, out = prepare()
    r.require(probe.pins.get(GDB) == GDB_SHA and probe.pins.get(LOADER) == LOADER_SHA,
              'Tool or packaged-loader pin missing')
    argv, labels = commands(probe)
    out.mkdir(mode=0o700)
    r.write_json(out / 'inputs.json', dict(pins=r.PINS, receipts=RECEIPTS, files=probe.files,
                 claim=probe.claim, argv=argv, labelled_queries=labels), exclusive=True)
    failure, queries = None, None
    try:
        probe.remote_postcheck()
        probe.installed_pins()
        probe.phase = 'file_only_native_init'
        reply = probe.dispatch(r.BOARD, argv, capture=True, timeout=60)
        r.require(not reply.stderr and len(reply.stdout.encode()) <= 1048576, 'Invalid API query output')
        queries = blocks(r, reply.stdout, labels)
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
    finalize(r, probe, out, queries, failure)


if __name__ == '__main__':
    main()
