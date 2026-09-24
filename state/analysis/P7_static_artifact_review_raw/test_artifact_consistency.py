# Checks the public cross-form allocation and entry-symbol obligations.
# Retains original-versus-fixed evidence and permits harmless section renumbering.
# Reviewer-owned probes reuse the independently frozen tiny synthetic fixture.
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import types
import unittest


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
IMPLEMENTATION = 'state/analysis/P7_static_link_probe_raw/static_artifacts.py'
FIXTURE = 'state/analysis/P7_static_artifact_test_draft/synthetic_elf.py'


def load_bytes(data, filename, name):
    module = types.ModuleType(name)
    module.__file__ = str(filename)
    exec(compile(data, str(filename), 'exec'), module.__dict__)
    return module


def reorder_sections(fixture, elf, order):
    result = bytearray(elf)
    shoff = fixture.header(elf, 'shoff')[2]
    count = fixture.header(elf, 'shnum')[2]
    rows = [list(struct.unpack_from('<10I', elf, shoff + i * 40))
            for i in range(count)]
    mapping = {old: new for new, old in enumerate(order)}
    assert order[0] == 0 and len(mapping) == len(order)
    for row in rows:
        if row[1] == 2:
            for offset in range(row[4], row[4] + row[5], 16):
                section = struct.unpack_from('<H', result, offset + 14)[0]
                if section < 0xff00:
                    struct.pack_into('<H', result, offset + 14, mapping[section])
    for new, old in enumerate(order):
        row = rows[old]
        if row[6]:
            row[6] = mapping[row[6]]
        if row[2] & 0x40 and row[7]:
            row[7] = mapping[row[7]]
        struct.pack_into('<10I', result, shoff + new * 40, *row)
    struct.pack_into('<H', result, 48, len(order))
    struct.pack_into('<H', result, 50, mapping[fixture.header(elf, 'shstrndx')[2]])
    return bytes(result)


class ArtifactConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        freeze = json.loads((HERE / 'freeze_consistency.json').read_text())
        if freeze['status'] != 'FROZEN_FOR_AUTHORIZED_HOST_TEST':
            raise RuntimeError('Private oracle is not frozen')
        for name, expected in freeze['inputs_sha256'].items():
            if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
                raise RuntimeError('Private frozen input changed: ' + name)
        cls.f = load_bytes((ROOT / FIXTURE).read_bytes(), ROOT / FIXTURE, 'review_fixture')
        if cls.source_ref == 'working':
            source = (ROOT / IMPLEMENTATION).read_bytes()
        else:
            source = subprocess.check_output(
                ['git', 'show', 'a986ffdb:' + IMPLEMENTATION], cwd=ROOT)
        cls.source_sha256 = hashlib.sha256(source).hexdigest()
        if cls.source_sha256 != freeze['source_sha256'][cls.source_ref]:
            raise RuntimeError('Reviewed implementation bytes changed')
        cls.module = load_bytes(source, ROOT / IMPLEMENTATION, 'review_artifacts')

    def call(self, packet):
        return self.module.validate_artifacts(packet)

    def empty_packet(self):
        packet = self.f.mutate_elfs(
            self.f.packet(), lambda elf: self.f.edit_section(elf, '.rodata', 'size', 0))
        raw = self.f.RAW[:16] + bytes(8) + self.f.RAW[24:]
        return self.f.replace_raw(packet, raw)

    def test_section_indices_can_change_without_semantic_change(self):
        packet = self.f.packet()
        for name in ('app.ino_debug.elf', 'app.ino_temp.elf'):
            count = self.f.header(packet[name], 'shnum')[2]
            order = list(range(count))
            order[1], order[3] = order[3], order[1]
            packet[name] = reorder_sections(self.f, packet[name], order)
        result = self.call(packet)
        self.assertEqual(result['status'], 'STATIC_LAYOUT_PACKAGE_PASS')
        self.assertEqual(result['entry'], 0x08100011)

    def test_matching_empty_allocation_is_accepted_and_omitted_from_report(self):
        result = self.call(self.empty_packet())
        self.assertEqual(result['status'], 'STATIC_LAYOUT_PACKAGE_PASS')
        self.assertNotIn('.rodata', [item['name'] for item in result['sections']])

    def test_missing_empty_allocation_in_one_form_fails(self):
        for name in self.f.ELF_NAMES:
            packet = self.empty_packet()
            removed = self.f.section(packet[name], '.rodata')[0]
            order = [i for i in range(self.f.header(packet[name], 'shnum')[2])
                     if i != removed]
            packet = self.f.mutate_elfs(
                packet, lambda elf: reorder_sections(self.f, elf, order), (name,))
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.call(packet)

    def test_changed_empty_metadata_in_one_form_fails(self):
        for name in self.f.ELF_NAMES:
            for field, value in (('alignment', 2), ('address', self.f.FLASH + 20)):
                packet = self.f.mutate_elfs(
                    self.empty_packet(),
                    lambda elf: self.f.edit_section(elf, '.rodata', field, value), (name,))
                with self.subTest(name=name, field=field), self.assertRaises(ValueError):
                    self.call(packet)

    def test_matching_entry_identity_variants_remain_supported(self):
        for field, value in (('size', 4), ('info', 0x22), ('other', 3)):
            packet = self.f.mutate_elfs(
                self.f.packet(), lambda elf: self.f.edit_symbol(elf, 'entry_point', field, value))
            with self.subTest(field=field):
                self.assertEqual(self.call(packet)['status'], 'STATIC_LAYOUT_PACKAGE_PASS')

    def test_changed_entry_identity_in_one_form_fails(self):
        for name in self.f.ELF_NAMES:
            for field, value in (('size', 4), ('info', 0x22), ('other', 3)):
                packet = self.f.mutate_elfs(
                    self.f.packet(),
                    lambda elf: self.f.edit_symbol(elf, 'entry_point', field, value), (name,))
                with self.subTest(name=name, field=field), self.assertRaises(ValueError):
                    self.call(packet)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-ref', choices=('working', 'a986ffdb'), required=True)
    args = parser.parse_args()
    ArtifactConsistency.source_ref = args.source_ref
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ArtifactConsistency)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'source_ref': args.source_ref,
                      'source_sha256': getattr(ArtifactConsistency, 'source_sha256', None),
                      'tests_run': result.testsRun, 'failures': len(result.failures),
                      'errors': len(result.errors), 'success': result.wasSuccessful()}, indent=2))
    raise SystemExit(0 if result.wasSuccessful() else 1)
