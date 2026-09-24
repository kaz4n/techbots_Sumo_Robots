"""Bind the configured-only draft correction to unchanged ordinary preprocessed code."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import tempfile

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent / 'default_equivalence.json'
assert not out.exists()
draft = root / 'state/analysis/P7_readiness_test_draft'
names = ['test_readiness_runtime_retry1.cc', 'test_readiness_runtime_retry2.cc']
record = {'utc': datetime.now(timezone.utc).isoformat(), 'pairs': [], 'hardware_access': False}
with tempfile.TemporaryDirectory(prefix='sumox_d138_equivalence_', dir='/dev/shm') as work:
    path = Path(work) / 'test_readiness_runtime.cc'
    for motors in (0, 1):
        outputs = []
        pair = {'motors_allowed': motors, 'sources': []}
        for name in names:
            content = (draft / name).read_bytes()
            path.write_bytes(content)
            argv = ['g++', '-std=c++17', '-E', '-P', '-DDOCTEST_CONFIG_NO_EXCEPTIONS',
                    f'-DMOTORS_ALLOWED={motors}', '-I' + str(root / 'src'),
                    '-I' + str(root / 'tests'), '-I' + str(root / 'host/third_party'), str(path)]
            result = subprocess.run(argv, capture_output=True, check=False)
            assert result.returncode == 0, result.stderr.decode(errors='replace')
            outputs.append(result.stdout)
            pair['sources'].append({'source': name, 'source_sha256': hashlib.sha256(content).hexdigest(),
                'argv': argv, 'returncode': result.returncode,
                'preprocessed_bytes': len(result.stdout),
                'preprocessed_sha256': hashlib.sha256(result.stdout).hexdigest(),
                'stderr': result.stderr.decode(errors='replace')})
        assert outputs[0] == outputs[1]
        pair['byte_identical_ordinary_translation'] = True
        record['pairs'].append(pair)
record['scratch_released'] = True
out.write_text(json.dumps(record, indent=2) + '\n')
print('Both M0/M1 ordinary preprocessed translations byte-identical; owned scratch released.')
