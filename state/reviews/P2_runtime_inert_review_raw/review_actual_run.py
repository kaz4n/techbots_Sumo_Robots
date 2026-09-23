"""Independent offline D104 receipt/byte/ABI/heap audit. No board or network access."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'state/analysis/P2_runtime_inert_raw'
FOLDER = RAW / 'runtime_run1'
OUT = Path(__file__).resolve().parent


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def load(name):
    return json.loads((RAW / name).read_text())


approval = json.loads((OUT / 'final_approval.json').read_text())
capture = load('runtime_run1/capture.json')
manifest = load('capture_run1_manifest.json')
assert set(manifest) == {p.name for p in FOLDER.iterdir() if p.is_file()}
for name, digest in manifest.items():
    assert sha((FOLDER / name).read_bytes()) == digest, name
assert capture['status'] == 'CAPTURED'
assert capture['local_identities_verified'] and capture['flash_identity_verified']

# Bind the pre-run commit and exact checked compile to the previously approved source.
upload = load('upload_run1.json')
revision = upload['software_revision']
assert revision == '1fa2a019b26dc1e7ff74e9491cca94477ce7f681'
source_manifest = load('target_sources_2bd817c4/manifest.json')
aggregate = hashlib.sha256()
for name, digest in sorted(source_manifest['source_files'].items()):
    path = 'bench/runtime_inert/' + name if (
        name == 'runtime_inert.ino' or name.startswith('src/runtime_')) else name
    blob = subprocess.check_output(['git', 'show', revision + ':' + path], cwd=ROOT)
    assert sha(blob) == digest, name
    aggregate.update(name.encode()); aggregate.update(b'\0'); aggregate.update(blob)
assert aggregate.hexdigest() == upload['source'] == approval['source_sha256']
assert len(source_manifest['source_files']) == 91
for name, key in [('tools/runtime_capture.py', 'capture_sha256'),
                  ('tools/board_tool.py', 'board_tool_sha256'),
                  ('state/analysis/P2_runtime_inert_capture_run.py', 'orchestrator_sha256')]:
    blob = subprocess.check_output(['git', 'show', revision + ':' + name], cwd=ROOT)
    # Git stores LF while these approved Windows tool files retain CRLF. The
    # executable bytes must match the approval; the committed text must normalize
    # to exactly the same contents, without otherwise changing a single byte.
    current = (ROOT / name).read_bytes()
    assert sha(current) == approval[key]
    assert blob == current.replace(b'\r\n', b'\n')
pre_run = subprocess.check_output(['git', 'show', revision + ':state/analysis/P2_runtime_inert_run.md'], cwd=ROOT)
assert approval['source_sha256'].encode() in pre_run and b'2629958581' in pre_run
assert json.loads(subprocess.check_output(['git', 'show', revision +
    ':state/reviews/P2_runtime_inert_review_raw/final_approval.json'], cwd=ROOT)) == approval
verified = load('upload_build_receipt/verified.json')
assert verified['source_sha256'] == approval['source_sha256']
assert verified['compiler_returncode'] == 0 and verified['precompile_checks']
assert verified['used_libraries'] == [] and verified['fqbn'] == 'arduino:zephyr:unoq'
assert upload['verified_receipt'] == '49aaf6a759164599850e6407ad22092d'
assert verified['artifacts'].endswith('/bench-default/' + upload['verified_receipt'] + '/artifacts')
compile_argv = load('upload_build_receipt/command.json')
assert compile_argv[compile_argv.index('--output-dir') + 1] == verified['artifacts']
assert 'compiler.cpp.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0' in compile_argv
assert 'compiler.c.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0' in compile_argv
assert upload['elf_sha256'] == approval['elf_sha256']
assert upload['package_sha256'] == approval['zsk_sha256']
upload_command = json.loads((ROOT / upload['upload_receipt']).read_text())
assert upload_command['returncode'] == 0
assert upload_command['argv'] == ['python', 'tools/board_tool.py', 'flash', 'bench/runtime_inert']
upload_text = (ROOT / 'state/analysis/P2_app_build_raw/d104_upload_run1.txt').read_text()
assert upload_text.count('UPLOAD command completed; physical operation still requires observation') == 1
assert upload_text.count('/tmp/remoteocd/runtime_inert.ino.elf-zsk.bin') == 1
assert 'MATCH=0 MOTORS_ALLOWED=0 STARTUP=default' in upload_text
assert approval['source_sha256'] in upload_text and upload['verified_receipt'] in upload_text

# Remote tool sync receipts are evidence only; this script never invokes those commands.
sync = load('capture_tool_sync.json')
synced = load('capture_tool_hashes.json')
for command in sync['commands']:
    assert command['returncode'] == 0 and command['argv'][1:3] == ['-s', approval['serial']]
assert {c['argv'][-1] for c in sync['commands'][1:]} == set(synced)
assert all(c['argv'][3] == 'push' for c in sync['commands'][1:])
for path, digest in synced.items():
    assert sha((ROOT / 'tools' / Path(path).name).read_bytes()) == digest
assert synced[sync['folder'] + '/runtime_capture.py'] == approval['capture_sha256']
capture_command = load('capture_run1_command.json')
assert capture_command['returncode'] == 0 and capture_command['stderr'] == ''
assert capture_command['argv'] == ['python3', sync['folder'] + '/runtime_capture.py',
    '--artifact-dir', approval['artifact_dir'], '--output', capture['capture_directory']]
wait_seconds = (datetime.fromisoformat(capture_command['start_utc']) -
                datetime.fromisoformat(upload_command['end_utc'])).total_seconds()
assert wait_seconds >= 201

# All 46 memory reads match fixed purposes, bounds, hashes, commands and complete streams.
reads, commands = capture['reads'], capture['commands']
assert len(reads) == capture['memory_read_attempts'] == 46 <= 48
assert sum(row['size'] for row in reads) == capture['memory_bytes_requested'] == 913688
assert len(commands) == 50 <= 64 and capture['capture_duration_seconds'] < 600
assert len({row['purpose'] for row in reads}) == len(reads)
payloads = {}
for index, row in enumerate(reads):
    data = (FOLDER / row['file']).read_bytes()
    assert len(data) == row['size'] and sha(data) == row['sha256']
    assert row['address_hex'] == f"0x{row['address']:08x}"
    assert row['size'] <= (16384 if row['region'] == 'ram' else 65536)
    command = commands[index + 4]
    assert command['argv'][:4] == ['/opt/openocd/bin/openocd', '-f',
                                    sync['folder'] + '/p0_mem_read.cfg', '-c']
    assert command['argv'][5:] == ['-c', 'shutdown']
    match = re.fullmatch(r'dump_image \{([^}]+)\} (0x[0-9a-f]+) ([0-9]+)', command['argv'][4])
    assert match and match[1] == capture['capture_directory'] + '/' + row['file']
    assert (int(match[2], 16), int(match[3])) == (row['address'], row['size'])
    assert row['requested_monotonic'] <= command['started_monotonic']
    assert command['finished_monotonic'] <= row['completed_monotonic']
    payloads[row['purpose']] = data
elf_path = approval['artifact_dir'] + '/runtime_inert.ino.elf'
readelf_path = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-readelf'
assert [c['argv'] for c in commands[:4]] == [
    ['/opt/openocd/bin/openocd', '--version'], [readelf_path, '--version'],
    [readelf_path, '-hSW', elf_path], [readelf_path, '-sW', elf_path]]
for command in commands:
    assert command['returncode'] == 0 and not command.get('timeout', False)
    assert command['timeout_seconds'] == 30
    assert 0 <= command['finished_monotonic'] - command['started_monotonic'] < 30
    for stream in ('stdout', 'stderr'):
        blob = (FOLDER / command[stream + '_file']).read_bytes()
        assert command[stream] == blob[:65536].decode('utf-8', errors='replace')
        assert command.get(stream + '_truncated', False) == (len(blob) > 65536)
assert commands[-1]['finished_monotonic'] - commands[0]['started_monotonic'] < 600

# Deployed ZSK bytes equal the audited local package. Loader bytes equal the earlier
# independently reviewed D091 capture, including the installed ELF/package difference.
loader = b''.join(payloads[f'loader-{i:02d}'] for i in range(5))
prior = ROOT / 'state/analysis/P2_recorder_bench_raw/runtime_retry1'
previous_loader = b''.join((prior / f'{i:02d}-loader-{i:02d}.bin').read_bytes() for i in range(5))
assert len(loader) == 263680 and loader == previous_loader
assert sha(loader) == capture['loader_identity']['expected_sha256'] == 'e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2'
assert loader[260287] == 0
sketch = b''.join(payloads[f'sketch-{i:02d}'] for i in range(2))
target = RAW / 'target_2bd817c4'
assert sketch == (target / 'runtime_inert.ino.elf-zsk.bin').read_bytes()
assert len(sketch) == 124996 and sha(sketch) == approval['zsk_sha256']
assert sha((target / 'runtime_inert.ino.elf').read_bytes()) == approval['elf_sha256']
assert capture['file_hashes'][elf_path] == approval['elf_sha256']
assert capture['file_hashes'][elf_path + '-zsk.bin'] == approval['zsk_sha256']

# Literal fixed ABI reconstruction, independent of tools/runtime_capture.py.
assert payloads['llext-list'] == payloads['llext-list-confirm']
node_address, tail = struct.unpack('<II', payloads['llext-list'])
assert node_address == tail == capture['extension']['node_address']
node = payloads['node-1']
assert struct.unpack_from('<I', node)[0] == 0
assert node[4:20].split(b'\0', 1)[0] == b'sketch'
bss = struct.unpack_from('<I', node, 32)[0]
bss_size = struct.unpack_from('<I', node, 92)[0]
assert bss == capture['extension']['bss_address'] and bss_size == 166856
assert capture['extension']['visited_nodes'] == [node_address]
assert payloads['diagnostics-first'] == payloads['diagnostics-last']
diagnostic = payloads['diagnostics-first']
words = struct.unpack('<58I', diagnostic)
assert words[0] == words[57] == 4 and words[43:49] == (0,) * 6
fields = '''schema_version byte_size phase failure boot_us first_s_us first_d_us first_c_us
last_s_us last_d_us last_a_us last_c_us elapsed_us epochs missed_releases maximum_execution_us
maximum_runner_us token_lo token_hi runtime_phase runtime_fault transaction_phase transaction_fault
robot_state contract_faults escape_fault gate_fault receipt_flags input_absent_mask initialization_complete
recorder_phase frame_count event_count setup_enable_calls setup_pwm_calls enable_low_calls pwm_zero_calls
settle_calls clock_calls enabled_requests nonzero_requests invalid_requests'''.split()
assert len(fields) == 42
report = dict(zip(fields, words[1:43]))
assert report == capture['diagnostics']['report']
assert words[1:5] == (1, 192, 2, 0)
for name in ('failure', 'runtime_fault', 'transaction_fault', 'robot_state', 'contract_faults',
             'escape_fault', 'gate_fault', 'initialization_complete', 'recorder_phase',
             'frame_count', 'event_count', 'enabled_requests', 'nonzero_requests',
             'invalid_requests', 'missed_releases'):
    assert report[name] == 0, name
assert report['runtime_phase'] == report['transaction_phase'] == 1
assert report['receipt_flags'] == 15 and report['input_absent_mask'] == 31
epochs = report['epochs']
assert epochs == report['token_lo'] + (report['token_hi'] << 32) == 200001
assert report['setup_enable_calls'] == 1 and report['setup_pwm_calls'] == 4
assert report['enable_low_calls'] == report['settle_calls'] == epochs + 1
assert report['pwm_zero_calls'] == 4 * (epochs + 1)
elapsed = [(report[k] - report['boot_us']) & 0xffffffff for k in
           ('first_s_us', 'first_d_us', 'first_c_us', 'last_s_us', 'last_d_us', 'last_a_us', 'last_c_us')]
assert elapsed == sorted(elapsed) and all(t < 0x80000000 for t in elapsed)
assert elapsed[2] < 1000000 and 200000000 <= elapsed[-1] <= report['elapsed_us'] < 201000000
assert report['elapsed_us'] == 200000311
assert max(elapsed[2] - elapsed[0], elapsed[-1] - elapsed[3]) <= report['maximum_execution_us'] == 269
assert report['maximum_runner_us'] == 285 >= report['maximum_execution_us']
stack_fields = 'valid region_start region_size region_delta minimum_sp samples sampled_headroom_bytes fault'.split()
stack = dict(zip(stack_fields, words[49:57]))
assert stack == capture['diagnostics']['stack']
assert stack['valid'] == 1 and stack['fault'] == 0
assert stack['samples'] == report['clock_calls'] == 35374939 < 0xffffffff
assert stack['region_size'] == 32768 and stack['region_delta'] == 64
assert 0x20000000 <= stack['region_start'] < stack['region_start'] + stack['region_size'] <= 0x200c0000
assert stack['region_start'] % 4 == stack['minimum_sp'] % 4 == 0
assert stack['region_start'] <= stack['minimum_sp'] <= stack['region_start'] + stack['region_size'] - stack['region_delta']
assert stack['minimum_sp'] - stack['region_start'] == stack['sampled_headroom_bytes'] == 30952
assert capture['diagnostics']['acceptance'] == {'passed': True, 'failures': []}
assert sha(diagnostic) == capture['diagnostic_sha256']
assert payloads['heap-descriptor-first'] == payloads['heap-descriptor-last']
descriptor = struct.unpack('<6I', payloads['heap-descriptor-first'])
POOL = 0x20013890
assert descriptor[:3] == (POOL, POOL, 262144)
assert list(descriptor) == capture['heap_descriptor']['words']
expected_reads = []
for region, base, length in [('loader', 0x08000000, 263680), ('sketch', 0x08100000, 124996)]:
    for i, offset in enumerate(range(0, length, 65536)):
        expected_reads.append((f'{region}-{i:02d}', base + offset, min(65536, length-offset), region))
expected_reads += [('llext-list', 0x200017bc, 8, 'ram'), ('node-1', node_address, 196, 'ram'),
                   ('llext-list-confirm', 0x200017bc, 8, 'ram'),
                   ('diagnostics-first', bss + 166624, 232, 'ram'),
                   ('heap-descriptor-first', 0x2000112c, 24, 'ram')]
for n in (1, 2):
    expected_reads += [(f'pool-{n}-{i:02d}', POOL+i*16384, 16384, 'ram') for i in range(16)]
expected_reads += [('heap-descriptor-last', 0x2000112c, 24, 'ram'),
                   ('diagnostics-last', bss+166624, 232, 'ram')]
assert expected_reads == [(r['purpose'], r['address'], r['size'], r['region']) for r in reads]
assert bss + 166624 == capture['symbol_addresses']['runtimeDiagnostics']

# Independently walk the allocator's small headers, left links and free bucket rings.
pools = [(FOLDER / name).read_bytes() for name in ('pool-first.bin', 'pool-second.bin')]
assert pools[0] == pools[1] and len(pools[0]) == 262144
for n in (1, 2):
    assert b''.join(payloads[f'pool-{n}-{i:02d}'] for i in range(16)) == pools[n-1]
pool = pools[0]
assert pool[bss-POOL+166624:bss-POOL+166856] == diagnostic
assert pool[node_address-POOL:node_address-POOL+196] == node
assert struct.unpack_from('<HH', pool, 0) == (0, 21)
end, mask = struct.unpack_from('<II', pool, 8)
assert end == 32767 and mask < (1 << 15)
heads = struct.unpack_from('<15I', pool, 16)
chunks, free = [], {}
position, previous = 10, 10
for _ in range(32768):
    left, tagged = struct.unpack_from('<HH', pool, position * 8)
    size, used = tagged >> 1, bool(tagged & 1)
    assert left == previous
    if position == end:
        assert size == 0 and used
        break
    assert size > 0 and position + size <= end
    assert used or not chunks or chunks[-1]['used']
    chunks.append(dict(index=position, size_units=size, used=used, payload_bytes=8*size-4))
    if not used:
        free[position] = (size, *struct.unpack_from('<HH', pool, position*8+4))
    previous, position = size, position + size
else:
    raise AssertionError('No bounded end marker')
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
        raise AssertionError('No bounded free-list cycle')
assert visited == set(free)
free_bytes = sum(c['payload_bytes'] for c in chunks if not c['used'])
used_bytes = sum(c['payload_bytes'] for c in chunks if c['used'])
largest = max(c['payload_bytes'] for c in chunks if not c['used'])
overhead = 80 + 8 + 4*len(chunks)
assert free_bytes + used_bytes + overhead == 262144
assert chunks == capture['heap']['chunks']
assert free_bytes == capture['heap']['free_payload_bytes'] == 28668
assert used_bytes == capture['heap']['used_payload_bytes'] == 233348
assert largest == capture['heap']['largest_free_payload_bytes'] == 25172
assert overhead == capture['heap']['overhead_bytes'] == 128
assert len(free) == 3 and len(chunks)-len(free) == 7
assert sha(pool) == capture['heap']['snapshot_sha256'] == capture['heap']['second_snapshot_sha256']
canonical = bytearray(b'SUMOX26_LLEXT_HEAP_METADATA_V1\0')
canonical.extend(struct.pack('<II', POOL, len(pool)))
spans = [(0, 4), (8, 68)] + [(c['index']*8, 4 if c['used'] else 8) for c in chunks] + [(32767*8, 4)]
for offset, length in spans:
    canonical.extend(struct.pack('<II', offset, length))
    canonical.extend(pool[offset:offset+length])
assert sha(canonical) == capture['heap']['metadata_sha256']

evidence_paths = ['capture_run1_manifest.json', 'runtime_run1/capture.json', 'upload_run1.json',
                  'upload_build_receipt/verified.json', 'capture_run1_command.json',
                  'capture_tool_sync.json', 'capture_tool_hashes.json',
                  'target_sources_2bd817c4/manifest.json']
result = dict(verdict='PASS_SCOPED_ACTUAL_INERT_RUNTIME_RUN', findings=[],
    software_revision=revision, source_sha256=approval['source_sha256'],
    elf_sha256=approval['elf_sha256'], zsk_sha256=approval['zsk_sha256'],
    capture_sha256=manifest['capture.json'], manifest_files_verified=len(manifest),
    source_files_verified=len(source_manifest['source_files']),
    uploaded_checked_receipt=upload['verified_receipt'], pre_capture_wait_seconds=wait_seconds,
    loader_sha256=sha(loader), loader_reference='Byte-for-byte prior independently reviewed D091 capture plus current pinned-ELF capture receipt',
    commands=len(commands), memory_reads=len(reads), bytes_requested=sum(r['size'] for r in reads),
    capture_duration_seconds=capture['capture_duration_seconds'],
    diagnostic_sha256=sha(diagnostic), diagnostic_report=report, sampled_stack=stack,
    heap=dict(free_payload_bytes=free_bytes, largest_free_payload_bytes=largest,
              used_payload_bytes=used_bytes, overhead_bytes=overhead,
              free_chunks=len(free), used_chunks=len(chunks)-len(free),
              snapshots_byte_identical=True, snapshot_sha256=sha(pool)),
    evidence_sha256={p:sha((RAW/p).read_bytes()) for p in evidence_paths},
    limitations=['One bare-board absent-source BOOT run; no peripheral or motor qualification.',
                 'MCU-reported timing, not calibrated clock accuracy or complete application WCET.',
                 'Stack sample minimum, not historical stack watermark; heap samples are not atomic or historical minimum.',
                 'No synthesized START/STOP, recording lifecycle, sensor freshness or human phase gate.'])
(OUT / 'actual_run_review.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k:v for k,v in result.items() if k not in
    ('evidence_sha256', 'diagnostic_report', 'sampled_stack', 'limitations')}, indent=2))
