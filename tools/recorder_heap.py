# Decode the pinned UNO Q LLEXT allocator from an offline byte snapshot.
# Validate every allocator link before reporting point-in-time payload capacity.
# Tested with independent source-derived fixtures and malformed offline snapshots.
"""D091 offline decoder for the pinned 32-bit, AUTO, no-stats/no-canary heap.

Layout authority: Zephyr 1743741760ee5d2d58da50d504855d43f9f8e826,
lib/heap/heap.h and heap.c, cached under
state/analysis/P2_recorder_bench_raw/native/primary/lib/heap/.
The installed-loader identity must be established separately before interpreting
captured bytes. This module neither captures memory nor verifies hardware origin.

Canonical metadata encoding, version 1:
  * ASCII b"SUMOX26_LLEXT_HEAP_METADATA_V1\\0";
  * base address and pool byte count, each unsigned 32-bit little endian;
  * ordered spans, each encoded as unsigned 32-bit little-endian byte offset,
    unsigned 32-bit little-endian length, then exactly those snapshot bytes.
The first spans are [0, 4) and [8, 76): the active chunk0 left-size/size-used
fields, end_chunk, avail_buckets and all fifteen uint32 bucket heads. They are
followed by ascending normal chunks' four-byte left-size/size-used headers,
extended to eight bytes for free chunks to include their prev/next links.
The final span is the four-byte end-marker header at byte offset 262136.
The unused chunk0_hdr second word [4, 8), chunk0 rounding bytes [76, 80), footer
alignment bytes [262140, 262144), normal used payload and stale free payload are
excluded. Offsets and lengths make the
encoding unambiguous; there are no native-endian values or JSON encodings.

Payload is allocator capacity (8 * size_units - 4), not original requested bytes.
Overhead includes chunk0, the reserved footer/alignment and normal headers.
Largest free payload does not guarantee an arbitrary aligned allocation.
Two matching metadata samples are not an atomic snapshot, a historical minimum,
or evidence that no allocate/free cycle occurred between reads. These numbers
do not describe stack space, other heaps, physical RAM qualification or WCET.
"""

from __future__ import annotations

import hashlib
import struct


_BASE_ADDRESS = 0x20013890
_POOL_BYTES = 262144
_CHUNK_BYTES = 8
_MAX_CHUNKS = 32768
_END_CHUNK = 32767
_METADATA_UNITS = 10
_METADATA_BYTES = 80
_BUCKET_COUNT = 15
_HEADER_AND_BUCKET_BYTES = 76
_DIGEST_PREFIX = b"SUMOX26_LLEXT_HEAP_METADATA_V1\0"


class HeapError(ValueError):
    """Rejected snapshot; ``code`` is a machine-readable failure category."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(f"{code}: {message}")


def _validate_input(blob: bytes, base_address: int) -> None:
    # Immutable input prevents a caller from changing fields during validation.
    if type(blob) is not bytes:
        raise HeapError("INPUT_TYPE", "snapshot must be immutable bytes")
    if len(blob) != _POOL_BYTES:
        raise HeapError("POOL_SIZE", "snapshot must contain exactly 262144 bytes")
    if type(base_address) is not int or base_address != _BASE_ADDRESS:
        raise HeapError("BASE_ADDRESS", "only the pinned base 0x20013890 is supported")


def _header(blob: bytes) -> tuple[int, tuple[int, ...]]:
    left, size_used = struct.unpack_from("<HH", blob, 0)
    end_chunk, avail = struct.unpack_from("<II", blob, 8)
    # AUTO chooses field width from end_chunk, after the original 8-byte footer.
    if end_chunk != _END_CHUNK or end_chunk > 0x7FFF:
        raise HeapError("HEADER", "unsupported end_chunk or chunk-field layout")
    if left != 0 or size_used != (_METADATA_UNITS << 1 | 1):
        raise HeapError("CHUNK_ZERO", "chunk0 must be used, ten units, with left_size zero")
    if avail & ~((1 << _BUCKET_COUNT) - 1):
        raise HeapError("BUCKET_MASK", "availability contains an unavailable bucket")
    heads = struct.unpack_from("<15I", blob, 16)
    for bucket in range(_BUCKET_COUNT):
        if bool(heads[bucket]) != bool(avail & (1 << bucket)):
            raise HeapError("BUCKET_HEAD", "bucket head and availability disagree")
    return avail, heads


def _append_span(canonical: bytearray, blob: bytes, offset: int, length: int) -> None:
    if offset < 0 or length < 0 or offset + length > _POOL_BYTES:
        raise HeapError("CHUNK_BOUNDS", "metadata span exceeds the pinned pool")
    canonical.extend(struct.pack("<II", offset, length))
    canonical.extend(blob[offset:offset + length])


def _walk_chunks(blob: bytes, canonical: bytearray) -> tuple[list[dict], dict]:
    chunks, free = [], {}
    index, previous_size, previous_free = _METADATA_UNITS, _METADATA_UNITS, False
    # The loop limit is fixed, never supplied by the snapshot or user payload.
    for _ in range(_MAX_CHUNKS):
        if not _METADATA_UNITS <= index <= _END_CHUNK:
            raise HeapError("CHUNK_BOUNDS", "chunk lies outside the normal chain")
        offset = index * _CHUNK_BYTES
        left, size_used = struct.unpack_from("<HH", blob, offset)
        size, used = size_used >> 1, bool(size_used & 1)
        if left != previous_size:
            raise HeapError("LEFT_LINK", f"chunk {index} has the wrong left_size")
        if index == _END_CHUNK:
            if size != 0 or not used:
                raise HeapError("END_MARKER", "footer must have zero size and be used")
            _append_span(canonical, blob, offset, 4)
            return chunks, free
        if size == 0:
            raise HeapError("CHUNK_ZERO_SIZE", f"normal chunk {index} cannot be empty")
        next_index = index + size
        if next_index <= index or next_index > _END_CHUNK:
            raise HeapError("CHUNK_BOUNDS", f"chunk {index} does not step within the pool")
        if previous_free and not used:
            raise HeapError("ADJACENT_FREE", "adjacent free chunks must be coalesced")
        chunks.append({"index": index, "size_units": size, "used": used,
                       "payload_bytes": size * _CHUNK_BYTES - 4})
        if not used:
            prev_id, next_id = struct.unpack_from("<HH", blob, offset + 4)
            free[index] = (size, prev_id, next_id)
        _append_span(canonical, blob, offset, 4 if used else 8)
        index, previous_size, previous_free = next_index, size, not used
    raise HeapError("WALK_LIMIT", "chunk chain exceeded the fixed walk limit")


def _free_node(free: dict, index: int, bucket: int) -> tuple[int, int, int]:
    # Only a boundary found by the validated chain may supply a free-list node.
    if not _METADATA_UNITS <= index < _END_CHUNK or index not in free:
        raise HeapError("FREE_LINK", f"{index} is not a normal free-chunk boundary")
    node = free[index]
    if node[0].bit_length() - 1 != bucket:
        raise HeapError("FREE_BUCKET", f"free chunk {index} is in the wrong bucket")
    return node


def _validate_free_lists(heads: tuple[int, ...], free: dict) -> None:
    visited = set()
    total_walked = 0
    for bucket in range(_BUCKET_COUNT):
        head = heads[bucket]
        if head == 0:
            continue
        current, local = head, set()
        for _ in range(_MAX_CHUNKS):
            if current in local:
                if current != head:
                    raise HeapError("FREE_CYCLE", "free-list cycle misses its head")
                break
            if current in visited:
                raise HeapError("FREE_DUPLICATE", "free chunk belongs to multiple lists")
            _, prev_id, next_id = _free_node(free, current, bucket)
            prev_node = _free_node(free, prev_id, bucket)
            next_node = _free_node(free, next_id, bucket)
            if prev_node[2] != current or next_node[1] != current:
                raise HeapError("FREE_RECIPROCITY", "free-list neighbors are not reciprocal")
            total_walked += 1
            if total_walked > _MAX_CHUNKS:
                raise HeapError("WALK_LIMIT", "free lists exceeded the fixed total walk limit")
            local.add(current)
            visited.add(current)
            current = next_id
        else:
            raise HeapError("WALK_LIMIT", "free list exceeded the fixed walk limit")
    if visited != set(free):
        raise HeapError("FREE_COVERAGE", "bucket lists do not cover exactly every free chunk")


def _report(blob: bytes, chunks: list[dict], canonical: bytes) -> dict:
    free_payload = sum(c["payload_bytes"] for c in chunks if not c["used"])
    used_payload = sum(c["payload_bytes"] for c in chunks if c["used"])
    free_count = sum(not c["used"] for c in chunks)
    # Account for the whole reserved footer, including its four alignment bytes.
    overhead = _METADATA_BYTES + (_POOL_BYTES - _END_CHUNK * _CHUNK_BYTES)
    overhead += 4 * len(chunks)
    if free_payload + used_payload + overhead != _POOL_BYTES:
        raise HeapError("ACCOUNTING", "payload and overhead do not partition the pool")
    return {
        "schema_version": 1, "base_address": _BASE_ADDRESS,
        "pool_bytes": _POOL_BYTES, "end_chunk": _END_CHUNK,
        "metadata_bytes": _METADATA_BYTES, "free_payload_bytes": free_payload,
        "largest_free_payload_bytes": max(
            (c["payload_bytes"] for c in chunks if not c["used"]), default=0),
        "used_payload_bytes": used_payload, "overhead_bytes": overhead,
        "free_chunk_count": free_count, "used_chunk_count": len(chunks) - free_count,
        "chunks": chunks, "metadata_sha256": hashlib.sha256(canonical).hexdigest(),
        "snapshot_sha256": hashlib.sha256(blob).hexdigest(),
    }


def _decode(blob: bytes, base_address: int) -> tuple[dict, bytes]:
    _validate_input(blob, base_address)
    _, heads = _header(blob)
    canonical = bytearray(_DIGEST_PREFIX)
    canonical.extend(struct.pack("<II", base_address, _POOL_BYTES))
    _append_span(canonical, blob, 0, 4)
    _append_span(canonical, blob, 8, _HEADER_AND_BUCKET_BYTES - 8)
    chunks, free = _walk_chunks(blob, canonical)
    _validate_free_lists(heads, free)
    encoded = bytes(canonical)
    return _report(blob, chunks, encoded), encoded


def decode_pool(blob: bytes, *, base_address: int = _BASE_ADDRESS) -> dict:
    """Validate one exact pinned-pool snapshot and report its current capacity."""
    report, _ = _decode(blob, base_address)
    return report


def compare_pools(first: bytes, second: bytes, *, base_address: int = _BASE_ADDRESS) -> dict:
    """Validate both samples and require byte-identical canonical metadata.

    The returned snapshot_sha256 refers to first; second_snapshot_sha256 refers
    to second. CONSISTENT_SAMPLED makes no atomicity or between-sample claim.
    """
    first_report, first_metadata = _decode(first, base_address)
    second_report, second_metadata = _decode(second, base_address)
    if first_metadata != second_metadata:
        raise HeapError("INCONSISTENT_METADATA", "validated allocator metadata changed")
    first_report["second_snapshot_sha256"] = second_report["snapshot_sha256"]
    first_report["consistency"] = "CONSISTENT_SAMPLED"
    return first_report
