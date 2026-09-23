# D111 IMU heading bench validation

IMPLEMENTED / HOST-TESTED / TARGET-COMPILED / REVIEW-PASS, no open scoped
findings. Final reviewer JSON SHA594c80228c8a1c5fd5cf666a44910f8165d7643e2e00d0ae88a92071ac0b2e75.
Physical P2 B3 acceptance and gates remain pending. No new MCU upload, reset or run occurred.

Contract/config/interfaces were adopted in9299192 after independent public API
and source preflight; literal checked build route2428071. D051/D075 permit this
software scope. Mounting, supply, bus ownership and stillness remain unverified;
checked-in grants are false. No existing core/HAL behavior, pin, locked test or
upload manifest changed. The five new registry defaults were exact additions.

The finite bench owns one native Acquirer and reuses the actual pure Estimator
and countdown Services. D111 explicitly permits its bench-only calibration timer
anchor. After accepted calibration it retains61 immutable actual checkpoints
for one60-second source-time trial. It preserves actual failed native/pure
reports separately from successful publication. It neither duplicates integration
nor claims to know whether a human physically turned360degrees.

## Source and host evidence

Worker first source freeze stayed unchanged: main6d3c6c5f, Native740054b0,
Runnerheaderbd63d529, sketch35829619. Full hashes/source bytes and seven passing
strict syntax profiles are in raw/worker;45 functions, maximum34lines.
Independent test author used public contracts/headers without body reads and
copied actual Runner/Estimator/Services opaquely. The author and reviewer reused
separate same-model contexts; this is not cross-model or human phase review.

The original complete run passed first execution:28 executable profiles,
61 compile/run commands, normal and ASan/UBSan each31cases/1,342,660assertions;
15 invalid configs, actual Estimator invalid config, short calibration, five-poll
limit, short valid trial and valid threshold profiles all passed. Three unsafe
MATCH/MOTORS flag compiles refused as required. Six registry profiles executed
all18 unchanged legacy checks (108 total); five deliberately wrong new values
failed their corresponding original assertion. Runtime stderr was empty.

Original tests a9e9fce1 and harnessbcc2b6da were frozen before execution. After
PASS, author and reviewer identified one startup assertion gap and approved one
new unlocked Native case. The exact insertion restores all original bytes when
removed; final casesffc0a596, unchanged harness. Affected Native normal/sanitizer
selections each passed3cases/38assertions, including passive global/local object
construction and10000 default loop calls. The addition is conditional on the
Native test profile, so unchanged main/config paths were not rerun unnecessarily.
Original runs/freeze, additive diff and targeted results are preserved in
raw/author/validation.md, run1_summary.json and startup_summary.json.

Coordinator policy fixtures were frozen before controlled red execution
(7tests:4failures/2errors because the route did not yet exist). Four literal
allowlist/map additions then passed121 methods,7new+114prior. Reviewer independently
passed all121 and confirmed prior policy test files/upload manifest unchanged.
These are script tests, not board builds. No normal product/behavior failure or
production fix was required. Root verified all original profile statuses,
expected refusals, exact additive oracle proof and targeted results.

## Exact target evidence

Checked source9520e47316b6edb7405bd5182f498453c4860f79fdd197a03ff34c14c7b69c05,
96files, compiled on board Linux in both profiles. Default receipt
20aecaa3aa124f75b870bc53ee372766; Immediate0a1f2fac4a514003b7695f5a59fabbab.
Both finalELFs SHA e55565ff4afeff9f61701ac789501f84ae3f39744adfa42680bb34dc0d68ba9b,
35,976bytes. Three ELF forms/package per profile and all source bytes are retained.
Collector P2_imu_heading_bench_target_collect.py verifies installed artifact pins,
exact staged tree and offline command statuses; root_target_verification.json
independently rehashes every byte and the Windows-order aggregate source identity.

Reviewer reconstructed actual native ownership, passive startup, disabled grants,
empty thread bounds and lack of unrelated owner/transport/allocator relocation.
Native516bytes; Runner10,784;61x164 checkpoint bytes10,004. Ordered conditional
loader model: payload26,833; peak28,224; free span233,920/largest233,916 in262,144.
This is not actual loading/freeRAM or timing evidence. See raw/reviewer exact
target JSONs/startup witnesses and reviews/P2_imu_heading_bench_review.md.

## Retained corrections and limits

Initial tooling red is preserved. Administrative verification corrections also
remain: adoption's guessed native-header filename; LF/CRLF checkpoint anchor;
reviewer literal/path/old-oracle-baseline inputs; root's extra newline assumption
when removing the declared additive test insertion. These altered verification
inputs only, with original errors/corrections recorded; no failing production
assertion, weakened oracle or hidden fixture repair occurred.

Natural timestamp wrap, real software60s/61point streams and public limits were
executed. Unreachable billions-of-calls saturation, sequence1-to-wrap, numeric
overflow and second-unfilled-checkpoint defenses are source-reviewed explicitly,
not privately seeded or reported as executed. Native substitutes establish
forwarding/default passivity, not silicon protocol or sensor generations.

The last actual MCU image remains frozen D1042bd817c4. Default-false bench
compilation does not prove IMU drift, hand-rotation accuracy, native cadence,
readout, oscillator calibration, physical wiring, full-app800us, loaded memory
or a human gate. D112 A1 bench remains a separate draft; native dump feasibility
is in P2_native_dump_bare_feasibility.md with clean framing still unverified.
