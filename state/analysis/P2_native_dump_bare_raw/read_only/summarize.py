"""Summarizes preserved read-only receipts without another board operation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def receipt(name):
    return json.loads((HERE / (name + '.json')).read_text(encoding='utf-8'))
def payload(name):
    return json.loads(receipt(name)['stdout'])

paths = sorted(HERE.glob('[0-9][0-9]_*.json'))
index = []
for path in paths:
    item = json.loads(path.read_text(encoding='utf-8'))
    for key in ('stdout', 'stderr'):
        assert hashlib.sha256((item.get(key) or '').encode()).hexdigest() == item[key + '_sha256']
    index.append({key: item.get(key) for key in ('target', 'start_utc', 'end_utc', 'returncode')}
        | {'file': path.name, 'sha256': digest(path)})
known = payload('05_known_files')['files']
old = json.loads((ROOT / 'state/analysis/P2_dump_raw/native/sources_receipt.json').read_text())
old_map = {item['path']: item.get('sha256') for item in old['files']}
for item in known:
    item.pop('text', None)
    item.pop('selected_lines', None)
    if item['path'] in old_map:
        item['matches_cached_D090'] = item.get('sha256') == old_map[item['path']]
source_paths = [
    'state/analysis/P2_dump_raw/native/router/main.go',
    'state/analysis/P2_dump_raw/native/router/internal/monitorapi/monitor-api.go',
    'state/analysis/P2_dump_raw/native/router/msgpackrpc/connection.go',
    'state/analysis/P2_dump_raw/native/router/cmd/arduino-router-cli/main.go',
    'state/analysis/P2_dump_raw/native/router_sources_receipt.json',
    'state/analysis/P2_recorder_bench_raw/native/serial_unix.go',
    'state/analysis/P2_recorder_bench_raw/native/serial_linux.go',
    'state/analysis/P2_recorder_bench_raw/native/router_go.mod',
    'state/analysis/P2_recorder_bench_raw/native/router_dependency_receipt.json',
    'state/analysis/P2_recorder_bench_raw/native/serial_dependency_receipt.json']
summary = {
    'schema': 1, 'generated_utc': datetime.now(timezone.utc).isoformat(), 'target': '2629958581',
    'scope': 'read-only Linux regular source/service files and filtered public process/socket metadata',
    'receipts': index, 'successful_commands': sum(item['returncode'] == 0 for item in index),
    'failed_commands': [item for item in index if item['returncode'] != 0],
    'known_files': known, 'proc_visibility': payload('06_socket_ownership')['coverage'],
    'socket_diag': receipt('10_monitor_socket_diag')['stdout'],
    'public_process_identity': payload('11_public_process_identity'),
    'router_socket': payload('12_router_socket_metadata'),
    'cached_source_inputs': [{'path': name, 'sha256': digest(ROOT / name)} for name in source_paths],
    'limits': ['No UART was opened/read/written.', 'No Monitor or router RPC socket was connected.',
        'No service or process was started/stopped/restarted/signalled.',
        'Root process fd lists remain unavailable; sudo -n attempt failed and is retained.',
        'Established Monitor client is identified by kernel socket cgroup metadata.',
        'No MCU, GPIO, upload, reset or config mutation.',
        'A source audit and idle socket queues do not prove clean parser/UART framing.']}
(HERE / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
manifest = [{'path': path.relative_to(HERE).as_posix(), 'bytes': path.stat().st_size, 'sha256': digest(path)}
    for path in sorted(HERE.rglob('*')) if path.is_file() and path.name != 'manifest.json']
(HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'receipt_count': len(index), 'success': summary['successful_commands'],
    'failure': len(summary['failed_commands']), 'known_files': len(known),
    'cached_core_matches': sum(item.get('matches_cached_D090') is True for item in known),
    'manifest_files': len(manifest)}))
