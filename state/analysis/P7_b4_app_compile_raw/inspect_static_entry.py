# Observes fixed B4 app entry and inhibited motor instructions from checked files.
# Reuses accepted entry parsing and the B4 file-only guarded reader lifecycle.
# Independent focused fixtures check current bindings and unchanged algorithms.
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import types


ROOT = Path(__file__).absolute().parents[3]
RAW = 'state/analysis/P7_b4_app_compile_raw/'
ABI = RAW + 'inspect_static_abi.py'
PARSER = 'state/analysis/P7_app_motor_fault_compile_raw/inspect_static_entry.py'
ABI_RESULT = RAW + 'native_abi_static01/result.json'
ABI_LAYOUT = RAW + 'native_abi_static01/abi.json'
ABI_CLOSURE = RAW + 'native_abi_static01/local_result.json'
ABI_REVIEW = 'state/reviews/P7_b4_app_abi_actual_review.md'
ARTIFACTS = RAW + 'native_static01/artifacts.json'
BINDING = RAW + 'entry_binding01.json'
CONTRACT = 'state/analysis/P7_b4_app_entry_contract.md'
CONTRACT_SHA = 'bcc3072ccb1a219c3cf70ab92ce78d6e140fb4b619b2a370fc56d112a6daa543'
ORIGINALS = {'state/analysis/P7_ordinary_app_static_compile_raw/inspect_static_entry.py': (18546, '5bcb6e12424237cb2701d271e2704281dedca76688d786eac1076daf8f9b3e0b'), 'state/analysis/P7_b4_app_compile_raw/inspect_static_abi.py': (32744, '4b31dfed3508ebd612abd7de31c5d25e5983c57b802fc55946d3996cf259943d'), 'state/analysis/P7_b4_app_compile_raw/native_abi_static01/local_result.json': (275, '7175682488de957b36582fc3b030554ac3cfb8a83ea6ab10ffde6fa2a8534729'), 'state/analysis/P7_b4_app_compile_raw/native_abi_static01/abi.json': (293222, '25bf57646977fec8b4614b06cfe2b3df2e3bb94172122b2ee8f5ceaaec6677bc'), 'state/analysis/P7_b4_app_compile_raw/native_abi_static01/result.json': (597470, 'ac0f379ad7da6d02d9cce4f1035405f48fd4f9fcf19de4bb7bcec7f31cf8f69a'), 'state/reviews/P7_b4_app_abi_actual_review.md': (5715, 'c7fe6fe9b0629e65548e69eb7aa66a94cbda3bf9da5f5e13baeaa18be32902b6'), 'state/analysis/P7_b4_app_compile_raw/native_static01/artifacts.json': (9484, '0acaa30a4ba01ac5c9ff8c8fddc66c4bec94e033b1194ec63271f12affb6c085'), 'state/analysis/P7_app_motor_fault_compile_raw/inspect_static_entry.py': (10317, 'cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34'), 'state/analysis/P7_b4_app_compile_raw/entry_binding01.json': (78168, 'fb2ab19d0cd0337f7d74a9578eee58d2e0029bf8a45ad6851a9ddbf558c79d55')}
READER_INPUT = (13204, '069af034c960acc478b11ec8c516da58121a8adf2d936531309d298d7ca3feba')
READER_PROJECTED = (13226, '5df04ffc6c532d236006bb67bfa772493d8b2dc165b5523e4777300a04f0bba9')
PARSER_PROJECTED = (14256, 'dd011caad902b86cc6e47fded3be1695e4a96f84581e6a654acf38a2c96a1bfc')
READER_REPLACEMENTS = ((b"'/inspect_static_abi.py'", b"'/inspect_static_entry.py'", 1), (b"'native_abi_static01'", b"'native_entry_static01'", 1), (b'b4-app-m0-abi-static01', b'b4-app-m0-entry-static01', 1), (b'D215_STATIC_FILE_ONLY_ABI', b'D217_STATIC_FILE_ONLY_ENTRY', 2), (b'STATIC_ABI_CHECKED', b'STATIC_ENTRY_CHECKED', 1), (b'STATIC_ABI_OBSERVED', b'STATIC_ENTRY_OBSERVED', 1), (b"'file-abi'", b"'file-entry'", 1), (b"'abi.json'", b"'entry.json'", 1), (b'StaticAbi', b'StaticEntry', 2))
PARSER_REPLACEMENTS = ((b'/home/arduino/sumox26_codex_build/app-motor-fault-static01/build/app_motor_fault.ino', b'/home/arduino/sumox26_codex_build/b4-app-m0-static01/build/app.ino', 1), (b"RANGES = (\n    ('entry_point', 0x08100010, 0x081000c8, ('entry_point',)),\n    ('setup', 0x081000c8, 0x081000e8, ('setup',)),\n    ('loop', 0x081000e8, 0x08100104, ('loop',)),\n    ('global_initializer', 0x08100104, 0x08100298, ('_GLOBAL__sub_I_setup',)),\n    ('app_dump_port', 0x081002a8, 0x081002d0, ('_ZN3app12unoQDumpPortERN8recorder4dump12UnoQDumpPortE',)),\n    ('sources_port', 0x081003e0, 0x0810045c, ('_ZN3app13NativeSources4portEv',)),\n    ('sources_adc_port', 0x0810045c, 0x08100470, ('_ZN3app13NativeSources7adcPortEv',)),\n    ('runner_constructor', 0x08103984, 0x08103b58, tuple('_ZN15app_motor_fault6RunnerC' + str(n) +\n        'ERKN6motors4PortERKN5power9InputPortERKN3app10SourcePortERKNS9_8DumpPortE' for n in (1, 2))),\n    ('runner_application_valid', 0x08103b58, 0x08103bb0, ('_ZNK15app_motor_fault6Runner16applicationValidEv',)),\n    ('runner_stop_reason', 0x08103bb0, 0x08103c08, ('_ZNK15app_motor_fault6Runner10stopReasonEv',)),\n    ('runner_freeze', 0x08103c08, 0x08103c94, ('_ZN15app_motor_fault6Runner6freezeENS_6ReasonE',)),\n    ('runner_begin', 0x08103c94, 0x08103d24, ('_ZN15app_motor_fault6Runner5beginERKN11motor_fault6GrantsE',)),\n    ('runner_poll', 0x08103d24, 0x08103d78, ('_ZN15app_motor_fault6Runner4pollEv',)),\n    ('dump_port', 0x0810c760, 0x0810c774, ('_ZN8recorder4dump12UnoQDumpPort4portEv',)),\n    ('loop_hook', 0x08110bfc, 0x08110bfe, ('_Z10__loopHookv',)),\n    ('candidate_rate', 0x08110c70, 0x08110cd8, ('_ZN6motors12_GLOBAL__N_113candidateRateEj',)),\n    ('candidate_period', 0x08110cd8, 0x08110d10, ('_ZN6motors12_GLOBAL__N_115candidatePeriodEj',)),\n    ('motor_port', 0x08110ed8, 0x08110f64, ('_ZN6motors8UnoQPort4portEv',)),\n    ('power_reader_port', 0x0811326c, 0x08113290, ('_ZN5power15readerInputPortERNS_6ReaderE',)),\n    ('trace_constructor', 0x08115bec, 0x08115c7c,\n        tuple('_ZN11motor_fault5TraceC' + str(n) + 'ERKN6motors4PortE' for n in (1, 2))),\n    ('trace_port', 0x08115c7c, 0x08115cfc, ('_ZN11motor_fault5Trace4portEv',)),\n    ('memcpy', 0x08115f6c, 0x08115f74, ('memcpy',)),\n    ('memset', 0x08115f74, 0x08115f7c, ('memset',)),\n    ('unsigned_divide', 0x0811602c, 0x08116036, ('__aeabi_uldivmod',)),\n    ('init_variant', 0x08116044, 0x08116046, ('initVariant',)),\n    ('main', 0x08116048, 0x08116074, ('main',)),\n    ('start_static_threads', 0x08116074, 0x081160e0, ('_Z20start_static_threadsv',)),\n)", b"RANGES = (\n    ('entry_point', 0x08100010, 0x081000c8, ('entry_point',)),\n    ('setup', 0x081000c8, 0x081000f0, ('setup',)),\n    ('loop', 0x081000f0, 0x08100100, ('loop',)),\n    ('global_initializer', 0x08100100, 0x08100294, ('_GLOBAL__sub_I_setup',)),\n    ('app_dump_port', 0x081002a4, 0x081002cc, ('_ZN3app12unoQDumpPortERN8recorder4dump12UnoQDumpPortE',)),\n    ('sources_port', 0x081003dc, 0x08100458, ('_ZN3app13NativeSources4portEv',)),\n    ('sources_adc_port', 0x08100458, 0x0810046c, ('_ZN3app13NativeSources7adcPortEv',)),\n    ('dump_port', 0x08109b40, 0x08109b54, ('_ZN8recorder4dump12UnoQDumpPort4portEv',)),\n    ('motor_port', 0x0810e22c, 0x0810e2b0, ('_ZN6motors8UnoQPort4portEv',)),\n    ('power_reader_port', 0x081105d0, 0x081105f4, ('_ZN5power15readerInputPortERNS_6ReaderE',)),\n    ('loop_hook', 0x0810dfdc, 0x0810dfde, ('_Z10__loopHookv',)),\n    ('memcpy', 0x08112f44, 0x08112f4c, ('memcpy',)),\n    ('memset', 0x08112f4c, 0x08112f54, ('memset',)),\n    ('init_variant', 0x08113010, 0x08113012, ('initVariant',)),\n    ('main', 0x08113014, 0x08113040, ('main',)),\n    ('start_static_threads', 0x08113040, 0x081130ac, ('_Z20start_static_threadsv',)),\n    ('runtime_constructor', 0x08100510, 0x08100a26, ('_ZN3app7RuntimeC1ERKN6motors4PortERKN5power9InputPortERKNS_10SourcePortERKNS_8DumpPortE', '_ZN3app7RuntimeC2ERKN6motors4PortERKN5power9InputPortERKNS_10SourcePortERKNS_8DumpPortE')),\n    ('transaction_constructor', 0x08102de4, 0x08102f94, ('_ZN3app11TransactionC1ERKN6motors4PortE', '_ZN3app11TransactionC2ERKN6motors4PortE')),\n    ('gate_constructor', 0x0810e97c, 0x0810e9b8, ('_ZN6motors9MotorGateC1ERKNS_4PortE', '_ZN6motors9MotorGateC2ERKNS_4PortE')),\n    ('input_owner_constructor', 0x0810ffec, 0x0811003e, ('_ZN5power10InputOwnerC1ERKNS_9InputPortE', '_ZN5power10InputOwnerC2ERKNS_9InputPortE')),\n    ('robot_constructor', 0x08102818, 0x08102de4, ('_ZN3fsm5RobotC1Ev', '_ZN3fsm5RobotC2Ev')),\n    ('fusion_observation_constructor', 0x081026d4, 0x081026f8, ('_ZN10opp_fusion17FusionObservationC1Ev', '_ZN10opp_fusion17FusionObservationC2Ev')),\n    ('flank_constructor', 0x081026f8, 0x08102748, ('_ZN7openers5FlankC1Ev', '_ZN7openers5FlankC2Ev')),\n    ('turn_constructor', 0x0810268c, 0x081026ba, ('_ZN6motion4TurnC1Ev', '_ZN6motion4TurnC2Ev')),\n    ('straight_constructor', 0x081026ba, 0x081026d4, ('_ZN6motion8StraightC1Ev', '_ZN6motion8StraightC2Ev')),\n    ('line_thresholds_constructor', 0x0810046c, 0x08100484, ('_ZN8line_qtr10ThresholdsC1Ev', '_ZN8line_qtr10ThresholdsC2Ev')),\n    ('qtr_report_constructor', 0x08100484, 0x081004bc, ('_ZN7qtr_cal6ReportC1Ev', '_ZN7qtr_cal6ReportC2Ev')),\n    ('line_snapshot_constructor', 0x081004bc, 0x0810050c, ('_ZN8line_qtr8SnapshotC1Ev', '_ZN8line_qtr8SnapshotC2Ev')),\n    ('robot_result_constructor', 0x08102748, 0x08102818, ('_ZN3fsm11RobotResultC1Ev', '_ZN3fsm11RobotResultC2Ev')),\n    ('runtime_begin', 0x08100fa0, 0x08101054, ('_ZN3app7Runtime5beginERKNS_11SetupGrantsE',)),\n    ('runtime_valid_ports', 0x08100a28, 0x08100aa8, ('_ZNK3app7Runtime10validPortsEv',)),\n    ('runtime_initialize_sources', 0x08100da8, 0x08100ef8, ('_ZN3app7Runtime17initializeSourcesEv',)),\n    ('runtime_initialize_dump', 0x08101ad0, 0x08101b0c, ('_ZN3app7Runtime14initializeDumpEv',)),\n    ('transaction_initialize', 0x08102f94, 0x08102fd0, ('_ZN3app11Transaction10initializeEv',)),\n    ('gate_begin', 0x0810eab0, 0x0810eb38, ('_ZN6motors9MotorGate5beginEv',)),\n    ('runtime_step', 0x08101450, 0x0810158c, ('_ZN3app7Runtime4stepEv',)),\n    ('transaction_open', 0x08103078, 0x08103104, ('_ZN3app11Transaction4openEv',)),\n    ('transaction_decide_from', 0x0810327c, 0x081032f0, ('_ZN3app11Transaction10decideFromERKNS_14DecisionSourceE',)),\n    ('transaction_apply_decision', 0x08103158, 0x0810327c, ('_ZN3app11Transaction13applyDecisionEN3fsm10RobotInputEj',)),\n    ('gate_apply', 0x0810ed4c, 0x0810ee48, ('_ZN6motors9MotorGate5applyEjRKN3fsm11RobotResultE',)),\n    ('gate_transact', 0x0810ece4, 0x0810ed4c, ('_ZN6motors9MotorGate8transactERKN4core7OutputsERN3fsm12PreviousTickE',)),\n    ('runtime_complete_epoch', 0x08101370, 0x08101450, ('_ZN3app7Runtime13completeEpochEv',)),\n    ('transaction_complete', 0x081032f0, 0x081033b8, ('_ZN3app11Transaction8completeEbj',)),\n    ('transaction_finish_after', 0x081033b8, 0x081033c4, ('_ZN3app11Transaction11finishAfterEj',)),\n    ('runtime_fail', 0x08100cf4, 0x08100d78, ('_ZN3app7Runtime4failENS_12RuntimeFaultE',)),\n    ('runtime_cancel_sources', 0x08100c74, 0x08100cf4, ('_ZN3app7Runtime13cancelSourcesEv',)),\n    ('transaction_fail', 0x08103004, 0x08103078, ('_ZN3app11Transaction4failENS_5FaultE',)),\n    ('transaction_abort', 0x081033c4, 0x081033d0, ('_ZN3app11Transaction5abortEv',)),\n    ('gate_halt', 0x0810ee48, 0x0810eee8, ('_ZN6motors9MotorGate4haltEv',)),\n    ('gate_inhibit', 0x0810ea12, 0x0810eab0, ('_ZN6motors9MotorGate7inhibitEv',)),\n    ('gate_zero_pwm', 0x0810e9f0, 0x0810ea12, ('_ZN6motors9MotorGate7zeroPwmEv',)),\n    ('configure_enable_low', 0x0810e35c, 0x0810e490, ('_ZN6motors8UnoQPort18configureEnableLowEPv',)),\n    ('configure_pwm', 0x0810e6a8, 0x0810e794, ('_ZN6motors8UnoQPort12configurePwmEPvNS_7ChannelE',)),\n    ('write_enable', 0x0810e490, 0x0810e4f4, ('_ZN6motors8UnoQPort11writeEnableEPvb',)),\n    ('write_pwm', 0x0810e794, 0x0810e878, ('_ZN6motors8UnoQPort8writePwmEPvNS_7ChannelEjj',)),\n    ('motor_settle', 0x0810e8bc, 0x0810e97c, ('_ZN6motors8UnoQPort6settleEPv',)),\n    ('motor_clock', 0x0810e08c, 0x0810e094, ('_ZN6motors8UnoQPort7clockUsEPv',)),\n    ('candidate_period', 0x0810e050, 0x0810e064, ('_ZN6motors12_GLOBAL__N_115candidatePeriodEj',)),\n    ('map_channel', 0x0810e124, 0x0810e22c, ('_ZN6motors12_GLOBAL__N_110mapChannelEjRj',)),\n    ('enable_owned', 0x0810e2b0, 0x0810e35c, ('_ZNK6motors8UnoQPort11enableOwnedEv',)),\n    ('enable_low', 0x0810e4f4, 0x0810e528, ('_ZNK6motors8UnoQPort9enableLowEv',)),\n    ('timer_valid', 0x0810e528, 0x0810e6a8, ('_ZNK6motors8UnoQPort10timerValidEj',)),\n    ('bank_valid', 0x0810e878, 0x0810e8bc, ('_ZNK6motors8UnoQPort9bankValidEv',)),\n    ('gate_valid_port', 0x0810e9b8, 0x0810e9f0, ('_ZNK6motors9MotorGate9validPortEv',)),\n)", 1), (b"BOUNDS = {name: (0x0811621c if name == '__init_array_end' else 0x08116218)\n          for name in ('__init_array_start', '__init_array_end', '__preinit_array_start',\n                       '__preinit_array_end', '__static_thread_data_list_start', '__static_thread_data_list_end')}", b"BOUNDS = {\n    '__init_array_start': 0x081131e4,\n    '__init_array_end': 0x081131e8,\n    '__preinit_array_start': 0x081131e4,\n    '__preinit_array_end': 0x081131e4,\n    '__static_thread_data_list_start': 0x081131e4,\n    '__static_thread_data_list_end': 0x081131e4,\n}", 1), (b"label in ('global_initializer', 'candidate_rate', 'candidate_period')", b"label in ('global_initializer', 'candidate_period', 'map_channel')", 1), (b"label in ('init_variant', 'main')", b"label in ('init_variant', 'main', 'robot_constructor', 'fusion_observation_constructor', 'flank_constructor', 'turn_constructor', 'straight_constructor', 'line_thresholds_constructor', 'qtr_report_constructor', 'line_snapshot_constructor', 'robot_result_constructor')", 1), (b"sections[0]['address'] == 0x08116218", b"sections[0]['address'] == 0x081131e4", 1), (b'int(lines[0][0], 16) == 0x08116218', b'int(lines[0][0], 16) == 0x081131e4', 1), (b'return dict(address=0x08116218, bytes_hex=data.hex(), pointer=pointer, bounds=BOUNDS)', b'return dict(address=0x081131e4, bytes_hex=data.hex(), pointer=pointer, bounds=BOUNDS)', 1), (b'pointer == 0x08100105', b'pointer == 0x08100101', 1))


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
    abi = _module('_sumox_d217_entry_abi', root / ABI, snapshots[ABI])
    original_projection = abi.project_reader

    def composed_projection(raw):
        return project_reader(original_projection(raw))

    abi.project_reader = composed_projection
    reader = abi.load_reader(root=root)
    parser = _module('_sumox_d217_entry_parser', root / PARSER, parser_raw)
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
