# Independently checks D147 exact native TLS extension and preserved D142 checks.
# Uses only public contracts, source-byte identity and synthetic in-memory packets.
# Refuses implementation execution until the independent expectation freeze exists.
import builtins
import collections
import hashlib
import json
from pathlib import Path
import struct
import sys
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
DRAFT = Path(__file__).resolve().parent
BASE_DRAFT = ROOT / 'state/analysis/P7_static_artifact_test_draft'
BASE_IMPL = ROOT / 'state/analysis/P7_static_link_probe_raw/static_artifacts.py'
NATIVE_IMPL = ROOT / 'state/analysis/P7_static_link_probe_raw/static_native_artifacts.py'
TLS_SOURCE = ROOT / 'state/analysis/P7_static_tls_raw/observed/tls-syms.S'
TLS_SHA = '68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70'
BASE_SHA = 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368'
LOADER_SHA = '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'


def load_source(data, name, filename):
    code = compile(data, str(filename), 'exec')
    module = types.ModuleType(name)
    module.__file__ = str(filename)
    sys.modules[name] = module
    exec(code, module.__dict__)
    return module


class BytesSubclass(bytes):
    pass


class StaticNativeArtifactsContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        freeze = json.loads((DRAFT / 'freeze_native_tls.json').read_text(encoding='utf-8'))
        if freeze.get('status') != 'FROZEN_FOR_AUTHORIZED_HOST_TEST':
            raise RuntimeError('Independent native TLS expectations are not frozen')
        for relative, expected in freeze['inputs_sha256'].items():
            if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
                raise RuntimeError('Frozen input changed: ' + relative)
        cls.native_source = TLS_SOURCE.read_bytes()
        cls.base_source = BASE_IMPL.read_bytes()
        if hashlib.sha256(cls.native_source).hexdigest() != TLS_SHA:
            raise RuntimeError('Exact public assembly fixture changed')
        if hashlib.sha256(cls.base_source).hexdigest() != BASE_SHA:
            raise RuntimeError('Opaque frozen legacy implementation bytes changed')
        support = load_source((BASE_DRAFT / 'test_static_artifacts.py').read_bytes(),
                              'native_public_test_support', BASE_DRAFT / 'test_static_artifacts.py')
        cls.effects = staticmethod(support.no_effects)
        load_source((BASE_DRAFT / 'synthetic_elf.py').read_bytes(), 'synthetic_elf',
                    BASE_DRAFT / 'synthetic_elf.py')
        cls.f = load_source((DRAFT / 'synthetic_native_elf.py').read_bytes(),
                            'independent_native_fixture', DRAFT / 'synthetic_native_elf.py')
        cls.b = cls.f.base
        native_code = compile(NATIVE_IMPL.read_bytes(), str(NATIVE_IMPL), 'exec')
        legacy_code = compile(cls.base_source, str(BASE_IMPL), 'exec')
        cls.module = types.ModuleType('independent_native_under_test')
        cls.module.__file__ = str(NATIVE_IMPL)
        cls.legacy = types.ModuleType('independent_frozen_legacy_under_test')
        cls.legacy.__file__ = str(BASE_IMPL)
        sys.modules[cls.module.__name__] = cls.module
        sys.modules[cls.legacy.__name__] = cls.legacy
        with cls.effects():
            exec(legacy_code, cls.legacy.__dict__)
            exec(native_code, cls.module.__dict__)

    def call(self, packet, native=None, frozen=None):
        native = self.native_source if native is None else native
        frozen = self.base_source if frozen is None else frozen
        with self.effects():
            return self.module.validate_artifacts(packet, native, frozen)

    def reject(self, packet):
        with self.assertRaises(ValueError):
            self.call(packet)

    def alter(self, change, name=None, packet=None):
        return self.b.mutate_elfs(self.f.packet() if packet is None else packet,
                                 change, self.f.ELF_NAMES if name is None else (name,))

    def expected(self, packet, weak=('optional_weak_hook',)):
        b = self.b
        fields = ('name', 'type', 'flags', 'address', 'size', 'alignment', 'load_address')
        rows = [('.text', 1, 6, b.FLASH, 8, 4, b.FLASH),
                ('.rodata', 1, 2, b.FLASH + 16, 8, 4, b.FLASH + 16),
                ('.data', 1, 3, b.RAM, 8, 4, b.FLASH + 32),
                ('.bss', 8, 3, b.RAM + 8, b.BSS_END - b.RAM - 8, 8, None)]
        return {
            'status': 'STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS', 'entry': b.FLASH | 1,
            'flash': {'start': b.FLASH, 'end': b.FLASH + 40,
                      'remaining': 0x081c0000 - b.FLASH - 40},
            'ram': {'start': b.RAM, 'end': b.BSS_END, 'remaining': 0x20053890 - b.BSS_END},
            'data_copy': {'source': b.FLASH + 32, 'destination': b.RAM, 'bytes': 8},
            'bss_zero': {'start': b.RAM + 8, 'end': b.RAM + 24, 'bytes': 16},
            'sections': [dict(zip(fields, row)) for row in rows],
            'weak_undefined': list(weak),
            'artifacts': {name: {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                          for name, data in packet.items()},
            'native_tls': {'source_sha256': TLS_SHA, 'loader_sha256': LOADER_SHA,
                           'symbols': [{'name': name, 'value': value, 'size': 0, 'bind': 1,
                                        'type': 6, 'other': 0, 'section': 0xfff1}
                                       for name, value in sorted(self.f.ALIASES.items())]},
        }

    def exact_types(self, actual, expected):
        self.assertIs(type(actual), type(expected))
        if isinstance(expected, dict):
            self.assertEqual(set(actual), set(expected))
            for key in expected:
                self.exact_types(actual[key], expected[key])
        elif isinstance(expected, list):
            self.assertEqual(len(actual), len(expected))
            for item, oracle in zip(actual, expected):
                self.exact_types(item, oracle)

    def test_complete_report_original_receipts_and_repeatability(self):
        packet = self.f.packet()
        before = dict(packet)
        identities = {key: id(value) for key, value in packet.items()}
        result = self.call(packet)
        self.assertEqual(result, self.expected(packet))
        self.exact_types(result, self.expected(packet))
        self.assertEqual(result, json.loads(json.dumps(result, allow_nan=False)))
        self.assertEqual(self.call(packet), result)
        self.assertEqual(packet, before)
        self.assertEqual(identities, {key: id(value) for key, value in packet.items()})
        self.assertEqual(hashlib.sha256(self.native_source).hexdigest(), TLS_SHA)
        self.assertEqual(hashlib.sha256(self.base_source).hexdigest(), BASE_SHA)

    def test_result_mutation_does_not_poison_subsequent_calls(self):
        packet = self.f.packet()
        result = self.call(packet)
        result['native_tls']['symbols'][0]['value'] = 123
        result['sections'].clear()
        result['artifacts']['app.ino.elf']['sha256'] = 'incorrect'
        self.assertEqual(self.call(packet), self.expected(packet))

    def test_all_aliases_are_required_in_every_elf_and_legacy_packet_fails(self):
        self.reject(self.b.packet())
        for image in self.f.ELF_NAMES:
            self.reject(self.alter(lambda elf: self.b.make_elf(), image))
            for alias in self.f.ALIASES:
                with self.subTest(image=image, alias=alias):
                    self.reject(self.alter(lambda elf: self.f.replace_symbols(
                        elf, [row for row in self.f.symbol_rows(elf) if row[0] != alias]), image))

    def test_every_alias_tuple_field_in_every_image(self):
        fields = {'value': (0, 9, 0x20013898, 0xffffffff), 'size': (1, 4, 0xffffffff),
                  'info': (0x06, 0x26, 0x36, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x17, 0x1f),
                  'other': (1, 2, 3, 4, 255), 'section': (0, 1, 3, 4, 0xfff2, 0xffff)}
        for image in self.f.ELF_NAMES:
            for alias in self.f.ALIASES:
                for field, values in fields.items():
                    for value in values:
                        with self.subTest(image=image, alias=alias, field=field, value=value):
                            self.reject(self.alter(lambda elf: self.b.edit_symbol(
                                elf, alias, field, value), image))

    def test_renamed_anonymous_duplicate_and_shadow_aliases_in_every_image(self):
        for image in self.f.ELF_NAMES:
            for alias in self.f.ALIASES:
                for kind in ('rename', 'anonymous', 'duplicate', 'global_shadow', 'local_shadow'):
                    def change(elf):
                        rows = self.f.symbol_rows(elf)
                        index = next(i for i, row in enumerate(rows) if row[0] == alias)
                        if kind in ('rename', 'anonymous'):
                            rows[index] = (alias + '_wrong' if kind == 'rename' else '', *rows[index][1:])
                        elif kind == 'duplicate':
                            rows.append(rows[index])
                        elif kind == 'global_shadow':
                            rows.append((alias, 0, 0, 0x10, 0, 0xfff1))
                        else:
                            rows.insert(4, (alias, 0, 0, 0, 0, 0xfff1))
                        return self.f.replace_symbols(elf, rows, 5 if kind == 'local_shadow' else 4)
                    with self.subTest(image=image, alias=alias, kind=kind):
                        self.reject(self.alter(change, image))

    def test_additional_tls_name_and_anonymous_tls_are_rejected_in_each_image(self):
        for image in self.f.ELF_NAMES:
            for name in ('extra_tls', '', '_TLS_MODULE_BASE_extra'):
                for info in (0x16, 0x26):
                    with self.subTest(image=image, name=name, info=info):
                        self.reject(self.alter(lambda elf: self.f.replace_symbols(
                            elf, self.f.symbol_rows(elf) + [(name, 8, 0, info, 0, 0xfff1)]), image))

    def test_local_alias_cannot_evade_tuple_check_by_moving_before_partition(self):
        for image in self.f.ELF_NAMES:
            for alias in self.f.ALIASES:
                def change(elf):
                    rows = self.f.symbol_rows(elf)
                    row = next(row for row in rows if row[0] == alias)
                    rows = [item for item in rows if item[0] != alias]
                    rows.insert(4, (*row[:3], 6, *row[4:]))
                    return self.f.replace_symbols(elf, rows, 5)
                with self.subTest(image=image, alias=alias):
                    self.reject(self.alter(change, image))

    def test_alias_order_and_diagnostic_differences_are_permitted(self):
        packet = self.f.packet()
        for image in self.f.ELF_NAMES:
            packet = self.alter(lambda elf: self.f.replace_symbols(
                elf, self.f.symbol_rows(elf)[:4] + list(reversed(self.f.symbol_rows(elf)[4:]))), image, packet)
        packet['app.ino_debug.elf'] = self.f.make_elf(96, b'Different metadata', weak_name='z_weak')
        packet['app.ino_temp.elf'] = self.f.make_elf(128, b'Other metadata', weak_name='a_weak')
        packet['app.ino.map'] = b'\0\xffOpaque map does not establish provenance'
        self.assertEqual(self.call(packet), self.expected(packet, ('a_weak', 'optional_weak_hook', 'z_weak')))

    def test_source_types_bounds_and_hashes_fail_before_execution(self):
        for label, good, bound in (('native', self.native_source, 65536),
                                   ('frozen', self.base_source, 32768)):
            variants = (None, '', 1, True, bytearray(good), memoryview(good), BytesSubclass(good),
                        b'', b'x', bytes(bound), bytes(bound + 1), good[:-1], good + b'\n',
                        bytes([good[0] ^ 1]) + good[1:], b'raise AssertionError("executed caller code")')
            for value in variants:
                args = [self.f.packet(), self.native_source, self.base_source]
                args[1 if label == 'native' else 2] = value
                with self.subTest(source=label, kind=type(value).__name__, size=len(value) if hasattr(value, '__len__') else None):
                    with self.effects(), mock.patch.object(builtins, 'exec', side_effect=AssertionError('Unverified source execution')):
                        with self.assertRaises(ValueError):
                            self.module.validate_artifacts(*args)

    def test_exact_argument_count(self):
        args = (self.f.packet(), self.native_source, self.base_source)
        for candidate in ((), args[:1], args[:2], args + (None,)):
            with self.assertRaises(TypeError):
                self.module.validate_artifacts(*candidate)

    def test_exact_artifact_mapping_and_nonempty_bytes_retained(self):
        for value in (None, [], (), '', 1, True, collections.UserDict(self.f.packet())):
            self.reject(value)
        for name in self.f.packet():
            packet = self.f.packet()
            del packet[name]
            self.reject(packet)
            for value in (b'', '', None, 1, True, bytearray(b'x'), memoryview(b'x')):
                packet = self.f.packet()
                packet[name] = value
                self.reject(packet)
        for key in ('extra.bin', 1, None):
            packet = self.f.packet()
            packet[key] = b'x'
            self.reject(packet)

    def test_each_original_artifact_byte_limit_retained(self):
        large = bytes(16777217)
        for name in self.f.packet():
            packet = self.f.packet()
            packet[name] = large if name not in ('app.ino.bin', 'app.ino.bin-zsk.bin') else bytes(
                786417 if name == 'app.ino.bin' else 786433)
            with self.subTest(name=name):
                self.reject(packet)

    def test_original_elf_table_section_symbol_bounds_retained(self):
        b = self.b
        changes = [lambda elf: b.edit_header(elf, 'phnum', 65),
                   lambda elf: b.edit_header(elf, 'shnum', 4097),
                   lambda elf: b.edit_header(elf, 'shoff', 0xfffffff0),
                   lambda elf: b.edit_section(elf, '.symtab', 'size', 65537 * 16),
                   lambda elf: b.edit_section(elf, '.strtab', 'offset', 0xffffffff),
                   lambda elf: b.edit_symbol(elf, '_rand_next', 'name', 0xffffffff)]
        for image in self.f.ELF_NAMES:
            for index, change in enumerate(changes):
                with self.subTest(image=image, case=index):
                    self.reject(self.alter(change, image))
        self.reject(self.f.packet(weak_name='w' * 4097))
        self.reject(self.f.packet(rodata_name='.' + 'n' * 4096))

    def test_no_tls_storage_program_section_or_relocations_admitted(self):
        b = self.b
        changes = [lambda elf: b.edit_program(elf, 2, 'type', 7),
                   lambda elf: b.edit_section(elf, '.rodata', 'flags', 0x402),
                   lambda elf: b.edit_section(elf, '.rodata', 'type', 4),
                   lambda elf: b.edit_section(elf, '.rodata', 'type', 9)]
        for image in self.f.ELF_NAMES:
            for index, change in enumerate(changes):
                with self.subTest(image=image, case=index):
                    self.reject(self.alter(change, image))
        for name in ('.tdata', '.tdata.extra', '.tbss', '.got', '.plt', '.ARM.attributes', '.orphan'):
            self.reject(self.f.packet(rodata_name=name))

    def test_retained_identity_regions_alignment_copy_zero_and_symbols(self):
        b = self.b
        changes = [lambda elf: b.edit_header(elf, 'flags', 0x05000200),
                   lambda elf: b.edit_header(elf, 'entry', b.FLASH + 3),
                   lambda elf: b.edit_section(elf, '.text', 'alignment', 3),
                   lambda elf: b.edit_section(elf, '.bss', 'size', 0x40000),
                   lambda elf: b.edit_program(elf, 0, 'flags', 4),
                   lambda elf: b.edit_program(elf, 1, 'paddr', b.FLASH + 4),
                   lambda elf: b.edit_symbol(elf, '_sidata', 'value', b.FLASH + 16),
                   lambda elf: b.edit_symbol(elf, '_ebss', 'value', b.RAM + 25),
                   lambda elf: b.edit_symbol(elf, 'entry_point', 'size', 0),
                   lambda elf: b.edit_symbol(elf, 'optional_weak_hook', 'info', 0x10),
                   lambda elf: b.edit_symbol(elf, 'local_label', 'info', 0x10),
                   lambda elf: b.edit_symbol(elf, 'optional_weak_hook', 'info', 0x30),
                   lambda elf: b.edit_symbol(elf, 'optional_weak_hook', 'info', 0x2f),
                   lambda elf: b.edit_symbol(elf, 'optional_weak_hook', 'other', 4)]
        for image in self.f.ELF_NAMES:
            for index, change in enumerate(changes):
                with self.subTest(image=image, case=index):
                    self.reject(self.alter(change, image))

    def test_normalized_three_image_equality_including_empty_and_entry_metadata(self):
        b = self.b
        for image in self.f.ELF_NAMES:
            for change in (lambda elf: b.edit_symbol(elf, 'entry_point', 'size', 4),
                           lambda elf: b.edit_symbol(elf, 'entry_point', 'other', 3),
                           lambda elf: b.edit_section(elf, '.rodata', 'alignment', 2),
                           lambda elf: b.edit_number(elf, b.section(elf, '.text')[2][4] + 4, 1, 'B')):
                self.reject(self.alter(change, image))
        empty = self.alter(lambda elf: b.edit_section(elf, '.rodata', 'size', 0))
        empty = b.replace_raw(empty, b.RAW[:16] + bytes(8) + b.RAW[24:])
        result = self.call(empty)
        self.assertNotIn('.rodata', [row['name'] for row in result['sections']])
        for image in self.f.ELF_NAMES:
            self.reject(self.alter(lambda elf: b.edit_section(elf, '.rodata', 'alignment', 2), image, empty))

    def test_flat_bin_gap_extent_and_both_package_pairs_retained(self):
        for raw in (self.b.RAW[:-1], self.b.RAW + b'\0', b'\x7fELF' + self.b.RAW[4:],
                    self.b.RAW[:8] + b'\1' + self.b.RAW[9:]):
            self.reject(self.b.replace_raw(self.f.packet(), raw))
        for key in ('app.ino.bin-zsk.bin', 'app.ino.elf-zsk.bin'):
            for offset in (*range(16), 16, -1):
                packet = self.f.packet()
                value = bytearray(packet[key])
                value[offset] ^= 1
                packet[key] = bytes(value)
                with self.subTest(key=key, offset=offset):
                    self.reject(packet)
            for suffix in (b'\0',):
                packet = self.f.packet()
                packet[key] += suffix
                self.reject(packet)
            packet = self.f.packet()
            packet[key] = packet[key][:-1]
            self.reject(packet)

    def test_rejection_preserves_caller_mapping(self):
        packet = self.alter(lambda elf: self.b.edit_symbol(elf, 'errno', 'value', 21))
        before = dict(packet)
        identities = {key: id(value) for key, value in packet.items()}
        self.reject(packet)
        self.assertEqual(packet, before)
        self.assertEqual(identities, {key: id(value) for key, value in packet.items()})

    def test_original_validator_still_rejects_tls_without_module_mutation(self):
        snapshot = dict(self.legacy.__dict__)
        old_packet = self.b.packet()
        tls_packet = self.f.packet()
        with self.effects():
            self.assertEqual(self.legacy.validate_artifacts(old_packet)['status'], 'STATIC_LAYOUT_PACKAGE_PASS')
            with self.assertRaises(ValueError):
                self.legacy.validate_artifacts(tls_packet)
        with mock.patch.dict(sys.modules, {'static_artifacts': self.legacy}):
            with mock.patch.object(self.legacy, 'validate_artifacts',
                                   side_effect=AssertionError('Existing module must not be reused')):
                self.assertEqual(self.call(tls_packet), self.expected(tls_packet))
        self.assertEqual(set(self.legacy.__dict__), set(snapshot))
        for key, value in snapshot.items():
            self.assertIs(self.legacy.__dict__[key], value, key)
        with self.effects():
            with self.assertRaises(ValueError):
                self.legacy.validate_artifacts(tls_packet)
            self.assertEqual(self.legacy.validate_artifacts(old_packet)['status'], 'STATIC_LAYOUT_PACKAGE_PASS')


if __name__ == '__main__':
    unittest.main(verbosity=2)
