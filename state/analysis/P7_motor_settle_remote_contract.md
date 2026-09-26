# D201 fixed inhibited SETTLE remote adapter

26 September 2026. Source/host preparation only. Implement one new fixed
`state/analysis/P7_motor_settle_run_raw/remote.py` as the exact metadata
derivative below. Preserve every historical source, assertion, receipt and
consumed owner. Accepted compile/ABI/entry file evidence supports this scope;
native use still requires the final caller scope and fresh admission.

The checked binding proposal is
`state/analysis/P7_motor_settle_run_raw/capture_binding01.json`,
24233 bytes, SHA256 0a9d4a6af736ff96efa3b9213696f4369cb861e07996e594ebce00c996e39619.
It records fixed observations and ordered derivations; it is not a native
upload/capture binding or attempt claim. Its entry evidence contains the actual
D199 result, summary, local closure and independent semantic review pins.
No runtime success or physical qualification is inferred from those files.

## Exact input and metadata derivative

Original D195 adapter:
`state/analysis/P7_app_motor_observe_run_raw/remote.py`,11357 bytes, SHA256
98b0f5394d64f61178277f701adb81eece3d5f136ea84a8c5fb30534a5b241db.
Apply only these11 ordered count-checked byte substitutions. Counts apply
after preceding replacements; the exact strings are also in the binding.

| Old literal | New literal | Count |
|---|---|---:|
| `3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0` | `117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da` | 1 |
| `app-motor-observe-3a08ddeb-run01` | `app-motor-settle-117cc0e7-run01` | 1 |
| `app-motor-observe` | `app-motor-settle` | 8 |
| `_app_motor_observe_private_` | `_app_motor_settle_private_` | 1 |
| `AppMotorObserveCapture` | `AppMotorSettleCapture` | 2 |
| `95344` | `95504` | 1 |
| `f1df5e7f4e094021e96947c53a204b6fac32c12ef35caba76eae61f2bfcdc3cc` | `d1033e627420e0de5d8ca90ebdf79c284228a23448f3d3e99130651d5afc65cc` | 1 |
| `95360` | `95520` | 2 |
| `85b05c564fd3545c6b6e16fb64ed2aef8893226e32048309f1b71f97a5db4b6c` | `e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0` | 1 |
| `('previous', 537115952, 48)` | `('settle', 537121768, 28)` | 1 |
| `727152` | `727432` | 1 |

Require final11343 bytes and SHA256
577f2f17ae532db1e21644868b624d0d8a903771309a39b0b3488f8ae4f98cb0.
This is a source derivation rule, not a new runtime projection framework.
Every existing branch, condition, call, wait and lifecycle body remains intact
apart from the fixed identities, window tuple and byte accounting above.
No new native behavior is authorized. Do not globally rename app_motor_observe:
it remains the sketch name and firmware namespace.

SOURCE is117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da.
RUN_ID is app-motor-settle-117cc0e7-run01. PARENT remains
/home/arduino/sumox26_codex_build; DATA remains /home/arduino/.arduino15.
SKETCH is PARENT/SOURCE/app_motor_observe. BUILD is
PARENT/app-motor-settle-static01/build. Fixed exclusive outputs are
PARENT/RUN_ID-upload and PARENT/RUN_ID-capture. No alternate caller input.

D198 artifacts are9648 bytes SHA256
e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10 at
`state/analysis/P7_motor_settle_compile_raw/native_static01/artifacts.json`.

| Role | Bytes | SHA256 |
|---|---:|---|
| raw app_motor_observe.ino.bin | 95504 | d1033e627420e0de5d8ca90ebdf79c284228a23448f3d3e99130651d5afc65cc |
| sketch app_motor_observe.ino.bin-zsk.bin | 95520 | e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0 |
| installed loader ELF | 2303728 | 39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd |
| loader_image | 263680 | e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2 |

The compiled image stays static/default, MATCH0/MOTORS_ALLOWED0/probe1.
No sketch, HAL, config, grants,150us deadline or4096poll bound is changed.
Retain these three exact dependency roles and all validation/private loading:

| Role/source | Bytes | SHA256 |
|---|---:|---|
| upload: P7_static_startup_raw/upload_remote.py | 24710 | e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1 |
| capture: P7_static_startup_raw/capture_remote.py | 37525 | 95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e |
| helper: P7_static_link_probe_raw/static_remote.py | 33321 | 8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8 |

The paths in that table are beneath state/analysis/. Check all dependency
selection/type/hash guards before private execution. Keep selected_profile
binding and fresh private modules, no sys.modules registration or disk mutation.

## Public seams and fixed bindings

Keep existing signatures without extra native options:

```python
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

The factory returns AppMotorSettleCapture extending the unchanged support.Capture.
Retain profile_bindings, prepare_plan, check_image, pre_sample_pause, gather
and complete. Import remains definitions only, without dependency/file/device
access. No CLI, configurable delay, generic profile or target is introduced.

Binding schemas are fixed-app-motor-settle-upload-v1 and
fixed-app-motor-settle-capture-v1; report/attempt/analysis prefixes are
app-motor-settle. Preserve exact keys, string/integer/bool refusal rules,
boot UUID/UID1000 admission, every installed path/hash, capture config,
absence list and Python-B requirement. Upload is the unchanged static/default
arduino-cli upload of the fixed raw file to the app_motor_observe sketch.
The /tmp/remoteocd absence requirement remains mandatory; this adapter has no
cleanup, sudo, retry or process-control facility.

## Current observed windows and exact read plan

D199 ABI raw result is905572 bytes SHA256
230ef847f74e84d032a87336f74a4817d4cd8317a0ea5abc72c54fdd0d03eb6e;
abi.json is5410 bytes SHA256
069ed01bee9fba11159a4d93d156b8ada35ea5c11414b77870d80b6182d59941.
Their fixed paths are new COMPILED/native_abi_static01/result.json and abi.json,
where COMPILED is state/analysis/P7_motor_settle_compile_raw/.

| Name | Address decimal | Bytes | Current type |
|---|---:|---:|---|
| trace | 536951180 | 2128 | motor_fault::TraceReport |
| report | 537119696 | 1168 | app_motor_observe::Report |
| runtime | 537117984 | 600 | app::RuntimeReport |
| transaction | 537115448 | 504 | app::TransactionReport |
| settle | 537121768 | 28 | motors::SettleProbeReport |
| gate | 536953520 | 88 | motors::MotorGate |

Keep this precise order. Replace only the previous live48-byte window with
settle28; the final Runtime, Transaction and Gate remain. Report includes
before_abort.previous at537120816,48 bytes, offset1120 inside Report. The omitted
live previous at537115952 is post-abort state; it is not equivalent to that
retained pre-abort copy.

The separately observed report is LOCAL OBJECT DEFAULT section5,
_ZN6motors12_GLOBAL__N_119settle_probe_reportE at0x2003d3e8,size28/alignment4.
This remote adapter reads bytes and does not decode fields, reason, validity,
stage, epoch, terminal state or atomicity.

Loader brackets start0x08000000 and span263680 as five chunks
[65536,65536,65536,65536,1536]. Sketch brackets start0x08100000 and span95520
as two chunks[65536,29984]. Each SRAM sample spans4516 bytes, giving
2*(263680+95520+4516)=727432. Retain exactly26 reads/commands and12 SRAM files.

Read indices0..4 are before.loader;5..6 before.sketch;7..12 first windows;
13..18 second windows;19..20 after.sketch;21..25 after.loader. Preserve four
whole-reference comparisons at4,6,20,25 and every raw read/hash/file receipt.
Keep explicit coherence=UNPROVEN, even if the two samples repeat exactly.

## Unchanged waits, failure handling and limits

At index7, after successful initial flash comparisons and before first SRAM,
retain one pre_sample_pause request30. Require budget()>30, record real checked
before/after times in analysis.pre_sample_wait, require elapsed>=30, and
check budget again without resetting the600s origin. At index13 retain the
original pause request2 and report.wait. Do not sleep elsewhere or add reads.

Keep partial wait evidence, monotonic finite clock guards, insufficient/equal
budget refusal, short/throwing sleeper failure and final deadline handling.
No first SRAM read follows a failed pre-sample wait. Existing first_error wins
over later closing or clock failures. Complete requires both recorded waits,
four flash matches,12 snapshots and exact26/26/727432 counts. Inner/outer closure
still requires no first_error before COLLECTED. Neither wait proves progress,
FROZEN state, a particular epoch or timing acceptance.

Keep original descriptor/path/file/process checks, exclusive ownership,
durable intent, before/after pin checks, partial results and final close behavior.
Upload budget180s; capture600s; child min(30,budget()) with original reap and
1MiB streams. No dependency guard, command count, callback order or error policy
is relaxed by metadata retargeting.

## Independent host and later native evidence

Freeze an independent oracle before reading the new adapter. Reuse all42 D195
remote methods (26 inherited+16 additions) by explicit checked fixture metadata
projection, preserving every old assertion and first failure. Fixed old oracle:
tests/tooling/test_app_motor_observe_remote.py20956B SHA256
f45218ea3d9fb118adfe796c12fc5f4bab654c843cf33cc531e81d99a3f41fc6.
The new oracle path is tests/tooling/test_motor_settle_remote.py.

Cover the exact11-step/source identity, private dependency and profile/binding
checks, all six windows/twelve snapshots/26 reads/727432 bytes, new package span,
unchanged flash/wait positions, insufficient budget and all clock/sleeper/read/
closing failures, retained first errors/partial reads, and old previous tuple/
old package/source refusals. Exercise both public collect and the returned
capture class with injected clocks/sleepers/files/executors, no board or sleep.
Preserve historical tests, validate Windows/Linux serially and record first
results. Native code/use follows separate reviewed caller scope and admission.

The actual D199 entry semantic review is 15336 bytes SHA256
20f54afaf33dbfc17c08f0406c3a00c575cf237956044be0581db1737a7109b7. It supports file instruction interpretation only; the
candidate run's success, SETTLE reason, physical cause, liveRAM/WCET, coherence,
electrical acceptance, motor-capable permission and human gates remain unproved.
