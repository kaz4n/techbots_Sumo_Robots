"""Independently reparse real Runtime-produced synthetic D103 postmatch streams."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P2_service_reset_raw/author/run_1790187758638920013'
sys.path.insert(0, str(ROOT / 'tools'))
spec = importlib.util.spec_from_file_location('d103_review_receiver', ROOT / 'tools/dump_match.py')
receiver = importlib.util.module_from_spec(spec); sys.modules[spec.name] = receiver
spec.loader.exec_module(receiver)
results = {}
for motor in (0, 1):
    for profile in ('normal', 'san'):
        label = 'configured-' + str(motor) + '-' + profile
        wire = (RAW / ('wire-' + label + '.txt')).read_bytes()
        receipt = json.loads((RAW / ('roundtrip-' + label + '.json')).read_text())
        assert hashlib.sha256(wire).hexdigest() == receipt['wire_sha256']
        parser = receiver.Parser()
        for byte in wire: parser.feed(bytes([byte]))
        capture = parser.finish()
        assert capture.origin == 1 and capture.session == 8651 and capture.epoch == 86
        assert capture.frame_count == 155 and capture.event_count == (7 if motor == 0 else 8)
        assert capture.crc32 == receipt['crc']
        csv_hashes = {}
        for name in ('frames', 'events', 'summary'):
            data = getattr(capture, name)
            assert data == (RAW / ('expected-' + label) / ('expected_' + name + '.csv')).read_bytes()
            csv_hashes[name] = hashlib.sha256(data).hexdigest()
        results[label] = {'wire_sha256': receipt['wire_sha256'], 'bytes': len(wire),
            'crc': capture.crc32, 'frames': capture.frame_count, 'events': capture.event_count,
            'exact_pre_reset_csv': csv_hashes}
    assert results['configured-' + str(motor) + '-normal'] == results['configured-' + str(motor) + '-san']
(OUT / 'stream_verification.json').write_text(json.dumps({
    'scope': 'Read-only strict independent receiver; genuine Runtime path with synthetic host callbacks',
    'streams': results}, indent=2) + '\n')
print(json.dumps(results, indent=2))
