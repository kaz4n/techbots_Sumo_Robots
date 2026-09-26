# D195 fixed observer remote adapter contract

26 September 2026. Prepare only a new fixed adapter at
state/analysis/P7_app_motor_observe_run_raw/remote.py. Derive it minimally from
the pinned D190 remote_run02.py below. Preserve every historical source, test,
receipt and consumed owner. This is host preparation: actual observer entry
instruction review, caller/action admission, scratch cleanup and a separately
bound native attempt remain prerequisites. No native execution follows from
this contract or its host tests.

## Fixed provenance and identities

Original source:
state/analysis/P7_app_motor_fault_run_raw/remote_run02.py,10518 bytes, SHA256
a77fb7d458ceb88f939ce785250d7c49727c56db231a9688890bef808c0c9162.

The exact source digest is
3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0.
RUN_ID is app-motor-observe-3a08ddeb-run01. Retain PARENT
/home/arduino/sumox26_codex_build and DATA /home/arduino/.arduino15.
SKETCH is PARENT/SOURCE/app_motor_observe; BUILD is
PARENT/app-motor-observe-static01/build. Exclusive remote output owners are
PARENT/RUN_ID-upload and PARENT/RUN_ID-capture. No caller-selected alternative.

The checked D193 artifacts receipt is
state/analysis/P7_app_motor_observe_compile_raw/native_static01/artifacts.json,
SHA2565ceba77dde7c493d66398bfd6d8e0e27e56345612290cb8fef9328f24b87625b.
It binds the following artifacts; retain exact integer sizes and string hashes:

| Role | Bytes | SHA256 |
|---|---:|---|
| raw: BUILD/app_motor_observe.ino.bin | 95344 | f1df5e7f4e094021e96947c53a204b6fac32c12ef35caba76eae61f2bfcdc3cc |
| sketch: BUILD/app_motor_observe.ino.bin-zsk.bin | 95360 | 85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c |
| installed loader ELF | 2303728 | 39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd |
| derived loader_image | 263680 | e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2 |

The source remains the compiled static/default-startup MATCH0/MOTORS_ALLOWED0/
SUMOX_MOTOR_FAULT_PROBE1 observer. No firmware, config, grants or runtime limits
are changed. Existing default-disabled peripheral and service grants remain.

Keep the original three private dependency roles and bytes unchanged:

| Role and source | Bytes | SHA256 |
|---|---:|---|
| upload: state/analysis/P7_static_startup_raw/upload_remote.py | 24710 | e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1 |
| capture: state/analysis/P7_static_startup_raw/capture_remote.py | 37525 | 95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e |
| helper: state/analysis/P7_static_link_probe_raw/static_remote.py | 33321 | 8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8 |

Retain the exact dependency selection/type/hash checks before any private exec,
private module loading, and the existing upload.selected_profile binding. No
global module registration, dependency mutation on disk or alternate helper.

## Metadata-only derivation

Apply these ordered count-checked byte replacements to the pinned original to
define the metadata-only baseline. Counts apply after earlier replacements.
This is a source derivation/review rule, not a new runtime projection framework.

| Old | New | Count |
|---|---|---:|
| 21df6ae82cca4b09dc6b1e0de5bc719cf98ec6887800d5ce8297522e491a7950 | 3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0 | 1 |
| app-motor-fault-21df6ae8-run02 | app-motor-observe-3a08ddeb-run01 | 1 |
| app-motor-fault | app-motor-observe | 8 |
| app_motor_fault | app_motor_observe | 4 |
| AppMotorFaultCapture | AppMotorObserveCapture | 2 |
| 95312 | 95344 | 1 |
| 18598e13f2b5601db504f5272826b0952b95477dd2b1b8d397d20bd2ff899144 | f1df5e7f4e094021e96947c53a204b6fac32c12ef35caba76eae61f2bfcdc3cc | 1 |
| 95328 | 95360 | 2 |
| deb40317e5c444af26e65da4b6f1d0e577d9897d59dbddff3bce03a7bc14335c | 85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c | 1 |
| 727088 | 727152 | 1 |

This baseline is10548 bytes, SHA256
e0bb7868e54a640499718d5c0d3df4ce6c6b4ef72a49f0bda9df64bbb60530f5.
The only behavioral changes beyond it are the wait deltas below. Freeze the
final source separately after implementation; do not confuse its hash with this
intermediate baseline. Preserve unchanged function bodies wherever possible.

## Public and fixture interfaces

Keep the same functions and signatures as the original:

```
load_dependencies(sources)
selected_profile(support, run_id=RUN_ID)
_artifact(support, name, pin)
checked_upload_bindings(dependencies, bindings)
checked_capture_bindings(dependencies, bindings)
_flash_plan(prefix, region)
read_plan()
upload(dependencies, *, fs_root=Path('/'), executor=None, clock=None, bindings=None)
_capture_type(dependencies)
collect(dependencies, loader_image, *, fs_root=Path('/'), executor=None,
        clock=None, sleeper=None, bindings=None)
```

The capture factory returns AppMotorObserveCapture extending the same pinned
support.Capture. Keep profile_bindings, prepare_plan, check_image, gather and
complete, and add only the bounded pre_sample_pause method. Existing injected
filesystem/executor/clock/sleeper seams remain available to controlled tests.
Import defines only; it does not load dependencies, inspect files or call a
device. No CLI, generic target, alternate run ID or configurable wait is added.

Binding schemas become fixed-app-motor-observe-upload-v1 and
fixed-app-motor-observe-capture-v1; report/attempt/analysis prefixes become
app-motor-observe. All exact-key checks, boot UUID/UID1000 checks, integer-type
checks (including bool rejection), paths, installed files, package/raw/loader
pins, capture config, absence lists and Python-B admission remain unchanged
apart from fixed observer identities above. Upload remains exactly the existing
static/default arduino-cli upload of the fixed raw file to the fixed sketch.
The inherited /tmp/remoteocd absence requirement remains mandatory; this adapter
performs no cleanup and does not weaken process-use/file checks.

## Observed SRAM windows and capture plan

Successful ABI02 result
state/analysis/P7_app_motor_observe_compile_raw/native_abi_static02/result.json
is893020 bytes, SHA256
a5e67635f43b96b813885687fbafe743cfc3ec6a93d089a66453ca574c0676da.
Its abi.json is3704 bytes, SHA256
dfc34596b65d3a82e21e28c3acf9fb1535bec2eb3b489d270c593c9fe3eab3a7.
These establish the six capture windows, unchanged from the original addresses
but now bound to the observer image and its current type layout:

| Name | Address, decimal | Bytes |
|---|---:|---:|
| trace | 536951180 | 2128 |
| report | 537119696 | 1168 |
| runtime | 537117984 | 600 |
| transaction | 537115448 | 504 |
| previous | 537115952 | 48 |
| gate | 536953520 | 88 |

Report.polls occupies offset12 inside the1168-byte report; its size/alignment
are4. No extra window is needed. This adapter captures bytes, not field values.
It does not reuse D149/D173 layouts, decode phase, or infer terminal state.

Keep the exact read ordering: before.loader chunks0..4, before.sketch chunks5..6,
first six windows7..12, second six windows13..18, after.sketch chunks19..20,
after.loader chunks21..25. Loader flash starts0x08000000 and spans263680 bytes;
sketch flash starts0x08100000 and spans95360 bytes. Chunks remain at most65536
bytes. Flash comparisons remain at indices4,6,20,25 against complete checked
references. Exactly26 commands/reads request727152 bytes, with12 SRAM snapshots.
Keep every raw read, hash, file receipt and explicit coherence=UNPROVEN.

## Sole behavioral addition: one pre-sample wait

prepare_plan initializes analysis.pre_sample_wait to None alongside the existing
schema, flash, snapshots and coherence fields. At index7 in gather, after both
initial flash comparisons succeed and before one_read(7,...), call
pre_sample_pause exactly once. Keep the inherited pause at index13 unchanged:
it still records report.wait and requests exactly2 seconds between samples.
Do not poll memory, retry a read, extend the plan, or sleep elsewhere.

pre_sample_pause first requires remaining budget greater than30 seconds, using
the inherited budget()/now() checks. It records in analysis.pre_sample_wait:

```
{'requested_seconds': 30, 'before': <checked monotonic now>, 'after': None}
```

Call the existing injected sleeper with exactly30. After it returns, populate
after from checked now(), require after-before >=30, then check budget() again.
No supplied, inferred or fabricated timestamps/alignment/phase are allowed.
The fixed request is an exact integer; both recorded times come through the
existing finite/nondecreasing monotonic checks. Do not reset the600-second
capture origin or increase any deadline. A short sleep, exception, reversed or
invalid clock, or exceeded budget fails before the first SRAM read.

Retain partial wait evidence: budget refusal before recording leaves None;
failure after recording leaves before and whatever after was actually obtained.
Do not swallow the failure or replace it with a later cleanup/clock error.
The existing _collect/finalize path preserves first_error, partial reads/flash
flags and closing errors in the owned capture result. Do not add a new transport,
retry, alternate result owner, or separate wait-file lifecycle.

complete retains the original flash/snapshot/count requirements with727152
bytes, and additionally requires a non-None pre_sample_wait with a populated
after and elapsed time at least30. Existing finalization still independently
requires no first_error before reporting COLLECTED. A recorded after does not
excuse a final budget failure. No FROZEN/10000-epoch assertion belongs here:
thirty seconds is a bounded observation delay, not proof of MCU progress.

The future actions validator must admit/check the one new analysis field while
preserving its exact top-level report keys, existing report.wait, byte accounting
and canonical result hash. It must check requested_seconds30, valid ordered
timestamps, >=30 elapsed, and ordering within capture start, two-second wait
and capture finish. That caller/actions work is outside this source contract.

## Preserved limits and independent evidence

Retain the original descriptor/path/file/process checks, exclusive claim,
durable intent, before/after pin checks, first-error/partial evidence and final
close semantics. Inherited upload budget remains180 seconds; capture budget600
seconds; each capture child remains bounded by min(30,budget()) with the original
reap behavior and1MiB stream limit. No native call, firmware alteration, motor
grant, compiler, reset, extra read or deletion is introduced by preparation.

An independent oracle must freeze before reading new implementation. It must
derive the metadata baseline from the pinned original, preserve old assertions
and check the bounded behavioral delta. Cover exact dependency/profile/binding
keys, paths, hashes, byte counts and bool rejection; private dependency loading;
upload delegation; all26 exact reads and flash brackets; wait initialization,
exact position after read6/before read7, one30-second sleep, unchanged index13
two-second pause, timestamps and completion predicates; insufficient/equal30
budget, short/throwing sleep, invalid/backward clock and oversleep/deadline;
no first SRAM call after wait failure; preserved partial reads, wait evidence,
first error and failing close/postchecks; wrong/short flash bytes, read failures,
and rejection of incomplete counts/snapshots/wait. Use injected clocks/sleepers,
temporary controlled files and mock executors, with no real sleeping or device.
Test both public collect and returned capture-class seams. Freeze inputs, retain
first failure evidence, and independently review before any native admission.

Source/ABI/artifact evidence supports this fixed capture plan only. Runtime
success, complete callback history, atomic SRAM coherence, electrical safety,
RAM/WCET qualification, powered-run permission and human gates remain separate.
