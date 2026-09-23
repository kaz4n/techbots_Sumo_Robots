from pathlib import Path
import hashlib, json, os, subprocess, tempfile, time
root = Path.cwd()
receipt = root / 'state/analysis/P2_app_transaction_raw/halt_worker'
base = ['g++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic', '-Werror', '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined', '-fno-sanitize-recover=all', '-DDOCTEST_CONFIG_NO_EXCEPTIONS', '-I', str(root / 'src'), '-isystem', str(root / 'host/third_party')]
sources = [str(p) for p in sorted((root / 'src/core').glob('*.cpp'))]
sources += [str(root / p) for p in ('src/hal/motors.cpp', 'tests/locked/test_motor_gate.cpp', 'host/motor_gate_main.cpp')]
def run(name, argv, env=None):
    result = subprocess.run(argv, capture_output=True, text=True, timeout=180, env=env)
    payload = dict(argv=argv, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr, motors_sha256=hashlib.sha256((root/'src/hal/motors.cpp').read_bytes()).hexdigest(), utc_ns=time.time_ns())
    (receipt / (name+'.json')).write_text(json.dumps(payload, indent=2)+'\n')
    print(name, result.returncode, result.stdout, result.stderr, flush=True)
    if result.returncode: raise SystemExit(result.returncode)
with tempfile.TemporaryDirectory(prefix='sumo-d095-halt-worker-') as tmp:
    for allowed in (0,1):
        binary = str(Path(tmp) / ('motor_gate_'+str(allowed)))
        run('compile_gate_'+str(allowed), base+[f'-DMOTORS_ALLOWED={allowed}']+sources+['-o',binary])
        run('run_gate_'+str(allowed), [binary, '--no-colors'])
env = dict(os.environ, SUMO_NATIVE_RECEIPT_DIR=str(receipt / 'native'))
run('native_regression', ['python3','-m','unittest',
    'tests.tooling.test_motor_port_unoq.NativeMotorPortTests.test_b3_b6_b7_actual_native_default_disabled_contract',
    'tests.tooling.test_motor_port_unoq.NativeMotorPortTests.test_b3_b6_b7_actual_native_host_only_enabled_contract'], env)
