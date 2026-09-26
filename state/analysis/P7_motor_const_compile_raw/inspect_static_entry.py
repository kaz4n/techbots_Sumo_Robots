# Observes fixed SETTLE and entry instructions through the reviewed file-only reader.
# Preserves accepted ABI evidence and reuses the historical entry parser privately.
# Independent entry fixtures check projections, parsing, pins and attempt closure.
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import types


ROOT = Path(__file__).absolute().parents[3]
RAW = 'state/analysis/P7_motor_const_compile_raw/'
ABI = RAW + 'inspect_static_abi.py'
PARSER = 'state/analysis/P7_app_motor_fault_compile_raw/inspect_static_entry.py'
ABI_RESULT = RAW + 'native_abi_static01/result.json'
ABI_LAYOUT = RAW + 'native_abi_static01/abi.json'
ABI_CLOSURE = RAW + 'native_abi_static01/local_result.json'
ABI_REVIEW = 'state/reviews/P7_motor_const_abi_actual_review.md'
ARTIFACTS = RAW + 'native_static01/artifacts.json'
BINDING = RAW + 'entry_binding01.json'
CONTRACT = 'state/analysis/P7_motor_const_entry_contract.md'
CONTRACT_SHA = '6663d1ea7309c809d8f727fc5bf68291128e54c83ca64b7d1ce53b9ff1cea9d9'
ORIGINALS = {
    ABI: (16087, 'f360a52d6e8c29227b8a59481f37f5e8a30b207d7b66fbffaa8e8785a4dedf3c'),
    PARSER: (10317, 'cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34'),
    ABI_RESULT: (904847, 'bbdecb404a42237fafaf0bf4b2e38690b62ee45119cdfabd9b2f7dde17a6b9b0'),
    ABI_LAYOUT: (5410, '6fed52b884c6015a2c9d2f6803bea20e764418fcc94cffe144161026259f6a97'),
    ABI_CLOSURE: (275, '3cd224b237fc1b18586d7b2fb22c2a47833a801fea06b96b338027102db5d55d'),
    ABI_REVIEW: (10178, '4cd28fe8ce3b689319da5ddb42739c664fd0e4bcdc2552b521ee23b8b3331411'),
    ARTIFACTS: (9645, 'fc5eb9e233c4642e0388f14132efdebab535d55134ce39c43d33c485d67e4ddd'),
    BINDING: (44374, '7417ff7055e30238e8a3231db3287ffb3520ec8929ce3437afbd0dff1c2d60ae'),
}
READER_INPUT = (17051, '938c1de2cc35f4c57f63c411ba1ca5e732bd4f0f86788e65034c6c91b5f848e6')
READER_PROJECTED = (17075, '580abb32b2597ceed62dadb6ea28ac028d3ffb66e5e5fa2d0c42a7400ad1b9f3')
PARSER_PROJECTED = (10866, 'c4c4f9e26b35da497e6a092de361b1727759ea1a16c7026b9242037c0544c90b')
READER_REPLACEMENTS = (
    (b"'/inspect_static_abi.py'", b"'/inspect_static_entry.py'", 1),
    (b"'native_abi_static01'", b"'native_entry_static01'", 1),
    (b'app-motor-const-abi-static01', b'app-motor-const-entry-static01', 1),
    (b'D204_STATIC_FILE_ONLY_ABI', b'D205_STATIC_FILE_ONLY_ENTRY', 2),
    (b'STATIC_ABI_CHECKED', b'STATIC_ENTRY_CHECKED', 1),
    (b'STATIC_ABI_OBSERVED', b'STATIC_ENTRY_OBSERVED', 2),
    (b"'file-abi'", b"'file-entry'", 1),
    (b"'abi.json'", b"'entry.json'", 1),
    (b'StaticAbi', b'StaticEntry', 2),
)
PARSER_REPLACEMENTS = (
    (b'/home/arduino/sumox26_codex_build/app-motor-fault-static01/build/app_motor_fault.ino', b'/home/arduino/sumox26_codex_build/app-motor-const-static01/build/app_motor_observe.ino', 1),
    (b"RANGES = (\n    ('entry_point', 0x08100010, 0x081000c8, ('entry_point',)),\n    ('setup', 0x081000c8, 0x081000e8, ('setup',)),\n    ('loop', 0x081000e8, 0x08100104, ('loop',)),\n    ('global_initializer', 0x08100104, 0x08100298, ('_GLOBAL__sub_I_setup',)),\n    ('app_dump_port', 0x081002a8, 0x081002d0, ('_ZN3app12unoQDumpPortERN8recorder4dump12UnoQDumpPortE',)),\n    ('sources_port', 0x081003e0, 0x0810045c, ('_ZN3app13NativeSources4portEv',)),\n    ('sources_adc_port', 0x0810045c, 0x08100470, ('_ZN3app13NativeSources7adcPortEv',)),\n    ('runner_constructor', 0x08103984, 0x08103b58, tuple('_ZN15app_motor_fault6RunnerC' + str(n) +\n        'ERKN6motors4PortERKN5power9InputPortERKN3app10SourcePortERKNS9_8DumpPortE' for n in (1, 2))),\n    ('runner_application_valid', 0x08103b58, 0x08103bb0, ('_ZNK15app_motor_fault6Runner16applicationValidEv',)),\n    ('runner_stop_reason', 0x08103bb0, 0x08103c08, ('_ZNK15app_motor_fault6Runner10stopReasonEv',)),\n    ('runner_freeze', 0x08103c08, 0x08103c94, ('_ZN15app_motor_fault6Runner6freezeENS_6ReasonE',)),\n    ('runner_begin', 0x08103c94, 0x08103d24, ('_ZN15app_motor_fault6Runner5beginERKN11motor_fault6GrantsE',)),\n    ('runner_poll', 0x08103d24, 0x08103d78, ('_ZN15app_motor_fault6Runner4pollEv',)),\n    ('dump_port', 0x0810c760, 0x0810c774, ('_ZN8recorder4dump12UnoQDumpPort4portEv',)),\n    ('loop_hook', 0x08110bfc, 0x08110bfe, ('_Z10__loopHookv',)),\n    ('candidate_rate', 0x08110c70, 0x08110cd8, ('_ZN6motors12_GLOBAL__N_113candidateRateEj',)),\n    ('candidate_period', 0x08110cd8, 0x08110d10, ('_ZN6motors12_GLOBAL__N_115candidatePeriodEj',)),\n    ('motor_port', 0x08110ed8, 0x08110f64, ('_ZN6motors8UnoQPort4portEv',)),\n    ('power_reader_port', 0x0811326c, 0x08113290, ('_ZN5power15readerInputPortERNS_6ReaderE',)),\n    ('trace_constructor', 0x08115bec, 0x08115c7c,\n        tuple('_ZN11motor_fault5TraceC' + str(n) + 'ERKN6motors4PortE' for n in (1, 2))),\n    ('trace_port', 0x08115c7c, 0x08115cfc, ('_ZN11motor_fault5Trace4portEv',)),\n    ('memcpy', 0x08115f6c, 0x08115f74, ('memcpy',)),\n    ('memset', 0x08115f74, 0x08115f7c, ('memset',)),\n    ('unsigned_divide', 0x0811602c, 0x08116036, ('__aeabi_uldivmod',)),\n    ('init_variant', 0x08116044, 0x08116046, ('initVariant',)),\n    ('main', 0x08116048, 0x08116074, ('main',)),\n    ('start_static_threads', 0x08116074, 0x081160e0, ('_Z20start_static_threadsv',)),\n)", b"RANGES = (\n    ('entry_point', 0x08100010, 0x081000c8, ('entry_point',)),\n    ('setup', 0x081000c8, 0x081000e8, ('setup',)),\n    ('loop', 0x081000e8, 0x08100104, ('loop',)),\n    ('global_initializer', 0x08100104, 0x08100298, ('_GLOBAL__sub_I_setup',)),\n    ('app_dump_port', 0x081002a8, 0x081002d0, ('_ZN3app12unoQDumpPortERN8recorder4dump12UnoQDumpPortE',)),\n    ('sources_port', 0x081003e0, 0x0810045c, ('_ZN3app13NativeSources4portEv',)),\n    ('sources_adc_port', 0x0810045c, 0x08100470, ('_ZN3app13NativeSources7adcPortEv',)),\n    ('runner_constructor', 0x08103984, 0x08103b5c, ('_ZN17app_motor_observe6RunnerC1ERKN6motors4PortERKN5power9InputPortERKN3app10SourcePortERKNS9_8DumpPortE', '_ZN17app_motor_observe6RunnerC2ERKN6motors4PortERKN5power9InputPortERKN3app10SourcePortERKNS9_8DumpPortE')),\n    ('runner_application_valid', 0x08103b5c, 0x08103bb4, ('_ZNK17app_motor_observe6Runner16applicationValidEv',)),\n    ('runner_stop_reason', 0x08103bb4, 0x08103c20, ('_ZNK17app_motor_observe6Runner10stopReasonEv',)),\n    ('runner_freeze', 0x08103c20, 0x08103cac, ('_ZN17app_motor_observe6Runner6freezeENS_6ReasonE',)),\n    ('runner_begin', 0x08103cac, 0x08103d3c, ('_ZN17app_motor_observe6Runner5beginERKN11motor_fault6GrantsE',)),\n    ('runner_poll', 0x08103d3c, 0x08103d98, ('_ZN17app_motor_observe6Runner4pollEv',)),\n    ('dump_port', 0x0810c780, 0x0810c794, ('_ZN8recorder4dump12UnoQDumpPort4portEv',)),\n    ('loop_hook', 0x08110c1c, 0x08110c1e, ('_Z10__loopHookv',)),\n    ('candidate_period', 0x08110c90, 0x08110ca4, ('_ZN6motors12_GLOBAL__N_115candidatePeriodEj',)),\n    ('motor_port', 0x08110ea8, 0x08110f2c, ('_ZN6motors8UnoQPort4portEv',)),\n    ('power_reader_port', 0x081132a8, 0x081132cc, ('_ZN5power15readerInputPortERNS_6ReaderE',)),\n    ('trace_constructor', 0x08115c2c, 0x08115cbc, ('_ZN11motor_fault5TraceC1ERKN6motors4PortE', '_ZN11motor_fault5TraceC2ERKN6motors4PortE')),\n    ('trace_port', 0x08115cbc, 0x08115d3c, ('_ZN11motor_fault5Trace4portEv',)),\n    ('memcpy', 0x08115fac, 0x08115fb4, ('memcpy',)),\n    ('memset', 0x08115fb4, 0x08115fbc, ('memset',)),\n    ('unsigned_divide', 0x0811606c, 0x08116076, ('__aeabi_uldivmod',)),\n    ('init_variant', 0x08116084, 0x08116086, ('initVariant',)),\n    ('main', 0x08116088, 0x081160b4, ('main',)),\n    ('start_static_threads', 0x081160b4, 0x08116120, ('_Z20start_static_threadsv',)),\n    ('publish_settle', 0x08110cd4, 0x08110d10, ('_ZN6motors12_GLOBAL__N_113publishSettleENS_17SettleProbeReasonEjjhh',)),\n    ('motor_settle', 0x08111538, 0x0811165c, ('_ZN6motors8UnoQPort6settleEPv',)),\n    ('timer_valid', 0x081111a4, 0x08111324, ('_ZNK6motors8UnoQPort10timerValidEj',)),\n    ('bank_valid', 0x081114f4, 0x08111538, ('_ZNK6motors8UnoQPort9bankValidEv',)),\n    ('write_pwm', 0x08111410, 0x081114f4, ('_ZN6motors8UnoQPort8writePwmEPvNS_7ChannelEjj',)),\n    ('map_channel', 0x08110da0, 0x08110ea8, ('_ZN6motors12_GLOBAL__N_110mapChannelEjRj',)),\n)", 1),
    (b"BOUNDS = {name: (0x0811621c if name == '__init_array_end' else 0x08116218)\n          for name in ('__init_array_start', '__init_array_end', '__preinit_array_start',\n                       '__preinit_array_end', '__static_thread_data_list_start', '__static_thread_data_list_end')}", b"BOUNDS = {\n    '__init_array_start': 0x08116258,\n    '__init_array_end': 0x0811625c,\n    '__preinit_array_start': 0x08116258,\n    '__preinit_array_end': 0x08116258,\n    '__static_thread_data_list_start': 0x08116258,\n    '__static_thread_data_list_end': 0x08116258,\n}", 1),
    (b"('global_initializer', 'candidate_rate', 'candidate_period')", b"('global_initializer', 'candidate_period', 'publish_settle', 'map_channel')", 1),
    (b"sections[0]['address'] == 0x08116218", b"sections[0]['address'] == 0x08116258", 1),
    (b'int(lines[0][0], 16) == 0x08116218', b'int(lines[0][0], 16) == 0x08116258', 1),
    (b'return dict(address=0x08116218, bytes_hex=data.hex(), pointer=pointer, bounds=BOUNDS)', b'return dict(address=0x08116258, bytes_hex=data.hex(), pointer=pointer, bounds=BOUNDS)', 1),
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
    abi = _module('_sumox_d205_entry_abi', root / ABI, snapshots[ABI])
    original_projection = abi.project_reader

    def composed_projection(raw):
        return project_reader(original_projection(raw))

    abi.project_reader = composed_projection
    reader = abi.load_reader(root=root)
    parser = _module('_sumox_d205_entry_parser', root / PARSER, parser_raw)
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
