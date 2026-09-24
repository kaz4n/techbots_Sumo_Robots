# Tests D118's exact unchanged-app observation from public contracts and literal bytes.
# Earlier app source context is disclosed; the prospective collector body was not read.
# Standard filesystem, clock and subprocess fixtures never contact a board or MCU.
from contextlib import ExitStack, redirect_stdout, redirect_stderr
import copy
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import re
import stat
import struct
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools'))
from tests.fixtures import recorder_heap_vectors as heap_vectors

# Keep the adopted literal separately rather than derive it from decoder constants.
SOURCE = 'e820c0e16c29cfd289889273f02721a995e5336b14397f64d6093cffd42b8b69'
ARTIFACT = Path('/home/arduino/sumox26-capture-input/app_default_' + SOURCE)
OUTPUT_ROOT = Path('/home/arduino/sumox26-capture')
OPENOCD = '/opt/openocd/bin/openocd'
READELF = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-readelf'
LOADER_ROOT = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx'
HELPER = '/opt/openocd/share/openocd/scripts/target/swj-dp.tcl'
CONFIG = str(ROOT / 'tools/p0_mem_read.cfg')
POOL_BASE, POOL_SIZE = 0x20013890, 262144
DESCRIPTOR, LIST = 0x2000112c, 0x200017bc
RUNTIME_OFFSET, TRANSACTION_OFFSET = 164664, 162128
BSS_SIZE, RUNTIME_SIZE = 167272, 166376
MAX_PLAN = {'reads': 62, 'commands': 66, 'requested_bytes': 1405088}
LAYOUT = {'bss_section': 8, 'bss_size': BSS_SIZE, 'bss_alignment': 8,
          'runtime_offset': 0, 'runtime_size': RUNTIME_SIZE,
          'runtime_report_offset': RUNTIME_OFFSET, 'runtime_prefix_size': 28,
          'transaction_report_offset': TRANSACTION_OFFSET, 'transaction_prefix_size': 24}
R_PHASES = ['NOT_STARTED', 'RUNNING', 'STOPPED', 'FAULT', 'STOP_OBSERVING']
R_FAULTS = ['NONE', 'PORT', 'CLOCK', 'SERVICE_LIMIT', 'TRANSACTION', 'PROJECTION']
T_PHASES = ['NOT_INITIALIZED', 'IDLE', 'ACQUIRING', 'DECIDED', 'FAULT']
T_FAULTS = ['NONE', 'SETUP', 'ORDER', 'CLOCK', 'IDENTITY', 'RECEIPT', 'ABORTED']
R_BYTES = ['phase', 'fault', 'fresh', 'initialization_complete', 'raw_lines',
           'imu_expired', 'calibration_interrupted']
R_WORDS = ['next_release_us', 'missed_releases', 'epochs', 'service_passes', 'maximum_execution_us']
T_BYTES = ['phase', 'fault', 'decision_made', 'finished', 'timing_valid']
T_WORDS = ['started_us', 'decision_us', 'completed_us', 'execution_us']


def runtime(phase=1, fault=0, epoch=17, flags=(1, 0, 1, 0, 1), padding=0xA5,
            words=None):
    return struct.pack('<8B5I', phase, fault, *flags, padding,
                       *(words if words is not None else (0xFFFFFFFE, 9, epoch, 11, 0xFFFFFFFF)))


def transaction(phase=1, fault=0, flags=(1, 0, 1), padding=b'\x81\x92\xA3', words=None):
    return struct.pack('<5B3s4I', phase, fault, *flags, padding,
                       *(words if words is not None else (0xFFFFFFFF, 3, 1, 0x80000000)))


def sample_expected(blob, kind):
    byte_names, word_names, phases, faults = (R_BYTES, R_WORDS, R_PHASES, R_FAULTS) if kind == 'r' else (
        T_BYTES, T_WORDS, T_PHASES, T_FAULTS)
    value = dict(zip(byte_names, blob[:len(byte_names)]))
    value.update(zip(word_names, struct.unpack_from('<' + 'I' * len(word_names), blob, 8)))
    value['phase_name'] = phases[value['phase']] if value['phase'] < len(phases) else 'UNKNOWN'
    value['fault_name'] = faults[value['fault']] if value['fault'] < len(faults) else 'UNKNOWN'
    return value


def changed(blob, offset, value, fmt='B'):
    result = bytearray(blob)
    struct.pack_into('<' + fmt, result, offset, value)
    return bytes(result)


def load_subject():
    # Import machinery loads code normally; module-level Path/process/clock work is forbidden.
    importlib.import_module('p0_capture')
    importlib.import_module('recorder_heap')
    with ExitStack() as guards:
        for owner, name in ((Path, 'open'), (Path, 'read_bytes'), (Path, 'mkdir'), (Path, 'stat'),
                            (Path, 'resolve'), (Path, 'exists'), (Path, 'is_file'),
                            (subprocess, 'run'), (subprocess, 'Popen'), (time, 'monotonic')):
            guards.enter_context(mock.patch.object(owner, name, side_effect=AssertionError('import ' + name)))
        return importlib.import_module('app_default_capture')


class AppSamplesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_subject()

    def decode(self, values=None):
        values = values or (runtime(), transaction(), runtime(epoch=18), transaction())
        result = self.module.decode_app_samples(*values)
        self.assertEqual(set(result), {'runtime', 'transaction', 'errors',
                                      'runtime_observation', 'transaction_fault_sampled'})
        self.assertEqual(len(result['runtime']), 2)
        self.assertEqual(len(result['transaction']), 2)
        errors = [(e['code'], e['path']) for e in result['errors']]
        self.assertEqual(len(errors), len(set(errors)))
        for error in result['errors']:
            self.assertEqual(set(error), {'code', 'path'})
            self.assertIn(error['code'], ('EXTENT', 'ENUM', 'BOOLEAN'))
        for slot, kind, index in ((0, 'r', 0), (1, 't', 0), (2, 'r', 1), (3, 't', 1)):
            actual = result['runtime' if kind == 'r' else 'transaction'][index]
            if type(values[slot]) is bytes and len(values[slot]) == (28 if kind == 'r' else 24):
                self.assertEqual(actual, sample_expected(values[slot], kind))
                for key, value in actual.items():
                    if not key.endswith('_name'):
                        self.assertIs(type(value), int)
            else:
                self.assertIsNone(actual)
        return result

    def test_literal_prefixes_preserve_every_field_and_live_inconsistency(self):
        result = self.decode()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['runtime_observation'], 'RUNNING_COUNTER_ADVANCED')
        self.assertIs(result['transaction_fault_sampled'], False)
        self.assertEqual(result['transaction'][0]['started_us'], 0xFFFFFFFF)
        self.assertEqual(result['transaction'][0]['execution_us'], 0x80000000)

    def test_all_known_phase_fault_values_and_fault_priority(self):
        for rphase in range(5):
            for rfault in range(6):
                for tphase in range(5):
                    for tfault in range(7):
                        with self.subTest(rphase=rphase, rfault=rfault, tphase=tphase, tfault=tfault):
                            values = (runtime(rphase, rfault), transaction(tphase, tfault),
                                      runtime(rphase, rfault, 18), transaction())
                            value = self.decode(values)
                            expected = 'FAULT_SAMPLED' if rphase == 3 or rfault else (
                                'RUNNING_COUNTER_ADVANCED' if rphase == 1 else 'INCONCLUSIVE_SAMPLED')
                            self.assertEqual(value['runtime_observation'], expected)
                            self.assertIs(value['transaction_fault_sampled'], tphase == 4 or tfault != 0)
                            self.assertEqual(value['errors'], [])

    def test_both_runtime_samples_control_fault_and_progress(self):
        for slot in (0, 2):
            for phase, fault in ((3, 0), (1, 1), (0, 5)):
                values = [runtime(), transaction(), runtime(epoch=18), transaction()]
                values[slot] = runtime(phase, fault)
                self.assertEqual(self.decode(values)['runtime_observation'], 'FAULT_SAMPLED')
        for a, b in ((0, 1), (0xFFFFFFFE, 0xFFFFFFFF), (7, 7), (8, 7),
                     (0xFFFFFFFF, 0), (0xFFFFFFFF, 0xFFFFFFFF)):
            result = self.decode((runtime(epoch=a), transaction(), runtime(epoch=b), transaction()))
            self.assertEqual(result['runtime_observation'],
                             'RUNNING_COUNTER_ADVANCED' if b > a else 'INCONCLUSIVE_SAMPLED')
        for phase in (0, 2, 4):
            self.assertEqual(self.decode((runtime(phase), transaction(), runtime(epoch=18), transaction()))[
                'runtime_observation'], 'INCONCLUSIVE_SAMPLED')

    def test_all_boolean_combinations_are_observations_not_cross_state_rules(self):
        for rbits in range(32):
            for tbits in range(8):
                rflags = tuple((rbits >> i) & 1 for i in range(5))
                tflags = tuple((tbits >> i) & 1 for i in range(3))
                result = self.decode((runtime(flags=rflags), transaction(3, flags=tflags),
                                      runtime(epoch=18, flags=rflags), transaction(2, flags=tflags)))
                self.assertEqual(result['errors'], [])
                self.assertIs(result['transaction_fault_sampled'], False)

    def test_padding_and_all_u32_extremes_have_no_extra_semantic_validation(self):
        for value in (0, 1, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF):
            result = self.decode((runtime(padding=255, words=(value,) * 5),
                                  transaction(padding=b'\xff\x00\xfe', words=(value,) * 4),
                                  runtime(padding=0, words=(value,) * 5), transaction(words=(value,) * 4)))
            self.assertEqual(result['errors'], [])
            self.assertEqual(result['runtime_observation'], 'INCONCLUSIVE_SAMPLED')

    def test_every_argument_type_extent_and_null_slot(self):
        good = [runtime(), transaction(), runtime(epoch=18), transaction()]
        for slot in range(4):
            for bad in (None, 'x', bytearray(good[slot]), memoryview(good[slot]),
                        b'', good[slot][:-1], good[slot] + b'\0', 42):
                with self.subTest(slot=slot, kind=type(bad).__name__):
                    values = list(good)
                    values[slot] = bad
                    result = self.decode(values)
                    path = ('runtime' if slot % 2 == 0 else 'transaction') + f'[{slot // 2}]'
                    self.assertIn({'code': 'EXTENT', 'path': path}, result['errors'])
                    self.assertEqual(result['runtime_observation'], 'MALFORMED_SAMPLE')
                    self.assertIs(result['transaction_fault_sampled'], None if slot % 2 else False)

    def test_unknown_enums_and_invalid_bools_preserve_exact_raw_values(self):
        good = [runtime(), transaction(), runtime(epoch=18), transaction()]
        for slot in range(4):
            names = R_BYTES if slot % 2 == 0 else T_BYTES
            for offset, name in enumerate(names):
                for invalid in (255, 254) if offset < 2 else (2, 255):
                    values = list(good)
                    values[slot] = changed(values[slot], offset, invalid)
                    result = self.decode(values)
                    path = ('runtime' if slot % 2 == 0 else 'transaction') + f'[{slot // 2}].{name}'
                    self.assertIn({'code': 'ENUM' if offset < 2 else 'BOOLEAN', 'path': path}, result['errors'])
                    self.assertEqual(result['runtime_observation'], 'MALFORMED_SAMPLE')
                    self.assertIs(result['transaction_fault_sampled'], None if slot % 2 else False)

    def test_known_transaction_fault_wins_true_over_other_malformed_evidence(self):
        bad_values = (None, changed(transaction(), 0, 255), changed(transaction(), 1, 255),
                      changed(transaction(), 2, 2))
        for bad in bad_values:
            for phase, fault in ((4, 0), (1, 1), (1, 6), (4, 255), (255, 2)):
                for first, second in ((bad, transaction(phase, fault)), (transaction(phase, fault), bad)):
                    result = self.decode((runtime(), first, runtime(epoch=18), second))
                    self.assertIs(result['transaction_fault_sampled'], True)
                    self.assertEqual(result['runtime_observation'], 'MALFORMED_SAMPLE')

    def test_diagnostic_order_is_acquisition_then_phase_fault_boolean_offsets(self):
        result = self.decode((bytes([255] * 7) + runtime()[7:],
                              bytes([255] * 5) + transaction()[5:],
                              bytes([255] * 7) + runtime()[7:],
                              bytes([255] * 5) + transaction()[5:]))
        order = [f'{kind}[{index}].{name}' for kind, index, fields in (
            ('runtime', 0, R_BYTES), ('transaction', 0, T_BYTES),
            ('runtime', 1, R_BYTES), ('transaction', 1, T_BYTES)) for name in fields]
        positions = [order.index(error['path']) for error in result['errors']]
        self.assertEqual(positions, sorted(positions))
        self.assertTrue(positions)
        self.assertIsNone(result['transaction_fault_sampled'])

    def test_pure_decode_and_capture_construction_are_passive(self):
        values = (runtime(), transaction(), runtime(epoch=18), transaction())
        with ExitStack() as guards:
            for owner, name in ((Path, 'read_bytes'), (Path, 'open'), (Path, 'mkdir'),
                                (Path, 'stat'), (os, 'open'), (subprocess, 'run'), (time, 'monotonic')):
                guards.enter_context(mock.patch.object(owner, name, side_effect=AssertionError(name)))
            self.assertEqual(self.module.decode_app_samples(*values)['errors'], [])
            self.module.Capture(Path('/never-created'), {})


PIN_HASHES = {
    OPENOCD: '04778a80c5c619ee4eef7505db91328f1d7e789107c496f2ddcf96d081f5b0ff',
    HELPER: 'aad132008735bbafea3d18a304632c638f0fb99bfc19530c9f577eda2b10410a',
    READELF: 'c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e',
    LOADER_ROOT + '.bin': '6b2ffd3a24aa77ca40bac1a8c61460c5cdd3292a2ff38cb377b938a6ac939713',
    LOADER_ROOT + '.elf': '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd',
    CONFIG: '89d16a28a1489c23ec743be55ade39824f9ca5213b02b20ef4785079122e4339',
    str(ROOT / 'tools/p0_capture.py'): '885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c',
    str(ROOT / 'tools/recorder_heap.py'): 'd661024975925a7d8a83f4b772199bbf59911adb5adb8ea69a2082b69eed4b92',
    str(ARTIFACT / 'app.ino.elf'): '8379f152554649fd1b96165f29fda1f165c2b5cfc51d8dca430a37e19f693257',
    str(ARTIFACT / 'app.ino.elf-zsk.bin'): 'c60443cd8d90c26a85591153dfa38d5f9233bd686b413b2ab7daa3e1457f6df5',
}
ELF_HEADER = '''ELF Header:
  Class:                             ELF32
  Data:                              2's complement, little endian
  Type:                              REL (Relocatable file)
  Machine:                           ARM
Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 8] .bss              NOBITS          00015740 0168e0 028d68 00  WA  0   0  8
'''
ELF_SYMBOLS = '''Symbol table '.symtab' contains 1 entries:
   Num:    Value  Size Type    Bind   Vis      Ndx Name
     1: 00000000 166376 OBJECT  LOCAL  DEFAULT    8 _ZN12_GLOBAL__N_17runtimeE
'''


def loader_image_reference(blob):
    """Literal ELF PT_LOAD concatenation independently checks the opaque fixture."""
    phoff = struct.unpack_from('<I', blob, 28)[0]
    stride, count = struct.unpack_from('<HH', blob, 42)
    image, covered = bytearray(263680), 0
    for index in range(count):
        kind, offset, virtual, physical, size = struct.unpack_from('<5I', blob, phoff + stride * index)
        del virtual
        if kind != 1 or not size or not 0x08000000 <= physical < 0x08040600:
            continue
        assert physical == 0x08000000 + covered and covered + size <= len(image)
        image[covered:covered + size] = blob[offset:offset + size]
        covered += size
    assert covered == 263680
    return bytes(image)


def node(next_address=0, name=b'sketch', bss=POOL_BASE + 88, **changes):
    blob = bytearray(196)
    struct.pack_into('<I', blob, 0, next_address)
    blob[4:20] = (name + b'\0').ljust(16, b'\0')[:16]
    struct.pack_into('<I', blob, 32, bss)
    blob[71] = 1
    struct.pack_into('<I', blob, 92, BSS_SIZE)
    struct.pack_into('<II', blob, 184, 16, 0x0812AD30)
    blob[192] = 0
    for offset, value in changes.items():
        blob[int(offset)] = value
    return bytes(blob)


def read_plan(addresses, present=True, bss=POOL_BASE + 88):
    def flash(when):
        result = []
        for kind, base, size in (('loader', 0x08000000, 263680), ('sketch', 0x08100000, 176048)):
            result += [(f'{kind}-{when}-{i:02}', base + offset, min(65536, size - offset), kind)
                       for i, offset in enumerate(range(0, size, 65536))]
        return result
    def pool(number):
        return [(f'pool-{number}-{i:02}', POOL_BASE + i * 16384, 16384, 'ram') for i in range(16)]
    result = flash('before') + [('heap-descriptor-before', DESCRIPTOR, 24, 'ram')] + pool(1)
    result += [('llext-list-before', LIST, 8, 'ram')]
    result += [(f'node-before-{i + 1}', address, 196, 'ram') for i, address in enumerate(addresses)]
    if present:
        result += [('runtime-first', bss + RUNTIME_OFFSET, 28, 'ram'),
                   ('transaction-first', bss + TRANSACTION_OFFSET, 24, 'ram')]
    result += pool(2) + [('heap-descriptor-after', DESCRIPTOR, 24, 'ram')]
    if present:
        result += [('runtime-second', bss + RUNTIME_OFFSET, 28, 'ram'),
                   ('transaction-second', bss + TRANSACTION_OFFSET, 24, 'ram')]
    result += [(f'node-after-{i + 1}', address, 196, 'ram') for i, address in enumerate(addresses)]
    return result + [('llext-list-after', LIST, 8, 'ram')] + flash('after')


class CollectorFixture:
    """Maps only standard filesystem/process/clock calls; production helpers remain real."""
    _files = None

    @classmethod
    def inputs(cls):
        if cls._files is not None:
            return cls._files
        target = ROOT / 'state/analysis/P2_dump_fifo_raw/target_e820c0e1_bench-default'
        loader = ROOT / 'state/analysis/P2_ui_adc_probe_raw/root_capture_inputs'
        external = ROOT / 'state/analysis/P2_app_default_probe_raw/fixture_tools'
        locations = {OPENOCD: external / 'openocd.bin', HELPER: external / 'swj-dp.tcl',
                     READELF: external / 'readelf.bin',
                     LOADER_ROOT + '.elf': loader / 'zephyr-arduino_uno_q_stm32u585xx.elf',
                     LOADER_ROOT + '.bin': loader / 'zephyr-arduino_uno_q_stm32u585xx.bin',
                     str(ARTIFACT / 'app.ino.elf'): target / 'app.ino.elf',
                     str(ARTIFACT / 'app.ino.elf-zsk.bin'): target / 'app.ino.elf-zsk.bin'}
        cls._files = {path: locations.get(path, Path(path)).read_bytes() for path in PIN_HASHES}
        for path, blob in cls._files.items():
            assert hashlib.sha256(blob).hexdigest() == PIN_HASHES[path], path
        return cls._files

    def __init__(self, module, folder, count=1, present=True, bss=POOL_BASE + 88):
        self.module, self.sandbox = module, Path(folder)
        self.folder = OUTPUT_ROOT / ('d118-' + self.sandbox.name)
        self.output = self.sandbox / 'result'
        self.files = dict(self.inputs())
        self.virtual_dirs = {str(ARTIFACT), str(OUTPUT_ROOT)}
        for name in self.files:
            self.virtual_dirs.update(str(parent) for parent in Path(name).parents)
        self.loader = loader_image_reference(self.files[LOADER_ROOT + '.elf'])
        self.addresses = [POOL_BASE + 200000 + i * 256 for i in range(count)]
        self.bss, self.present = bss, present and count > 0
        self.plan = read_plan(self.addresses, self.present, bss)
        self.pools = [heap_vectors.all_used(), heap_vectors.all_used()]
        self.memory = {'heap-descriptor-before': struct.pack('<6I', POOL_BASE, POOL_BASE, POOL_SIZE, 0, 0, 0),
                       'llext-list-before': struct.pack('<II', self.addresses[0] if count else 0,
                                                      self.addresses[-1] if count else 0),
                       'runtime-first': runtime(), 'transaction-first': transaction(),
                       'runtime-second': runtime(epoch=18), 'transaction-second': transaction()}
        for index in range(count):
            name = b'sketch' if index == count - 1 and self.present else b'lib' + bytes([0x80 + index])
            self.memory[f'node-before-{index + 1}'] = node(
                self.addresses[index + 1] if index + 1 < count else 0, name, bss)
        self.header, self.symbols = ELF_HEADER, ELF_SYMBOLS
        self.overrides, self.symlinks, self.nonfiles, self.missing = {}, set(), set(), set()
        self.commands, self.reads, self.paths, self.timeouts, self.file_reads = [], [], [], [], []
        self.now, self.report = 100.0, {}
        self.on_command, self.on_file = None, None
        self.command_failure = None
        self.context = ExitStack()

    def payload(self, label, address, size, region):
        if label in self.overrides:
            return self.overrides[label]
        if region == 'loader':
            return self.loader[address - 0x08000000:address - 0x08000000 + size]
        if region == 'sketch':
            image = self.files[str(ARTIFACT / 'app.ino.elf-zsk.bin')]
            return image[address - 0x08100000:address - 0x08100000 + size]
        if label.startswith('pool-'):
            return self.pools[int(label[5]) - 1][address - POOL_BASE:address - POOL_BASE + size]
        return self.memory[label.replace('-after', '-before')]

    @staticmethod
    def stream_output(options, key, value):
        stream = options.get(key)
        if hasattr(stream, 'write'):
            try:
                stream.write(value)
            except TypeError:
                stream.write(value.encode())
            stream.flush()

    def run(self, argv, **options):
        argv = [str(value) for value in argv]
        self.commands.append(argv)
        assert options.get('shell', False) is False
        assert 0 < options['timeout'] <= 30
        self.timeouts.append(options['timeout'])
        number = len(self.commands)
        expected = ([OPENOCD, '--version'], [READELF, '--version'],
                    [READELF, '-h', '-S', '-W', str(ARTIFACT / 'app.ino.elf')],
                    [READELF, '-s', '-W', str(ARTIFACT / 'app.ino.elf')])
        output = ('Open On-Chip Debugger 0.12.0\n', 'GNU readelf (GNU Binutils) 2.38\n',
                  self.header, self.symbols)[number - 1] if number <= 4 else 'bounded fixture memory read\n'
        if number <= 4:
            assert argv == expected[number - 1], argv
        else:
            assert len(argv) == 7 and argv[:3] == [OPENOCD, '-f', CONFIG], argv
            assert argv[3] == '-c' and argv[5:] == ['-c', 'shutdown'], argv
            parsed = re.fullmatch(r'dump_image \{([^{}]+)\} (0x[0-9a-fA-F]+) ([0-9]+)', argv[4])
            assert parsed, argv
            path, address, size = Path(parsed[1]), int(parsed[2], 16), int(parsed[3])
            assert path.parent == self.folder
            assert len(self.reads) < len(self.plan), 'No additional private read'
            label, planned_address, planned_size, region = self.plan[len(self.reads)]
            assert (address, size) == (planned_address, planned_size), (label, address, size)
            self.reads.append((label, address, size, region))
            self.paths.append(path)
            value = self.payload(label, address, size, region)
            if isinstance(value, Exception):
                path.write_bytes(b'actual-partial-blob')
                raise value
            path.write_bytes(value)
        self.stream_output(options, 'stdout', output)
        self.stream_output(options, 'stderr', 'fixture stderr retained\n')
        if self.on_command:
            self.on_command(argv, options)
        if self.command_failure and self.command_failure[0] == number:
            failure = self.command_failure[1]
            if isinstance(failure, Exception):
                raise failure
            return subprocess.CompletedProcess(argv, failure, output, 'fixture stderr retained\n')
        return subprocess.CompletedProcess(argv, 0, output, 'fixture stderr retained\n')

    def mapped(self, path):
        path = Path(path)
        if path == OUTPUT_ROOT:
            return self.sandbox
        if path == self.folder or self.folder in path.parents:
            return self.output / path.relative_to(self.folder)
        return path

    def filesystem_patches(self):
        fixture = self
        original_open, original_read = Path.open, Path.read_bytes
        original_stat, original_exists = Path.stat, Path.exists
        original_file, original_link, original_dir = Path.is_file, Path.is_symlink, Path.is_dir
        original_iterdir, original_mkdir, original_chmod = Path.iterdir, Path.mkdir, os.chmod
        virtual_dirs = self.virtual_dirs
        mapped = self.mapped
        def mkdir(path, *args, **kwargs):
            destination = mapped(path)
            assert destination == fixture.sandbox or fixture.sandbox in destination.parents
            return original_mkdir(destination, *args, **kwargs)
        def touch(path):
            fixture.file_reads.append(str(path))
            if fixture.on_file:
                fixture.on_file(str(path))
            if str(path) in fixture.missing:
                raise FileNotFoundError(str(path))
        def read(path):
            if str(path) in fixture.files:
                touch(path)
                return fixture.files[str(path)]
            return original_read(mapped(path))
        def opened(path, mode='r', *args, **kwargs):
            if str(path) in fixture.files and 'r' in mode:
                touch(path)
                data = fixture.files[str(path)]
                return io.BytesIO(data) if 'b' in mode else io.StringIO(data.decode(kwargs.get('encoding') or 'utf-8'))
            return original_open(mapped(path), mode, *args, **kwargs)
        def exists(path):
            if str(path) in fixture.missing:
                return False
            return str(path) in fixture.files or str(path) in virtual_dirs or original_exists(mapped(path))
        def stat_result(path, *args, **kwargs):
            if str(path) in fixture.missing:
                raise FileNotFoundError(str(path))
            if str(path) in fixture.files or str(path) in virtual_dirs:
                fields = list(original_stat(fixture.sandbox))
                fields[0] = stat.S_IFDIR | 0o700 if str(path) in virtual_dirs else stat.S_IFREG | 0o600
                fields[6] = len(fixture.files.get(str(path), b''))
                return os.stat_result(fields)
            return original_stat(mapped(path), *args, **kwargs)
        def iterdir(path):
            if path == ARTIFACT:
                return iter(Path(name) for name in fixture.files if Path(name).parent == ARTIFACT)
            return original_iterdir(mapped(path))
        return [(Path, 'open', opened), (Path, 'read_bytes', read), (Path, 'exists', exists),
                   (Path, 'stat', stat_result), (Path, 'iterdir', iterdir),
                   (Path, 'mkdir', mkdir),
                   (os, 'chmod', lambda p, *a, **k: original_chmod(mapped(p), *a, **k)),
                   (Path, 'is_file', lambda p: False if str(p) in fixture.nonfiles | fixture.missing else
                    (str(p) in fixture.files or original_file(mapped(p)))),
                   (Path, 'is_dir', lambda p: str(p) in virtual_dirs or original_dir(mapped(p))),
                   (Path, 'is_symlink', lambda p: str(p) in fixture.symlinks or original_link(mapped(p))),
                   (subprocess, 'run', self.run), (time, 'monotonic', lambda: self.now)]

    def __enter__(self):
        for owner, name, callback in self.filesystem_patches():
            self.context.enter_context(mock.patch.object(owner, name, callback))
        self.capture = self.module.Capture(self.folder, self.report)
        return self

    def __exit__(self, *args):
        return self.context.__exit__(*args)

    def collect(self, artifact=ARTIFACT):
        return self.module.collect(self.capture, artifact)


class AppCollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_subject()
        cls.heap = importlib.import_module('recorder_heap')

    def schema(self, fixture, result):
        self.assertIs(result, fixture.report)
        for key in ('schema_version', 'collection_status', 'counts', 'maximum_read_plan',
                    'output_directory', 'layout', 'extension', 'heap', 'app_samples', 'errors'):
            self.assertIn(key, result)
        self.assertEqual(result['schema_version'], 1)
        self.assertEqual(result['maximum_read_plan'], MAX_PLAN)
        self.assertEqual(result['output_directory'], str(fixture.folder))
        self.assertEqual(result['counts'], {'commands': len(fixture.commands), 'reads': len(fixture.reads),
                                          'requested_bytes': sum(item[2] for item in fixture.reads)})
        for key in ('before', 'after', 'comparison'):
            self.assertIn(key, result['heap'])
        for key in ('status', 'nodes', 'sketch'):
            self.assertIn(key, result['extension'])
        for error in result['errors']:
            self.assertIsInstance(error['type'], str)
            self.assertIsInstance(error['message'], str)
            self.assertNotEqual(error['type'], 'AssertionError', error)
        return result

    def good(self, fixture):
        result = self.schema(fixture, fixture.collect())
        self.assertEqual(result['collection_status'], 'CAPTURED', result.get('errors'))
        self.assertEqual(result['errors'], [])
        for key, value in LAYOUT.items():
            self.assertEqual(result['layout'][key], value)
        self.assertEqual(fixture.reads, fixture.plan)
        self.assertEqual(len(fixture.commands), 4 + len(fixture.plan))
        self.assertEqual(result['extension']['status'], 'PRESENT' if fixture.present else 'ABSENT')
        self.assertEqual(len(result['extension']['nodes']), len(fixture.addresses))
        self.assertEqual(stat.S_IMODE(fixture.output.stat().st_mode), 0o700)
        return result

    def failed(self, fixture, maximum_reads=None, maximum_commands=None):
        result = self.schema(fixture, fixture.collect())
        self.assertEqual(result['collection_status'], 'FAILED')
        self.assertEqual(result['extension']['status'], 'UNKNOWN')
        self.assertIsNone(result['extension']['sketch'])
        self.assertTrue(result['errors'])
        if maximum_reads is not None:
            self.assertLessEqual(len(fixture.reads), maximum_reads)
        if maximum_commands is not None:
            self.assertLessEqual(len(fixture.commands), maximum_commands)
        self.assertEqual(len(fixture.commands), len(set(tuple(argv) for argv in fixture.commands)))
        return result

    def test_one_and_three_nodes_have_exact_read_trace_schema_and_real_heap_results(self):
        for count in (1, 3):
            with self.subTest(count=count), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder, count) as fixture:
                    result = self.good(fixture)
                    self.assertEqual(result['extension']['sketch'], {
                        'node_address': fixture.addresses[-1], 'bss_address': POOL_BASE + 88,
                        'runtime_address': POOL_BASE + 88})
                    for index, observed in enumerate(result['extension']['nodes']):
                        raw_name = fixture.memory[f'node-before-{index + 1}'][4:20].split(b'\0', 1)[0]
                        self.assertEqual(observed['address'], fixture.addresses[index])
                        self.assertEqual(bytes.fromhex(observed['name_hex']), raw_name)
                    self.assertEqual(result['heap']['before'], self.heap.decode_pool(fixture.pools[0]))
                    self.assertEqual(result['heap']['after'], self.heap.decode_pool(fixture.pools[1]))
                    self.assertEqual(result['heap']['comparison'], self.heap.compare_pools(*fixture.pools))
                    self.assertEqual(result['app_samples']['runtime_observation'], 'RUNNING_COUNTER_ADVANCED')
                    self.assertIs(result['app_samples']['transaction_fault_sampled'], False)
                    self.assertEqual(result['counts']['reads'], 58 if count == 1 else 62)
                    self.assertEqual(result['counts']['requested_bytes'], 1404304 if count == 1 else 1405088)

    def test_zero_and_three_unrelated_nodes_are_captured_absence_not_load_failure(self):
        for count in (0, 3):
            with self.subTest(count=count), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder, count, present=False) as fixture:
                    for index in range(count):
                        value = bytearray(fixture.memory[f'node-before-{index + 1}'])
                        value[71] = value[192] = 255
                        struct.pack_into('<III', value, 184, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF)
                        fixture.memory[f'node-before-{index + 1}'] = bytes(value)
                    result = self.good(fixture)
                    self.assertIsNone(result['app_samples'])
                    self.assertIsNone(result['extension']['sketch'])
                    self.assertEqual(result['counts']['reads'], 52 if count == 0 else 58)
                    self.assertEqual(result['counts']['commands'], 56 if count == 0 else 62)
                    self.assertEqual(result['counts']['requested_bytes'], 1403808 if count == 0 else 1404984)

    def test_live_payload_changes_are_distinct_from_allocator_metadata_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            with CollectorFixture(self.module, folder) as fixture:
                second = bytearray(fixture.pools[1])
                second[1000:1010] = b'live-bytes'
                fixture.pools[1] = bytes(second)
                result = self.good(fixture)
                self.assertNotEqual(result['heap']['before']['snapshot_sha256'],
                                    result['heap']['after']['snapshot_sha256'])
                self.assertEqual(result['heap']['before']['metadata_sha256'],
                                 result['heap']['after']['metadata_sha256'])

    def test_captured_fault_and_malformed_samples_do_not_become_transport_failures(self):
        variants = [('runtime-first', runtime(3), 'FAULT_SAMPLED'),
                    ('transaction-second', transaction(fault=6), 'RUNNING_COUNTER_ADVANCED'),
                    ('runtime-second', runtime(epoch=17), 'INCONCLUSIVE_SAMPLED'),
                    ('runtime-first', changed(runtime(), 0, 255), 'MALFORMED_SAMPLE'),
                    ('transaction-second', changed(transaction(), 4, 2), 'MALFORMED_SAMPLE')]
        for label, blob, outcome in variants:
            with self.subTest(label=label, outcome=outcome), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    fixture.memory[label] = blob
                    self.assertEqual(self.good(fixture)['app_samples']['runtime_observation'], outcome)

    def test_all_actual_pinned_file_hashes_are_checked_before_commands(self):
        for name in PIN_HASHES:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    original = fixture.files[name]
                    fixture.files[name] = bytes([original[0] ^ 1]) + original[1:]
                    self.failed(fixture, maximum_commands=0)

    def test_missing_nonregular_and_symlink_inputs_or_ancestry_refuse_without_commands(self):
        candidates = list(PIN_HASHES) + [str(ARTIFACT), str(ARTIFACT.parent), '/opt/openocd']
        for name in candidates:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    fixture.symlinks.add(name)
                    self.failed(fixture, maximum_commands=0)
        for condition in ('missing', 'nonfiles'):
            for name in PIN_HASHES:
                with self.subTest(condition=condition, name=name), tempfile.TemporaryDirectory() as folder:
                    with CollectorFixture(self.module, folder) as fixture:
                        getattr(fixture, condition).add(name)
                        self.failed(fixture, maximum_commands=0)

    def test_output_is_exclusively_created_after_anchor_and_existing_path_refuses(self):
        with tempfile.TemporaryDirectory() as folder:
            with CollectorFixture(self.module, folder) as fixture:
                self.assertFalse(fixture.output.exists())
                self.good(fixture)
                self.assertTrue(fixture.output.is_dir())
        for mode in ('directory', 'file', 'dangling'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    if mode == 'directory':
                        fixture.output.mkdir()
                    elif mode == 'file':
                        fixture.output.write_bytes(b'keep-me')
                    else:
                        fixture.output.symlink_to(fixture.sandbox / 'missing')
                    self.failed(fixture, maximum_commands=0)
                    if mode == 'file':
                        self.assertEqual(fixture.output.read_bytes(), b'keep-me')
                    if mode == 'dangling':
                        self.assertTrue(fixture.output.is_symlink())

    def test_wrong_artifact_extra_file_and_non_direct_output_refuse_before_commands(self):
        for path in ('/tmp/foreign', str(ARTIFACT) + '-other'):
            with self.subTest(path=path), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    result = self.schema(fixture, fixture.collect(path))
                    self.assertEqual(result['collection_status'], 'FAILED')
                    self.assertEqual(fixture.commands, [])
        with tempfile.TemporaryDirectory() as folder:
            with CollectorFixture(self.module, folder) as fixture:
                fixture.files[str(ARTIFACT / 'unexpected.bin')] = b'unexpected'
                self.failed(fixture, maximum_commands=0)
        for path in ('/tmp/outside-d118', str(OUTPUT_ROOT / 'parent' / 'child'), str(OUTPUT_ROOT)):
            with tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    fixture.capture = self.module.Capture(Path(path), fixture.report)
                    result = fixture.collect()
                    self.assertEqual(result['collection_status'], 'FAILED')
                    self.assertEqual(fixture.commands, [])

    def test_path_and_string_artifact_values_both_use_the_exact_public_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            with CollectorFixture(self.module, folder) as fixture:
                result = self.schema(fixture, fixture.collect(str(ARTIFACT)))
                self.assertEqual(result['collection_status'], 'CAPTURED', result['errors'])

    def test_every_elf_and_symbol_constraint_and_duplicate_refuses_before_ram(self):
        headers = [ELF_HEADER.replace(a, b) for a, b in (
            ('ELF32', 'ELF64'), ('little endian', 'big endian'), ('REL (Relocatable file)', 'EXEC (Executable file)'),
            ('ARM', 'AArch64'), ('[ 8]', '[ 7]'), ('NOBITS', 'PROGBITS'), ('00015740', '00015748'),
            ('0168e0', '0168e8'), ('028d68', '028d60'), (' WA ', '  A '), ('0   0  8', '0   0  4'),
            ('.bss', '.bss2'))]
        headers += [ELF_HEADER + ELF_HEADER.split('Section Headers:')[1]]
        symbols = [ELF_SYMBOLS.replace(a, b) for a, b in (
            ('00000000', '00015740'), ('166376', '166375'), ('OBJECT', 'FUNC'), ('LOCAL', 'GLOBAL'),
            ('DEFAULT', 'HIDDEN'), ('    8 ', '    7 '), ('17runtimeE', '17runtimeX'))]
        symbols += [ELF_SYMBOLS + ELF_SYMBOLS.splitlines()[-1] + '\n']
        for header, symbols_text in [(x, ELF_SYMBOLS) for x in headers] + [(ELF_HEADER, x) for x in symbols]:
            with self.subTest(header=header, symbols=symbols_text), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    fixture.header, fixture.symbols = header, symbols_text
                    self.failed(fixture, maximum_reads=0, maximum_commands=4)

    def test_full_bss_exact_used_allocation_right_boundary_and_alignment_slack(self):
        for base in (POOL_BASE + 88, POOL_BASE + 262136 - BSS_SIZE):
            with self.subTest(base=hex(base)), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder, bss=base) as fixture:
                    self.assertEqual(self.good(fixture)['extension']['sketch']['bss_address'], base)
        invalid = (POOL_BASE + 80, POOL_BASE + 84, POOL_BASE + 89,
                   POOL_BASE + 262136 - BSS_SIZE + 8, POOL_BASE + 262136 - RUNTIME_SIZE,
                   0x20000000, 0x200BFFF8, 0xFFFFFFF8)
        for base in invalid:
            with self.subTest(base=hex(base)), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder, bss=base) as fixture:
                    self.failed(fixture, maximum_reads=27)

    def test_bss_in_free_chunk_refuses_even_with_valid_nodes_elsewhere(self):
        with tempfile.TemporaryDirectory() as folder:
            with CollectorFixture(self.module, folder) as fixture:
                fixture.pools = [heap_vectors.layout([(24000, False), (8757, True)])] * 2
                self.failed(fixture, maximum_reads=27)

    def test_nodes_must_fit_aligned_used_allocation_before_any_private_read(self):
        invalid = (0x20000000, POOL_BASE + 80, POOL_BASE + 82, POOL_BASE + 262136 - 192,
                   0x200BFFF0, 0xFFFFFFFC, 0x40000000)
        for address in invalid:
            with self.subTest(address=hex(address)), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    fixture.memory['llext-list-before'] = struct.pack('<II', address, address)
                    self.failed(fixture, maximum_reads=26)
        with tempfile.TemporaryDirectory() as folder:
            with CollectorFixture(self.module, folder) as fixture:
                fixture.pools = [heap_vectors.layout([(23000, True), (9757, False)])] * 2
                self.failed(fixture, maximum_reads=26)

    def test_null_head_tail_disagreement_cycle_duplicate_and_fourth_node_refuse(self):
        for head, tail in ((0, POOL_BASE + 200000), (POOL_BASE + 200000, 0)):
            with tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    fixture.memory['llext-list-before'] = struct.pack('<II', head, tail)
                    self.failed(fixture, maximum_reads=27)
        for mode in ('cycle', 'duplicate', 'tail', 'fourth', 'next-outside'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder, 4 if mode == 'fourth' else 3) as fixture:
                    if mode == 'cycle':
                        fixture.memory['node-before-2'] = changed(fixture.memory['node-before-2'], 0,
                                                                 fixture.addresses[0], 'I')
                    elif mode == 'duplicate':
                        fixture.memory['node-before-1'] = node(fixture.addresses[1], b'sketch')
                    elif mode == 'tail':
                        fixture.memory['llext-list-before'] = struct.pack('<II', fixture.addresses[0],
                                                                         fixture.addresses[1])
                    elif mode == 'next-outside':
                        fixture.memory['node-before-2'] = changed(fixture.memory['node-before-2'], 0, 0xFFFFFFFF, 'I')
                    self.failed(fixture, maximum_reads=29)
                    self.assertFalse(any('runtime-' in row[0] for row in fixture.reads))

    def test_name_termination_and_each_selected_sketch_field_are_checked(self):
        edits = [(4, b'X' * 16), (71, 0), (71, 2), (92, 167271), (92, 0xFFFFFFFF),
                 (184, 15), (184, 17), (188, 0x0812AD34), (188, 0x20010000), (192, 1), (192, 2)]
        for offset, value in edits:
            with self.subTest(offset=offset, value=value), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    blob = bytearray(fixture.memory['node-before-1'])
                    if isinstance(value, bytes):
                        blob[offset:offset + len(value)] = value
                    else:
                        struct.pack_into('<B' if offset in (71, 192) else '<I', blob, offset, value)
                    fixture.memory['node-before-1'] = bytes(blob)
                    self.failed(fixture, maximum_reads=27)

    def test_raw_non_utf8_unrelated_names_and_bytes_after_first_nul_are_opaque(self):
        with tempfile.TemporaryDirectory() as folder:
            with CollectorFixture(self.module, folder, 3) as fixture:
                fixture.memory['node-before-1'] = node(fixture.addresses[1], b'\xff\xfe')
                fixture.memory['node-before-2'] = node(fixture.addresses[2], b'sketch-extra')
                final = bytearray(fixture.memory['node-before-3'])
                final[11:20] = b'\xff' * 9
                fixture.memory['node-before-3'] = bytes(final)
                self.good(fixture)

    def test_before_descriptor_and_heap_corruption_stop_before_list_or_node_reads(self):
        for offset, value in ((0, POOL_BASE + 8), (4, POOL_BASE + 8), (8, POOL_SIZE - 8)):
            with tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    fixture.memory['heap-descriptor-before'] = changed(
                        fixture.memory['heap-descriptor-before'], offset, value, 'I')
                    self.failed(fixture, maximum_reads=9)
        with tempfile.TemporaryDirectory() as folder:
            with CollectorFixture(self.module, folder) as fixture:
                fixture.pools[0] = changed(fixture.pools[0], 262138, 0, 'H')
                self.failed(fixture, maximum_reads=25)

    def test_after_descriptor_metadata_and_full_node_list_changes_refuse(self):
        variants = ('descriptor', 'metadata', 'invalid-second-pool', 'node-padding', 'node-next', 'list')
        for mode in variants:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    if mode == 'descriptor':
                        fixture.overrides['heap-descriptor-after'] = changed(
                            fixture.memory['heap-descriptor-before'], 23, 1)
                    elif mode == 'metadata':
                        fixture.pools[1] = heap_vectors.layout([(20000, True), (12757, True)])
                    elif mode == 'invalid-second-pool':
                        fixture.pools[1] = changed(fixture.pools[1], 262138, 0, 'H')
                    elif mode.startswith('node-'):
                        fixture.overrides['node-after-1'] = changed(fixture.memory['node-before-1'],
                                                                  150 if mode == 'node-padding' else 0, 1)
                    else:
                        fixture.overrides['llext-list-after'] = bytes(8)
                    self.failed(fixture)
                    self.assertFalse(any(row[0].startswith('loader-after') for row in fixture.reads))
                    if mode in ('descriptor', 'metadata', 'invalid-second-pool'):
                        self.assertFalse(any(row[0] == 'runtime-second' for row in fixture.reads))

    def test_each_before_after_flash_block_is_compared_in_full(self):
        labels = [(f'{kind}-{when}-{index:02}', edge) for kind, count in (('loader', 5), ('sketch', 3))
                  for when in ('before', 'after') for index in range(count) for edge in (0, -1)]
        for label, edge in labels:
            with self.subTest(label=label, edge=edge), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    row = next(row for row in fixture.plan if row[0] == label)
                    blob = bytearray(fixture.payload(*row))
                    blob[edge] ^= 1
                    fixture.overrides[label] = bytes(blob)
                    self.failed(fixture)
                    if '-before-' in label:
                        self.assertFalse(any(row[3] == 'ram' for row in fixture.reads))

    def test_launch_nonzero_timeout_short_and_partial_read_failures_return_same_report(self):
        for failure in (FileNotFoundError('fixture executable missing'),
                        subprocess.TimeoutExpired(['opaque-command'], 30, output='partial stdout', stderr='partial stderr'), 7):
            with self.subTest(failure=str(failure)), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    fixture.command_failure = (1, failure)
                    result = self.failed(fixture, maximum_commands=1)
                    if isinstance(failure, Exception):
                        self.assertEqual(result['errors'][0]['type'], type(failure).__name__)
        for value in (b'x', b'x' * 65537, RuntimeError('actual read failure')):
            with tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    fixture.overrides['loader-before-00'] = value
                    self.failed(fixture, maximum_reads=1, maximum_commands=5)
                    self.assertEqual(len(fixture.paths), 1)
                    self.assertTrue(fixture.paths[0].is_file())
                    expected = b'actual-partial-blob' if isinstance(value, Exception) else value
                    self.assertEqual(fixture.paths[0].read_bytes(), expected)

    def test_lifetime_starts_at_collect_includes_validation_and_exact_600_boundary(self):
        with tempfile.TemporaryDirectory() as folder:
            with CollectorFixture(self.module, folder) as fixture:
                fixture.now = 90000.0
                self.good(fixture)
        with tempfile.TemporaryDirectory() as folder:
            with CollectorFixture(self.module, folder) as fixture:
                fixture.on_file = lambda path: setattr(fixture, 'now', 700.0)
                self.failed(fixture, maximum_commands=0)
        for elapsed in (599.999, 600.0, 600.001):
            with self.subTest(elapsed=elapsed), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    fixture.on_command = lambda argv, options: setattr(fixture, 'now', 100.0 + elapsed)
                    if elapsed < 600:
                        self.good(fixture)
                        self.assertAlmostEqual(fixture.timeouts[1], 600 - elapsed, places=6)
                        self.assertTrue(all(0 < value <= 600 - elapsed + 1e-6 for value in fixture.timeouts[1:]))
                    else:
                        result = self.failed(fixture, maximum_commands=1)
                        self.assertTrue(result['errors'])
                        self.assertTrue(any(path.is_file() for path in fixture.output.iterdir()))

    def test_late_final_success_is_timeout_with_all_actual_bytes_retained(self):
        with tempfile.TemporaryDirectory() as folder:
            with CollectorFixture(self.module, folder) as fixture:
                def late(argv, options):
                    if len(fixture.reads) == len(fixture.plan):
                        fixture.now = 700.0
                fixture.on_command = late
                result = self.failed(fixture)
                self.assertEqual(fixture.reads, fixture.plan)
                self.assertEqual(result['counts']['commands'], 62)
                self.assertEqual(fixture.paths[-1].read_bytes(), fixture.payload(*fixture.plan[-1]))

    def test_direct_commands_and_reads_without_collect_admission_are_passive_refusals(self):
        actions = [lambda c: c.run([OPENOCD, '--version']),
                   lambda c: c.run(['sh', '-c', 'false']),
                   lambda c: c.read('heap-descriptor-before', DESCRIPTOR, 24),
                   lambda c: c.read('arbitrary', 0x40000000, 4)]
        for action in actions:
            with tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    with self.assertRaises(ValueError):
                        action(fixture.capture)
                    self.assertEqual(fixture.commands, [])
                    self.assertFalse(fixture.output.exists())

    def test_repeated_collection_preserves_original_report_and_has_no_action(self):
        for failure in (False, True):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    if failure:
                        fixture.command_failure = (1, FileNotFoundError('missing executable'))
                        self.failed(fixture)
                    else:
                        self.good(fixture)
                    old, count = copy.deepcopy(fixture.report), len(fixture.commands)
                    with self.assertRaises(ValueError):
                        fixture.collect()
                    self.assertEqual(fixture.report, old)
                    self.assertEqual(len(fixture.commands), count)
                    for action in (lambda: fixture.capture.run([OPENOCD, '--version']),
                                   lambda: fixture.capture.read('heap-descriptor-before', DESCRIPTOR, 24)):
                        with self.assertRaises(ValueError):
                            action()
                    self.assertEqual(len(fixture.commands), count)

    def test_active_arbitrary_out_of_order_replay_and_wrong_ram_request_poison_without_io(self):
        actions = [lambda c: c.run(['sh', '-c', 'false']),
                   lambda c: c.run([OPENOCD, '--version']),
                   lambda c: c.run([READELF, '-s', '-W', str(ARTIFACT / 'app.ino.elf')]),
                   lambda c: c.read('heap-descriptor-before', DESCRIPTOR, 24),
                   lambda c: c.read('unused-diagnostic', DESCRIPTOR, 24),
                   lambda c: c.read('loader-before-00', 0x08000000, 65536, 'ram'),
                   lambda c: c.read('heap-descriptor-before', DESCRIPTOR + 4, 24),
                   lambda c: c.read('heap-descriptor-before', DESCRIPTOR, 25)]
        for index, action in enumerate(actions):
            with self.subTest(action=index), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    refused = []
                    def request(argv, options):
                        fixture.on_command = None
                        with self.assertRaises(ValueError):
                            action(fixture.capture)
                        refused.append(True)
                    fixture.on_command = request
                    self.failed(fixture, maximum_commands=1)
                    self.assertEqual(refused, [True])
        with tempfile.TemporaryDirectory() as folder:
            with CollectorFixture(self.module, folder) as fixture:
                refused = []
                def replay(argv, options):
                    if fixture.reads and fixture.reads[-1][0] == 'heap-descriptor-before':
                        fixture.on_command = None
                        with self.assertRaises(ValueError):
                            fixture.capture.read('heap-descriptor-before', DESCRIPTOR, 24)
                        refused.append(True)
                fixture.on_command = replay
                self.failed(fixture, maximum_reads=9)
                self.assertEqual(refused, [True])

    def test_correct_ram_purpose_wrong_address_size_region_refuses_at_its_admission(self):
        for address, size, region in ((DESCRIPTOR + 4, 24, 'ram'), (DESCRIPTOR, 23, 'ram'),
                                      (DESCRIPTOR, 16385, 'ram'), (DESCRIPTOR, 24, 'flash'),
                                      (0x40000000, 4, 'ram'), (0xFFFFFFFF, 2, 'ram')):
            with self.subTest(address=address, size=size, region=region), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    refused = []
                    def hostile(argv, options):
                        if len(fixture.reads) == 8:
                            fixture.on_command = None
                            with self.assertRaises(ValueError):
                                fixture.capture.read('heap-descriptor-before', address, size, region)
                            refused.append(True)
                    fixture.on_command = hostile
                    self.failed(fixture, maximum_reads=8)
                    self.assertEqual(refused, [True])

    def test_cli_actual_collection_prints_persists_and_returns_honest_observation_status(self):
        scenarios = [('progress', 0), ('equal', 1), ('runtime-fault', 1),
                     ('transaction-fault', 1), ('malformed', 1), ('absent', 1), ('transport', 1)]
        for mode, expected_status in scenarios:
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder, present=mode != 'absent') as fixture:
                    if mode == 'equal':
                        fixture.memory['runtime-second'] = runtime()
                    elif mode == 'runtime-fault':
                        fixture.memory['runtime-first'] = runtime(fault=1)
                    elif mode == 'transaction-fault':
                        fixture.memory['transaction-first'] = transaction(4)
                    elif mode == 'malformed':
                        fixture.memory['transaction-second'] = changed(transaction(), 0, 255)
                    elif mode == 'transport':
                        fixture.command_failure = (1, FileNotFoundError('actual fixture launch failure'))
                    output, errors = io.StringIO(), io.StringIO()
                    with redirect_stdout(output), redirect_stderr(errors):
                        code = self.module.main(['--artifact-dir', str(ARTIFACT), '--output', str(fixture.folder)])
                    self.assertEqual(code, expected_status, errors.getvalue())
                    printed = json.loads(output.getvalue())
                    saved = json.loads((fixture.output / 'capture.json').read_text())
                    self.assertEqual(printed, saved)
                    self.assertEqual(saved['collection_status'], 'FAILED' if mode == 'transport' else 'CAPTURED')
                    self.assertEqual(saved['maximum_read_plan'], MAX_PLAN)
                    if mode == 'transport':
                        self.assertTrue(saved['errors'])
                    else:
                        self.assertEqual(saved['errors'], [])

    def test_cli_bad_arguments_do_not_create_output_or_invoke_process(self):
        for args in ([], ['--artifact-dir'], ['--artifact-dir', str(ARTIFACT), '--address', '0x20000000'],
                     ['--artifact-dir', str(ARTIFACT), '--limit', '100'],
                     ['--artifact-dir', str(ARTIFACT), '--phase', 'RUNNING']):
            with self.subTest(args=args), tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module, folder) as fixture:
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        try:
                            result = self.module.main(args)
                        except SystemExit as error:
                            result = error.code
                    self.assertEqual(result, 2)
                    self.assertEqual(fixture.commands, [])
                    self.assertFalse(fixture.output.exists())

    def test_cli_failed_creation_does_not_modify_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            with CollectorFixture(self.module, folder) as fixture:
                fixture.output.mkdir()
                protected = fixture.output / 'capture.json'
                protected.write_bytes(b'original-unowned-receipt')
                output = io.StringIO()
                with redirect_stdout(output), redirect_stderr(io.StringIO()):
                    result = self.module.main(['--artifact-dir', str(ARTIFACT), '--output', str(fixture.folder)])
                self.assertEqual(result, 1)
                self.assertEqual(json.loads(output.getvalue())['collection_status'], 'FAILED')
                self.assertEqual(protected.read_bytes(), b'original-unowned-receipt')
                self.assertEqual(fixture.commands, [])

    def test_cli_report_write_failure_cannot_return_success(self):
        with tempfile.TemporaryDirectory() as folder:
            with CollectorFixture(self.module, folder) as fixture:
                original_open = Path.open
                def refuse_report(path, *args, **kwargs):
                    if path.name == 'capture.json':
                        raise OSError('fixture final receipt write refused')
                    return original_open(path, *args, **kwargs)
                with mock.patch.object(Path, 'open', refuse_report):
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        try:
                            result = self.module.main(['--artifact-dir', str(ARTIFACT), '--output', str(fixture.folder)])
                        except OSError:
                            result = 1
                self.assertEqual(result, 1)
                self.assertEqual(fixture.reads, fixture.plan)


if __name__ == '__main__':
    unittest.main(verbosity=2)
