# D085 asynchronous QTR implementation validation

2026-09-23 Asia/Dubai. Contract dcd4682; implementation 47f4d9a. P2 software
under D051/D075, with all physical acceptance and human gates still pending.

## Implemented behavior

The actual native Reader owns the fixed proposed four-pad bank after explicit
setup admission. It charges, releases, observes and cleans up through finite
native passes, preserving uncertain RC bounds, source identity, statuses and
cleanup evidence. It never waits synchronously for the full1500us discharge.
The pure adapter qualifies complete intervals; ambiguous color inhibits instead
of becoming black. Robot admits distinct frames separately from fresh opponent
observations, expires retained data and breaks confirmation across gaps. Escape
timers continue on retained levels, but replans/exits require fresh observations.
Countdown warning source windows and stuck-warning continuity are explicit.
The original10/1500us values,1kHz tick and all existing B16 values are unchanged.
The selected2000/2500/6000us guards are development policies, not measurements.

## Actual validation

All paths below are relative to `state/analysis/P2_qtr_native_raw/` unless stated.

| Check | Result and evidence |
|---|---|
| Root full host | PASS2/2,1173 main cases/22840417 assertions plus37 enabled MotorGate cases/3796846 assertions;7.35s. `root_host_final.json/.txt` |
| Root full ASan/UBSan | Same cases/assertions PASS2/2;34.54s. `root_sanitizer_final.json/.txt` |
| Independent spec-derived pure cases |22 cases/26881 assertions PASS normal and ASan/UBSan; independent author did not read production CPP bodies. `author/HANDOFF.md` and receipts |
| Actual native substitutes |14 contract cases,10 boundary cases and3 actual Reader-to-adapter-to-Robot cases pass UBSan; finite operations, cleanup, ownership, timing, wrap and allocation paths exercised. Parent/child assertions separately reported in author handoff |
| Additional author checks |11 tooling methods pass;11 invalid-config variants,22 metadata variants after final foreign-device check, higher confirmation3, two inert build modes/10000loops and eight upload refusals. Failure/crash sentinels prove isolated-child failures propagate |
| Configuration |16 strict methods PASS;147 established declarations/B16 values unchanged. Only explicit D085 additions admitted. `config_final.json/.txt` |
| Target compile only |PASS exit0,145012program/71092compiler globals. source57f4b00192c4b4aaf87c70c60244e9f392abf54908a22e3ded7d215499b1165c; `target_final.json/.txt` |
| Target/source integrity |Exact56-file current source map and aggregate match;3ELFs,36native exports,42AEABI plus fmod/sqrt bindings checked. `target_57f4b001_bench-default.json`, `target_additional_math.json`, `root_target_integrity.json` |
| Fresh separate review |PASS/no open BLOCKER/MAJOR/MINOR. Independent full normal/sanitizer and11native/16config methods PASS;364frozen files unchanged during execution and329reviewed source/test/host/bench files still match. Final disposition in `state/reviews/P2_qtr_native_review.md`. Separate same-model context, not cross-model or human acceptance |
| Existing script/staging regression |25 unchanged tool methods PASS18.899s under WSL;2staging methods PASS8.789s. `tooling_linux_final` and `staging_final` receipts.54distinct scoped methods including11new+16config; not an all-tooling rerun |
| Existing inert registry |Exactly5existing keys independently approved and reproduced before adoption; no new key. `manifest_adoption_final.json` and `manifest_adoption.json` |

Root clean normal/sanitizer builds first encountered the new test's REQUIRE
incompatibility with the established no-exceptions configuration. Five new test
predicates were preserved as CHECK plus safe guards; the successful final builds
complete the clean rebuild. No established test or locked assertion was changed.

## Findings and failed attempts retained

- Reviewer reproduced retained-white GO entry consuming a false replan across
  six masks (12/36 failures), then verified the entry-baseline repair (36PASS).
- Source review found final native guard work outside the timestamp budget,
  unknown GPIO-device admission, expired confirmation and stuck-warning gaps.
  Native timing/metadata and higher-confirm-count/controller tests cover repairs.
- First actual target build failed on Arduino's `bit` macro colliding with the
  helper name. Rename to `padBit` fixed it; fixture now contains the actual macro.
  `target_initial.json/.txt` preserves the exit1 and compiler diagnostic.
- Author/reviewer fixture failures (missing initializer_list, duplicate LL macro,
  missing GPIOC binding, double-begin fixture, REQUIRE compatibility) and required
  negative sentinels are indexed in author receipts, never reported as passes.
- Root first manifest-adoption command used a previous receipt filename before
  this reviewer had persisted that format. It failed closed without changing
  the manifest. Two subsequent tooling invocations used Windows Python against
  the Linux shell/symlink suite; untranslated paths and WinError1314 caused their
  failures. The initial manifest diagnosis was incorrect; see
  `P2_qtr_tooling_invocation_failure.md`. All receipts remain; the unchanged suite
  is rerun under WSL, without weakening assertions or changing Windows privileges.

## Scope and remaining work

No upload, reset, MCU execution, GPIO/ADC/I2C operation, connected sensor reading,
motor action, physical pin approval or human gate occurred. Board operations were
Linux compilation and offline source/ELF inspection only. The last-known MCU
image remains the earlier inert P0 QTR image; no fresh runtime inspection claimed.

No optical white/black/brown separation, capture precision, exclusive pad/debug
handoff, ADC reference, full RAM/runtime-loader qualification, full tick<800us,
hold-on-robot, ring behavior or physical acceptance is inferred. SC-AJ/F091 remain
open. IMU600us + motor settle150us + ADC100us ceilings already exceed800us before
other work; asynchronous QTR alone does not solve the later application schedule.

Next actual P2 task: extend the single concrete ADC1 owner for optional A1 raw
sampling while preserving battery-only operation. `next_ui_task.md` specifies
the source prerequisites and why a second ADC owner or invented BOTH voltage is
invalid. The supplemental `P2_adc_pair_audit.md` supplies exact source constraints.
Physical START/BOTH ambiguity remains SC-A. Full P0-P7 goal stays ACTIVE/incomplete.
