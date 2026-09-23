"""Independent offline audit of captured D091 bytes; issues no hardware command."""
from collections import Counter
from datetime import datetime
import csv
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'state/analysis/P2_recorder_bench_raw'
FOLDER = RAW / 'runtime_retry1'
OUT = Path(__file__).resolve().parent

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load(name):
    return json.loads((RAW / name).read_text())

capture = load('runtime_retry1/capture.json')
manifest = load('capture_retry1_manifest.json')
for name, digest in manifest.items():
    assert sha((FOLDER / name).read_bytes()) == digest, name
assert capture['status'] == 'CAPTURED' and capture['flash_identity_verified'] is True
reads, commands = capture['reads'], capture['commands']
assert len(reads) == capture['memory_read_attempts'] == 47 <= 48
assert sum(row['size'] for row in reads) == capture['memory_bytes_requested'] == 934892 <= 2097152
assert len(commands) == 51 <= 64
assert capture['capture_duration_seconds'] < 600
assert len({row['purpose'] for row in reads}) == len(reads)
payloads = {}
for i, row in enumerate(reads):
    data = (FOLDER / row['file']).read_bytes()
    assert len(data) == row['size'] and sha(data) == row['sha256']
    if row['region'] == 'ram':
        assert row['size'] <= 16384
    assert row['requested_monotonic'] <= row['completed_monotonic']
    command = commands[i + 4]
    assert command['argv'][:2] == ['/opt/openocd/bin/openocd', '-f']
    assert command['argv'][2].endswith('/recorder-fd1932ac/p0_mem_read.cfg')
    assert command['argv'][3] == '-c' and command['argv'][5:] == ['-c', 'shutdown']
    match = re.fullmatch(r'dump_image \{([^}]+)\} (0x[0-9a-f]+) ([0-9]+)', command['argv'][4])
    assert match and Path(match[1]).name == row['file']
    assert (int(match[2], 16), int(match[3])) == (row['address'], row['size'])
    assert row['requested_monotonic'] <= command['started_monotonic']
    assert command['finished_monotonic'] <= row['completed_monotonic']
    payloads[row['purpose']] = data
for command in commands:
    assert command['returncode'] == 0 and not command.get('timeout', False)
    assert 0 < command['timeout_seconds'] <= 30
    assert 0 <= command['finished_monotonic'] - command['started_monotonic'] < 30
    for stream in ('stdout', 'stderr'):
        data = (FOLDER / command[stream + '_file']).read_bytes()
        assert command.get(stream, '') == data[:65536].decode('utf-8', errors='replace')
        assert command.get(stream + '_truncated', False) == (len(data) > 65536)
assert commands[-1]['finished_monotonic'] - commands[0]['started_monotonic'] < 600
sync = load('capture_retry_tool_sync.json')
sync_hashes = dict(line.split(maxsplit=1)[::-1] for line in sync['records'][-1]['stdout'].splitlines())
for remote, digest in sync_hashes.items():
    assert sha((ROOT / 'tools' / Path(remote).name).read_bytes()) == digest
assert any(digest == 'fd1932acc3f78ce68fb833f54b1e1ce72ab97aeb3942cc53dad27acb45dc6e25'
           for digest in sync_hashes.values())
loader = b''.join(payloads[f'loader-{i:02d}'] for i in range(5))
sketch = b''.join(payloads[f'sketch-{i:02d}'] for i in range(3))
assert len(loader) == 263680 and sha(loader) == capture['loader_identity']['expected_sha256']
assert loader[260287] == 0
assert len(sketch) == 146072 and sha(sketch) == '0448e3ac5a5409bdfd08226f42f0d74c66dbe85d7bfd2ffb27a76acc3a7bfd2a'

# Reconstruct the actual LLEXT node, addresses, terminal record and descriptor.
assert payloads['llext-list'] == payloads['llext-list-confirm']
head, tail = struct.unpack('<II', payloads['llext-list'])
assert head == tail == capture['extension']['node_address']
node = payloads['node-1']
assert struct.unpack_from('<I', node)[0] == 0 and node[4:20].split(b'\0')[0] == b'sketch'
bss, bss_bytes = struct.unpack_from('<I', node, 32)[0], struct.unpack_from('<I', node, 92)[0]
assert bss == capture['extension']['bss_address'] and bss_bytes == 173892
assert payloads['diagnostics-first'] == payloads['diagnostics-last']
assert payloads['heap-descriptor-first'] == payloads['heap-descriptor-last']
diagnostic = payloads['diagnostics-first']
words = struct.unpack('<74I', diagnostic)
assert words[0] == words[73] == 410166 and words[0] % 2 == 0
assert words[1:5] == (1, 256, 4, 0) and words[59:65] == (0,) * 6
report = capture['diagnostics']['report']
fields = '''schema_version byte_size phase failure boot_us last_us release_us stop_us
elapsed_us ticks missed_slots max_lateness_us max_step_us nonzero_pwm enabled_en configure_calls
crc32 checksum_rows source_phase frame_count event_count epoch_lo epoch_hi last_frame_lo
last_frame_hi mode observed_results missing_results rejected_results identity_rejected malformed_batches
event_semantic_rejected upstream_event_rejected upstream_event_invalid source_regressions skipped_frames
timing_ticks_lo timing_ticks_hi timing_overruns_lo timing_overruns_hi timing_max_us timing_saturated
upstream_event_overflow timing_incomplete recording_incomplete go_seen final_frame_missing interrupted
terminal_exhausted frame_overwritten frame_rejected_status frame_clamped frame_invalid event_overflow
event_rejected incomplete robot_faults gate_fault'''.split()
assert len(fields) == 58
assert all(report[name] == words[i + 1] for i, name in enumerate(fields))
assert report['frame_count'] == 5001 and report['event_count'] == 8 and report['checksum_rows'] == 5009
losses = ['missed_slots','nonzero_pwm','enabled_en','missing_results','rejected_results',
          'identity_rejected','malformed_batches','event_semantic_rejected','upstream_event_rejected',
          'upstream_event_invalid','source_regressions','skipped_frames','timing_overruns_lo',
          'timing_overruns_hi','timing_saturated','upstream_event_overflow','timing_incomplete',
          'recording_incomplete','final_frame_missing','interrupted','terminal_exhausted',
          'frame_overwritten','frame_rejected_status','frame_clamped','frame_invalid','event_overflow',
          'event_rejected','incomplete','robot_faults']
assert all(report[key] == 0 for key in losses)
assert report['source_phase'] == 3 and report['gate_fault'] == 6 and report['go_seen'] == 1
valid, stack_start, stack_size, delta, minimum_sp, samples, headroom, fault = words[65:73]
assert valid == 1 and fault == 0 and samples > 0
assert 0x20000000 <= stack_start < 0x200c0000 and stack_start + stack_size <= 0x200c0000
assert 0 <= delta <= stack_size and stack_start <= minimum_sp <= stack_start + stack_size - delta
assert headroom == minimum_sp - stack_start == 31208
descriptor = struct.unpack('<6I', payloads['heap-descriptor-first'])
POOL = 0x20013890
assert descriptor[:3] == (POOL, POOL, 262144)
expected_reads = []
for region, base, total in [('loader',0x08000000,263680),('sketch',0x08100000,146072)]:
    for i,start in enumerate(range(0,total,65536)):
        expected_reads.append((f'{region}-{i:02d}',base+start,min(65536,total-start),region))
expected_reads += [('llext-list',0x200017bc,8,'ram'),('node-1',head,196,'ram'),
                   ('llext-list-confirm',0x200017bc,8,'ram'),
                   ('diagnostics-first',bss+0x28928,296,'ram'),
                   ('heap-descriptor-first',0x2000112c,24,'ram')]
for number in (1,2):
    expected_reads += [(f'pool-{number}-{i:02d}',POOL+i*16384,16384,'ram') for i in range(16)]
expected_reads += [('heap-descriptor-last',0x2000112c,24,'ram'),
                   ('diagnostics-last',bss+0x28928,296,'ram')]
assert expected_reads == [(r['purpose'],r['address'],r['size'],r['region']) for r in reads]

# Independently walk the pinned small-chunk allocator and its free lists.
pools = [(FOLDER / name).read_bytes() for name in ('pool-first.bin','pool-second.bin')]
assert pools[0] == pools[1]
for number in (1, 2):
    assert b''.join(payloads[f'pool-{number}-{i:02d}'] for i in range(16)) == pools[number - 1]
pool = pools[0]
assert len(pool) == 262144
assert struct.unpack_from('<HH', pool, 0) == (0, 21)
end, mask = struct.unpack_from('<II', pool, 8)
assert end == 32767 and mask < 1 << 15
heads = struct.unpack_from('<15I', pool, 16)
chunks = []
free = {}
position, previous = 10, 10
for _ in range(32768):
    left, tagged = struct.unpack_from('<HH', pool, position * 8)
    size, used = tagged >> 1, tagged & 1
    assert left == previous
    if position == end:
        assert size == 0 and used == 1
        break
    assert size > 0 and position + size <= end
    assert used or not chunks or chunks[-1]['used']
    chunks.append(dict(index=position, size_units=size, used=bool(used), payload_bytes=size * 8 - 4))
    if not used:
        free[position] = (size, *struct.unpack_from('<HH', pool, position * 8 + 4))
    previous, position = size, position + size
else:
    raise AssertionError('No end marker')
visited = set()
for bucket, head in enumerate(heads):
    assert bool(head) == bool(mask & (1 << bucket))
    if not head:
        continue
    current = head
    for _ in range(32768):
        assert current in free and current not in visited
        size, prev_node, next_node = free[current]
        assert size.bit_length() - 1 == bucket
        assert prev_node in free and next_node in free
        assert free[prev_node][2] == current and free[next_node][1] == current
        visited.add(current)
        current = next_node
        if current == head:
            break
    else:
        raise AssertionError('No finite free-list cycle')
assert visited == set(free)
free_bytes = sum(c['payload_bytes'] for c in chunks if not c['used'])
used_bytes = sum(c['payload_bytes'] for c in chunks if c['used'])
overhead = 80 + 8 + 4 * len(chunks)
assert free_bytes + used_bytes + overhead == 262144
assert chunks == capture['heap']['chunks']
assert (free_bytes, used_bytes, overhead) == (25116,236892,136)
assert max(c['payload_bytes'] for c in chunks if not c['used']) == 21604
assert sha(pool) == capture['heap']['snapshot_sha256'] == capture['heap']['second_snapshot_sha256']
canonical = bytearray(b'SUMOX26_LLEXT_HEAP_METADATA_V1\0' + struct.pack('<II',POOL,262144))
spans = [(0,4),(8,68)] + [(c['index']*8,4 if c['used'] else 8) for c in chunks] + [(end*8,4)]
for start,length in spans:
    canonical += struct.pack('<II',start,length) + pool[start:start+length]
assert sha(canonical) == capture['heap']['metadata_sha256']
assert any(c['used'] and POOL + c['index'] * 8 + 4 <= bss and
           bss + bss_bytes <= POOL + (c['index'] + c['size_units']) * 8 for c in chunks)

# Resolve offsets from actual DWARF expressions and readelf symbols, not extraction code.
layout = load('storage_layout.json')
target = load('target_1502e948_bench-default.json')
assert layout['returncode'] == layout['remote_returncode'] == 0
assert any(r['sha256'] == layout['sha256'] for r in target['records'])
values = [int(value,16) for value in re.findall(r'^\$\d+ = (0x[0-9a-f]+)$', layout['stdout'], re.M)]
offset = dict(zip(layout['expressions'], values))
assert len(values) == len(layout['expressions']) == 13
assert offset['frame_stride'] == 26 and offset['event_stride'] == 8 and offset['pointer_bytes'] == 4
symbols = load('final_symbols.json')['stdout'].splitlines()
symbol = next(s.split() for s in symbols if s.endswith('_ZN15recorder_native12_GLOBAL__N_16runnerE'))
runner = int(symbol[1],16)
assert runner == 0x90 and int(symbol[2],0) == offset['runner_size']
base = bss - POOL + runner + offset['runner_source']
frames_base = base + offset['source_frames'] + offset['frames_rows']
first = struct.unpack_from('<I',pool,base + offset['source_frames'] + offset['frames_first'])[0]
count = struct.unpack_from('<I',pool,base + offset['source_frames'] + offset['frames_size'])[0]
events_base = base + offset['source_events'] + offset['events_rows']
event_count = struct.unpack_from('<I',pool,base + offset['source_events'] + offset['events_size'])[0]
assert first == 0 and count == 5001 and event_count == 8
assert 0 <= frames_base and frames_base + 5001 * 26 <= len(pool)
assert 0 <= events_base and events_base + 4096 * 8 <= len(pool)
frames = [pool[frames_base + ((first+i)%5001)*26:frames_base + ((first+i)%5001)*26 + 26] for i in range(count)]
events = [pool[events_base+i*8:events_base+i*8+8] for i in range(event_count)]
crc = 0xffffffff
for data in frames + events:
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xedb88320 if crc & 1 else 0)
crc ^= 0xffffffff
assert crc == report['crc32'] == 900325728
times = [int.from_bytes(row[:4], 'little') for row in frames]
intervals = Counter(b-a for a,b in zip(times,times[1:]))
assert (times[0],times[-1],intervals) == (0,200000,Counter({39:809,40:3382,41:809}))
assert all(len(row) == 26 and row[25] == 0 and row[6] == 0 and row[18:20] == b'\0\0' for row in frames)
decoded_events = [struct.unpack('<IBBH', row) for row in events]
assert decoded_events[0][0] == report['release_us'] and decoded_events[0][1] == 0
go = next(row[0] for row in decoded_events if row[1] == 1)
assert go - report['release_us'] == 5100000
assert decoded_events[-1][0] == report['stop_us']
assert [event for event in decoded_events if event[1] == 9] == [(5007803,9,5,1)]
for name, raw_rows in [('memap_frames.csv',frames),('memap_events.csv',events)]:
    with (FOLDER/name).open(newline='') as stream:
        exported = list(csv.DictReader(stream))
    assert len(exported) == len(raw_rows)
    assert all(int(row['ordinal']) == i and bytes.fromhex(row['raw_hex']) == raw[:25 if name.startswith('memap_frames') else 8]
               for i,(row,raw) in enumerate(zip(exported,raw_rows)))
    for row, raw in zip(exported,raw_rows):
        frame_csv = name.startswith('memap_frames')
        scalar_values = tuple(int(value) for value in list(row.values())[3 if frame_csv else 2:-1])
        assert scalar_values == struct.unpack('<IBBBBihhhbbHBH' if frame_csv else '<IBBH',raw[:25 if frame_csv else 8])
        if frame_csv:
            assert int(row['pack_status']) == raw[25]

final_manifest = load('runtime_final_manifest.json')
assert len(final_manifest) == 155
assert all(final_manifest[name] == digest for name,digest in manifest.items())
assert all(sha((FOLDER/name).read_bytes()) == digest for name,digest in final_manifest.items())

upload = load('upload_run1.json')
assert upload['returncode'] == upload['remote_returncode'] == 0
result = dict(verdict='PASS_SCOPED_SYNTHETIC_RUNTIME_EVIDENCE', hardware_commands_by_reviewer=False,
    reviewed_manifest_files=len(manifest), final_manifest_files=len(final_manifest), scalar_csv_fields_verified=True,
    capture_reads=47, capture_commands=51, capture_bytes=934892,
    capture_seconds=capture['capture_duration_seconds'],
    max_command_seconds=max(c['finished_monotonic']-c['started_monotonic'] for c in commands),
    frozen_diagnostic_sequence=words[0], diagnostic_sha256=sha(diagnostic), pool_sha256=sha(pool),
    identical_pools=True, descriptor_stable=True, diagnostic_stable=True,
    frame_count=count,event_count=event_count,crc32=crc,crc_method='independent reflected bitwise ISO-HDLC',
    first_frame_ms=times[0],last_frame_ms=times[-1],interval_ms_counts=dict(intervals),
    frame_flag_counts=dict(Counter(row[22] for row in frames)),all_pack_statuses_ok=True,
    nonzero_applied_frame_duties=0, synthetic_calibration_rejection_events=[list(x) for x in decoded_events if x[1]==9],
    release_to_stop_mcu_us=report['stop_us']-report['release_us'],
    release_to_terminal_mcu_us=report['last_us']-report['release_us'],
    go_hold_mcu_us=go-report['release_us'], runner_max_step_us=report['max_step_us'],
    retained_timing_ticks=report['timing_ticks_lo'],sampled_stack_headroom_bytes=headroom,
    heap_free_payload_bytes=free_bytes,heap_largest_free_payload_bytes=21604,
    heap_used_payload_bytes=used_bytes,heap_overhead_bytes=overhead,heap_free_chunks=len(free),heap_used_chunks=len(chunks)-len(free),
    linux_upload_end_to_first_diagnostic_seconds=reads[11]['requested_monotonic']-upload['linux_monotonic_after'],
    source_sha256=target['source_sha256'],source_commit='17bb38a',
    input_artifacts_sha256={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [FOLDER/'capture.json', RAW/'storage_layout.json', RAW/'final_symbols.json', RAW/'capture_retry1_manifest.json', RAW/'capture_retry_tool_sync.json']},
    limitations=['Synthetic MCU inputs and MEM-AP extraction; not native UART dump or physical B8.',
                 'MCU duration is not independent clock qualification; Linux bracket is not synchronized timing.',
                 '203us covers instrumented runner only, not full app/HAL/diagnostic WCET.',
                 'Heap and stack values are sampled, not historical minima/high-water or other heaps.',
                 'Full matching pools and terminal samples do not prove atomicity or no intervening cycles.',
                 'No human phase gate follows.'])
(OUT/'runtime_review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
