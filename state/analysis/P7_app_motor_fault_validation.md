# D186 inhibited full-application diagnostic validation

25 September 2026, Asia/Dubai. IMPLEMENTED / HOST-TESTED; final scoped review
recorded separately. No target compilation, upload, MCU query or motor run.

Contract/header3b6bfef7 and implementationb14c207a add a default-disabled bench
using the existing Trace around the real Runtime/Transaction/Robot/MotorGate.
It preserves the first callback failure and pre-abort reports, accepts only
inhibited zero-output receipts, and stops after at most four completed epochs.
Generic flashing rejects this sketch before I/O. Fresh staging copies the two
canonical Trace files exactly;539bfbb0 repairs the initial review's source-tree
reparse MAJOR. No shipping source/config, existing Trace, locked test or CMake
change occurred in D186; integrity.json verifies the diff against0907a3a3.

## Independent expectations and actual results

The separate fresh-context same-model author used the contract/public headers;
the first150lines of an existing runtime test supplied fixture mechanics only.
No implementation CPP was used to derive expectations. Oracle c1f8d8f6 and
eight contract/source/tool identities were frozen before execution.

| Receipt under P7_app_motor_fault_raw/ | Actual result |
|---|---|
| runtime_first.json | Both normal/sanitized13/14cases; sole stalled-clock reason mismatch;3other driver methods PASS |
| oracle_correction_freeze.json | Independent author/reviewer agree published receipt-invalid priority; new oracle588acb99, source unchanged |
| runtime_corrected.json |5driver methods PASS; normal and ASan/UBSan each14cases/23885assertions, no skips |
| staging_linux_first.json |10methods,9PASS/1Windows-onlyskip; real symlinks exercised |
| staging_windows_first.json |10methods, real3junctions PASS;7symlink subtests skip for missing OS privilege |
| legacy_tooling.json |68methods:56PASS/11import errors/1Windows-onlyskip; coordinator omitted sibling import path |
| legacy_tooling_import_retry.json |Only11import-error methods rerun with tests/tooling on PYTHONPATH:11PASS, no edits |
| legacy_motor_fault.json |3driver methods PASS; unchanged Trace/real Gate normal+sanitized each18cases/2570assertions |
| integrity.json |8current pins exact, protected paths/history prefix unchanged,0owned RAM/Windows fixture remnants |
| git_bytes.json |16checked blobs byte-exact; board_tool.py Git LF/working CRLF explicitly mapped, frozen execution pin remains exact |

The corrected stalled-clock case retains every other check and adds explicit
decision-made and invalidated-feedback assertions. Runtime abort invalidates
the last receipt; D186 APPLICATION_INVALID therefore precedes RUNTIME_TERMINAL.
Original failure/source/oracle remain in Git and the first receipt. No existing
or locked test was amended. No sanitizer finding occurred.

Commands, durations, exit statuses and complete outputs are in each receipt.
Observed host tools: Windows Python3.13.11; WSL Python3.12.3/g++13.3.0. Heavy
normal/sanitizer compiles ran serially in owned RAM and executed through memfd.
Legacy tooling's final union is67PASS/1platformskip. Historical22-target CTest
PASS at90e73959 remains in P7_motor_fault_raw/full_host.json; it was not rerun
or presented as current. Later D169/D180 config declarations have their own
focused evidence; D186 changes none of those files.

## Limits and exact next task

Empty grants cannot naturally reach every Robot STOPPED or Trace overflow state;
tests do not manufacture private state or synthetic Robot commands to claim it.
Mock clocks/native callbacks and sketch substitutes are host evidence only.
Tracing perturbs timing; blocked native setup remains possible. No source-cause,
live RAM/stack, R4 WCET, physical acceptance, human gate or competition claim.
D160/D161's actual static full-app IO fault remains unresolved.

Next prepare one fixed static/default/M0 compile adapter using existing bounded
executor and D141/D147 policy/artifact checks, with independent controlled tests.
Keep dynamic/generic admission closed and historical helpers/pins unchanged.
Use fresh stage/source/artifact/attempt binding; exact new project/flag metadata
and a documented bijection of seven artifact names preserve all byte checks.
Only after that host closure, a separately reviewed native invocation can obtain
new ET_EXEC/package/native initialization/ABI/capture identities. Do not reuse
D149 addresses or the isolated D1732592-byte decoder. Board-dependent work and
all physical/human gates remain pending.
