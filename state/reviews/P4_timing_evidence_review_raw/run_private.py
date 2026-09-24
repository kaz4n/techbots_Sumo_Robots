"""D129 reviewer-only synthetic host checks and pre-D129 object layout comparison."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
WORK = Path(tempfile.mkdtemp(prefix='sumox_d129_review_', dir='/dev/shm'))
FIX = WORK / 'fixture'
for directory in ('src', 'tests', 'host'):
    shutil.copytree(ROOT / directory, FIX / directory)
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in sorted((ROOT / 'src').rglob('*')) if p.is_file()}
commands = []


def save(status, **extra):
    (OUT / 'private_validation.json').write_text(json.dumps(dict(
        result=status, commands=commands, hashes=hashes,
        finished_utc=datetime.now(timezone.utc).isoformat(), **extra), indent=2) + '\n')


def run(name, argv, timeout=300):
    result = subprocess.run(argv, text=True, capture_output=True, timeout=timeout)
    (OUT / (name + '.log')).write_text(result.stdout + result.stderr)
    commands.append(dict(name=name, command=argv, exit_code=result.returncode))
    if result.returncode:
        save('FAIL')
        raise SystemExit(result.returncode)
    return result.stdout.strip()


config = FIX / 'src/config.h'
text = config.read_text()
for before, after in (
    ('BUTTON_WINDOWS_CONFIGURED = 0U', 'BUTTON_WINDOWS_CONFIGURED = 1U'),
    ('BUTTON_LOW_RAW[4] = {0U, 0U, 0U, 0U}',
     'BUTTON_LOW_RAW[4] = {0U, 900U, 1900U, 2900U}'),
    ('BUTTON_HIGH_RAW[4] = {0U, 0U, 0U, 0U}',
     'BUTTON_HIGH_RAW[4] = {100U, 1100U, 2100U, 3100U}'),
):
    if text.count(before) != 1:
        raise RuntimeError('Unexpected fixture configuration: ' + before)
    text = text.replace(before, after)
config.write_text(text)
shutil.copy2(OUT / 'private_boundaries.cc', WORK / 'private_boundaries.cc')
shutil.copy2(OUT / 'private_fixture.h', WORK / 'private_fixture.h')
sources = sorted((FIX / 'src/core').glob('*.cpp')) + sorted((FIX / 'src/app').glob('*.cpp'))
hal = ('ui power_inputs imu_heading imu_adapter ui_display motors recorder_frames '
       'recorder recorder_csv recorder_dump line_qtr_adapter qtr_cal qtr_cal_format').split()
sources += [FIX / 'src/hal' / (name + '.cpp') for name in hal]
sources += [FIX / 'host/motor_gate_main.cpp', WORK / 'private_boundaries.cc']
cmake = 'cmake_minimum_required(VERSION 3.20)\nproject(private_d129 LANGUAGES CXX)\n'
cmake += 'set(CMAKE_CXX_STANDARD 17)\nenable_testing()\n'
for motors in (0, 1):
    target = f'private_m{motors}'
    cmake += f'add_executable({target}\n' + ''.join(f'  "{p}"\n' for p in sources) + ')\n'
    cmake += f'target_include_directories({target} PRIVATE "{FIX}/src" "{FIX}/tests" "{FIX}/host/third_party")\n'
    cmake += f'target_compile_definitions({target} PRIVATE DOCTEST_CONFIG_NO_EXCEPTIONS APP_TEST_CONFIGURED_BUTTONS=1 SUMOX_P4_REACTIVE=1 SUMOX_TIMING_EVIDENCE=1 MOTORS_ALLOWED={motors})\n'
    cmake += f'target_compile_options({target} PRIVATE -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti)\n'
    cmake += f'add_test(NAME {target} COMMAND {target})\n'
(WORK / 'CMakeLists.txt').write_text(cmake)
run('configure', ['cmake', '-S', str(WORK), '-B', str(WORK / 'build')])
run('build', ['cmake', '--build', str(WORK / 'build'), '--parallel', '2'], 600)
run('tests', ['ctest', '--test-dir', str(WORK / 'build'), '--verbose'])

# Only public headers are needed to compare sizeof with the pre-D129 contract.
BASE = WORK / 'baseline'
shutil.copytree(FIX / 'src', BASE / 'src')
for relative in ('src/config.h', 'src/core/fsm.h', 'src/core/types.h', 'src/core/logframe.h'):
    content = subprocess.run(['git', '-C', str(ROOT), 'show', '3985da16:' + relative],
                             capture_output=True, check=True).stdout
    (BASE / relative).write_bytes(content)
probe = WORK / 'layout.cc'
probe.write_text('#include "app/runtime.h"\n#include <cstdio>\nint main(){std::printf("%zu %zu %zu %zu %zu %zu %zu\\n", sizeof(fsm::Robot), sizeof(fsm::RobotResult), sizeof(app::Transaction), sizeof(app::Runtime), sizeof(fsm::RobotInput), sizeof(logframe::EventInput), sizeof(logframe::EventBatch));}\n')
layouts = {}
profiles = (('default', []), ('b4', ['-DSUMOX_B4_STAND=1']),
            ('drive', ['-DSUMOX_P3_DRIVE_TEST=1']), ('turn', ['-DSUMOX_P3_TURN_TRIAL=1']),
            ('stop', ['-DSUMOX_P3_STOP_TRIAL=1']), ('reactive', ['-DSUMOX_P4_REACTIVE=1']))
for profile, flags in profiles:
    for version, folder in (('prior', BASE), ('current', FIX)):
        binary = WORK / ('layout_' + profile + '_' + version)
        run('layout_build_' + profile + '_' + version,
            ['g++', '-std=c++17', '-I', str(folder / 'src'), *flags, str(probe), '-o', str(binary)])
        layouts[profile + '_' + version] = run('layout_run_' + profile + '_' + version, [str(binary)])
binary = WORK / 'layout_timing'
run('layout_build_reactive', ['g++', '-std=c++17', '-I', str(FIX / 'src'),
                              '-DSUMOX_P4_REACTIVE=1', '-DSUMOX_TIMING_EVIDENCE=1', str(probe), '-o', str(binary)])
layouts['timing_current'] = run('layout_run_reactive', [str(binary)])
equal = all(layouts[p + '_prior'] == layouts[p + '_current'] for p, _ in profiles)
equal = equal and layouts['reactive_current'] == layouts['default_prior']
unchanged = all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == value
                for p, value in hashes.items())
status = 'PASS' if equal and unchanged else 'FAIL'
save(status, layouts=layouts, all_layouts_unchanged=equal,
     source_unchanged_during_execution=unchanged,
     synthetic_overlays={'button_windows': 'configured'},
     limits='Synthetic host observations and object layouts only; no board operations or physical/WCET evidence.')
print(json.dumps(dict(result=status, layouts=layouts)))
raise SystemExit(0 if status == 'PASS' else 1)
