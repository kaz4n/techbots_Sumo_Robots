# Independently tests the public static ELF/BIN/package structural contract.
# Uses tiny synthetic packets without compiler, hardware or origin assertions.
# Draft only until freeze_artifacts.json binds the reviewed adopted contract.
import builtins
import collections
from contextlib import ExitStack
import dataclasses
import datetime
import enum
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import socket
import struct
import subprocess
import sys
import time
import types
import typing
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
DRAFT = Path(__file__).resolve().parent
IMPLEMENTATION = ROOT / 'state/analysis/P7_static_link_probe_raw/static_artifacts.py'


def load_without_bytecode(path, name):
    code = compile(path.read_bytes(), str(path), 'exec')
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(code, module.__dict__)
    return module


def no_effects():
    stack = ExitStack()
    forbidden = {
        builtins: ('open',), io: ('open',),
        subprocess: ('Popen', 'run', 'call', 'check_call', 'check_output'),
        socket: ('socket', 'create_connection', 'getaddrinfo'),
        time: ('time', 'time_ns', 'monotonic', 'monotonic_ns', 'perf_counter',
               'perf_counter_ns', 'process_time', 'sleep'),
        os: ('open', 'read', 'write', 'stat', 'lstat', 'listdir', 'scandir',
             'readlink', 'access', 'mkdir', 'makedirs', 'remove', 'unlink',
             'rename', 'replace', 'rmdir', 'chmod', 'chdir', 'getcwd',
             'getenv', 'getenvb', 'system', 'popen', 'urandom'),
    }
    for module, names in forbidden.items():
        for name in names:
            if hasattr(module, name):
                stack.enter_context(mock.patch.object(
                    module, name, side_effect=AssertionError('Forbidden component effect: ' + name)))
    environment = mock.MagicMock()
    for name in ('__getitem__', '__iter__', '__len__', '__setitem__', 'get', 'keys', 'items', 'values'):
        getattr(environment, name).side_effect = AssertionError('Forbidden environment access')
    stack.enter_context(mock.patch.object(os, 'environ', environment))
    for kind in ('date', 'datetime'):
        clock = mock.MagicMock()
        for name in ('now', 'utcnow', 'today'):
            getattr(clock, name).side_effect = AssertionError('Forbidden datetime access')
        stack.enter_context(mock.patch.object(datetime, kind, clock))
    return stack


class StaticArtifactsContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        freeze = json.loads((DRAFT / 'freeze_artifacts.json').read_text(encoding='utf-8'))
        if freeze.get('status') != 'FROZEN_FOR_AUTHORIZED_HOST_TEST':
            raise RuntimeError('Artifact oracle has not been frozen and authorized')
        for relative, expected in freeze['inputs_sha256'].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            if actual != expected:
                raise RuntimeError('Frozen artifact input changed: ' + relative)
        cls.f = load_without_bytecode(DRAFT / 'synthetic_elf.py', 'independent_synthetic_elf')
        code = compile(IMPLEMENTATION.read_bytes(), str(IMPLEMENTATION), 'exec')
        module = types.ModuleType('independent_static_artifacts_under_test')
        module.__file__ = str(IMPLEMENTATION)
        sys.modules[module.__name__] = module
        with no_effects():
            exec(code, module.__dict__)
        cls.module = module

    def call(self, packet):
        with no_effects():
            return self.module.validate_artifacts(packet)

    def reject(self, packet):
        with self.assertRaises(ValueError):
            self.call(packet)

    def altered(self, change, packet=None, names=None):
        return self.f.mutate_elfs(packet or self.f.packet(), change,
                                 names or self.f.ELF_NAMES)

    def reject_header(self, field, values):
        for value in values:
            with self.subTest(field=field, value=value):
                self.reject(self.altered(lambda elf: self.f.edit_header(elf, field, value)))

    def reject_section(self, name, field, values):
        for value in values:
            with self.subTest(section=name, field=field, value=value):
                self.reject(self.altered(lambda elf: self.f.edit_section(elf, name, field, value)))

    def reject_program(self, index, field, values):
        for value in values:
            with self.subTest(program=index, field=field, value=value):
                self.reject(self.altered(lambda elf: self.f.edit_program(elf, index, field, value)))

    def reject_symbol(self, name, field, values):
        for value in values:
            with self.subTest(symbol=name, field=field, value=value):
                self.reject(self.altered(lambda elf: self.f.edit_symbol(elf, name, field, value)))

    def expected(self, packet):
        f = self.f
        records = [('.text', 1, 6, f.FLASH, 8, 4, f.FLASH),
                   ('.rodata', 1, 2, f.FLASH + 16, 8, 4, f.FLASH + 16),
                   ('.data', 1, 3, f.RAM, 8, 4, f.FLASH + 32),
                   ('.bss', 8, 3, f.RAM + 8, f.BSS_END - f.RAM - 8, 8, None)]
        fields = ('name', 'type', 'flags', 'address', 'size', 'alignment', 'load_address')
        return {
            'status': 'STATIC_LAYOUT_PACKAGE_PASS', 'entry': f.FLASH | 1,
            'flash': {'start': f.FLASH, 'end': f.FLASH + 40,
                      'remaining': 0x081c0000 - f.FLASH - 40},
            'ram': {'start': f.RAM, 'end': f.BSS_END, 'remaining': 0x20053890 - f.BSS_END},
            'data_copy': {'source': f.FLASH + 32, 'destination': f.RAM, 'bytes': 8},
            'bss_zero': {'start': f.RAM + 8, 'end': f.RAM + 24, 'bytes': 16},
            'sections': [dict(zip(fields, row)) for row in records],
            'weak_undefined': ['optional_weak_hook'],
            'artifacts': {name: {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                          for name, data in packet.items()},
        }

    def test_complete_positive_gap_lma_padding_debug_and_receipts(self):
        packet = self.f.packet()
        before = dict(packet)
        self.assertNotEqual(packet['app.ino.elf'], packet['app.ino_debug.elf'])
        self.assertEqual(len(packet['app.ino.bin']), 40)
        result = self.call(packet)
        self.assertEqual(result, self.expected(packet))
        json.dumps(result, allow_nan=False)
        self.assertEqual(packet, before)
        self.assertEqual(self.call(packet), result)

    def test_input_mapping_and_exact_seven_keys(self):
        for value in (None, [], (), '', 1, True, collections.UserDict(self.f.packet())):
            with self.subTest(value=type(value).__name__):
                self.reject(value)
        for name in self.f.packet():
            packet = self.f.packet()
            del packet[name]
            self.reject(packet)
        for key in ('extra.bin', 1, None):
            packet = self.f.packet()
            packet[key] = b'x'
            self.reject(packet)

    def test_each_value_is_nonempty_bytes(self):
        for name in self.f.packet():
            for value in (b'', '', None, 1, True, bytearray(b'x'), memoryview(b'x')):
                packet = self.f.packet()
                packet[name] = value
                with self.subTest(name=name, value=type(value).__name__):
                    self.reject(packet)

    def test_one_transient_oversize_buffer_rejected_for_every_input(self):
        excessive = b'x' * (16777216 + 1)
        for name in self.f.packet():
            packet = self.f.packet()
            packet[name] = excessive
            with self.subTest(name=name):
                self.reject(packet)

    def test_all_ident_fields_and_padding_are_exact(self):
        for offset, value in ((0, 0), (1, 0), (2, 0), (3, 0), (4, 2), (5, 2),
                              (6, 0), (7, 1), (8, 1), *[(i, 1) for i in range(9, 16)]):
            with self.subTest(offset=offset):
                self.reject(self.altered(lambda elf: self.f.edit_number(elf, offset, value, 'B')))

    def test_header_identity_entry_flags_and_exact_sizes(self):
        cases = {'type': (0, 1, 3), 'machine': (0, 3, 183), 'version': (0, 2),
                 'entry': (self.f.FLASH, self.f.FLASH + 3, 0),
                 'flags': (0, 0x05000200, 0x05000401, 0x04000400),
                 'ehsize': (0, 51, 53), 'phentsize': (0, 31, 33),
                 'shentsize': (0, 39, 41)}
        for field, values in cases.items():
            self.reject_header(field, values)

    def test_header_counts_indices_and_table_extents(self):
        for field, values in {'phnum': (0, 65, 65535), 'shnum': (0, 4097, 65535),
                              'shstrndx': (0, 1, 8, 65535),
                              'phoff': (0, 51, 0xfffffff0),
                              'shoff': (0, 52, 0xfffffff0)}.items():
            self.reject_header(field, values)
        for length in (1, 16, 51, 147):
            self.reject(self.altered(lambda elf: elf[:length]))

    def test_null_section_and_section_string_table_rules(self):
        self.reject_section('', 'flags', (1,))
        self.reject_section('.shstrtab', 'type', (1, 2, 8))
        self.reject_section('.rodata', 'name', (0, 0xffffffff))
        self.reject(self.altered(lambda elf: self.f.edit_section(
            elf, '.rodata', 'name', self.f.section(elf, '.text')[2][0])))
        self.reject(self.altered(lambda elf: self.f.edit_number(
            elf, self.f.section(elf, '.shstrtab')[2][4] + 1, 255, 'B')))
        self.reject(self.altered(lambda elf: self.f.edit_number(
            elf, sum(self.f.section(elf, '.shstrtab')[2][4:6]) - 1, 65, 'B')))

    def test_section_names_have_bounded_decode_work(self):
        self.reject(self.f.packet(rodata_name='.' + 'n' * 4096))

    def test_section_alignment_and_file_extents(self):
        self.reject_section('.text', 'alignment', (3, 6, 32))
        self.reject_section('.text', 'address', (self.f.FLASH + 1,))
        self.reject(self.altered(lambda elf: self.f.edit_section(
            elf, '.text', 'offset', self.f.section(elf, '.text')[2][4] + 1)))
        self.reject_section('.rodata', 'offset', (0, 52, 0xfffffff0))
        self.reject_section('.rodata', 'size', (0xffffffff,))
        self.reject(self.altered(lambda elf: self.f.edit_section(
            elf, '.rodata', 'offset', self.f.section(elf, '.text')[2][4])))
        self.reject(self.altered(lambda elf: self.f.edit_section(elf, '.bss', 'offset', len(elf) + 1)))

    def test_nonallocated_file_section_must_obey_bounds_and_alignment(self):
        self.reject_section('.strtab', 'offset', (0xffffffff,))
        self.reject_section('.strtab', 'alignment', (3,))
        self.reject(self.altered(lambda elf: self.f.edit_section(
            elf, '.strtab', 'offset', self.f.header(elf, 'shoff')[2])))

    def nonallocated_variant(self, name, kind=1, empty=False):
        packet = self.f.packet(rodata_name=name, rodata_type=kind, rodata_flags=0)
        if empty:
            packet = self.altered(lambda elf: self.f.edit_section(elf, name, 'size', 0), packet)
        return self.f.replace_raw(packet, self.f.RAW[:16] + bytes(8) + self.f.RAW[24:])

    def test_nonallocated_metadata_and_empty_relocations_are_permitted(self):
        for name, kind, empty in (('.metadata', 1, False), ('.note.test', 7, False),
                                  ('.rel.empty', 9, True), ('.rela.empty', 4, True)):
            with self.subTest(name=name):
                self.assertEqual(self.call(self.nonallocated_variant(name, kind, empty))['status'],
                                 'STATIC_LAYOUT_PACKAGE_PASS')

    def test_forbidden_names_reject_even_when_nonallocated(self):
        for name in ('.tdata', '.tdata.extra', '.tbss', '.got', '.got.extra', '.igot',
                     '.plt', '.iplt', '.ARM.attributes', '.ARM.attributes.vendor'):
            with self.subTest(name=name):
                self.reject(self.nonallocated_variant(name))

    def test_forbidden_nonallocated_types_and_tls_flags(self):
        for kind in (0, 4, 5, 6, 9, 11, 17, 18):
            with self.subTest(kind=kind):
                self.reject(self.nonallocated_variant('.metadata', kind))
        self.reject(self.altered(lambda elf: self.f.edit_section(
            elf, '.rodata', 'flags', 0x400), self.nonallocated_variant('.rodata')))

    def test_every_unexplained_allocated_orphan_even_empty_is_rejected(self):
        packet = self.f.packet(rodata_name='.orphan')
        self.reject(packet)
        packet = self.altered(lambda elf: self.f.edit_section(elf, '.orphan', 'size', 0), packet)
        self.reject(self.f.replace_raw(packet, self.f.RAW[:16] + bytes(8) + self.f.RAW[24:]))

    def test_optional_flash_output_names_types_and_flags(self):
        choices = (('.static_thread_data_area', 1, 2), ('.static_thread_data_area', 1, 3),
                   ('.preinit_array', 16, 2), ('.preinit_array', 16, 3),
                   ('.init_array', 14, 2), ('.fini_array', 15, 3),
                   ('.ARM.extab', 1, 2), ('.ARM', 0x70000001, 2), ('.ARM', 0x70000001, 130))
        for name, kind, flags in choices:
            packet = self.f.packet(rodata_name=name, rodata_type=kind, rodata_flags=flags)
            if flags & 1:
                packet = self.altered(lambda elf: self.f.edit_program(elf, 0, 'flags', 7), packet)
            if flags & 128:
                packet = self.altered(lambda elf: self.f.edit_section(elf, name, 'link', 1), packet)
            with self.subTest(name=name, flags=flags):
                self.assertEqual(self.call(packet)['status'], 'STATIC_LAYOUT_PACKAGE_PASS')
                self.reject(self.altered(lambda elf: self.f.edit_section(elf, name, 'type', 8), packet))
                self.reject(self.altered(lambda elf: self.f.edit_section(elf, name, 'flags', 0), packet))

    def test_empty_optional_section_still_requires_named_type_flags_alignment(self):
        packet = self.altered(lambda elf: self.f.edit_section(elf, '.rodata', 'size', 0))
        packet = self.f.replace_raw(packet, self.f.RAW[:16] + bytes(8) + self.f.RAW[24:])
        self.assertEqual(self.call(packet)['status'], 'STATIC_LAYOUT_PACKAGE_PASS')
        for field, value in (('type', 8), ('flags', 6), ('alignment', 3)):
            self.reject(self.altered(lambda elf: self.f.edit_section(elf, '.rodata', field, value), packet))

    def test_required_sections_type_flags_nonempty_and_regions(self):
        for name, kind, flags in (('.text', 1, 6), ('.data', 1, 3), ('.bss', 8, 3)):
            self.reject_section(name, 'size', (0,))
            self.reject_section(name, 'type', ((8 if kind == 1 else 1),))
            self.reject_section(name, 'flags', (0, 2, flags | 0x400))
        self.reject_section('.text', 'size', (1,))
        self.reject_section('.text', 'address', (self.f.FLASH - 4, self.f.FLASH + 4, self.f.RAM))
        self.reject_section('.data', 'address', (self.f.RAM - 4, self.f.RAM + 4, self.f.FLASH))
        self.reject_section('.bss', 'address', (self.f.RAM, 0x20053890, self.f.FLASH))
        self.reject_section('.bss', 'size', (1, 0x40000, 0xffffffff))

    def test_allocated_vma_overlap_and_upper_bounds(self):
        self.reject_section('.rodata', 'address', (self.f.FLASH + 4, 0x081bfffc, 0xfffffff8))
        self.reject_section('.rodata', 'size', (0x0c0000,))
        self.reject_section('.data', 'size', (0x40004,))

    def test_program_types_nulls_and_executable_stack(self):
        self.reject_program(2, 'type', (2, 3, 4, 5, 7, 0xffffffff))
        self.reject_program(2, 'flags', (1, 5, 7))
        packet = self.altered(lambda elf: self.f.edit_program(elf, 2, 'type', 0))
        self.assertEqual(self.call(packet)['status'], 'STATIC_LAYOUT_PACKAGE_PASS')

    def test_program_alignment_size_bounds_and_load_permissions(self):
        self.reject_program(0, 'alignment', (3, 6, 64))
        self.reject_program(0, 'offset', (0, 1, 0xfffffff0))
        self.reject_program(0, 'filesz', (25, 0xffffffff))
        self.reject_program(0, 'flags', (0, 1, 4, 8, 0xffffffff))
        self.reject_program(1, 'flags', (0, 2, 4, 5, 8))
        self.reject_program(0, 'memsz', (0, 7, 0xffffffff))

    def test_segment_vma_lma_bounds_overlaps_and_empty_ownership(self):
        self.reject_program(0, 'vaddr', (self.f.FLASH - 16, self.f.RAM, 0xfffffff0))
        self.reject_program(0, 'paddr', (self.f.FLASH - 16, self.f.FLASH + 4, 0x081bfff8))
        self.reject_program(1, 'paddr', (self.f.RAM, self.f.FLASH + 4, 0x081bfffc))
        self.reject_program(1, 'vaddr', (self.f.RAM - 4, self.f.FLASH, 0x20053890))
        self.reject_program(1, 'memsz', (0x40001, self.f.BSS_END - self.f.RAM + 4))
        self.reject_program(0, 'memsz', (41,))
        packet = self.altered(lambda elf: self.f.edit_program(elf, 2, 'type', 1))
        self.reject(packet)

    def test_section_mapping_requires_segment_coverage_and_matching_offsets(self):
        self.reject_program(0, 'filesz', (7, 20))
        self.reject_program(1, 'filesz', (4,))
        self.reject(self.altered(lambda elf: self.f.edit_section(
            elf, '.rodata', 'offset', self.f.section(elf, '.rodata')[2][4] + 4)))
        self.reject_program(0, 'type', (0,))
        self.reject_program(1, 'type', (0,))

    def test_overlapping_physical_segment_padding_is_not_hidden_by_disjoint_sections(self):
        packet = self.altered(lambda elf: self.f.edit_program(
            self.f.edit_program(elf, 0, 'filesz', 36), 0, 'memsz', 36))
        self.reject(packet)

    def test_executable_data_requires_executable_ram_segment(self):
        packet = self.altered(lambda elf: self.f.edit_section(elf, '.data', 'flags', 7))
        self.reject(packet)
        packet = self.altered(lambda elf: self.f.edit_program(elf, 1, 'flags', 7), packet)
        self.assertEqual(self.call(packet)['status'], 'STATIC_LAYOUT_PACKAGE_PASS')

    def test_bin_exact_extent_contents_zero_gaps_and_no_elf_magic(self):
        for raw in (self.f.RAW[:-1], self.f.RAW + b'\0', b'\x7fELF' + self.f.RAW[4:]):
            self.reject(self.f.replace_raw(self.f.packet(), raw))
        for index in (0, 7, 8, 15, 16, 23, 24, 31, 32, 39):
            raw = bytearray(self.f.RAW)
            raw[index] ^= 1
            with self.subTest(index=index):
                self.reject(self.f.replace_raw(self.f.packet(), bytes(raw)))

    def test_one_symtab_exact_entry_shape_and_link(self):
        self.reject_section('.symtab', 'type', (1,))
        self.reject_section('.symtab', 'entsize', (0, 15, 17))
        self.reject_section('.symtab', 'size', (0, 1, 17, 16 * 65537))
        self.reject_section('.symtab', 'link', (0, 1, 7, 65535))
        self.reject(self.altered(lambda elf: self.f.edit_section(elf, '.rodata', 'type', 2),
                                 self.nonallocated_variant('.rodata')))

    def test_symbol_null_local_boundary_bindings_types_and_visibility(self):
        self.reject_symbol('', 'value', (1,))
        self.reject_section('.symtab', 'info', (0, 1, 3, 5, 12))
        self.reject_symbol('entry_point', 'info', (0x02, 0x32, 0x1f, 0x13, 0x14))
        self.reject_symbol('entry_point', 'other', (4, 128, 255))
        self.reject_symbol('local_label', 'info', (0x10, 0x20, 0x04))

    def test_symbol_names_bounds_termination_ascii_and_work_limit(self):
        self.reject_symbol('entry_point', 'name', (0xffffffff,))
        self.reject(self.altered(lambda elf: self.f.edit_number(
            elf, self.f.section(elf, '.strtab')[2][4] + 1, 255, 'B')))
        self.reject(self.altered(lambda elf: self.f.edit_number(
            elf, sum(self.f.section(elf, '.strtab')[2][4:6]) - 1, 65, 'B')))
        self.reject(self.f.packet(weak_name='w' * 4097))

    def test_local_section_file_and_permitted_visibility_forms(self):
        packet = self.altered(lambda elf: self.f.edit_symbol(
            self.f.edit_symbol(self.f.edit_symbol(elf, 'local_label', 'value', 0),
                               'local_label', 'section', 0xfff1),
            'local_label', 'info', 0x04))
        self.assertEqual(self.call(packet)['status'], 'STATIC_LAYOUT_PACKAGE_PASS')
        packet = self.altered(lambda elf: self.f.edit_symbol(elf, 'entry_point', 'other', 3))
        self.assertEqual(self.call(packet)['status'], 'STATIC_LAYOUT_PACKAGE_PASS')
        for index in (0, 0xfff1, 0xfff2, 0xffff):
            self.reject(self.altered(lambda elf: self.f.edit_symbol(
                elf, '', 'section', index, occurrence=1)))

    def test_symbol_indices_common_extended_and_named_strong_undefined(self):
        self.reject_symbol('optional_weak_hook', 'section', (8, 0xfff2, 0xffff))
        self.reject_symbol('optional_weak_hook', 'info', (0x10, 0x00))
        self.reject_symbol('entry_point', 'section', (0, 0xfff1, 0xfff2, 0xffff))
        self.reject_symbol('', 'section', (0xfff1,))

    def test_essential_symbol_names_are_unique_defined_and_exact(self):
        for name in ('entry_point', '_sidata', '_sdata', '_edata', '_sbss', '_ebss'):
            with self.subTest(name=name):
                self.reject_symbol(name, 'name', (0,))
                self.reject_symbol(name, 'section', (0,))
                self.reject(self.altered(lambda elf: self.f.edit_symbol(
                    elf, 'optional_weak_hook', 'name', self.f.symbol(elf, name)[2][0])))
        self.reject_symbol('_sidata', 'value', (self.f.FLASH + 16, self.f.FLASH + 33))
        self.reject_symbol('_sdata', 'value', (self.f.RAM + 1, self.f.RAM + 4))
        self.reject_symbol('_edata', 'value', (self.f.RAM + 7, self.f.RAM + 12))
        self.reject_symbol('_sbss', 'value', (self.f.RAM + 4, self.f.RAM + 9))
        self.reject_symbol('_ebss', 'value', (self.f.RAM + 4, self.f.RAM + 25,
                                            self.f.BSS_END + 4, self.f.BSS_END - 1024))

    def test_entry_function_thumb_address_size_and_section(self):
        self.reject_symbol('entry_point', 'info', (0x10, 0x11))
        self.reject_symbol('entry_point', 'value', (self.f.FLASH, self.f.FLASH + 3))
        self.reject_symbol('entry_point', 'size', (0, 9, 0xffffffff))
        self.reject_symbol('entry_point', 'section', (2, 3, 4))

    def test_undefined_weak_result_is_sorted_union_across_three_forms(self):
        packet = self.f.packet()
        packet['app.ino_debug.elf'] = self.f.make_elf(32, b'Debug only', weak_name='z_weak')
        packet['app.ino_temp.elf'] = self.f.make_elf(64, b'Temp only', weak_name='a_weak')
        self.assertEqual(self.call(packet)['weak_undefined'], ['a_weak', 'optional_weak_hook', 'z_weak'])

    def test_each_elf_allocation_and_essential_symbol_mismatch_fails(self):
        for name in self.f.ELF_NAMES:
            with self.subTest(elf=name):
                self.reject(self.altered(lambda elf: self.f.edit_number(
                    elf, self.f.section(elf, '.text')[2][4] + 4, 1, 'B'), names=(name,)))
                self.reject(self.altered(lambda elf: self.f.edit_section(
                    elf, '.rodata', 'alignment', 2), names=(name,)))
                self.reject(self.altered(lambda elf: self.f.edit_symbol(
                    elf, '_ebss', 'value', self.f.RAM + 28), names=(name,)))

    def test_flat_header_every_fixed_byte_field_and_length(self):
        for offset in range(16):
            packet = self.f.packet()
            data = bytearray(packet['app.ino.bin-zsk.bin'])
            data[offset] ^= 1
            packet['app.ino.bin-zsk.bin'] = bytes(data)
            with self.subTest(offset=offset):
                self.reject(packet)
        for flags in (0, 1, 3, 6, 10, 255):
            packet = self.f.packet()
            packet['app.ino.bin-zsk.bin'] = self.f.edit_number(packet['app.ino.bin-zsk.bin'], 14, flags, 'B')
            self.reject(packet)

    def test_flat_package_payload_length_and_independent_pair_failures(self):
        for value in (self.f.metadata(16), self.f.metadata(57) + self.f.RAW + b'\0',
                      self.f.metadata(55) + self.f.RAW[:-1], self.f.RAW):
            packet = self.f.packet()
            packet['app.ino.bin-zsk.bin'] = value
            self.reject(packet)
        packet = self.f.packet()
        data = bytearray(packet['app.ino.bin-zsk.bin'])
        data[16] ^= 1
        packet['app.ino.bin-zsk.bin'] = bytes(data)
        self.reject(packet)

    def test_diagnostic_package_only_patches_bytes_seven_through_fifteen(self):
        for offset in (*range(16), 16, 51, -1):
            packet = self.f.packet()
            data = bytearray(packet['app.ino.elf-zsk.bin'])
            data[offset] ^= 1
            packet['app.ino.elf-zsk.bin'] = bytes(data)
            with self.subTest(offset=offset):
                self.reject(packet)
        for wrap in (lambda elf: self.f.metadata(len(elf) + 16) + elf,
                     lambda elf: self.f.diagnostic(elf) + b'\0',
                     lambda elf: self.f.diagnostic(elf)[:-1]):
            packet = self.f.packet()
            packet['app.ino.elf-zsk.bin'] = wrap(packet['app.ino.elf'])
            self.reject(packet)

    def test_map_is_opaque_hash_bound_without_layout_or_origin_claim(self):
        packet = self.f.packet()
        packet['app.ino.map'] = b'\x00\xffopaque arbitrary nonempty map receipt'
        expected = self.expected(packet)
        self.assertEqual(self.call(packet), expected)


if __name__ == '__main__':
    unittest.main(verbosity=2)
