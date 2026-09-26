"""Archive and verify the two fixed D235 output owners before releasing copies."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

RAW = Path(__file__).resolve().parent
OWNERS = [('host01', RAW / 'host01'), ('host02', Path('/dev/shm/d235-host02'))]
records = []
for name, source in OWNERS:
    source = source.resolve(strict=True)
    assert source == (RAW / 'host01').resolve() or source == Path('/dev/shm/d235-host02')
    archive = RAW / (name + '.zip')
    assert not archive.exists()
    members = []
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as saved:
        for path in sorted(source.rglob('*')):
            assert not path.is_symlink()
            if path.is_file():
                data = path.read_bytes()
                relative = path.relative_to(source).as_posix()
                members.append({'path': relative, 'bytes': len(data),
                                'sha256': hashlib.sha256(data).hexdigest()})
                saved.writestr(relative, data)
    with zipfile.ZipFile(archive) as saved:
        assert saved.namelist() == [item['path'] for item in members]
        for item in members:
            data = saved.read(item['path'])
            assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
    record = {'source': str(source), 'archive': archive.name,
              'archive_bytes': archive.stat().st_size,
              'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'uncompressed_bytes': sum(item['bytes'] for item in members), 'members': members}
    (RAW / (name + '_archive.json')).write_text(json.dumps(record, indent=2) + '\n')
    # Only the exact verified task output copies are released; archive retains every byte.
    shutil.rmtree(source)
    records.append({key: value for key, value in record.items() if key != 'members'})
(RAW / 'storage.json').write_text(json.dumps({'reason': 'Verified compact archives retain all successful and failed output evidence; release reproducible loose copies.',
                                            'owners': records}, indent=2) + '\n')
print(json.dumps(records, indent=2))
