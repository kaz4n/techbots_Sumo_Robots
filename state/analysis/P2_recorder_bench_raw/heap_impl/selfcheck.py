# Exercise the offline allocator decoder with literal pinned-layout snapshots.
# Keep implementation smoke evidence separate from independent acceptance tests.
# Run locally with Python; no board, network, capture or hardware interaction.
import hashlib
import json
from pathlib import Path
import struct
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))
import recorder_heap


def pool(layout):
    blob = bytearray(262144)
    struct.pack_into("<HH", blob, 0, 0, 21)
    struct.pack_into("<II", blob, 8, 32767, 0)
    index, previous = 10, 10
    buckets = [[] for _ in range(15)]
    for size, used in layout:
        struct.pack_into("<HH", blob, index * 8, previous, size * 2 + used)
        if not used:
            buckets[size.bit_length() - 1].append(index)
        previous, index = size, index + size
    assert index == 32767
    struct.pack_into("<HH", blob, index * 8, previous, 1)
    avail = 0
    for bucket, ids in enumerate(buckets):
        if not ids:
            continue
        avail |= 1 << bucket
        struct.pack_into("<I", blob, 16 + 4 * bucket, ids[0])
        for position, chunk_id in enumerate(ids):
            struct.pack_into("<HH", blob, 8 * chunk_id + 4,
                             ids[position - 1], ids[(position + 1) % len(ids)])
    struct.pack_into("<I", blob, 12, avail)
    return bytes(blob)


def rejected(blob, **kwargs):
    try:
        recorder_heap.decode_pool(blob, **kwargs)
    except recorder_heap.HeapError as error:
        assert isinstance(error.code, str) and error.code
        return error.code
    raise AssertionError("invalid pool accepted")


def main():
    started = time.monotonic()
    checks = []
    all_free = pool([(32757, 0)])
    report = recorder_heap.decode_pool(all_free)
    assert (report["free_payload_bytes"], report["used_payload_bytes"],
            report["overhead_bytes"], report["largest_free_payload_bytes"]) == (262052, 0, 92, 262052)
    checks.append("all_free_exact_totals")
    all_used = pool([(32757, 1)])
    report = recorder_heap.decode_pool(all_used)
    assert (report["free_payload_bytes"], report["used_payload_bytes"],
            report["overhead_bytes"], report["largest_free_payload_bytes"]) == (0, 262052, 92, 0)
    checks.append("all_used_exact_totals")
    fragmented = pool([(1, 1), (2, 0), (1, 1), (2, 0), (32751, 1)])
    report = recorder_heap.decode_pool(fragmented)
    assert (report["free_payload_bytes"], report["used_payload_bytes"],
            report["overhead_bytes"], report["largest_free_payload_bytes"]) == (24, 262012, 108, 12)
    checks.append("fragmented_exact_totals")
    maximal = pool([(1, 1)] * 32757)
    report = recorder_heap.decode_pool(maximal)
    assert len(report["chunks"]) == 32757 and report["used_payload_bytes"] == 131028
    assert report["overhead_bytes"] == 131116
    checks.append("maximal_forward_chain")
    changed = bytearray(fragmented)
    changed[84] = 63
    changed[96] = 127
    compared = recorder_heap.compare_pools(fragmented, bytes(changed))
    assert compared["consistency"] == "CONSISTENT_SAMPLED"
    assert compared["snapshot_sha256"] != compared["second_snapshot_sha256"]
    checks.append("used_and_stale_payload_excluded")
    try:
        recorder_heap.compare_pools(all_free, all_used)
    except recorder_heap.HeapError as error:
        assert error.code == "INCONSISTENT_METADATA"
    else:
        raise AssertionError("changed allocator metadata accepted")
    checks.append("different_valid_metadata_rejected")
    return started, checks, all_free, fragmented


def corruption_checks(all_free, fragmented):
    failures = {}
    for name, offset, fmt, value in [
            ("zero_normal_size", 82, "H", 0),
            ("left_link", 80, "H", 9),
            ("bad_footer", 262138, "H", 0),
            ("high_bucket_bit", 12, "I", (1 << 31) | (1 << 14)),
            ("bad_free_link", 84, "H", 32767),
            ("wrong_end_chunk", 8, "I", 32768),
            ("wrong_metadata_size", 2, "H", 19)]:
        changed = bytearray(all_free)
        struct.pack_into("<" + fmt, changed, offset, value)
        failures[name] = rejected(bytes(changed))
    failures["pool_size"] = rejected(all_free[:-1])
    failures["base_address"] = rejected(all_free, base_address=0x20013898)
    failures["mutable_input"] = rejected(bytearray(all_free))
    failures["adjacent_free"] = rejected(pool([(1, 0), (32756, 0)]))
    changed = bytearray(fragmented)
    struct.pack_into("<HH", changed, 92, 11, 11)
    failures["missing_free_node"] = rejected(bytes(changed))
    return failures


if __name__ == "__main__":
    start, cases, free_pool, fragmented_pool = main()
    errors = corruption_checks(free_pool, fragmented_pool)
    result = {"result": "PASS", "scope": "offline synthetic implementation smoke only",
              "checks": cases, "rejected": errors, "elapsed_s": time.monotonic() - start,
              "source_sha256": hashlib.sha256((ROOT / "tools/recorder_heap.py").read_bytes()).hexdigest()}
    Path(__file__).with_name("selfcheck.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
