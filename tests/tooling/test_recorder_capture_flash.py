"""Test D091 indexed flash identity reads from literal frozen sizes and ranges.

Independent tests retain the original capture suite and inspect no parser body.
All command, ELF and memory inputs are synthetic; no hardware action is invoked.
"""
from contextlib import contextmanager
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock

from tests.tooling.test_recorder_capture import diagnostics, import_without_actions, LinkedExtensions
from tests.fixtures import recorder_heap_vectors

LOADER_BASE = 0x08000000
SKETCH_BASE = 0x08100000
_loader = bytearray(((index * 37 + index // 65536 * 13) & 255) for index in range(263680))
_loader[0x3F8BF] = 0  # Pinned ELF's documented byte; package binary holds255.
LOADER_BYTES = bytes(_loader)
SKETCH_BYTES = bytes(((index * 53 + index // 65536 * 17) & 255) for index in range(146072))
FLASH_READS = [
    ("loader-00", 0x08000000, 65536, "loader"),
    ("loader-01", 0x08010000, 65536, "loader"),
    ("loader-02", 0x08020000, 65536, "loader"),
    ("loader-03", 0x08030000, 65536, "loader"),
    ("loader-04", 0x08040000, 1536, "loader"),
    ("sketch-00", 0x08100000, 65536, "sketch"),
    ("sketch-01", 0x08110000, 65536, "sketch"),
    ("sketch-02", 0x08120000, 15000, "sketch"),
]


def expected_block(address, size, region):
    base, data = (LOADER_BASE, LOADER_BYTES) if region == "loader" else (SKETCH_BASE, SKETCH_BYTES)
    return data[address - base:address - base + size]


class FlashFixture:
    def __init__(self, overrides=None, verified=True, previous_flash_flag=False):
        self.report = {"flash_identity_verified": previous_flash_flag}
        self.identities_verified = verified
        self.binary_size = 146072
        self.calls = []
        self.flags_at_read = []
        self.overrides = overrides or {}

    def read(self, label, address, size, region="ram"):
        assert region in ("loader", "sketch"), "No RAM read is part of verifying flash"
        self.calls.append((label, address, size, region))
        self.flags_at_read.append(self.report.get("flash_identity_verified", False))
        value = self.overrides.get(label, expected_block(address, size, region))
        if isinstance(value, Exception):
            raise value
        return value


class RecorderFlashIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject, _, _ = import_without_actions()

    @contextmanager
    def images(self, folder, packaged=LOADER_BYTES, reconstructed=LOADER_BYTES, binary=SKETCH_BYTES):
        path = Path(folder)
        loader = path / "loader.bin"
        elf = path / "loader.elf"
        sketch = path / "recorder_inert.ino.bin"
        loader.write_bytes(packaged)
        elf.write_bytes(b"opaque synthetic ELF fixture")
        sketch.write_bytes(binary)
        with mock.patch.multiple(self.subject, LOADER=loader, LOADER_ELF=elf), \
             mock.patch.object(self.subject.p0, "loader_image", return_value=reconstructed) as reconstruct:
            yield sketch, reconstruct

    def test_exact_five_loader_three_sketch_blocks_match_every_byte_before_authority(self):
        with tempfile.TemporaryDirectory() as folder, self.images(folder) as (binary, reconstruct):
            capture = FlashFixture()
            self.subject.verify_flash(capture, binary)
            self.assertEqual(capture.calls, FLASH_READS)
            self.assertEqual(sum(call[2] for call in capture.calls), 409752)
            self.assertEqual(capture.flags_at_read, [False] * 8)
            self.assertIs(capture.report["flash_identity_verified"], True)
            self.assertIn("loader_identity", capture.report)
            reconstruct.assert_called_once_with(b"opaque synthetic ELF fixture")

    def test_first_and_last_byte_of_every_flash_block_are_compared(self):
        with tempfile.TemporaryDirectory() as folder, self.images(folder) as (binary, _):
            for label, address, size, region in FLASH_READS:
                for offset in (0, size - 1):
                    with self.subTest(label=label, byte_offset=offset):
                        changed = bytearray(expected_block(address, size, region))
                        changed[offset] ^= 1
                        capture = FlashFixture({label: bytes(changed)})
                        with self.assertRaises(ValueError):
                            self.subject.verify_flash(capture, binary)
                        self.assertFalse(capture.report.get("flash_identity_verified", False))
                        self.assertTrue(all(flag is False for flag in capture.flags_at_read))

    def test_partial_and_failed_each_block_never_grant_ram_authority(self):
        with tempfile.TemporaryDirectory() as folder, self.images(folder) as (binary, _):
            for label, address, size, region in FLASH_READS:
                for response in (expected_block(address, size, region)[:-1], ValueError("synthetic read failure")):
                    with self.subTest(label=label, response_type=type(response).__name__):
                        capture = FlashFixture({label: response})
                        with self.assertRaises(ValueError):
                            self.subject.verify_flash(capture, binary)
                        self.assertFalse(capture.report.get("flash_identity_verified", False))
                        self.assertTrue(all(flag is False for flag in capture.flags_at_read))

    def test_prior_true_flag_is_cleared_before_a_fresh_failed_verification(self):
        with tempfile.TemporaryDirectory() as folder, self.images(folder) as (binary, _):
            capture = FlashFixture({"sketch-02": bytes(15000)}, previous_flash_flag=True)
            with self.assertRaises(ValueError):
                self.subject.verify_flash(capture, binary)
            self.assertEqual(capture.flags_at_read, [False] * 8)
            self.assertFalse(capture.report.get("flash_identity_verified", False))

    def test_unverified_artifact_fails_before_reads(self):
        with tempfile.TemporaryDirectory() as folder, self.images(folder) as (binary, _):
            capture = FlashFixture(verified=False)
            with self.assertRaises(ValueError):
                self.subject.verify_flash(capture, binary)
            self.assertEqual(capture.calls, [])

    def test_package_difference_is_reported_but_deployed_flash_must_match_elf_even_there(self):
        changed = bytearray(LOADER_BYTES)
        changed[0x3F8BF] = 255
        with tempfile.TemporaryDirectory() as folder, self.images(folder, packaged=bytes(changed)) as (binary, _):
            capture = FlashFixture()
            self.subject.verify_flash(capture, binary)
            identity = capture.report["loader_identity"]
            self.assertIs(identity["package_binary_matches"], False)
            self.assertEqual(identity["package_binary_different_bytes"], 1)
            self.assertEqual(identity["package_binary_first_differences"],
                             [{"offset": 260287, "elf": 0, "binary": 255}])
            self.assertTrue(capture.report["flash_identity_verified"])
            live_package_byte = bytes(changed[0x30000:0x40000])
            capture = FlashFixture({"loader-03": live_package_byte})
            with self.assertRaises(ValueError):
                self.subject.verify_flash(capture, binary)
            self.assertFalse(capture.report.get("flash_identity_verified", False))


class RecorderFlashReadBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject, _, _ = import_without_actions()

    def capture(self, folder):
        report = {"flash_identity_verified": False,
                  "extension": {"bss_address": 0x20060000},
                  "layout": {"bss_size": 4096, "symbols": {
                      "recorderDiagnostics": {"offset": 128, "size": 296}}}}
        capture = self.subject.Capture(Path(folder), report)
        capture.identities_verified = True
        capture.binary_size = 146072
        return capture

    @staticmethod
    def write_block(argv, attach=False):
        del attach
        command = argv[4]
        destination, address_size = command[len("dump_image {"):].split("} ", 1)
        address_text, size_text = address_size.split()
        address, size = int(address_text, 16), int(size_text)
        if LOADER_BASE <= address < LOADER_BASE + 263680:
            data = expected_block(address, size, "loader")
        elif SKETCH_BASE <= address < SKETCH_BASE + 146072:
            data = expected_block(address, size, "sketch")
        else:
            data = bytes(size)
        Path(destination).write_bytes(data)

    def test_indexed_flash_allowlist_accepts_only_exact_eight_ranges(self):
        with tempfile.TemporaryDirectory() as folder:
            capture = self.capture(folder)
            with mock.patch.object(capture, "run", side_effect=self.write_block):
                for label, address, size, region in FLASH_READS:
                    self.assertEqual(capture.read(label, address, size, region),
                                     expected_block(address, size, region))
            self.assertEqual(capture.read_count, 8)
            self.assertEqual(capture.read_bytes, 409752)
            self.assertFalse(capture.report["flash_identity_verified"])

    def test_bad_indices_addresses_sizes_and_region_never_issue_commands(self):
        cases = [
            ("loader-05", 0x08050000, 65536, "loader"),
            ("loader-0", 0x08000000, 65536, "loader"),
            ("loader-000", 0x08000000, 65536, "loader"),
            ("loader--1", 0x07FF0000, 65536, "loader"),
            ("loader-00", 0x08000004, 65536, "loader"),
            ("loader-00", 0x08000000, 65535, "loader"),
            ("loader-04", 0x08040000, 65536, "loader"),
            ("loader-04", 0x08040000, 1535, "loader"),
            ("loader-00", 0x08000000, 65536, "sketch"),
            ("sketch-03", 0x08130000, 65536, "sketch"),
            ("sketch-02", 0x08120000, 15001, "sketch"),
            ("sketch-02", 0x08120000, 65536, "sketch"),
            ("sketch-01", 0x08100000, 65536, "sketch"),
            ("sketch-00", 0x08100000, 65536, "ram"),
        ]
        with tempfile.TemporaryDirectory() as folder:
            for values in cases:
                with self.subTest(values=values):
                    capture = self.capture(folder)
                    with mock.patch.object(capture, "run", side_effect=AssertionError("external action forbidden")):
                        with self.assertRaises(ValueError):
                            capture.read(*values)

    def test_actual_ram_gate_stays_closed_during_all_flash_chunks_and_opens_after_match(self):
        with tempfile.TemporaryDirectory() as folder:
            capture = self.capture(folder)
            fixture = RecorderFlashIdentityTests()
            fixture.subject = self.subject
            checked = []
            def run(argv, attach=False):
                if "0x080" in argv[4] or "0x081" in argv[4]:
                    with self.assertRaises(ValueError):
                        capture.read("heap-descriptor-first", 0x2000112C, 24)
                    checked.append(capture.report["flash_identity_verified"])
                self.write_block(argv, attach)
            with fixture.images(folder) as (binary, _), mock.patch.object(capture, "run", side_effect=run):
                self.subject.verify_flash(capture, binary)
                self.assertEqual(checked, [False] * 8)
                self.assertEqual(capture.read_count, 8)
                self.assertEqual(capture.read("heap-descriptor-first", 0x2000112C, 24), bytes(24))
                self.assertEqual(capture.read_count, 9)

    def test_new_flash_blocks_retain_old_read_and_byte_limits(self):
        with tempfile.TemporaryDirectory() as folder:
            capture = self.capture(folder)
            capture.read_count = 47
            with mock.patch.object(capture, "run", side_effect=self.write_block) as run:
                capture.read("loader-00", LOADER_BASE, 65536, "loader")
                with self.assertRaises(ValueError):
                    capture.read("loader-01", LOADER_BASE + 65536, 65536, "loader")
                self.assertEqual(run.call_count, 1)
            fresh = Path(folder) / "bytes"
            fresh.mkdir()
            capture = self.capture(fresh)
            capture.read_bytes = 2097152 - 65536
            with mock.patch.object(capture, "run", side_effect=self.write_block) as run:
                capture.read("loader-00", LOADER_BASE, 65536, "loader")
                with self.assertRaises(ValueError):
                    capture.read("loader-01", LOADER_BASE + 65536, 65536, "loader")
                self.assertEqual(run.call_count, 1)

    def test_failed_and_short_flash_block_remain_charged_and_cannot_be_retried(self):
        for failed in (False, True):
            with self.subTest(failed=failed), tempfile.TemporaryDirectory() as folder:
                capture = self.capture(folder)
                def response(argv, attach=False):
                    del argv, attach
                    if failed:
                        raise ValueError("synthetic flash command failure")
                    (Path(folder) / "00-loader-00.bin").write_bytes(LOADER_BYTES[:942])
                with mock.patch.object(capture, "run", side_effect=response) as run:
                    with self.assertRaises(ValueError):
                        capture.read("loader-00", LOADER_BASE, 65536, "loader")
                    with self.assertRaises(ValueError):
                        capture.read("loader-00", LOADER_BASE, 65536, "loader")
                    self.assertEqual(run.call_count, 1)
                self.assertEqual(capture.read_count, 1)
                self.assertEqual(capture.read_bytes, 65536)
                self.assertFalse(capture.report["flash_identity_verified"])
                if not failed:
                    self.assertEqual((Path(folder) / "00-loader-00.bin").read_bytes(), LOADER_BYTES[:942])

    def test_whole_path_uses_47_reads_one_extension_48_two_and_rejects_third(self):
        for count in (1, 2, 3):
            with self.subTest(extensions=count), tempfile.TemporaryDirectory() as folder:
                capture = self.capture(folder)
                topology = LinkedExtensions(count)
                image_fixture = RecorderFlashIdentityTests()
                image_fixture.subject = self.subject
                pool = recorder_heap_vectors.all_free()
                def run(argv, attach=False):
                    del attach
                    destination, address_size = argv[4][len("dump_image {"):].split("} ", 1)
                    address_text, size_text = address_size.split()
                    address, size = int(address_text, 16), int(size_text)
                    if LOADER_BASE <= address < LOADER_BASE + 263680:
                        data = expected_block(address, size, "loader")
                    elif SKETCH_BASE <= address < SKETCH_BASE + 146072:
                        data = expected_block(address, size, "sketch")
                    elif address == 0x200017BC and size == 8:
                        data = topology.list_bytes
                    elif address in topology.nodes and size == 196:
                        data = topology.nodes[address]
                    elif address == 0x20060080 and size == 296:
                        data = diagnostics()[0]
                    elif address == 0x2000112C and size == 24:
                        data = struct.pack("<6I", 0x20013890, 0x20013890, 262144, 0, 0, 0)
                    elif 0x20013890 <= address < 0x20053890 and size == 16384:
                        offset = address - 0x20013890
                        data = pool[offset:offset + size]
                    else:
                        raise AssertionError((address, size))
                    Path(destination).write_bytes(data)
                with image_fixture.images(folder) as (binary, _), mock.patch.object(capture, "run", side_effect=run):
                    self.subject.verify_flash(capture, binary)
                    base = self.subject.find_bss(capture, 4096)
                    symbols = capture.report["layout"]["symbols"]
                    if count < 3:
                        self.subject.capture_values(capture, base, symbols)
                        self.assertEqual(capture.read_count, 46 + count)
                        self.assertEqual(capture.report["heap"]["consistency"], "CONSISTENT_SAMPLED")
                    else:
                        with self.assertRaises(ValueError):
                            self.subject.capture_values(capture, base, symbols)
                        self.assertEqual(capture.read_count, 48)
                        self.assertTrue((Path(folder) / "pool-first.bin").exists())
                        self.assertTrue((Path(folder) / "pool-second.bin").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
