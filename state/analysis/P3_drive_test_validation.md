# D123 P3 DRIVE_TEST validation — 24 September 2026

Status: IMPLEMENTED / HOST-TESTED / TARGET-COMPILED. Physical P3 results remain
unmeasured under D122's scheduling assumption. No upload, MCU read/write/reset,
UART operation, source grant or motor run occurred in this task.

The isolated profile admits only a locally selected DRIVE_TEST START through the
actual complete countdown, then runs SEARCH and edge escape with real perception,
Governor, Transaction, MotorGate and recording. No combat path runs. Profile0
defaults and all 35 established locked tests are unchanged; B16 values are intact.

## Host and independent evidence

Commands, timestamps, exit statuses, exact source hashes and preserved logs:
[raw evidence](P3_drive_test_raw/). The `run_host.py` invocations use WSL Ubuntu,
g++13.3.0, CMake3.28.3 and Python3.12.3. Artifacts are copied before WSL exits.

| Target | Cases | Assertions | Result |
|---|---:|---:|---|
| Existing main | 1496 | 50,418,546 | Normal and ASan/UBSan PASS |
| Existing motor-enabled Gate | 187 | 4,536,952 | Normal and ASan/UBSan PASS |
| Existing B4 M0 | 18 | 200,690 | Normal and ASan/UBSan PASS |
| Existing B4 M1 | 18 | 200,641 | Normal and ASan/UBSan PASS |
| New P3 M0 | 27 | 248,475 | Normal and ASan/UBSan PASS |
| New P3 M1 | 27 | 231,229 | Normal and ASan/UBSan PASS |
| Configured synthetic A1 P3 M0 | 28 | 289,681 | Normal and ASan/UBSan PASS |
| Configured synthetic A1 P3 M1 | 28 | 272,435 | Normal and ASan/UBSan PASS |

The configured overlay changes only three copied A1 window declarations and adds
APP_TEST_CONFIGURED_BUTTONS. Production A1 remains unconfigured. It is a fixture,
not an electrical measurement. There are no skipped or weakened safety cases.

The first normal run exposed one incorrect field expectation in the new draft
oracle; all existing targets passed. [The full disposition](P3_drive_test_oracle_disposition.md)
preserves the original oracle/failure and separately adjudicated correction before
acceptance. The focused normal rerun passes; the final full six-target sanitizer
run passes. Production was never changed to accommodate that oracle mistake.

Independent spec/public-header authoring froze expectations before execution.
Accepted new locked safety SHA256:
`5bde79679c8af6a362686acf205ac2401837b49da88eac1eec7cfd82a77fea0f`.
This is now established and protected. Tooling: 93 methods pass, including 14 new
literal profile checks. Original legacy launcher import failures are retained;
setting PYTHONPATH corrected only the launcher, not tests or production.

[Separate review](../reviews/P3_drive_test_review.md) is a fresh same-model Codex
context, not cross-model or human review. Its additional 20 config/policy probes
pass, plus four actual Runtime scenarios per M0/M1 (79,829 / 79,074 assertions).
Those cover real local ADC/menu/countdown delivery, source faults, empty grants,
and post-calibration START rearming. Traversing QTR_CAL temporarily selects raw
line acquisition; fresh classified frames and a complete neutral rearm are needed
before a subsequent START. An early release is suppressed and never replayed.
The review retains its initial fixture/compiler diagnostics; firmware is unchanged.

## Actual target compilation, no firmware execution

Both checked builds ran on UNO Q Linux through existing ADB fallback. Exact CLI,
core, compiler, startup, recipes and artifacts are recorded in checked receipts.

| Build | Source SHA256 prefix | ELF SHA256 prefix | Conditional loader peak / free span |
|---|---|---|---|
| Default app/M0 | 090e21826d9a8ff7 | 21b28ee366e77701 | 262128 / 16 bytes |
| DRIVE_TEST/M0 | cc1ef324331c06c9 | bf530d1555c897df | 251520 / 10624 bytes |

Receipts: default `ff7d13a6424740c7b725470fc0f1e695`, P3
`53c63c61eecc4c1cac6349e6bec3cb56`. All 95 default / 96 P3 staged files match their
repository source. The P3 ELF retains routeDriveTest and omits routeNormal,
checkStall and startOpener symbols. The strong empty loop hook is present.

Default ELF/payload is eight bytes smaller than D120; it is **not byte-identical**.
The profile0 source refactor is semantically equivalent and its existing suites
pass. The resident loader is unchanged. These pristine-pool estimates and retained
compiler low-memory warnings do not prove actual loading, heap, stack or WCET.
D118 remains the last actual MCU image/observation; its evidence does not transfer
to these newly compiled images.

The source comparison harness initially mapped the new README to the .ino path;
that invalid mapping failed explicitly. The final `check_sources.py` maps every
non-src file to its actual sketch-directory file, preserving all comparisons.
No source or checked build changed for this harness correction.

## Remaining P3 work

This profile prepares 3.1/3.5/3.6/3.7 software, not measured acceptance. P3 3.2
R_room, all stopping/turn/ring results, actual sensor qualification and human gates
remain pending. Next software task is a finite isolated 3.4 turn trial, including
exact left and right 180-degree commands; the existing match Turn tie remains
unchanged. P3 3.3 needs an isolated sub-full-duty trial and a common distance datum:
rest after reverse/escape is not forward stopping distance. No production search
cap or fallback timing value may be tuned from synthetic results.
