"""Construct independent pinned Zephyr heap byte vectors.

Derived from cached heap.h fields and heap.c sys_heap_init, without decoder access.
Checked by tests/tooling/test_recorder_heap.py with literal accounting expectations.
"""
import struct

POOL_BYTES = 262144
BASE_ADDRESS = 0x20013890
END_CHUNK = 32767


def put16(blob, offset, value):
    struct.pack_into("<H", blob, offset, value)


def put32(blob, offset, value):
    struct.pack_into("<I", blob, offset, value)


def all_free():
    # sys_heap_init: 16-byte z_heap + 15 four-byte buckets rounded to 80.
    blob = bytearray(POOL_BYTES)
    blob[:16] = bytes.fromhex("0000150000000000ff7f000000400000")
    blob[72:76] = bytes.fromhex("0a000000")  # bucket 14 -> chunk 10
    blob[80:88] = bytes.fromhex("0a00eaff0a000a00")
    blob[262136:262140] = bytes.fromhex("f57f0100")
    return bytes(blob)


def all_used():
    blob = bytearray(all_free())
    blob[12:16] = bytes(4)
    blob[72:76] = bytes(4)
    blob[82:84] = bytes.fromhex("ebff")
    return bytes(blob)


def layout(chunks):
    """Fixture-only serializer; sizes and expected accounting live in each test."""
    blob = bytearray(POOL_BYTES)
    blob[:16] = bytes.fromhex("0000150000000000ff7f000000000000")
    index, previous = 10, 10
    buckets = {}
    for size, used in chunks:
        put16(blob, index * 8, previous)
        put16(blob, index * 8 + 2, size * 2 + int(used))
        if not used:
            buckets.setdefault(size.bit_length() - 1, []).append(index)
        index, previous = index + size, size
    assert index == END_CHUNK, "fixture must exactly tile the pinned pool"
    put16(blob, index * 8, previous)
    put16(blob, index * 8 + 2, 1)
    available = 0
    for bucket, nodes in buckets.items():
        available |= 1 << bucket
        put32(blob, 16 + 4 * bucket, nodes[0])
        for number, node in enumerate(nodes):
            put16(blob, node * 8 + 4, nodes[number - 1])
            put16(blob, node * 8 + 6, nodes[(number + 1) % len(nodes)])
    put32(blob, 12, available)
    return bytes(blob)


def fragmented():
    return layout([(5, True), (8, False), (7, True), (8, False),
                   (3, True), (32726, False)])


def edit16(blob, offset, value):
    result = bytearray(blob)
    put16(result, offset, value)
    return bytes(result)


def edit32(blob, offset, value):
    result = bytearray(blob)
    put32(result, offset, value)
    return bytes(result)
