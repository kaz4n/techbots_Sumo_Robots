# Observes fixed ordinary-app entry and inhibited motor instructions from checked files.
# Preserves ordinary ABI evidence and the reviewed single-attempt file-only lifecycle.
# Independent entry fixtures verify metadata projections, parsing, guards and closure.
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import types


ROOT = Path(__file__).absolute().parents[3]
RAW = 'state/analysis/P7_ordinary_app_static_compile_raw/'
ABI = RAW + 'inspect_static_abi.py'
PARSER = 'state/analysis/P7_app_motor_fault_compile_raw/inspect_static_entry.py'
ABI_RESULT = RAW + 'native_abi_static01/result.json'
ABI_LAYOUT = RAW + 'native_abi_static01/abi.json'
ABI_CLOSURE = RAW + 'native_abi_static01/local_result.json'
ABI_REVIEW = 'state/reviews/P7_ordinary_app_abi_actual_review.md'
ARTIFACTS = RAW + 'native_static01/artifacts.json'
BINDING = RAW + 'entry_binding01.json'
CONTRACT = 'state/analysis/P7_ordinary_app_entry_contract.md'
CONTRACT_SHA = 'd28204206a0adb06cb19e38f5cd48bc70edeec14260ab015b21b1a65eb55f637'
ORIGINALS = {
    ABI: (44449, 'f816a52366d7031f860d5cdd93e0715905df4b675a24e89d8dbb1d2b63eda97d'),
    ABI_CLOSURE: (275, '9c78721cfaa7330cc523619c31ad207832ffe6f9ca3abcc9e93bec7743212cf0'),
    ABI_LAYOUT: (274942, 'e224750ea11a9bd462c1708e2d797b622e9fee56e3e46e479242bff19eefdbf4'),
    ABI_RESULT: (581671, '6a17c12cb24396bf9a58a883ea295ec51feff2abe68d826983f363b3bcbb6d3b'),
    ABI_REVIEW: (9627, '585be669385e1ca85ddd188d3eeda5fdf11cfc3392eea614370d9bfabbcc4b6a'),
    ARTIFACTS: (9281, '275ebb61be4a0487fe381d915ec28eea4634926b1d06a627850266f5c0a750e0'),
    PARSER: (10317, 'cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34'),
    BINDING: (106946, '36cafffcfebc647b5019b438705fa42a8be94edfb5d8b67deac2508878c6ae89'),
}
READER_INPUT = (12965, '7fb42d51a3f42f99c7e7890b4f4c1dc90360c2d84c09d3bbde7ccea4d1138aea')
READER_PROJECTED = (12987, '331f10914c77f1ece7255262db0d2f0c6472d31f86e680e6ec23c39c4b682b45')
PARSER_PROJECTED = (14259, 'a71d5c172b65952ab010441bfd894f2552e08bf2a66c19adf0eed29c381a6e05')
READER_REPLACEMENTS = (
    (b"'/inspect_static_abi.py'", b"'/inspect_static_entry.py'", 1),
    (b"'native_abi_static01'", b"'native_entry_static01'", 1),
    (b'ordinary-app-abi-static01', b'ordinary-app-entry-static01', 1),
    (b'D209_STATIC_FILE_ONLY_ABI', b'D210_STATIC_FILE_ONLY_ENTRY', 2),
    (b'STATIC_ABI_CHECKED', b'STATIC_ENTRY_CHECKED', 1),
    (b'STATIC_ABI_OBSERVED', b'STATIC_ENTRY_OBSERVED', 1),
    (b"'file-abi'", b"'file-entry'", 1),
    (b"'abi.json'", b"'entry.json'", 1),
    (b'StaticAbi', b'StaticEntry', 2),
)
PARSER_REPLACEMENTS = (
    (b'/home/arduino/sumox26_codex_build/app-motor-fault-static01/build/app_motor_fault.ino', b'/home/arduino/sumox26_codex_build/ordinary-app-static01/build/app.ino', 1),
    (b"RANGES = (\n    ('entry_point', 0x08100010, 0x081000c8, ('entry_point',)),\n    ('setup', 0x081000c8, 0x081000e8, ('setup',)),\n    ('loop', 0x081000e8, 0x08100104, ('loop',)),\n    ('global_initializer', 0x08100104, 0x08100298, ('_GLOBAL__sub_I_setup',)),\n    ('app_dump_port', 0x081002a8, 0x081002d0, ('_ZN3app12unoQDumpPortERN8recorder4dump12UnoQDumpPortE',)),\n    ('sources_port', 0x081003e0, 0x0810045c, ('_ZN3app13NativeSources4portEv',)),\n    ('sources_adc_port', 0x0810045c, 0x08100470, ('_ZN3app13NativeSources7adcPortEv',)),\n    ('runner_constructor', 0x08103984, 0x08103b58, tuple('_ZN15app_motor_fault6RunnerC' + str(n) +\n        'ERKN6motors4PortERKN5power9InputPortERKN3app10SourcePortERKNS9_8DumpPortE' for n in (1, 2))),\n    ('runner_application_valid', 0x08103b58, 0x08103bb0, ('_ZNK15app_motor_fault6Runner16applicationValidEv',)),\n    ('runner_stop_reason', 0x08103bb0, 0x08103c08, ('_ZNK15app_motor_fault6Runner10stopReasonEv',)),\n    ('runner_freeze', 0x08103c08, 0x08103c94, ('_ZN15app_motor_fault6Runner6freezeENS_6ReasonE',)),\n    ('runner_begin', 0x08103c94, 0x08103d24, ('_ZN15app_motor_fault6Runner5beginERKN11motor_fault6GrantsE',)),\n    ('runner_poll', 0x08103d24, 0x08103d78, ('_ZN15app_motor_fault6Runner4pollEv',)),\n    ('dump_port', 0x0810c760, 0x0810c774, ('_ZN8recorder4dump12UnoQDumpPort4portEv',)),\n    ('loop_hook', 0x08110bfc, 0x08110bfe, ('_Z10__loopHookv',)),\n    ('candidate_rate', 0x08110c70, 0x08110cd8, ('_ZN6motors12_GLOBAL__N_113candidateRateEj',)),\n    ('candidate_period', 0x08110cd8, 0x08110d10, ('_ZN6motors12_GLOBAL__N_115candidatePeriodEj',)),\n    ('motor_port', 0x08110ed8, 0x08110f64, ('_ZN6motors8UnoQPort4portEv',)),\n    ('power_reader_port', 0x0811326c, 0x08113290, ('_ZN5power15readerInputPortERNS_6ReaderE',)),\n    ('trace_constructor', 0x08115bec, 0x08115c7c,\n        tuple('_ZN11motor_fault5TraceC' + str(n) + 'ERKN6motors4PortE' for n in (1, 2))),\n    ('trace_port', 0x08115c7c, 0x08115cfc, ('_ZN11motor_fault5Trace4portEv',)),\n    ('memcpy', 0x08115f6c, 0x08115f74, ('memcpy',)),\n    ('memset', 0x08115f74, 0x08115f7c, ('memset',)),\n    ('unsigned_divide', 0x0811602c, 0x08116036, ('__aeabi_uldivmod',)),\n    ('init_variant', 0x08116044, 0x08116046, ('initVariant',)),\n    ('main', 0x08116048, 0x08116074, ('main',)),\n    ('start_static_threads', 0x08116074, 0x081160e0, ('_Z20start_static_threadsv',)),\n)", b"RANGES = (\n    ('entry_point', 0x08100010, 0x081000c8, ('entry_point',)),\n    ('setup', 0x081000c8, 0x081000f0, ('setup',)),\n    ('loop', 0x081000f0, 0x08100100, ('loop',)),\n    ('global_initializer', 0x08100100, 0x08100294, ('_GLOBAL__sub_I_setup',)),\n    ('app_dump_port', 0x081002a4, 0x081002cc, ('_ZN3app12unoQDumpPortERN8recorder4dump12UnoQDumpPortE',)),\n    ('sources_port', 0x081003dc, 0x08100458, ('_ZN3app13NativeSources4portEv',)),\n    ('sources_adc_port', 0x08100458, 0x0810046c, ('_ZN3app13NativeSources7adcPortEv',)),\n    ('dump_port', 0x0810c248, 0x0810c25c, ('_ZN8recorder4dump12UnoQDumpPort4portEv',)),\n    ('motor_port', 0x08110934, 0x081109b8, ('_ZN6motors8UnoQPort4portEv',)),\n    ('power_reader_port', 0x08112cd0, 0x08112cf4, ('_ZN5power15readerInputPortERNS_6ReaderE',)),\n    ('loop_hook', 0x081106e4, 0x081106e6, ('_Z10__loopHookv',)),\n    ('memcpy', 0x08115644, 0x0811564c, ('memcpy',)),\n    ('memset', 0x0811564c, 0x08115654, ('memset',)),\n    ('init_variant', 0x0811571c, 0x0811571e, ('initVariant',)),\n    ('main', 0x08115720, 0x0811574c, ('main',)),\n    ('start_static_threads', 0x0811574c, 0x081157b8, ('_Z20start_static_threadsv',)),\n    ('runtime_constructor', 0x08100510, 0x08100a26, ('_ZN3app7RuntimeC1ERKN6motors4PortERKN5power9InputPortERKNS_10SourcePortERKNS_8DumpPortE', '_ZN3app7RuntimeC2ERKN6motors4PortERKN5power9InputPortERKNS_10SourcePortERKNS_8DumpPortE')),\n    ('transaction_constructor', 0x081030f8, 0x081032a8, ('_ZN3app11TransactionC1ERKN6motors4PortE', '_ZN3app11TransactionC2ERKN6motors4PortE')),\n    ('gate_constructor', 0x08111084, 0x081110c0, ('_ZN6motors9MotorGateC1ERKNS_4PortE', '_ZN6motors9MotorGateC2ERKNS_4PortE')),\n    ('input_owner_constructor', 0x081126ec, 0x0811273e, ('_ZN5power10InputOwnerC1ERKNS_9InputPortE', '_ZN5power10InputOwnerC2ERKNS_9InputPortE')),\n    ('robot_constructor', 0x08102b58, 0x081030f8, ('_ZN3fsm5RobotC1Ev', '_ZN3fsm5RobotC2Ev')),\n    ('fusion_observation_constructor', 0x08102a20, 0x08102a44, ('_ZN10opp_fusion17FusionObservationC1Ev', '_ZN10opp_fusion17FusionObservationC2Ev')),\n    ('flank_constructor', 0x08102a44, 0x08102a94, ('_ZN7openers5FlankC1Ev', '_ZN7openers5FlankC2Ev')),\n    ('turn_constructor', 0x081029d8, 0x08102a06, ('_ZN6motion4TurnC1Ev', '_ZN6motion4TurnC2Ev')),\n    ('straight_constructor', 0x08102a06, 0x08102a20, ('_ZN6motion8StraightC1Ev', '_ZN6motion8StraightC2Ev')),\n    ('line_thresholds_constructor', 0x0810046c, 0x08100484, ('_ZN8line_qtr10ThresholdsC1Ev', '_ZN8line_qtr10ThresholdsC2Ev')),\n    ('qtr_report_constructor', 0x08100484, 0x081004bc, ('_ZN7qtr_cal6ReportC1Ev', '_ZN7qtr_cal6ReportC2Ev')),\n    ('line_snapshot_constructor', 0x081004bc, 0x0810050c, ('_ZN8line_qtr8SnapshotC1Ev', '_ZN8line_qtr8SnapshotC2Ev')),\n    ('robot_result_constructor', 0x08102a94, 0x08102b54, ('_ZN3fsm11RobotResultC1Ev', '_ZN3fsm11RobotResultC2Ev')),\n    ('runtime_begin', 0x08100f9c, 0x08101050, ('_ZN3app7Runtime5beginERKNS_11SetupGrantsE',)),\n    ('runtime_valid_ports', 0x08100a28, 0x08100aa8, ('_ZNK3app7Runtime10validPortsEv',)),\n    ('runtime_initialize_sources', 0x08100da4, 0x08100ef4, ('_ZN3app7Runtime17initializeSourcesEv',)),\n    ('runtime_initialize_dump', 0x08101acc, 0x08101b08, ('_ZN3app7Runtime14initializeDumpEv',)),\n    ('transaction_initialize', 0x081032a8, 0x081032e4, ('_ZN3app11Transaction10initializeEv',)),\n    ('gate_begin', 0x081111b8, 0x08111240, ('_ZN6motors9MotorGate5beginEv',)),\n    ('runtime_step', 0x0810144c, 0x08101588, ('_ZN3app7Runtime4stepEv',)),\n    ('transaction_open', 0x0810338c, 0x08103418, ('_ZN3app11Transaction4openEv',)),\n    ('transaction_decide_from', 0x0810358c, 0x08103600, ('_ZN3app11Transaction10decideFromERKNS_14DecisionSourceE',)),\n    ('transaction_apply_decision', 0x0810346c, 0x0810358c, ('_ZN3app11Transaction13applyDecisionEN3fsm10RobotInputEj',)),\n    ('gate_apply', 0x08111448, 0x08111540, ('_ZN6motors9MotorGate5applyEjRKN3fsm11RobotResultE',)),\n    ('gate_transact', 0x081113e0, 0x08111448, ('_ZN6motors9MotorGate8transactERKN4core7OutputsERN3fsm12PreviousTickE',)),\n    ('runtime_complete_epoch', 0x0810136c, 0x0810144c, ('_ZN3app7Runtime13completeEpochEv',)),\n    ('transaction_complete', 0x08103600, 0x081036c8, ('_ZN3app11Transaction8completeEbj',)),\n    ('transaction_finish_after', 0x081036c8, 0x081036d4, ('_ZN3app11Transaction11finishAfterEj',)),\n    ('runtime_fail', 0x08100cf0, 0x08100d74, ('_ZN3app7Runtime4failENS_12RuntimeFaultE',)),\n    ('runtime_cancel_sources', 0x08100c70, 0x08100cf0, ('_ZN3app7Runtime13cancelSourcesEv',)),\n    ('transaction_fail', 0x08103318, 0x0810338c, ('_ZN3app11Transaction4failENS_5FaultE',)),\n    ('transaction_abort', 0x081036d4, 0x081036e0, ('_ZN3app11Transaction5abortEv',)),\n    ('gate_halt', 0x08111540, 0x081115e0, ('_ZN6motors9MotorGate4haltEv',)),\n    ('gate_inhibit', 0x0811111a, 0x081111b8, ('_ZN6motors9MotorGate7inhibitEv',)),\n    ('gate_zero_pwm', 0x081110f8, 0x0811111a, ('_ZN6motors9MotorGate7zeroPwmEv',)),\n    ('configure_enable_low', 0x08110a64, 0x08110b98, ('_ZN6motors8UnoQPort18configureEnableLowEPv',)),\n    ('configure_pwm', 0x08110db0, 0x08110e9c, ('_ZN6motors8UnoQPort12configurePwmEPvNS_7ChannelE',)),\n    ('write_enable', 0x08110b98, 0x08110bfc, ('_ZN6motors8UnoQPort11writeEnableEPvb',)),\n    ('write_pwm', 0x08110e9c, 0x08110f80, ('_ZN6motors8UnoQPort8writePwmEPvNS_7ChannelEjj',)),\n    ('motor_settle', 0x08110fc4, 0x08111084, ('_ZN6motors8UnoQPort6settleEPv',)),\n    ('motor_clock', 0x08110794, 0x0811079c, ('_ZN6motors8UnoQPort7clockUsEPv',)),\n    ('candidate_period', 0x08110758, 0x0811076c, ('_ZN6motors12_GLOBAL__N_115candidatePeriodEj',)),\n    ('map_channel', 0x0811082c, 0x08110934, ('_ZN6motors12_GLOBAL__N_110mapChannelEjRj',)),\n    ('enable_owned', 0x081109b8, 0x08110a64, ('_ZNK6motors8UnoQPort11enableOwnedEv',)),\n    ('enable_low', 0x08110bfc, 0x08110c30, ('_ZNK6motors8UnoQPort9enableLowEv',)),\n    ('timer_valid', 0x08110c30, 0x08110db0, ('_ZNK6motors8UnoQPort10timerValidEj',)),\n    ('bank_valid', 0x08110f80, 0x08110fc4, ('_ZNK6motors8UnoQPort9bankValidEv',)),\n    ('gate_valid_port', 0x081110c0, 0x081110f8, ('_ZNK6motors9MotorGate9validPortEv',)),\n)", 1),
    (b"BOUNDS = {name: (0x0811621c if name == '__init_array_end' else 0x08116218)\n          for name in ('__init_array_start', '__init_array_end', '__preinit_array_start',\n                       '__preinit_array_end', '__static_thread_data_list_start', '__static_thread_data_list_end')}", b"BOUNDS = {\n    '__init_array_start': 0x081158f0,\n    '__init_array_end': 0x081158f4,\n    '__preinit_array_start': 0x081158f0,\n    '__preinit_array_end': 0x081158f0,\n    '__static_thread_data_list_start': 0x081158f0,\n    '__static_thread_data_list_end': 0x081158f0,\n}", 1),
    (b"label in ('global_initializer', 'candidate_rate', 'candidate_period')", b"label in ('global_initializer', 'candidate_period', 'map_channel')", 1),
    (b"label in ('init_variant', 'main')", b"label in ('init_variant', 'main', 'robot_constructor', 'fusion_observation_constructor', 'flank_constructor', 'turn_constructor', 'straight_constructor', 'line_thresholds_constructor', 'qtr_report_constructor', 'line_snapshot_constructor', 'robot_result_constructor')", 1),
    (b"sections[0]['address'] == 0x08116218", b"sections[0]['address'] == 0x081158f0", 1),
    (b'int(lines[0][0], 16) == 0x08116218', b'int(lines[0][0], 16) == 0x081158f0', 1),
    (b'return dict(address=0x08116218, bytes_hex=data.hex(), pointer=pointer, bounds=BOUNDS)', b'return dict(address=0x081158f0, bytes_hex=data.hex(), pointer=pointer, bounds=BOUNDS)', 1),
    (b'pointer == 0x08100105', b'pointer == 0x08100101', 1),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, getattr(info, 'st_file_attributes', 0), info.st_ctime_ns)


def _plain_chain(path):
    stamps = []
    for item in (*reversed(path.parents), path):
        info = item.lstat()
        expected = stat.S_ISREG if item == path else stat.S_ISDIR
        require(expected(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 1024,
                'Nonplain ABI input path: ' + str(item))
        require(item != path or info.st_nlink == 1, 'ABI input has multiple links')
        stamps.append(_stamp(info))
    return stamps


def _read_handle(path, expected, limit, before):
    descriptor, stream, primary = None, None, None
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_CLOEXEC', 0)
    flags |= getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    try:
        descriptor = os.open(path, flags)
        info = os.fstat(descriptor)
        opened = _stamp(info)
        path_identity = before[-1][:-1] if os.name == 'nt' else before[-1]
        handle_identity = opened[:-1] if os.name == 'nt' else opened
        # CPython adds all execute bits to these Windows pathname stat results.
        if (os.name == 'nt' and path.suffix.lower() in ('.exe', '.bat', '.cmd', '.com') and
                stat.S_ISREG(path_identity[2]) and stat.S_ISREG(handle_identity[2]) and
                path_identity[2] == (handle_identity[2] | 0o111) and
                path_identity[2] ^ handle_identity[2] == 0o111):
            handle_identity = (*handle_identity[:2], path_identity[2], *handle_identity[3:])
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                not getattr(info, 'st_file_attributes', 0) & 1024 and
                path_identity == handle_identity, 'ABI input changed before reading')
        stream = os.fdopen(descriptor, 'rb')
        descriptor = None
        raw = stream.read(limit + 1)
        closed = _stamp(os.fstat(stream.fileno()))
        after = _plain_chain(path)
        require(before == after and opened == closed and
                0 < len(raw) == before[-1][4] <= limit, 'ABI input changed while reading')
        require(hashlib.sha256(raw).hexdigest() == expected, 'ABI input digest changed: ' + str(path))
        return raw
    except BaseException as error:
        primary = error
        raise
    finally:
        try:
            if stream is not None:
                stream.close()
            elif descriptor is not None:
                os.close(descriptor)
        except BaseException:
            if primary is None:
                raise


def pinned(path, expected, limit=1048576):
    require(type(expected) is str and re.fullmatch('[0-9a-f]{64}', expected),
            'Expected a fixed lowercase input digest')
    require(type(limit) is int and 0 < limit <= 16777216, 'Invalid ABI input bound')
    path = Path(path).absolute()
    before = _plain_chain(path)
    require(0 < before[-1][4] <= limit, 'ABI input exceeds byte bound')
    return _read_handle(path, expected, limit, before)


def _verify(raw, identity, label):
    require(type(raw) is bytes and len(raw) == identity[0] and
            hashlib.sha256(raw).hexdigest() == identity[1], 'Fixed source changed: ' + label)


def _project(raw, original, replacements, projected):
    _verify(raw, original, 'entry projection input')
    for old, new, count in replacements:
        require(raw.count(old) == count, 'Entry projection occurrence count changed')
        raw = raw.replace(old, new)
    _verify(raw, projected, 'entry projection output')
    return raw


def project_reader(raw):
    return _project(raw, READER_INPUT, READER_REPLACEMENTS, READER_PROJECTED)


def project_parser(raw):
    return _project(raw, ORIGINALS[PARSER], PARSER_REPLACEMENTS, PARSER_PROJECTED)


def _module(name, path, raw):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def load_reader(*, root=ROOT):
    root = Path(root).absolute()
    snapshots = {}
    for name, identity in ORIGINALS.items():
        snapshots[name] = pinned(root / name, identity[1])
        _verify(snapshots[name], identity, name)
    pinned(root / CONTRACT, CONTRACT_SHA)
    parser_raw = project_parser(snapshots[PARSER])
    abi = _module('_sumox_d210_entry_abi', root / ABI, snapshots[ABI])
    original_projection = abi.project_reader

    def composed_projection(raw):
        return project_reader(original_projection(raw))

    abi.project_reader = composed_projection
    reader = abi.load_reader(root=root)
    parser = _module('_sumox_d210_entry_parser', root / PARSER, parser_raw)
    reader.HARD_PINS = dict(reader.HARD_PINS)
    reader.HARD_PINS.update({name: identity[1] for name, identity in ORIGINALS.items()})
    reader.HARD_PINS[CONTRACT] = CONTRACT_SHA
    reader.queries = parser.queries
    reader.summarize = parser.summarize
    return reader


def main(argv):
    require(type(argv) is list and all(type(item) is str for item in argv),
            'Expected an exact argument list')
    require(len(argv) == 3 and argv[0] in ('--check-only', '--execute') and
            argv[1] == '--reviewed-head' and re.fullmatch('[0-9a-f]{40}', argv[2]),
            'Expected --check-only|--execute --reviewed-head <40lowerhex>')
    require(sys.dont_write_bytecode, 'Python -B required')
    return load_reader(root=ROOT).main(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
