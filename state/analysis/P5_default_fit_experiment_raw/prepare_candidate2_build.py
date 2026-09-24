"""Materialize exactly the approved candidate2 and prepare its one isolated compile."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

out = Path(__file__).resolve().parent
root = out.parents[2]
old_project = root / 'build/p5_default_fit_candidate'
project = root / 'build/p5_default_fit_candidate2'
project.mkdir(exist_ok=False)
candidate = json.loads((out / 'candidate2_manifest.json').read_text())
assert hashlib.sha256((out / 'candidate2.patch').read_bytes()).hexdigest() == candidate['patch_sha256']
manifest = json.loads((out / 'materialized_manifest_attempt02.json').read_text())
manifest.update(candidate_root=str(project), created_utc=datetime.now(timezone.utc).isoformat(),
                candidate_diff_sha256=candidate['patch_sha256'])
for name, row in manifest['files'].items():
    source = old_project / name
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['sha256'], name
    target = project / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
for name, row in candidate['files'].items():
    source = out / 'candidate2' / name
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['candidate_sha256'], name
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == row['base_sha256'], name
    shutil.copy2(source, project / name)
    manifest['files'][name] = {'sha256': row['candidate_sha256'], 'bytes': row['bytes']}
(out / 'candidate2_materialized_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
wrapper = (out / 'invoke_checked_attempt02.py').read_text()
for old, new in (
    ('p5_default_fit_candidate', 'p5_default_fit_candidate2'),
    ('remote_snapshot_ready_attempt02.json', 'candidate2_remote_snapshot_ready.json'),
    ('actual_remote_commands_attempt02.jsonl', 'candidate2_actual_remote_commands.jsonl'),
):
    wrapper = wrapper.replace(old, new)
(out / 'invoke_candidate2.py').write_text(wrapper)
runner = (out / 'compile_target_attempt02.py').read_text()
for old, new in (
    ('p5_default_fit_candidate', 'p5_default_fit_candidate2'),
    ('materialized_manifest_attempt02.json', 'candidate2_materialized_manifest.json'),
    ("folder = out / 'app_attempt02'", "folder = out / 'app_candidate2'"),
    ('invoke_checked_attempt02.py', 'invoke_candidate2.py'),
    ('compile_attempt02.txt', 'candidate2_compile.txt'),
    ('compile_attempt02.json', 'candidate2_compile.json'),
    ('candidate1', 'candidate2'),
):
    runner = runner.replace(old, new)
(out / 'compile_candidate2.py').write_text(runner)
print('Approved candidate2 materialized from exact106 inputs; production unchanged')
