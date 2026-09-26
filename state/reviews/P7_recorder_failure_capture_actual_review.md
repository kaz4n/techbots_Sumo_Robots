# D230 independent actual passive capture review

Reviewed2026-09-27. **PASS: identified passive diagnostic collection and
retrieved evidence accepted.** This is not recorder delivery success. The
snapshots observe a terminal dump/port failure and poisoned native owner;
the original native error remains unidentified. No material evidence blocker
was found. The reviewer performed local evidence reconciliation only, with
no tests, native command, upload, reset or source change.

Collector HEAD `269433775746eaf7038b0a9e3f237a0f67c3cd3e`; run
`recorder-377911abefabd094-failure-capture01`; original recorder attempt
`377911abefabd094971ee6d089326604`; source
`702ad99ee4f888c58de1715cb91512cb0a174a646d914db6ce9155489ffa63e8`.
Expected session3997245574426120340, serial2629958581 and boot
55c386b9-fe6d-4388-a7f4-1d91e0bb49d8 agree throughout. Local owner is
state/analysis/P7_recorder_failure_raw/native_capture01; remote owner is
/home/arduino/sumox26_codex_build/recorder-377911abefabd094-failure-capture01.

All171 retained input pins match current bytes, including the ADB executable;
the170 repository pins also match exact collector-HEAD Git blobs. The accepted
ABI remains de0cb0ecb558937a9ad251fd81168fe340bf2440aa9ebd3108a60d7758b89ee9.
Its mechanical spec SHA256 is
c6c668d8b5b2168fa4a1d08eea63391bb3913f6a6b24728fcce17c5a1f135bd0.
The240567B literal adapter is
54b816ad746dd94d2424a80917d2b6504638ccac689a1c9b8250d062e92f5fe4.
Both actual capability observations match that adapter and all109 hashes of
the original recorder's staged source manifest. The historical compile HEAD
and current collector HEAD remain distinct; no D229 p99 image is substituted.

The sequence completed with one capture and one retrieval,10 transports and
no first, postcheck, local, prerequisite, transport or finish errors. All10
actual command arrays/timeouts reconcile with the frozen input hashes; all
returned0 with empty transport stderr. Durable staging, capture and retrieval
intents and the expected dispatched sets agree. Maximum command length was
25708 UTF16 units. The44 retained Git checks succeeded, keeping the exact HEAD,
committed scope and clean tracked tree throughout; only this owned output was
allowed untracked. The external coordinator reported209.534s total.

The native report is COLLECTED with24 reads requesting638936B and a194.451s
collection interval. It comprises full263680B loader and55104B sketch reads,
six684B-total status ranges for each of two snapshots, then the full sketch
and loader again. The sample-separation receipt is2.000452s. All four full
flash comparisons passed in the reviewed native collector. Before/after
loader chunk hashes agree; both full sketch read hashes equal the compiled
package91b6042a3f13e3650fc4b23892f88e69d4c0c56edebd6514662fa2d8cd8208c6.
This adds actual image readback around SRAM observation. Full flash bytes and
per-read receipts remain in the durable remote owner; only status bytes and
the complete report were retrieved locally by this fixed workflow.

The retrieval packet has13 files and13 independent closing file checks, with
matching expected board identity before and after. Each packet file's decoded
bytes, size and SHA256 matches its saved local file. The durable report is
exactly the returned report; its hash matches the envelope. The reviewer
independently decoded all56 fields in each snapshot from the12 raw SRAM files
using the accepted ABI's offsets, widths and enum values. Both decoded maps
match the report and local export analysis. There are no decode errors and
all56 compared field values agree. Coherence remains **UNPROVEN**: these are
sequential, non-atomic reads despite their agreement.

Observed in both snapshots:

| Field group | Observation |
| --- | --- |
| Runner | phase FAILED; failure DUMP; setup completed; dump_setup OK |
| Progress | 202480 completed epochs; missed releases0; reset_done and service_only true |
| Session | 3997245574426120340, matching expected and transfer session |
| Transfer | phase FAILED; reason PORT; accounted bytes0, frames0, events0, CRC0 |
| Native owner | initialized and attempted true; active false; poisoned true; status POISONED; cleanup_verified false |
| Last transaction | FAULT/ABORTED; decision_made true; finished false; timing_valid false |
| Inert callback counters | enabled_en0, nonzero_pwm0, invalid_motor_calls0 |
| Retained completed-epoch timing | maximum_execution_us484; maximum_lateness_us2 |

The484us value covers the Runner's successfully completed Transaction S..C
population. The aborted final transaction has no valid completion duration.
Neither value is whole-loop WCET, p99, all-sensor performance or P2.2 acceptance.
The inert callbacks' zero nonzero-output counters are not physical motor evidence.

The transfer PORT status narrows the observed failure location but does not
identify the original native reason. In the exact source, fail(reason) calls
abort then restores a status, while abort/poison and later readiness checks can
publish POISONED; the current object retains no separate first-native-error
field. Therefore POISONED cannot distinguish TIMEOUT, REGISTER, OWNERSHIP or
another originating condition. cleanup_verified=false means cleanup was not
verified, not a recovered error code. Zero accounted transfer bytes also does
not prove no UART prefix was ever shifted. The earlier receive attempt's
TIMEOUT/zero observed wire remains distinct evidence; it cannot supply the
missing native reason.

Principal local SHA256 pins:

- inputs.json19490B: `33ed4c6435af4d4faa38b2a7eac16a9fffaf846e86f15b323a914d3fdd65a8c2`.
- result.json73836B: `5b80a3f7ea4e75da8aa3fa681ca50a51b5310d3a95b2fa5156ff2441dcf41bdc`.
- final_checks.json54465B: `413bfb3bdf031c88bc4632e3e1e273e95dbd1263cdff070084b19e5f4d99f8b4`.
- capture_envelope.json11325B: `ae57c6b0f99c9f49ac8f7b6349e54767bd1f5b24c80d5b0b9a6f5652b994d9ec`.
- capture_result.json10816B: `cbc438bec73e907649c5086db61fc7bc1da2b4b5d328aefb0b23f76925d93142`.
- export.json7865B: `c2073ba00130944fa086000130cddf4abda5f54a2a244ca95d050c255fe9b54f`.

Accept this consumed diagnostic attempt and preserve its raw evidence. A narrow
future diagnostic change can retain the first native failure without changing
the UART safety/ownership/cleanup rules; this review does not approve such
source edits or another native run. No delivery retry, upload, reset, grant/pin
change, motor permission, physical qualification or phase pass follows.
