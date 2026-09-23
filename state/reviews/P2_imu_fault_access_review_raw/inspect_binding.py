"""Inspect actual native callback object dependencies without defining either getter."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).parent
source = ROOT / 'src/app/native_sources_unoq.cpp'
receipt = dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), commands=[])
with tempfile.TemporaryDirectory(prefix='d097-native-bind-review-', dir='/dev/shm') as temp:
    obj = str(Path(temp) / 'binding.o')
    commands = [
        ['g++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Werror', '-fno-exceptions', '-fno-rtti',
         '-DARDUINO_ARCH_ZEPHYR', '-I', str(ROOT / 'src'), '-c', str(source), '-o', obj],
        ['nm', '-u', '-C', obj], ['objdump', '-drC', obj]]
    for cmd in commands:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        receipt['commands'].append(dict(argv=cmd, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr))
        if p.returncode: break
    if not p.returncode:
        imports = receipt['commands'][1]['stdout']
        assert 'imu::Acquirer::setupFailure() const' in imports
        assert 'imu::Acquirer::read(unsigned int)' not in imports
        block = re.search(r'<app::NativeSources::imuSetupFailure\(.*?\)>:(.*?)(?=\n[0-9a-f]+ <|\Z)',
                          receipt['commands'][2]['stdout'], re.S)
        assert block and 'imu::Acquirer::setupFailure() const' in block.group(1)
        receipt['callback_object_excerpt'] = block.group(0)
        receipt['get_failure_dependency_only'] = True
out = RAW / 'binding_object.json'
assert not out.exists(), 'Preserve earlier evidence'
out.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: v for k, v in receipt.items() if k != 'commands'}, indent=2))
raise SystemExit(p.returncode)
