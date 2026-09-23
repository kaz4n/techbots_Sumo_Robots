"""Validate D091's offline heap decoder from the pinned allocator contract.

Fixtures and assertions were authored without reading the new decoder body.
Uses source-derived literal accounting and hostile metadata, never MCU access.
"""
import hashlib
import re
import unittest

from tests.fixtures import recorder_heap_vectors as fixture
from tools import recorder_heap as subject


class RecorderHeapTests(unittest.TestCase):
    def reject(self, blob, **options):
        with self.assertRaises(subject.HeapError) as caught:
            subject.decode_pool(blob, **options)
        self.assertIsInstance(caught.exception, ValueError)
        self.assertIsInstance(caught.exception.code, str)
        self.assertTrue(caught.exception.code)

    def accounting(self, report, free, used, overhead, free_count, used_count, largest):
        expected = {
            "schema_version": 1, "base_address": 0x20013890,
            "pool_bytes": 262144, "end_chunk": 32767, "metadata_bytes": 80,
            "free_payload_bytes": free, "used_payload_bytes": used,
            "overhead_bytes": overhead, "free_chunk_count": free_count,
            "used_chunk_count": used_count, "largest_free_payload_bytes": largest,
        }
        for key, value in expected.items():
            self.assertEqual(report[key], value, key)
        self.assertEqual(free + used + overhead, 262144)
        for key in ("metadata_sha256", "snapshot_sha256"):
            self.assertRegex(report[key], re.compile(r"^[0-9a-f]{64}$"))

    def test_fresh_free_heap_literal(self):
        blob = fixture.all_free()
        result = subject.decode_pool(blob)
        self.accounting(result, 262052, 0, 92, 1, 0, 262052)
        self.assertEqual(result["chunks"], [
            {"index": 10, "size_units": 32757, "used": False, "payload_bytes": 262052}])
        self.assertEqual(result["snapshot_sha256"], hashlib.sha256(blob).hexdigest())

    def test_all_used_literal(self):
        result = subject.decode_pool(fixture.all_used())
        self.accounting(result, 0, 262052, 92, 0, 1, 0)
        self.assertEqual(result["chunks"], [
            {"index": 10, "size_units": 32757, "used": True, "payload_bytes": 262052}])

    def test_minimum_used_chunk_and_split(self):
        result = subject.decode_pool(fixture.layout([(1, True), (32756, False)]))
        self.accounting(result, 262044, 4, 96, 1, 1, 262044)
        self.assertEqual(result["chunks"][0],
                         {"index": 10, "size_units": 1, "used": True, "payload_bytes": 4})

    def test_fragmented_circular_bucket_accounting(self):
        result = subject.decode_pool(fixture.fragmented())
        self.accounting(result, 261924, 108, 112, 3, 3, 261804)
        self.assertEqual([c["index"] for c in result["chunks"]], [10, 15, 23, 30, 38, 41])

    def test_all_fifteen_size_buckets(self):
        # Use a separate exact power-of-two representative per pool: all buckets
        # cannot coexist in 32757 units with the required used separators.
        for exponent in range(15):
            size = 1 << exponent
            with self.subTest(bucket=exponent):
                result = subject.decode_pool(fixture.layout([(size, False), (32757 - size, True)]))
                self.assertEqual(result["free_chunk_count"], 1)
                self.assertEqual(result["free_payload_bytes"], size * 8 - 4)

    def test_maximum_forward_chain_all_used(self):
        result = subject.decode_pool(fixture.layout([(1, True)] * 32757))
        self.accounting(result, 0, 131028, 131116, 0, 32757, 0)
        self.assertEqual(len(result["chunks"]), 32757)

    def test_maximum_bounded_free_list(self):
        result = subject.decode_pool(fixture.layout([(1, number % 2 == 1) for number in range(32757)]))
        self.accounting(result, 65516, 65512, 131116, 16379, 16378, 4)
        self.assertEqual(len(result["chunks"]), 32757)

    def test_snapshot_requires_exact_length(self):
        blob = fixture.all_free()
        for wrong in (b"", blob[:-1], blob + b"\0", blob[:80]):
            with self.subTest(length=len(wrong)):
                self.reject(wrong)

    def test_snapshot_requires_exact_pinned_address(self):
        for address in (0, 0x20013891, 0x20013888, 0x2000AF90, -1, 1 << 64):
            with self.subTest(base=address):
                self.reject(fixture.all_free(), base_address=address)

    def test_unsupported_end_chunk_rejected_before_field_width_assumption(self):
        for value in (0, 10, 32766, 32768, 0xFFFFFFFF):
            with self.subTest(end_chunk=value):
                self.reject(fixture.edit32(fixture.all_free(), 8, value))

    def test_metadata_chunk_left_size_used_and_size(self):
        for offset, value in ((0, 1), (2, 20), (2, 19), (2, 23), (2, 1), (2, 0xFFFF)):
            with self.subTest(offset=offset, value=value):
                self.reject(fixture.edit16(fixture.all_free(), offset, value))

    def test_zero_size_and_overrunning_normal_chunks(self):
        for value in (0, 1, 0xFFFC, 0xFFFF):
            with self.subTest(size_used=value):
                self.reject(fixture.edit16(fixture.all_free(), 82, value))

    def test_each_normal_left_neighbor_is_validated(self):
        for index in (10, 15, 23, 30, 38, 41):
            with self.subTest(index=index):
                self.reject(fixture.edit16(fixture.fragmented(), index * 8, 0))

    def test_terminal_used_size_and_left_neighbor(self):
        for offset, value in ((262136, 0), (262136, 32756), (262138, 0), (262138, 3), (262138, 65535)):
            with self.subTest(offset=offset, value=value):
                self.reject(fixture.edit16(fixture.all_free(), offset, value))

    def test_adjacent_free_chunks_are_rejected(self):
        self.reject(fixture.layout([(1, False), (32756, False)]))

    def test_available_mask_unknown_and_missing_bits(self):
        for mask in (0, 1, (1 << 14) | (1 << 15), 0xFFFFFFFF):
            with self.subTest(mask=mask):
                self.reject(fixture.edit32(fixture.all_free(), 12, mask))

    def test_bucket_head_must_name_a_free_chain_chunk(self):
        for head in (0, 1, 9, 11, 32767, 32768, 0xFFFFFFFF):
            with self.subTest(head=head):
                self.reject(fixture.edit32(fixture.all_free(), 72, head))

    def test_absent_bucket_cannot_have_head(self):
        for bucket in range(14):
            with self.subTest(bucket=bucket):
                self.reject(fixture.edit32(fixture.all_free(), 16 + 4 * bucket, 10))

    def test_wrong_size_bucket_and_duplicate_membership(self):
        blob = fixture.edit32(fixture.all_free(), 12, 1 << 13)
        blob = fixture.edit32(blob, 72, 0)
        self.reject(fixture.edit32(blob, 68, 10))
        blob = fixture.edit32(fixture.all_free(), 12, (1 << 13) | (1 << 14))
        self.reject(fixture.edit32(blob, 68, 10))

    def test_free_links_cannot_name_metadata_end_used_or_interior(self):
        blob = fixture.fragmented()
        for offset in (124, 126):
            for target in (0, 1, 10, 16, 23, 32767, 65535):
                with self.subTest(offset=offset, target=target):
                    self.reject(fixture.edit16(blob, offset, target))

    def test_reciprocal_links_and_head_missing_cycle(self):
        blob = fixture.fragmented()
        for offset, target in ((124, 15), (126, 15), (244, 30), (246, 30)):
            with self.subTest(offset=offset, target=target):
                self.reject(fixture.edit16(blob, offset, target))
        # Head 15 points to 30, whose self-cycle never returns to head 15.
        hostile = fixture.edit16(fixture.edit16(blob, 244, 30), 246, 30)
        self.reject(hostile)

    def test_unlisted_free_chunk_is_rejected(self):
        blob = fixture.fragmented()
        blob = fixture.edit16(fixture.edit16(blob, 124, 15), 126, 15)
        blob = fixture.edit16(fixture.edit16(blob, 244, 30), 246, 30)
        self.reject(blob)

    def test_payload_changes_do_not_change_allocator_metadata(self):
        first = fixture.fragmented()
        second = bytearray(first)
        second[84:120] = b"\xA5" * 36  # all payload of used chunk 10
        second[128:184] = b"\x5A" * 56  # stale free payload, after both links
        first_report = subject.decode_pool(first)
        second_report = subject.decode_pool(bytes(second))
        self.assertEqual(first_report["metadata_sha256"], second_report["metadata_sha256"])
        self.assertNotEqual(first_report["snapshot_sha256"], second_report["snapshot_sha256"])
        result = subject.compare_pools(first, bytes(second))
        self.assertEqual(result["consistency"], "CONSISTENT_SAMPLED")
        self.assertEqual(result["second_snapshot_sha256"], hashlib.sha256(second).hexdigest())
        self.assertEqual(result["snapshot_sha256"], hashlib.sha256(first).hexdigest())
        self.accounting(result, 261924, 108, 112, 3, 3, 261804)

    def test_same_pool_comparison(self):
        blob = fixture.all_free()
        result = subject.compare_pools(blob, blob)
        self.assertEqual(result["consistency"], "CONSISTENT_SAMPLED")
        self.assertEqual(result["snapshot_sha256"], result["second_snapshot_sha256"])

    def test_reserved_small_header_and_alignment_padding_are_not_metadata(self):
        blob = fixture.all_free()
        first = subject.decode_pool(blob)
        for start in (4, 76, 262140):
            with self.subTest(offset=start):
                changed = bytearray(blob)
                changed[start:start + 4] = b"\xF1\xE2\xD3\xC4"
                second = subject.decode_pool(bytes(changed))
                self.assertEqual(first["metadata_sha256"], second["metadata_sha256"])
                self.assertNotEqual(first["snapshot_sha256"], second["snapshot_sha256"])
                self.assertEqual(subject.compare_pools(blob, bytes(changed))["consistency"],
                                 "CONSISTENT_SAMPLED")

    def test_valid_circular_head_rotation_changes_metadata(self):
        first = fixture.fragmented()
        second = fixture.edit32(first, 28, 30)  # bucket3 starts at the other size8 node
        self.accounting(subject.decode_pool(second), 261924, 108, 112, 3, 3, 261804)
        self.assertNotEqual(subject.decode_pool(first)["metadata_sha256"],
                            subject.decode_pool(second)["metadata_sha256"])
        with self.assertRaises(subject.HeapError):
            subject.compare_pools(first, second)

    def test_changed_valid_allocator_layout_rejected(self):
        with self.assertRaises(subject.HeapError) as caught:
            subject.compare_pools(fixture.all_free(), fixture.all_used())
        self.assertIsInstance(caught.exception.code, str)
        self.assertTrue(caught.exception.code)

    def test_comparison_validates_both_inputs(self):
        valid = fixture.all_free()
        corrupt = fixture.edit16(valid, 262138, 0)
        for first, second in ((corrupt, valid), (valid, corrupt), (corrupt, corrupt)):
            with self.subTest(first_valid=first == valid, second_valid=second == valid):
                with self.assertRaises(subject.HeapError):
                    subject.compare_pools(first, second)


if __name__ == "__main__":
    unittest.main(verbosity=2)
