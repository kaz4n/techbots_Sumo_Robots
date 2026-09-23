# Rehashes the exact accepted D112 source and target evidence independently.
# Runs locally against retained bytes; performs no board or MCU operation.
# A mismatch fails before the final verification receipt is written.
import hashlib
import json
from pathlib import Path

RAW = Path(__file__).resolve().parent
SOURCE = 'bf67d46da629cd4a59e14be62721b766070feac1c95d28b7a797f47d3a8172f6'
frozen = RAW / 'target_sources_bf67d46d'
manifest = json.loads((frozen / 'manifest.json').read_text())
digest = hashlib.sha256()
for item in sorted(frozen / name for name in manifest['source_files']):
    name = item.relative_to(frozen).as_posix()
    blob = item.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == manifest['source_files'][name]
    digest.update(name.encode() + b'\0')
    digest.update(blob)
assert digest.hexdigest() == SOURCE and len(manifest['source_files']) == 96
result = dict(source_sha256=SOURCE, files=96, profiles={})
for mode in ('bench-default', 'bench-immediate'):
    folder = RAW / ('target_bf67d46d_' + mode + '_checked')
    audit = json.loads((folder / 'audit.json').read_text())
    receipt = json.loads((folder / 'receipt.json').read_text())
    checked = json.loads((folder / 'build_receipt/verified.json').read_text())
    assert receipt['returncode'] == 0 and not (folder / 'stderr.txt').read_text()
    assert audit['source_sha256'] == checked['source_sha256'] == SOURCE
    assert audit['source_files'] == manifest['source_files']
    assert checked['compiler_returncode'] == 0 and checked['precompile_checks']
    commands = [audit['abi']]
    artifacts = {}
    for record in audit['records']:
        blob = (folder / record['name']).read_bytes()
        assert len(blob) == record['bytes']
        actual = hashlib.sha256(blob).hexdigest()
        assert actual == record['sha256'] == checked['file_sha256'][record['path']]
        artifacts[record['name']] = actual
        commands.extend(record.get('commands', []))
    assert len(artifacts) == 4 and len(commands) == 13
    assert all(c['returncode'] == 0 and not c['stderr'] for c in commands)
    result['profiles'][mode] = dict(artifact_sha256=artifacts, offline_commands=13)
assert result['profiles']['bench-default']['artifact_sha256']['ui.ino.elf'] == result['profiles']['bench-immediate']['artifact_sha256']['ui.ino.elf']
(RAW / 'root_target_verification.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
