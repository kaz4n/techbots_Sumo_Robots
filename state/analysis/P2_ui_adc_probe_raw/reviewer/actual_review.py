"""Offline review of the original D114 run01 receipts and captured bytes.
No production module import, board command, or original-file modification.
Assertions bind the prior source review to actual deployment and passive reads.
"""
import hashlib
import json
from pathlib import Path
import struct
from datetime import datetime

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / 'state/analysis/P2_ui_adc_probe_raw'
ACTUAL = RAW / 'actual_run01'
checks = []


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes())


def check(condition, label):
    assert condition, label
    checks.append(label)


def utc(value):
    return datetime.fromisoformat(value)


approval_path = RAW / 'reviewer/run01_approval.json'
approval = read_json(approval_path)
record = read_json(ROOT / 'state/analysis/P2_ui_adc_probe_run01.json')
attempt = read_json(RAW / 'run01_upload_attempt.json')
outcome = read_json(RAW / 'run01_upload_outcome.json')
verified = read_json(RAW / 'run01_build_receipt/verified.json')
check(record['review_sha256'] == attempt['approval_sha256'] == digest(approval_path.read_bytes()), 'exact one-run approval hash')
check(len(approval['file_sha256']) == 11, 'eleven approved file pins')
for name, expected in approval['file_sha256'].items():
    check(digest((ROOT / name).read_bytes()) == expected, 'unchanged approved file: ' + name)
for name in ('run_id', 'source_sha256', 'elf_sha256', 'binary_sha256'):
    check(record[name] == attempt[name] == approval[name], 'record/attempt/approval binding: ' + name)
check(record['transport'] == 'adb' and record['target'] == attempt['target'] == '2629958581', 'exact ADB target')
check(record['software_commit'] == '9bb947b45c3270364fd827734d91d21fe50ad742', 'identified software commit')
check(outcome['run_id'] == record['run_id'] and outcome['returncode'] == 0 and
      not outcome['timed_out'] and outcome['error'] is None and outcome['stderr'] == '', 'upload returned success without timeout or error')
check(verified['source_sha256'] == record['source_sha256'] and verified['policy'] == 'native-app-v1' and
      verified['fqbn'] == 'arduino:zephyr:unoq' and verified['compiler_returncode'] == 0 and
      verified['used_libraries'] == [] and verified['precompile_checks'] is True, 'fresh checked default compile receipt')
artifact_dir = verified['artifacts']
build_dir = verified['build_path']
check(artifact_dir.endswith('/bench-default/68f3d6d38d9541c5afec8e54e5bcbec0/artifacts') and
      build_dir == artifact_dir.rsplit('/', 1)[0] + '/build', 'fresh unique sibling build/artifact directories')
for name, expected in [('ui_adc_probe.ino.elf', record['elf_sha256']), ('ui_adc_probe.ino.elf-zsk.bin', record['binary_sha256'])]:
    prefix = build_dir if name.endswith('.elf') else artifact_dir
    check(verified['file_sha256'][prefix + '/' + name] == expected, 'fresh reviewed artifact hash: ' + name)
sketch = '/home/arduino/sumox26_codex_build/' + record['source_sha256'] + '/ui_adc_probe'
check(attempt['argv'] == ['arduino-cli', 'upload', '--fqbn', 'arduino:zephyr:unoq', '--input-dir', artifact_dir, sketch], 'exact identified upload argv')
compile_result = read_json(RAW / 'run01_build_receipt/compile.stdout.json')
check(compile_result['success'] is True and compile_result['compiler_err'] == '', 'compiler success, no compiler diagnostic error')
props = dict(item.split('=', 1) for item in compile_result['builder_result']['build_properties'])
for key, expected in [('compiler.cpp.extra_flags', '-DMATCH=0 -DMOTORS_ALLOWED=0'), ('compiler.c.extra_flags', '-DMATCH=0 -DMOTORS_ALLOWED=0'),
                      ('build.library_discovery_phase_flag', '-DARDUINO_LIBRARY_DISCOVERY_PHASE=0'), ('build.boot_mode', 'wait')]:
    check(props[key] == expected, 'actual compiler property: ' + key)

capture = read_json(ACTUAL / 'capture.json')
capture_command = read_json(RAW / 'run01_capture_command.json')
check(capture_command['returncode'] == 0 and capture_command['stderr'] == '' and
      json.loads(capture_command['stdout']) == capture, 'capture command success and exact returned report')
check(utc(outcome['finished_utc']) < utc(capture_command['started_utc']), 'capture began after upload completed, host clock domain')
check(capture['source_sha256'] == record['source_sha256'] and capture['collection_integrity'] == 'VERIFIED', 'actual report source and integrity')
check(capture['physical_acceptance'] is False and capture['diagnostic']['physical_acceptance'] is False, 'physical acceptance remains false')
remote = read_json(RAW / 'run01_capture_remote_manifest.json')
local = read_json(RAW / 'run01_capture_local_manifest.json')
actual_manifest = {p.name: {'bytes': len(p.read_bytes()), 'sha256': digest(p.read_bytes())} for p in ACTUAL.iterdir() if p.is_file()}
check(remote['returncode'] == 0 and json.loads(remote['stdout']) == local == actual_manifest, 'all remote/local/original manifest entries equal')
check(len(actual_manifest) == 63 and sum(item['bytes'] for item in actual_manifest.values()) == 936771, '63 files, 936771 transferred bytes')
pull = read_json(RAW / 'run01_capture_pull.json')
check(pull['returncode'] == 0 and pull['stderr'] == '' and pull['argv'] == read_json(RAW / 'run01_capture_pull_attempt.json')['argv'] and
      pull['argv'][1:4] == ['-s', record['target'], 'pull'], 'one recorded ADB pull succeeded for exact target')
tools = read_json(RAW / 'run01_capture_tool_hashes.json')
for path, sha in tools.items():
    check(sha == approval['file_sha256']['tools/' + Path(path).name], 'staged tool hash: ' + Path(path).name)
check(len(tools) == 3, 'three staged tools')

commands, reads = capture['commands'], capture['reads']
check(len(commands) == 22 and len(reads) == capture['memory_read_attempts'] == 18, 'exact 22 commands and 18 memory reads')
check(sum(r['size'] for r in reads) == capture['memory_bytes_requested'] == 587232, 'exact 587232 memory bytes')
check(0 < capture['capture_duration_seconds'] < 600 and capture['maximum_read_budget'] ==
      {'reads': 22, 'bytes': 588016, 'commands': 26, 'extension_nodes': 3}, 'actual duration and complete precomputed maximum fit')
openocd = '/opt/openocd/bin/openocd'
readelf = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-readelf'
tool_dir = '/home/arduino/sumox26-capture-tools/ui_adc_d114_run01'
input_dir = '/home/arduino/sumox26-capture-input/ui_adc_probe_' + record['source_sha256']
expected_meta = [[openocd, '--version'], [readelf, '--version'], [readelf, '-hSW', input_dir + '/ui_adc_probe.ino.elf'], [readelf, '-sW', input_dir + '/ui_adc_probe.ino.elf']]
check([c['argv'] for c in commands[:4]] == expected_meta, 'exact four metadata queries')
for i, command in enumerate(commands):
    check(command['returncode'] == 0 and 0 < command['timeout_seconds'] <= 30 and
          0 <= command['finished_monotonic'] - command['started_monotonic'] < command['timeout_seconds'], 'command status and monotonic duration ' + str(i))
    for stream in ('stdout', 'stderr'):
        check(not command[stream + '_truncated'] and (ACTUAL / command[stream + '_file']).read_bytes().decode() == command[stream], 'complete command stream ' + str(i) + ' ' + stream)
    if i:
        check(commands[i - 1]['finished_monotonic'] <= command['started_monotonic'], 'serialized command chronology ' + str(i))
for i, read in enumerate(reads):
    data = (ACTUAL / read['file']).read_bytes()
    check(len(data) == read['bytes_present'] == read['size'] and digest(data) == read['sha256'], 'memory file length/hash ' + str(i))
    expected = [openocd, '-f', tool_dir + '/p0_mem_read.cfg', '-c',
                'dump_image {' + capture['capture_directory'] + '/' + read['file'] + '} ' + f"0x{read['address']:08x} {read['size']}", '-c', 'shutdown']
    check(commands[i + 4]['argv'] == expected, 'read-only exact MEM-AP command ' + str(i))
    check(read['requested_monotonic'] <= commands[i + 4]['started_monotonic'] <= commands[i + 4]['finished_monotonic'] <= read['completed_monotonic'], 'read command bracket ' + str(i))

def blob(purpose):
    found = [r for r in reads if r['purpose'] == purpose]
    assert len(found) == 1
    return (ACTUAL / found[0]['file']).read_bytes()


loader_elf = (RAW / 'root_capture_inputs/zephyr-arduino_uno_q_stm32u585xx.elf').read_bytes()
loader_binary = (RAW / 'root_capture_inputs/zephyr-arduino_uno_q_stm32u585xx.bin').read_bytes()
check(digest(loader_elf) == '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd', 'pinned loader ELF input')
check(digest(loader_binary) == '6b2ffd3a24aa77ca40bac1a8c61460c5cdd3292a2ff38cb377b938a6ac939713', 'pinned packaged loader input')
phoff = struct.unpack_from('<I', loader_elf, 28)[0]
phsize, phcount = struct.unpack_from('<HH', loader_elf, 42)
segments = []
for i in range(phcount):
    kind, offset, _, address, size, memory_size, _, _ = struct.unpack_from('<8I', loader_elf, phoff + i * phsize)
    if kind == 1 and size:
        assert size <= memory_size and offset + size <= len(loader_elf)
        segments.append((address, loader_elf[offset:offset + size]))
image = b''
for address, data in sorted(segments):
    assert address == 0x08000000 + len(image)
    image += data
check(len(image) == 263680 and digest(image) == capture['loader_identity']['expected_sha256'], 'independent ELF PT_LOAD reconstruction')
differences = [{'offset': i, 'elf': a, 'binary': b} for i, (a, b) in enumerate(zip(image, loader_binary)) if a != b]
check(differences == [{'offset': 260287, 'elf': 0, 'binary': 255}] == capture['loader_identity']['package_binary_first_differences'], 'packaged BIN difference honestly retained')
target = RAW / 'target_396bcc45_bench-default_checked'
elf = (target / 'ui_adc_probe.ino.elf').read_bytes()
zsk = (target / 'ui_adc_probe.ino.elf-zsk.bin').read_bytes()
check(digest(elf) == record['elf_sha256'] and digest(zsk) == record['binary_sha256'], 'original reviewed ELF/ZSK cached bytes')
for phase in ('before', 'after'):
    actual_loader = b''.join(blob(f'loader-{phase}-{i:02d}') for i in range(5))
    check(actual_loader == image, 'full deployed loader ' + phase)
    check(blob('sketch-' + phase + '-00') == zsk, 'full deployed sketch ' + phase)
check(blob('llext-list-before') == blob('llext-list-after'), 'list bracket byte identity')
check(blob('node-before-1') == blob('node-after-1'), 'extension node bracket byte identity')
head, tail = struct.unpack('<II', blob('llext-list-before'))
node = blob('node-before-1')
next_node = struct.unpack_from('<I', node)[0]
name = node[4:20].split(b'\x00', 1)[0]
bss = struct.unpack_from('<I', node, 32)[0]
bss_size = struct.unpack_from('<I', node, 92)[0]
check(head == tail == 0x200138e4 and next_node == 0 and name == b'sketch', 'single terminated sketch extension')
check(bss == 0x2001530c and bss_size == 9893 and bss % 4 == 0 and 0x20000000 <= bss < bss + bss_size <= 0x200c0000, 'actual whole BSS range')
check(capture['extension'] == {'node_address': head, 'bss_address': bss, 'bss_size': bss_size, 'visited_nodes': [head]}, 'raw node agrees with mapping report')
# Raw ELF32 symtab values are section-relative for this ET_REL image.
shoff = struct.unpack_from('<I', elf, 32)[0]
shsize, shcount = struct.unpack_from('<HH', elf, 46)
sections = [struct.unpack_from('<10I', elf, shoff + i * shsize) for i in range(shcount)]
matches = []
for section in sections:
    if section[1] != 2:
        continue
    strings = sections[section[6]]
    table = elf[strings[4]:strings[4] + strings[5]]
    for offset in range(section[4], section[4] + section[5], section[9]):
        n, value, size, info, other, index = struct.unpack_from('<IIIBBH', elf, offset)
        if table[n:].split(b'\0', 1)[0] == b'_ZN12_GLOBAL__N_16runnerE':
            matches.append((value, size, info, other, index))
check(matches == [(0, 9892, 1, 0, 8)] and sections[8][3:6] == (5776, 6616, 9893), 'raw ELF Runner st_value zero, correct BSS, no VMA subtraction')
for r in reads:
    if r['purpose'].startswith('runner-'):
        check(r['address'] == bss and r['size'] == 9892, 'actual relocated Runner address ' + r['purpose'])
first, second = blob('runner-first'), blob('runner-second')
check(first == second and len(first) == 9892 and digest(first) == '3d33a0ed00c6cdfb467aefa8c2f51ee8349482fba6c15fcca201ec2f189298a6', 'two original whole Runner snapshots identical')
diagnostic = capture['diagnostic']
check(diagnostic['frozen'] and diagnostic['acquisition'] == 'COMPLETE_128' and
      all(s['valid'] and not s['errors'] for s in diagnostic['snapshots']), 'bounded decoder result is frozen complete diagnostic')
analysis = read_json(RAW / 'actual_analysis/independent_decode.json')
check(analysis['analysis_source_sha256'] == digest((RAW / 'actual_analysis/decode_original.py').read_bytes()) and
      analysis['independent_schema_decode'] and analysis['frozen_terminal'] and analysis['byte_identical'], 'separate literal decoder provenance and terminal result')
for index, independently_decoded in enumerate(analysis['snapshots']):
    check(independently_decoded['sha256'] == digest(first) and independently_decoded['bytes'] == len(first) and
          independently_decoded['valid'] and independently_decoded['errors'] == [], 'independent original-byte decode ' + str(index))
    check(independently_decoded['summary']['report'] == diagnostic['snapshots'][index]['report'] and
          independently_decoded['captures'] == diagnostic['snapshots'][index]['captures'], 'every independent public field agrees ' + str(index))
statistics = analysis['snapshots'][0]['summary']['committed_statistics']
summary = {
    'verdict': 'PASS_ACTUAL_D114_BOUNDED_INERT_ADC_DIAGNOSTIC',
    'independence': 'Reused separate same-model reviewer; offline original-byte/receipt validation; no board operation. Literal Runner analysis separately authored.',
    'checks_passed': len(checks), 'checks': checks,
    'run_id': record['run_id'], 'source_sha256': record['source_sha256'], 'elf_sha256': record['elf_sha256'], 'binary_sha256': record['binary_sha256'],
    'capture_sha256': digest((ACTUAL / 'capture.json').read_bytes()), 'runner_sha256': digest(first),
    'files': len(actual_manifest), 'transfer_bytes': sum(v['bytes'] for v in actual_manifest.values()),
    'reads': len(reads), 'read_bytes': sum(r['size'] for r in reads), 'commands': len(commands),
    'capture_seconds': capture['capture_duration_seconds'], 'mapping': capture['extension'],
    'actual_sample_statistics': statistics,
    'evidence_sha256': {str(p.relative_to(ROOT)).replace('\\', '/'): digest(p.read_bytes()) for p in
        [approval_path, ROOT / 'state/analysis/P2_ui_adc_probe_run01.json', RAW / 'run01_upload_attempt.json', RAW / 'run01_upload_outcome.json',
         RAW / 'run01_build_receipt/verified.json', RAW / 'run01_capture_command.json', RAW / 'run01_capture_local_manifest.json',
         RAW / 'run01_capture_remote_manifest.json', RAW / 'actual_analysis/independent_decode.json', RAW / 'actual_analysis/decode_original.py']},
    'limitations': ['Floating bare A1; no physical button, voltage, wiring, calibrated clock or noise acceptance.',
                    'Two sampled terminal snapshots and bracketing identities, not an atomic snapshot or future lease.',
                    'MCU micros durations are diagnostic, not full-app WCET or a physical timing qualification.',
                    'ADC remains enabled/idle with shutdown NOT_ATTEMPTED; no fabricated stop.',
                    'No motor permission or human phase gate is established. Upload halt/reset is separate from passive capture.'],
    'findings': [],
}
output = RAW / 'reviewer/actual_review.json'
output.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: summary[k] for k in ('verdict', 'checks_passed', 'files', 'reads', 'read_bytes', 'commands', 'runner_sha256')}, indent=2))
