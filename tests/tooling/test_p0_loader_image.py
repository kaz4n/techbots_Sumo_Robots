# Checks canonical flash-image reconstruction from fabricated ELF32 ARM program headers.
# Prevents gap filling, padding exceptions or virtual-address confusion in identity evidence.
# Pure byte fixtures exercise the public loader_image function without any board operation.
import struct
import unittest

import test_p0_capture as capture_fixture


FLASH_BASE = 0x08000000
FLASH_END = 0x08040600
IMAGE_SIZE = 263680
ELF_HEADER_SIZE = 52
PROGRAM_HEADER_SIZE = 32
PT_LOAD = 1
UINT32_MAX = 0xFFFFFFFF


def expected_image():
    image = bytearray(b'\x11' * 0x10000 + b'\x22' * 0x10000 +
                      b'\x33' * (IMAGE_SIZE - 0x20000))
    image[0x3F8BF] = 0
    return bytes(image)


def segment(address, data, virtual=None, memory=None, kind=PT_LOAD):
    return dict(address=address, data=data,
                virtual=address if virtual is None else virtual,
                memory=len(data) if memory is None else memory, kind=kind)


def valid_segments(image=None):
    image = expected_image() if image is None else image
    return [segment(FLASH_BASE, image[:0x10000]),
            segment(FLASH_BASE + 0x10000, image[0x10000:0x20000], virtual=0x20000000),
            segment(FLASH_BASE + 0x20000, image[0x20000:])]


def make_elf(segments=None):
    # ELF32 header: ident, type, machine, version, entry, PH offset, SH offset,
    # flags, ELF size, PH size/count, SH size/count/string index. No section table.
    segments = valid_segments() if segments is None else segments
    identification = b'\x7fELF' + bytes((1, 1, 1)) + bytes(9)
    header = struct.pack('<16sHHIIIIIHHHHHH', identification, 2, 40, 1,
        FLASH_BASE + 1, ELF_HEADER_SIZE, 0, 0x05000000, ELF_HEADER_SIZE,
        PROGRAM_HEADER_SIZE, len(segments), 0, 0, 0)
    program_headers, payload = bytearray(), bytearray()
    offset = ELF_HEADER_SIZE + PROGRAM_HEADER_SIZE * len(segments)
    for entry in segments:
        data = entry['data']
        # ELF32 PH: type, file offset, virtual, physical, file size, memory, flags, alignment.
        program_headers += struct.pack('<8I', entry['kind'], offset,
            entry['virtual'], entry['address'], len(data), entry['memory'], 5, 1)
        payload += data
        offset += len(data)
    return header + bytes(program_headers) + bytes(payload)


def replace_u16(elf, offset, value):
    changed = bytearray(elf)
    struct.pack_into('<H', changed, offset, value)
    return bytes(changed)


def replace_u32(elf, offset, value):
    changed = bytearray(elf)
    struct.pack_into('<I', changed, offset, value)
    return bytes(changed)


class P0LoaderImageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module, cls.import_stdout, cls.import_stderr = capture_fixture.load_capture_without_actions()

    def load(self, elf):
        return self.module.loader_image(elf)

    def assert_rejected(self, elf):
        with self.assertRaises(ValueError):
            self.load(elf)

    def test_import_stays_quiet_and_three_adjacent_segments_reconstruct_exact_bytes(self):
        self.assertEqual('', self.import_stdout)
        self.assertEqual('', self.import_stderr)
        result = self.load(make_elf())
        self.assertIs(type(result), bytes)
        self.assertEqual(FLASH_END - FLASH_BASE, IMAGE_SIZE)
        self.assertEqual(IMAGE_SIZE, len(result))
        self.assertEqual(expected_image(), result)

    def test_physical_flash_address_controls_ram_virtual_segment_placement(self):
        segments = valid_segments()
        self.assertEqual(0x20000000, segments[1]['virtual'])
        self.assertEqual(FLASH_BASE + 0x10000, segments[1]['address'])
        self.assertEqual(expected_image(), self.load(make_elf(segments)))

    def test_program_header_order_does_not_change_canonical_physical_image(self):
        segments = valid_segments()
        for order in ((2, 0, 1), (1, 2, 0), (2, 1, 0)):
            with self.subTest(order=order):
                reordered = [segments[index] for index in order]
                self.assertEqual(expected_image(), self.load(make_elf(reordered)))

    def test_alignment_byte_is_preserved_exactly_and_never_ignored_or_normalized(self):
        original = expected_image()
        self.assertEqual(0, original[0x3F8BF])
        self.assertEqual(original, self.load(make_elf(valid_segments(original))))
        changed = bytearray(original)
        changed[0x3F8BF] = 0xFF
        changed = bytes(changed)
        result = self.load(make_elf(valid_segments(changed)))
        self.assertEqual(changed, result)
        self.assertNotEqual(original, result)

    def test_unloaded_trailing_debug_bytes_and_nonload_segment_are_not_flash_content(self):
        segments = valid_segments()
        segments.append(segment(0x30000000, b'unloaded note bytes', kind=4))
        elf = make_elf(segments) + b'debug data outside PT_LOAD\x00' * 2000
        self.assertEqual(expected_image(), self.load(elf))

    def test_zero_file_size_ram_load_is_ignored_including_its_unread_file_offset(self):
        segments = valid_segments()
        segments.append(segment(0x20000000, b'', memory=4096))
        elf = make_elf(segments)
        fourth_offset = ELF_HEADER_SIZE + 3 * PROGRAM_HEADER_SIZE + 4
        elf = replace_u32(elf, fourth_offset, UINT32_MAX)
        self.assertEqual(expected_image(), self.load(elf))

    def test_file_sizes_not_memory_sizes_define_the_reconstructed_image(self):
        segments = valid_segments()
        segments[1]['memory'] += 4096
        segments[2]['memory'] += 8192
        self.assertEqual(expected_image(), self.load(make_elf(segments)))

    def test_nonzero_ram_or_other_outside_load_is_rejected_even_with_complete_flash(self):
        for address in (0x20000000, FLASH_BASE - 1, FLASH_END, UINT32_MAX):
            with self.subTest(address=hex(address)):
                segments = valid_segments()
                segments.append(segment(address, b'X'))
                self.assert_rejected(make_elf(segments))

    def test_one_byte_gaps_at_start_middle_or_end_are_not_filled(self):
        for index in (0, 1, 2):
            with self.subTest(segment=index):
                segments = valid_segments()
                if index < 2:
                    segments[index]['address'] += 1
                    segments[index]['data'] = segments[index]['data'][1:]
                else:
                    segments[index]['data'] = segments[index]['data'][:-1]
                self.assert_rejected(make_elf(segments))

    def test_one_byte_overlap_and_duplicate_load_are_rejected(self):
        segments = valid_segments()
        segments[0]['data'] += b'X'
        segments[0]['memory'] += 1
        self.assert_rejected(make_elf(segments))
        segments = valid_segments()
        segments.append(dict(segments[0]))
        self.assert_rejected(make_elf(segments))

    def test_missing_flash_loads_or_zero_file_loads_only_cannot_make_an_image(self):
        for segments in ([], [segment(0x20000000, b'', memory=4096)],
                         [segment(FLASH_BASE, expected_image(), kind=4)]):
            with self.subTest(segment_count=len(segments)):
                self.assert_rejected(make_elf(segments))

    def test_truncated_elf_header_program_table_or_segment_payload_is_rejected(self):
        elf = make_elf()
        cuts = (0, 15, ELF_HEADER_SIZE - 1,
                ELF_HEADER_SIZE + 3 * PROGRAM_HEADER_SIZE - 1, len(elf) - 1)
        for end in cuts:
            with self.subTest(length=end):
                self.assert_rejected(elf[:end])

    def test_load_file_offset_and_file_size_must_stay_inside_elf_bytes(self):
        elf = make_elf()
        for field, value in ((4, len(elf)), (4, UINT32_MAX),
                             (16, len(elf)), (16, UINT32_MAX)):
            with self.subTest(field=field, value=value):
                self.assert_rejected(replace_u32(elf, ELF_HEADER_SIZE + field, value))

    def test_class_byte_order_machine_magic_and_versions_are_validated(self):
        elf = make_elf()
        for offset, value in ((0, 0), (4, 0), (4, 2), (5, 0), (5, 2), (6, 0), (6, 2)):
            with self.subTest(ident_offset=offset, value=value):
                changed = bytearray(elf)
                changed[offset] = value
                self.assert_rejected(bytes(changed))
        for machine in (0, 3, 183):
            with self.subTest(machine=machine):
                self.assert_rejected(replace_u16(elf, 18, machine))
        for version in (0, 2):
            with self.subTest(header_version=version):
                self.assert_rejected(replace_u32(elf, 20, version))

    def test_header_sizes_and_program_table_bounds_are_validated(self):
        elf = make_elf()
        for size in (0, ELF_HEADER_SIZE - 1, ELF_HEADER_SIZE + 1):
            with self.subTest(elf_header_size=size):
                self.assert_rejected(replace_u16(elf, 40, size))
        for size in (0, PROGRAM_HEADER_SIZE - 1, PROGRAM_HEADER_SIZE + 1):
            with self.subTest(program_header_size=size):
                self.assert_rejected(replace_u16(elf, 42, size))
        for offset in (0, len(elf) - PROGRAM_HEADER_SIZE, len(elf), UINT32_MAX):
            with self.subTest(program_table_offset=offset):
                self.assert_rejected(replace_u32(elf, 28, offset))

    def test_32_program_headers_are_bounded_and_33_are_rejected_even_if_extra_loads_empty(self):
        segments = valid_segments()
        segments.extend(segment(0x20000000 + index * 4096, b'', memory=4096)
                        for index in range(29))
        self.assertEqual(32, len(segments))
        self.assertEqual(expected_image(), self.load(make_elf(segments)))
        segments.append(segment(0x20030000, b'', memory=4096))
        self.assert_rejected(make_elf(segments))


if __name__ == '__main__':
    unittest.main()
