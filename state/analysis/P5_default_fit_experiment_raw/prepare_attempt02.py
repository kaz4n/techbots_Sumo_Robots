"""Preserve the failed fixture attempt and prepare the same candidate's one compile."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess

out = Path(__file__).resolve().parent
root = out.parents[2]
project = root / 'build/p5_default_fit_candidate'
failed = out / 'attempt01'
failed.mkdir(exist_ok=True)
for name in ('invoke_checked.py', 'compile_target.py', 'compile.json', 'compile.txt',
             'actual_remote_commands.jsonl', 'materialized_manifest.json'):
    if (failed / name).exists():
        assert (failed / name).read_bytes() == (out / name).read_bytes()
    else:
        shutil.copy2(out / name, failed / name)
commands = [json.loads(line) for line in (out / 'actual_remote_commands.jsonl').read_text().splitlines()]
assert not any(row['argv'][:2] == ['arduino-cli', 'compile'] for row in commands)
(failed / 'failure_adjudication.json').write_text(json.dumps({
    'utc': datetime.now(timezone.utc).isoformat(),
    'actual_native_compiler_invocations': 0,
    'outer_runner_returncode': 1,
    'wrapper_reported_returncode': 0,
    'cause': 'Missing unchanged app_build_pins.json fixture; app_build_commands.json also required',
    'runner_defect': 'board_tool.main return value was not propagated; original failure receipts remain intact',
    'candidate_source_unchanged': True,
}, indent=2) + '\n')
manifest = json.loads((out / 'materialized_manifest.json').read_text())
for name in ('app_build_pins.json', 'app_build_commands.json'):
    relative = 'tools/' + name
    source = root / relative
    committed = subprocess.run(['git', 'show', '2d924f1f:' + relative], cwd=root,
                               capture_output=True, check=True).stdout
    working = source.read_bytes()
    assert working.replace(b'\r\n', b'\n') == committed.replace(b'\r\n', b'\n'), relative
    shutil.copy2(source, project / relative)
    manifest['files'][relative] = {'sha256': hashlib.sha256(working).hexdigest(),
                                   'bytes': len(working),
                                   'commit_blob_sha256': hashlib.sha256(committed).hexdigest(),
                                   'git_checkout_eol_only_difference': working != committed}
(out / 'materialized_manifest_attempt02.json').write_text(json.dumps(manifest, indent=2) + '\n')
wrapper = (out / 'invoke_checked.py').read_text()
wrapper = wrapper.replace('remote_snapshot_ready.json', 'remote_snapshot_ready_attempt02.json')
wrapper = wrapper.replace('actual_remote_commands.jsonl', 'actual_remote_commands_attempt02.jsonl')
wrapper = wrapper.replace('board_tool.main()\n', 'sys.exit(board_tool.main())\n')
(out / 'invoke_checked_attempt02.py').write_text(wrapper)
runner = (out / 'compile_target.py').read_text()
for old, new in (
    ('materialized_manifest.json', 'materialized_manifest_attempt02.json'),
    ("folder = out / 'app'", "folder = out / 'app_attempt02'"),
    ('invoke_checked.py', 'invoke_checked_attempt02.py'),
    ('compile.txt', 'compile_attempt02.txt'),
    ('compile.json', 'compile_attempt02.json'),
):
    runner = runner.replace(old, new)
(out / 'compile_target_attempt02.py').write_text(runner)
print('Preserved attempt01; fixture complete; candidate identical; actual native compiler count=0')
