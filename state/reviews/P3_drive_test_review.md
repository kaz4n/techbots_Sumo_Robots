# D123 P3 DRIVE_TEST scoped software review

Date: 2026-09-24. Reviewer: separate **same-model, fresh-context** review agent,
independent of the implementation and public test author. This is a scoped
software/source/compile-evidence review, not a human phase-gate approval.

Scope: implementation diff from `1672de8b`, the adopted
`state/analysis/P3_drive_test_contract.md`, public interfaces, relevant actual
Runtime/Transaction/MotorGate paths, frozen independent tests, tooling, native
wrapper, and retained host/target receipts. Read AGENTS.md and relevant P3,
B1/B2/B3/B4/B5/B6/B8/B13/B15 and D089/D095/D103 contracts. The date remains before
the 28 September scope-cut deadline and 1 October freeze; neither deadline nor
any human acceptance requirement is changed by this review.

The reviewer changed only this report and `P3_drive_test_review_raw/` evidence.
Private compiler/runtime probes used an isolated host fixture. No reviewer
board connection, upload, reset, MCU operation, motor operation, production
edit, or public-oracle edit occurred.

## Findings

No open BLOCKER, MAJOR or MINOR finding in the reviewed D123 software slice.

The first public run exposed one incorrect assertion in the newly authored,
unaccepted draft oracle. Its original hash was
`bed2418c6dd7bc2f2840694e0cbd0f7daa6969b0fd90e4e4c88a10ecd2d86aa3`.
It expected the preceding Robot token inside a new current report after
`Transaction::open()` and rejection of a duplicate decision clock. D095 clears
the current report on open and preserves the separate previous receipt.
Existing unchanged D095 tests independently establish that behavior.

The independent author corrected the assertion to current `robot.token == 0`
**and** retained `previous().token == before.token`, preserving CLOCK,
no-decision and actual-zero-output checks. The reviewer independently concurred
from the public contract and established tests. The amended, re-frozen hash is
`5bde79679c8af6a362686acf205ac2401837b49da88eac1eec7cfd82a77fea0f`.
Production did not change to satisfy this assertion. Original oracle, failing
run and disposition remain in
[P3_drive_test_oracle_disposition.md](../analysis/P3_drive_test_oracle_disposition.md)
and `../analysis/P3_drive_test_raw/`. This disposition grants no authority to
change an established locked test.

## Safety and behavior trace

- Local admission: profile1 admits only initialized, fault-free IDLE with the
  actual service menu at DRIVE_TEST and classified-line readiness. Existing
  button source admission, neutral qualification, press/release debounce and
  boot-held rejection remain active. Other services and all six match selections
  consume releases without starting. Menu intent itself conveys no authority.
- R1: the original Lifecycle gate anchors the full 5,100,000 us after qualified
  release. MODE cancellation wins at the deadline. MotorGate independently
  checks matching release, armed hold, READY permission, token, output validity,
  faults and actual port receipts before allowing any energized output.
- Motion: `routeDriveTest()` is a bounded route to actual B8 Search after the
  existing edge evaluation. It cannot enter an opener, TRACK, ATTACK, DEFEND or
  REFLANK; stall execution is excluded. Real Fusion observations and final
  commitments remain, but contact cannot latch outside ATTACK. ALL_IN and
  CONTACT/STALL/REFLANK events acquire no new route.
- Search: only its interruption mask becomes zero. Real opponent masks,
  bearing history, memory, stuck detection and edge pushed-out context remain.
  Directed full scans, memory turns, latched timed fallback, inward heading and
  alternating advance cycles use the existing helper.
- R5/R6: edge at GO and during motion wins; persistent white, three/all-white
  patterns and bounded replan faults retain inhibition. Successful escape exit
  brakes on that observation; a later distinct eligible observation starts
  fresh Search. Final forward SEARCH remains capped at 0.30 after voltage
  compensation; pivots and edge escape retain their existing approved caps.
- Actual authority: energized DRIVE_TEST is accepted only in profile1's final
  moving classification and MotorGate validation. Profile0 still rejects it.
  Independent full-duty centered-contact checks remain. Only MotorGate owns
  motor enable/PWM transactions; no new direct motor-I/O path was introduced.
- D103: a post-STOP service-only Runtime keeps RAW/absent line projection,
  line-start inhibition and the permanently STOPPED MotorGate. Selecting
  DRIVE_TEST cannot rearm it. The action remains UNAVAILABLE and the explicit
  display flag retains D+cross.
- UI/evidence: profile1 displays D without the unavailable cross for available
  selection/active drive, preserves explicit unavailable and fault/battery
  overlays, and retains profile0 presentation. Duplicate suppression and real
  receipt-based FIRST_NONZERO recording remain. Existing frame state identifies
  DRIVE_TEST; running_mode remains metadata, not evidence of an opener.
- R2/R3/R4: the wrapper uses actual NativeSources, UnoQPort and Runtime with
  empty SetupGrants. The checked route is default-startup, exact compiler-wide
  C/C++ `MATCH=0`, `MOTORS_ALLOWED=0`, `SUMOX_P3_DRIVE_TEST=1`, compile-only.
  Invalid upload/match/startup paths reject before transport. No remote motion
  input, new Bridge dependency, blocking call, heap allocation, clock access in
  core or unbounded loop was introduced by this slice.

Traversing SENSOR_VIEW -> QTR_CAL -> DRIVE_TEST briefly invokes the existing
RAW-to-CONTROL line handover. A fresh classified frame and full neutral rearm are
still required before a new START. The reviewer's first Runtime fixture pressed
START too early, and it was correctly consumed without replay. A corrected
fixture provides the real neutral interval; a separate retained test verifies
both early suppression and subsequent genuine release. D089 was not relaxed.

## Validation inspected and independently extended

| Evidence | Result |
|---|---|
| Initial normal full build/run | Four established targets PASS; each new target 26/27 before the documented draft-oracle correction |
| Amended focused normal profile tests | M0 27/27, 248,475 assertions; M1 27/27, 231,229 assertions; no skips |
| Full ASan/UBSan run | All six targets PASS, 0 skips; retained CTest duration 129.84 s |
| Configured ADC-window overlay, normal and ASan/UBSan | Each profile 28/28 including actual D103 service-only case; M0 289,681 and M1 272,435 assertions |
| Tooling tests | 93 PASS: 14 new plus 79 established; original launcher/import diagnostics retained |
| Reviewer config/policy probes | 20 PASS: 11 config-only compiler combinations and 9 synthetic checked-policy cases |
| Reviewer actual Runtime source-port extension | Four cases per M0/M1, 79,829/79,074 assertions PASS |
| Independent evidence bindings | 101 current frozen files match; all 35 established locked worktree files retain pre-task hashes; Git contents also match after existing CRLF normalization |

The private Runtime extension covers real typed acquisition callbacks and local
ADC/menu/full-hold routing, all-opponent no-combat observations, actual source
fault inhibition, empty grants, and the line handover/start boundary. These are
host callbacks, not physical measurements. Two earlier private harness compile
errors (missing fixture include and doctest expression parentheses) and the
too-early START fixture failure are retained, with no production repair.

Primary receipts are in `../analysis/P3_drive_test_raw/`: `normal.json`,
`normal_amended.json`, `sanitize.json`, `configured.json`,
`configured_sanitize.json`, corresponding logs and collected LastTest logs.
Reviewer scripts, failures, final runtime logs, private probes and
`evidence_bindings.json` are in [P3_drive_test_review_raw/](P3_drive_test_review_raw/).
An initial direct Git/worktree byte comparison also remains there: 19 native
fixture files have preexisting CRLF/LF representation differences, while their
worktree bytes remain exactly equal to the pre-task manifest.

## Target evidence and limits

Both actual checked compiler JSON receipts revalidate offline under the final
policy. Collected ELF hashes independently match the checked receipt and loader
account. Source manifests are tied to the frozen reviewed source.

| Candidate | Source / ELF prefix | Conditional pristine loader peak / free span |
|---|---|---|
| P3 drive, default/M0 | `cc1ef324` / `bf530d15` | 251,520 / 10,624 bytes |
| Default app, M0 | `090e2182` / `21b28ee3` | 262,128 / 16 bytes |

The P3 ELF contains the DRIVE_TEST route and excludes ordinary-route/opener/stall
symbols from the collected symbol check. Its native loop hook remains the
reviewed strong inert hook. The default app ELF is 176,040 bytes, eight bytes
smaller than D120; ELF and ZSK are **not** byte-identical to D120, while the pinned
loader firmware identity is unchanged. Profile0 source changes reduce to the
same behavior: the new menu getter is a pure copied selection and the reordered
start predicate is equivalent. This review does not attribute the exact binary
size delta to a particular compiler optimization without disassembly.

The model numbers are conditional source-model accounting, not an actual load,
measured free heap, largest live allocation, stack result or full-tick WCET.
Especially the default app's 16-byte modeled span cannot establish live margin.
No D118 live observation is transferred to this changed default ELF.

D122 authorizes continued software scheduling under an assumed physical
prerequisite. It does not establish electrical acceptance, source grants,
PINMAP/EXPLAINED evidence, STAND OK/RING OK, or a human GATE PASS. This profile
prepares the software used by P3 3.1/3.5/3.6/3.7; their physical trials remain
unmeasured. P3 3.2 ring room measurement, 3.3 higher-duty stopping-table trials,
and 3.4 isolated 90/180-degree turn trials remain separate unfinished work.
No timing spread, 24/24 edge survival, brown-line reliability, solo-ring result,
powered qualification or on-robot 800 us WCET is claimed.

## Verdict

**PASS — scoped D123 software/source/host/compile-only review.** No open software
finding remains in this slice. This is not full P3 acceptance, permission to run
motors, or a human phase gate.
