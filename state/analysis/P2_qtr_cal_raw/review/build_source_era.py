"""Build only the reviewer source-era reproducer with current real modules."""
from pathlib import Path
import subprocess
import sys
root = Path.cwd()
sources = sorted(str(p) for p in Path('src/core').glob('*.cpp'))
sources += [str(Path('src/hal') / p) for p in ('motors.cpp', 'ui.cpp', 'line_qtr_adapter.cpp', 'qtr_cal.cpp', 'qtr_cal_format.cpp')]
sources += ['state/analysis/P2_qtr_cal_raw/review/source_era_probe.cpp']
destination = Path('build/qtr_cal_fresh_review/source_era_probe')
destination.parent.mkdir(parents=True, exist_ok=True)
argv = ['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-pedantic', '-fno-exceptions', '-fno-rtti', '-Isrc', '-Itests', *sources, '-o', str(destination)]
print(argv, flush=True)
raise SystemExit(subprocess.run(argv).returncode)
