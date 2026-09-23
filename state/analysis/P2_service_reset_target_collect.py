# Collect the exact D103 completed source/ELF evidence from board Linux only.
# Freeze the newly selected 87-file source without changing earlier count checks.
# Reuse D101 collection and D098 offline inspection after explicit source validation.
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE = '1fbd72385c9a729be869bebaaabcc28b5614aa8ff23616843d7b2809a187301f'
RAW = REPO / 'state/analysis/P2_service_reset_raw'
spec = importlib.util.spec_from_file_location('d101_collector',
    REPO / 'state/analysis/P2_app_dump_target_collect.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


def freeze_source():
    folder = RAW / ('target_sources_' + SOURCE[:8])
    manifest = folder / 'manifest.json'
    if manifest.exists():
        return collector.policy.decode(manifest.read_text())
    files = collector.prior.current_sources()
    if len(files) != 87:
        raise ValueError('D103 requires exactly the selected 87 source files')
    digest = hashlib.sha256()
    payloads = {}
    for name in sorted(files):
        path = REPO / ('src/app/app.ino' if name == 'app.ino' else name)
        payload = path.read_bytes()
        if collector.prior.sha256(payload) != files[name]:
            raise ValueError('Source changed while freezing')
        digest.update(name.encode()+b'\0'); digest.update(payload)
        payloads[name] = payload
    if digest.hexdigest() != SOURCE:
        raise ValueError('Current source differs from the exact authorized D103 build')
    folder.mkdir(parents=True, exist_ok=False)
    for name, payload in payloads.items():
        target = folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    data = dict(source_sha256=SOURCE, source_files=files,
                frozen_utc=datetime.now(timezone.utc).isoformat())
    collector.prior.write_json(manifest, data)
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('receipt', type=Path)
    parser.add_argument('mode', choices=('bench-default', 'match-immediate'))
    args = parser.parse_args()
    collector.SOURCE = SOURCE
    collector.RAW = RAW
    collector.freeze_source = freeze_source
    collector.collect(args.receipt.resolve(), args.mode)
