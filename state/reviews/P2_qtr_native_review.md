# D085 independent QTR review

Review started 2026-09-23 Asia/Dubai against baseline `4ada2cd`. This is a separate
reviewer from the implementation and independently authored tests. Scope is the
actual native Reader, raw-record adapter, explicit Robot admission and retained
line behavior, plus inert target retention and unchanged safety assertions.
Only this report and `P2_qtr_native_raw/` are reviewer-owned. No board action.

## Final result

**PASS within the D085 software scope; no open BLOCKER, MAJOR or MINOR finding.**
Completed 2026-09-23 at 14:30:14 Asia/Dubai against contract commit `dcd4682` and
implementation/test commit `47f4d9a207534af8b23ae116ffd89d9c6981e302`. Normal and
sanitizer regressions, actual native-source controlled tests, complete native to
adapter to Robot tests, staged-core compilation, installed-source fixture audit,
and offline actual-target source/ELF/import/startup review passed. The exact five
existing inert identity replacements are approved and their adoption is verified.
This is neither physical acceptance nor a phase gate.

The final isolated test snapshot contained 364 files and remained unchanged
throughout the run. A subsequent check found all 329 reviewed source/test/host/
bench files still byte-identical. See `P2_qtr_native_raw/final_evidence_audit.json`.
The reviewer modified only this report and its raw evidence directory.

## Findings during implementation review

- **MAJOR, fixed and independently reproduced/retested:** retained white at GO
  did not establish Escape's initial mask baseline. The next same-white fresh
  frame consumed a replan. `src/core/edge.cpp:400` now records the entry mask even
  when entry uses retained evidence. Reviewer-only regression across six allowed
  masks failed 12 of 36 assertions before the fix, then passed all 36. Receipts:
  `retained_entry_boundary.json` and `retained_entry_fixed.json`. The earlier
  `retained_entry_initial.json` preserves a reviewer harness compile error; it is
  not a production execution result.
- **MAJOR, source finding fixed and independently tested:** final setup/start/
  sample ownership checks followed the last call timestamp, excluding their
  readiness/MMIO work from the call budget. The native owner now completes the
  final guard before its terminal `checkTime(clockUs())` in
  `src/hal/line_qtr.cpp:248`, `:288` and `:347`. Native guard-cost boundary tests
  at `tests/native_qtr/boundaries.cc:55` pass; the actual target setupBank
  relocation sequence also resolves to bankOwned, micros, then checkTime.
- **MAJOR, source admission gap fixed and independently tested:** excluded
  pin proposals with arbitrary otherwise-valid GPIO device metadata were treated
  as distinct without a known physical binding. `src/hal/line_qtr.cpp:49`
  now accepts only exact named GPIOA/B/C devices before comparing pad identities.
  The otherwise-valid foreign-device variant and all overlap variants pass.
- **MAJOR, source finding fixed and independently tested:** expiration during
  BOOT could preserve partial confirmation into a later distinct frame when
  QTR_CONFIRM_TICKS exceeds one. `src/core/fsm_line.cpp:69` clears classifier,
  previous-mask and QTR-stuck age state whenever the prior accepted interval has
  expired, including when a new valid frame arrives that tick. Identity ordering
  remains retained. The reviewer count-two variant passed 2 cases/43 assertions;
  the author's count-three test also passed independently. The receipt named
  `boot_confirmation_initial.json` already uses the fix and is not a claimed
  pre-fix reproduction.
- **MINOR, source finding fixed and independently tested:** a missing/expired
  line could continue QTR_STUCK aging for the prior applied-pivot tick.
  `src/core/fsm_robot.cpp:711` now requires available line evidence to qualify.

Two pre-freeze contract questions were resolved explicitly and verified in the
final contract/code/tests: countdown warning admission requires both source start
and decision inside the original window; a newly delivered black frame on the
DONE tick can exit, but a previously retained black frame cannot. Pending timing
fields are diagnostic only: structurally valid pending snapshots map to ABSENT
and never renew source age. Full interval qualification applies to COMPLETE.

## Independent execution evidence

All paths in this section are under `P2_qtr_native_raw/` unless stated otherwise.
Commands ran from isolated Linux snapshots, without transport or board access.

| Check | Independently observed result | Receipt |
| --- | --- | --- |
| Full normal host | 1173 cases / 22,840,417 assertions; enabled MotorGate 37 / 3,796,846; CTest 2/2, 6.51 s | `full_review_final2/normal_run.txt` |
| Full ASan + UBSan host | Same counts, CTest 2/2, 27.72 s, no sanitizer diagnostic | `full_review_final2/sanitized_run.txt` |
| Native tooling | 11 methods passed in 53.617 s | `full_review_final2/test_qtr_native.txt` |
| Adapter/controller focused normal and sanitizer | Each 22 cases / 26,881 assertions | Same native tooling receipt |
| Native lifecycle | 14 cases / 834 parent assertions + 1098 successful child assertions | Same native tooling receipt |
| Native faults/deadlines | 10 cases / 918 parent assertions + 25,637 successful child assertions | Same native tooling receipt |
| Actual native → adapter → Robot | 3 cases / 108 parent assertions + 497 successful child assertions | Same native tooling receipt |
| Invalid setup inputs | 11 config variants and 22 metadata variants; each 1 case / 4 assertions | Same native tooling receipt |
| Probe inertness | Two macro modes; each 1 case / 19 assertions, setup plus 10,000 loops | Same native tooling receipt |
| Config defaults | 16 Python tests passed | `full_review_final2/test_p0_config.txt` |
| Staged core/public includes | 2 tests passed using fake transport; every staged core source compiled | `staging_receipt.json`, `staging_stderr.txt` |

Native tests compile the actual production line_qtr.cpp, not a parallel reader
implementation. The pipeline covers all 16 optical masks, a second successful
native frame at the minimum start period, 1 kHz opponent progress between line
frames, a real modeled 600 us observation gap producing AMBIGUOUS/LINE_CONTRACT,
and guarded allocation checks across three acquisitions plus 10,000 replays.
Eight probe upload combinations reject before transport lookup. Confirmation
three is tested using only an isolated config variant; the production value is
unchanged. Generation wrap uses a disclosed test-only seed after an ordinary
frame, not billions of observed acquisitions.

The process isolation listener propagates assertion failures and signals to its
parent. Exactly two intentional sentinel commands return 1 with FAILURE; all
other native command receipts return 0. These are expected test successes, not
ignored failures. `final_evidence_audit.json` indexes and hashes every command
receipt and identifies both sentinels. Successful child assertions are reported
separately from doctest parent counts.

The fixture source audit independently matches 3431 installed macro definitions,
four register layouts and eight selected LL getter bodies against saved installed
headers. `fixture_source_audit.json` binds both fixture and installed inputs by
hash. The controlled Zephyr declarations model the used API subset and preserve
the installed Arduino bit macro; they do not claim full Zephyr ABI equivalence.

`scope_audit.json` confirms 190 baseline tests/app/board-tool files unchanged
after CRLF normalization and all 147 original config declarations unchanged.
The only altered original nonlocked test is the config declaration allowlist:
its existing predicates remain and its new D085 method checks all additive values
and the unchanged proposed pin array. Every locked assertion remains untouched.

## Actual target and exact inert identities

The root's compile-only receipt is
`state/analysis/P2_qtr_native_raw/target_57f4b001_bench-default.json`.
The reviewer independently reconstructs all 56 staged source hashes and the
aggregate `57f4b00192c4b4aaf87c70c60244e9f392abf54908a22e3ded7d215499b1165c`.
Compiler result is exit 0, 145,012 program bytes and 71,092 compiler-reported
global bytes. This is not a free-RAM or loader measurement.

| Artifact | SHA-256 |
| --- | --- |
| Upload ELF, 145,012 bytes | `4529736c7a4ef135ae971434167ec6c2150d7e9e25bcd619fbd5d6ff1382509c` |
| Debug ELF, 4,348,188 bytes | `335d035a19f9d48cbb6542a9c84ad28226b288d719eba81ceb2bdfba2608008d` |
| Temporary ELF, 4,364,040 bytes | `e840763153a48d4c17357c513c3e711cbe836ae8841fc28e74bec60612efe00f` |
| Cached installed base ELF | `39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd` |

`identity_audit.json`, `target_binding_audit.json` and `target_disassembly.txt`
record the evidence. The final native source hash is
`ba6e5a3a2ca02049117f2a8f47896ea43989f2f15cafc37b5bdbcae4d90b10aa`.
The adapter, freshness core, probe and all other staged sources are individually
bound by the same target/source manifest and independent test snapshot.

All 36 native imports and 42 AEABI export addresses were checked against the
cached base. Referenced AEABI wrappers have the expected relocated bindings;
fmod and sqrt are separately checked against their base Thumb addresses and
actual ABS32 literals. GPIOA/B/C device identities are positive bindings to
ordinals 89/90/91. Native GPIO calls use the checked device API path; no undefined
z_impl_gpio_ call is attributed to a usable null export.

Fourteen required Reader/adapter/Robot/classifier/Escape/countdown/probe methods
are retained in the actual ELF. setup stores the exercise function address and
returns; loop immediately returns. The never-called exercise contains the real
Reader snapshot → adapter → two Robot calls → frame codec path. Its exclusive
grant is false and its motor receipt is a disabled memory object. The two new
translation-unit initializers have no calls and only inherited HCI/Bridge memory
initialization. Existing wider Bridge/loader startup remains an open runtime
question; this review does not generalize the inert sketch result to all runtime
paths.

The reviewer approved only the five existing keys below. `inert_approval.json`
contains the machine-readable approval; `final_evidence_audit.json` confirms that
the live registry equals this exact map, with no additional key.

| Existing key | Approved source identity |
| --- | --- |
| bench/p0_adc | `71380910b3f359a708d18f33a84a582bd066160c63fc269bf9aab5d97b78c7fe` |
| bench/p0_gpio | `b5ec44dab6dd9073f4a5aaacb77ab1b5079a189a3454af8dd6699217ce1cf179` |
| bench/p0_matrix | `ddfd99ceb8a289e391b0ef86336936d00e1ff3f4eb88be7f78daf59dd2e630b0` |
| bench/p0_qtr | `96284da5af8eee83e6c36997e95682cc38d27fc9ae47fba21e990eae76721329` |
| bench/p0_timing | `4379a8b4be23cfb0dc0c689b70b58922461718fbca75412122ba639c8f9fc971` |

## Preserved failures and corrections

`full_review_1/` preserves the first full-host compile failure from a missing
initializer_list include in the new tests. `full_review_final/` preserves the
subsequent unsupported REQUIRE sites under the established no-exceptions host
mode. The author added the include and replaced only five new REQUIRE sites with
identical CHECK predicates and safe early returns; no assertion was removed.
The final focused and complete suites use the established no-exceptions mode.
The root's first actual target failure preserves the Arduino bit macro collision;
the production helper is now padBit and the fixture includes that real macro.
Earlier reviewer harness errors, pre-fix retained-entry failure, and author
fixture/test development failures remain separately recorded. An early pass is
not attributed to the final source without the final rerun.

The root's two additional Windows invocations of the unchanged tooling suite
failed on untranslated C: shell paths (exit 127) and Windows symlink privilege
(WinError 1314). Those are invocation failures, not an inert-manifest regression;
the root explicitly corrected that initial diagnosis. The separate missing
approval-file adoption failure was real and was resolved by the reviewer's
five-key receipt. The reviewer inspected the root's final unchanged Linux run:
`state/analysis/P2_qtr_native_raw/tooling_linux_final.json` and `.txt` report all
25 methods passed in 18.899 s, exit 0. Disposition: corrected environment-only
failure, no open software finding and no relaxed test or privilege requirement.
This root run is additional evidence, distinct from the reviewer's own isolated
native/config/staging runs above. Earlier failed receipts remain preserved.

## Limits retained

No GPIO/MCU execution, upload, reset, motor action, sensor/pad/debug handoff,
physical color separation, optical capture latency, ring stopping distance,
whole-image WCET, SC-AJ/F091 closure, human hardware acceptance or phase gate is
proved by this software review. The 2000 us start period, 2500 us frame cap and
6000 us age limit are development policies. App scheduling remains separate.

Observed GPIO configuration consistency cannot prove exclusive physical control.
Unknown device identities, uncertain overlap and failed ownership guards inhibit
the source; the explicit ownership grant still requires a real future handoff.
The future scheduler must resolve the serialized 600 us IMU + 150 us motor settle
+ 100 us ADC maxima before claiming the 800 us tick budget. No hardware run was
performed by this reviewer. Next action: record this software result in the root
handoff and continue only the separately authorized P2 work; physical checks and
human phase acceptance remain pending.
