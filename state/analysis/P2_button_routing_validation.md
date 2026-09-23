# D087 button decoder and gesture routing validation

2026-09-23 Asia/Dubai. Contract6c01bb4; implementationb69fa12. Status:
IMPLEMENTED / HOST-TESTED / TARGET-COMPILED. Separate reviewer final disposition
is PASS with no open finding, recorded in state/reviews/P2_button_routing_review.md. All physical and human
phase gates remain pending; no software checkpoint passes a phase.

## Actual change

A1 ButtonSample enters the real raw-window decoder and thin adapter, then one
Robot admission owner validates source identity/time/continuity and routes fresh
observations to START, STOP and MODE/menu services. Missing/replayed data cannot
manufacture a release or advance a gesture; Gate/services still advance at decision
time. Earliest-source age and bounded gaps expire into reset-only inhibition.
Fresh neutral qualification prevents boot-held START from becoming a release.
All full hold anchors remain actual qualifying decision ticks. Legacy APIs/tests
are preserved. Unconfigured production windows intentionally inhibit rather than
claim a unique START/BOTH voltage. D087 is a software contract, not calibration.

B15 detail11 retains LINE_CONTRACT256/BUTTON_CONTRACT512 and combined known masks
through real Robot/recorder/CSV paths. Original detail7 still rejects256;8-byte
records, existing numeric codes and21-event capacity are unchanged.

## Validation actually run

| Check | Result | Direct evidence |
|---|---|---|
| Full normal host |2/2PASS20.51s;1209main cases22954190assertions;38enabledMotorGate3843482assertions |raw/host_final_build.json/.txt,host_final_tests.txt |
| Full ASan/UBSan host |2/2PASS28.73s, same cases/assertions |raw/sanitizer_final_build.json;sanitizer_final.json/.txt |
| Independent author spec cases |36D087cases113773assertions plus enabledGate1case46636assertions PASS |raw/author/HANDOFF.md,focused receipts |
| Separate reviewer focused normal and sanitizer |each36D087cases113773 +1enabledGate46636 PASS |reviews/P2_button_routing_raw/final_focused_v2/receipt.json |
| Independent decoder/probe/CSV tooling |8methodsPASS51.571s; reviewer8PASS42.347s |raw/author/tooling_*;reviews/P2_button_routing_raw/final_tooling |
| Config inventory |18methodsPASS; additive exact D087 constants only |raw/config_initial.json/.txt |
| Existing scripts after LF repair |25methodsPASS18.392s |raw/tooling_repaired.json/.txt |
| Staged core/include layout |2methodsPASS3.632s |raw/staging_initial.json/.txt |
| Actual board-side compile-only |exit0;142288program/69864compiler globals |raw/target_final.json/.txt |
| Exact final source/ELF identity |59sources/3ELFs;36native/42AEABI and fmod/sqrt bindings;59Git index blobs exactly match compiled bytes |raw/target_557e0e5f_bench-default.json,root_target_integrity.json,final_source_index_identity.json |
| Existing inert registry |exact5keys independently approved/reproduced/adopted, no newkey |review inert_approval_final.json;raw/manifest_adoption_final.json and *_command.json |

The scoped Python method count is53 distinct methods (8new+18config+25tools+2staging),
not an all-tooling-suite claim. Four synthetic profiles each enumerate0..16383,
plus six malformed profiles; no window is physical data. Two probe macro variants
execute startup and10000loops with no counted I/O/allocation. Eight mocked upload
combinations refuse before transport. Real default and host-enabled MotorGate
callbacks traverse the complete5100ms hold; invalid/expired input and actual
unconfigured decode then force EN-low/fourPWM-zero writes with genuine receipts.
These are host port callbacks, not motor or electrical measurements.

Final source SHA256:
557e0e5fe1c30aeda84d4f1aa6171f3aa56e5a67d5df00fcf51173c8c894bf60.
The source map and offline ELF inspections came from board Linux files only.
The installed base's inherited Bridge loop hook/static threads remain explicitly
unqualified (F091). Probe setup retains an address; loop is empty; retained exercise
is not called. Compiler-reported globals are not measured free RAM or loader proof.

## Preserved failures and review independence

See P2_button_routing_failures.md and raw receipts. Early draft fixtures lacked
direct standard includes or expected the wrong documented MotorGate STOP status;
all were corrected before final strict/full runs. Source behavior was not changed
to satisfy them. Existing LF-checkout tests caught root's CRLF header comment edit;
only line endings were corrected, target rebuilt and exact hashes reapproved.
Initial a4a4b803 target/math/identity/approval remains preserved separately.
No existing locked/behavioral assertion changed. The sole established test change
adds exact new D087 declarations to the config inventory and one extra check.

Fresh reviewer spawning hit the thread limit. The completed D086 reviewer context
was reused, separate from implementation and independent test authoring, on the
same model. This is not newly fresh-context or cross-model review, and cannot
stand in for a human phase approval. Final report records its precise disposition.

## Remaining and next action

HARDWARE-PENDING: physical windows and START/BOTH circuit decision SC-A, cadence,
ADC accuracy/settling, SC-AJ/F091, full-tick800us, pin/electrical acceptance and all
human gates. No upload, MCU reset/read, sensor/pad operation or motor run occurred.
Actual full application scheduling and service consumers remain unfinished.
Next actual B6 task is fixed104-byte rendering plus a source-verified bounded
matrix adapter; follow raw/next_ui_task.md. Full P0-P7 objective remains active.
