# D120 isolated configured-button validation

PASS on 2026-09-24. This is controlled host evidence, not an electrical profile,
physical acceptance, upload authorization or phase gate.

| Build | Target | Executed cases | Passed assertions | Exit |
|---|---|---:|---:|---:|
| Normal | stand_integration_m0_tests | 19 | 207591 | 0 |
| Normal | stand_integration_m1_tests | 19 | 207542 | 0 |
| ASan/UBSan | stand_integration_m0_tests | 19 | 207591 | 0 |
| ASan/UBSan | stand_integration_m1_tests | 19 | 207542 | 0 |

The copied src/host/tests trees and exact bench/motor_stand and bench/recorder
dependencies stayed in `/dev/shm/sumox_d120_configured`. The two bench trees are
needed for CMake's existing target declarations; only the two dedicated stand
targets were built. Parallelism was bounded at two. Tests ran directly, so
their archived stdout/stderr replace a CTest LastTest log.

The only isolated source overlay is `config_overlay.diff`: configured=1,
LOW={0,900,1900,2900}, HIGH={100,1100,2100,3100}. Every target also received
`-DAPP_TEST_CONFIGURED_BUTTONS=1`. No assertion or implementation was changed.

`commands.json` records the exact argv, cwd, environment, times and exit code of
each configure/build/test command. Every stdout/stderr stream is retained.
`summary.json` and the original/isolated before-and-after manifests confirm
unchanged repository files, unchanged isolated source after its overlay, and
unchanged frozen oracle/public inputs. All stderr files are empty.

Outer invocation: `wsl.exe python3 /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots/state/analysis/P2_stand_integration_raw/configured/run_configured.py`
completed with exit 0. After the runs, the exact Python body saved in
`archive_build_metadata.py` was passed by PowerShell literal here-string to
`wsl.exe python3 -`, exit 0, while the existing WSL lifetime remained live.
The resulting stdout is the JSON retained in `build_metadata/manifest.json`.
This archived both CMakeCaches, each target's flags.make/link.txt, and hashes
and sizes of all four executables. Executable binaries are not archived.

No tracked source, board, run authorization or ledger was modified by this
validation subtask. Temporary build files were not deleted.
