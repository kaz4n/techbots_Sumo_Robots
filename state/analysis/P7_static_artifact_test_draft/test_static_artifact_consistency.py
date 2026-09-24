# Supplements frozen artifact tests with complete cross-ELF consistency oracles.
# Preserves permitted empty allocations and semantic entry identity across indexing.
# Run only after freeze_consistency.json binds this independent supplement.
import hashlib
import json
from pathlib import Path
import struct
import sys
import types
import unittest


ROOT = Path(__file__).resolve().parents[3]
DRAFT = Path(__file__).resolve().parent


def load_support():
    path = DRAFT / 'test_static_artifacts.py'
    module = types.ModuleType('independent_frozen_artifact_test_support')
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def renumber_text_rodata(elf, fixture):
    result = bytearray(elf)
    shoff = fixture.header(elf, 'shoff')[2]
    first, second = shoff + 40, shoff + 80
    result[first:first + 40] = elf[second:second + 40]
    result[second:second + 40] = elf[first:first + 40]
    table = fixture.section(elf, '.symtab')[2]
    for index in range(table[5] // 16):
        offset = table[4] + index * 16 + 14
        section = struct.unpack_from('<H', elf, offset)[0]
        if section in (1, 2):
            struct.pack_into('<H', result, offset, 3 - section)
    return bytes(result)


class StaticArtifactConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        freeze = json.loads((DRAFT / 'freeze_consistency.json').read_text(encoding='utf-8'))
        if freeze.get('status') != 'FROZEN_FOR_AUTHORIZED_HOST_TEST':
            raise RuntimeError('Consistency supplement has not been frozen')
        for relative, expected in freeze['inputs_sha256'].items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            if actual != expected:
                raise RuntimeError('Frozen consistency input changed: ' + relative)
        support = load_support()
        support.StaticArtifactsContract.setUpClass()
        cls.base = support.StaticArtifactsContract('test_complete_positive_gap_lma_padding_debug_and_receipts')
        cls.f = cls.base.f

    def empty_packet(self):
        packet = self.base.altered(lambda elf: self.f.edit_section(elf, '.rodata', 'size', 0))
        return self.f.replace_raw(packet, self.f.RAW[:16] + bytes(8) + self.f.RAW[24:])

    def test_matching_empty_allocation_record_can_change_consistently(self):
        for field, value in (('alignment', 2), ('address', self.f.FLASH + 12)):
            packet = self.base.altered(
                lambda elf: self.f.edit_section(elf, '.rodata', field, value), self.empty_packet())
            with self.subTest(field=field):
                result = self.base.call(packet)
                self.assertEqual(result['status'], 'STATIC_LAYOUT_PACKAGE_PASS')
                self.assertNotIn('.rodata', [item['name'] for item in result['sections']])

    def test_one_empty_allocation_record_drift_is_rejected(self):
        for name in self.f.ELF_NAMES:
            for field, value in (('alignment', 2), ('address', self.f.FLASH + 12)):
                packet = self.base.altered(
                    lambda elf: self.f.edit_section(elf, '.rodata', field, value),
                    self.empty_packet(), names=(name,))
                with self.subTest(elf=name, field=field):
                    self.base.reject(packet)

    def test_one_empty_allocation_name_drift_is_rejected(self):
        for name in self.f.ELF_NAMES:
            packet = self.empty_packet()
            alternate = self.f.make_elf(rodata_name='.ARM.extab')
            packet[name] = self.f.edit_section(alternate, '.ARM.extab', 'size', 0)
            packet['app.ino.elf-zsk.bin'] = self.f.diagnostic(packet['app.ino.elf'])
            with self.subTest(elf=name):
                self.base.reject(packet)

    def test_entry_size_binding_visibility_are_valid_when_matching(self):
        for field, value in (('size', 4), ('info', 0x22), ('other', 3)):
            packet = self.base.altered(lambda elf: self.f.edit_symbol(elf, 'entry_point', field, value))
            with self.subTest(field=field):
                self.assertEqual(self.base.call(packet)['status'], 'STATIC_LAYOUT_PACKAGE_PASS')

    def test_one_entry_size_binding_visibility_drift_is_rejected(self):
        for name in self.f.ELF_NAMES:
            for field, value in (('size', 4), ('info', 0x22), ('other', 3)):
                packet = self.base.altered(
                    lambda elf: self.f.edit_symbol(elf, 'entry_point', field, value), names=(name,))
                with self.subTest(elf=name, field=field):
                    self.base.reject(packet)

    def test_section_index_renumbering_preserves_semantic_entry_and_allocations(self):
        for name in self.f.ELF_NAMES:
            packet = self.base.altered(lambda elf: renumber_text_rodata(elf, self.f), names=(name,))
            with self.subTest(elf=name):
                self.assertEqual(self.base.call(packet), self.base.expected(packet))


if __name__ == '__main__':
    unittest.main(verbosity=2)
