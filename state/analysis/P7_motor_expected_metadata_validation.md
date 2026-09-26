# D202 compile-time motor metadata: host validation

The corrected independent oracle passes all seven methods, including all 45
numeric configurations across four variants and all 21 four-way diagnostic
transcripts. Locked regression tests also pass. Separate independent review
f7b8a116 PASS has no open material finding. No new target build or firmware
upload has occurred.

## Change and preserved behavior

The production edit moves immutable timer-rate and period arithmetic into
mandatory constant expressions. Existing runtime helper names select three
automatic scalar results; invalid timer indices still return zero. Original
calculation bodies and all bytes outside their region are unchanged. No live
rate, readiness, ownership, GPIO or timer-register observation is cached.
The SETTLE body, 150us/4096 limits, call order, configuration, pins and grants
remain unchanged.

Production19906B/fdbc27d972a59a9c955b67b88072a03df3b90a4629e22fd7833ff5f09e0c8f8b
was committed37139e83. The independent oracle was frozen before its author or
the separate reviewer inspected that implementation. The initial coordinator
closure bound148 files; revised closure binds154. All first-run closing checks
passed. Contract: [D202 scope](P7_motor_expected_metadata_contract.md).

## Preserved first executions

- Independent oracle:7 methods,6 passed,1 fixture compile failure. All21 complete
  native/clock/state transcripts matched across predecessor/current and probe0/1
  (84 executions). The first36 numeric configurations passed four ways. The
  explicit carrier-zero row stopped while compiling the pinned predecessor.
  Other passing checks cover exact source boundaries, forced constexpr
  selection, diagnostic storage/exclusion, inert guards and protected inputs.
- Unchanged locked motor suites:76 cases and217020 assertions passed, no skips,
  across disabled and host-only enabled variants. These do not energize hardware.
- Unchanged D197 oracle:4 methods passed and1 failed. Its exact SETTLE body,
  all21 three-way transcripts, report cases, public inert guards and protected
  fixtures passed. Complete symbol equality failed; it remains a recorded FAIL.

The zero-carrier projection makes GCC diagnose the predecessor's unreachable
`rate / carrier` after its earlier zero-carrier return. This is not a production
regression; the real carrier remains10000. Independent author/reviewer agreed
to admit only that explicit fixture's warning with `-Wno-error=div-by-zero`,
identically in all four variants. The test requires exactly the visible warning
and its complete saved diagnostic, and retains all numeric/zero-return/Port
assertions, UBSan and every other `-Werror` condition. No warning is suppressed.
Original source/oracle/freeze and first failure remain in2b7449b2/4d7b92a9.
The bounded fixture correction is239fc472; production is unchanged.

## Explicit historical symbol adjudication

The first D197 failure truncated its display. A fresh auxiliary run of only its
unchanged symbol method set `unittest.TestCase.maxDiff=None` for display alone.
No assertion, list normalization, compiler flag, symbol or verdict was changed.
The complete saved difference contains precisely three removals and no additions:

- `r motors::(anonymous namespace)::DOMAINS`
- `r motors::(anonymous namespace)::SELECTORS`
- `t motors::(anonymous namespace)::candidateRate(unsigned int)`

Both array declarations remain byte-exact and now feed constant evaluation.
The internal selector can be inlined/eliminated; unchanged liveRateValid still
observes the PWM getter and compares candidateRate. PRESCALERS remains emitted
for the unchanged live PSC comparison. The new oracle separately verifies
probe0 diagnostic exclusion, exactly one28B zero-initialized probe1 report and
its accessor, and absence of dynamic initialization, so D197's early failed
assertion does not hide those checks. Separate review adjudicates this exact
host emission difference under D202. Neither historical invocation becomes PASS.
Target emission and size are still unobserved.

## Evidence and next step

Corrected result7249f9bf completed with exit0 in145.437 seconds. All154 frozen
inputs remained exact. Four explicit carrier-zero builds each retain their
required warning; their executed guards, numeric results and UBSan checks pass.
All owned RAM fixture directories are absent in the direct `wsl --exec` closing
observation. An earlier read-only observation's WSL shell-argument error is
retained in scratch_closing02; it did not affect any compiler, test or source.

- [Initial independent freeze](P7_motor_expected_metadata_raw/independent_freeze01.json)
  and [first result](P7_motor_expected_metadata_raw/metadata_first_linux01/result.json).
- [Locked result](P7_motor_expected_metadata_raw/locked_first_linux01/result.json).
- [Historical result](P7_motor_expected_metadata_raw/probe_first_linux01/result.json)
  and [full symbol difference](P7_motor_expected_metadata_raw/symbols_audit_linux01/stderr).
- [Fixture correction](P7_motor_expected_metadata_raw/correction01.json),
  [revised independent freeze](P7_motor_expected_metadata_raw/independent_freeze02.json)
  and [revised coordinator closure](P7_motor_expected_metadata_raw/coordinator_freeze02.json).
- [Corrected result](P7_motor_expected_metadata_raw/metadata_corrected_linux02/result.json),
  [input closure](P7_motor_expected_metadata_raw/closing01.json) and
  [scratch closure](P7_motor_expected_metadata_raw/scratch_closing03.json).
- [Separate review](../reviews/P7_motor_expected_metadata_review.md),12702B,
  SHA256f7b8a116464ac0590aa93dc19a66db0d4f4cebe4eed717a5a4f67780c75021ae.

The review independently checked all465 command receipts, all45 four-variant
numeric groups, all21 four-variant transcript groups, four complete expected
carrier-zero warnings and154 closing pins. Only the four intended negative
interface/flag compiler invocations returned nonzero.

Standard `tools/test_host.sh` uses CMake/CTest and does not run these Python
oracles. The broad unittest discovery command documented in tools/README.md
does include the preserved D197 failure and requires evidence-owner setup for
newer oracles. This record is scoped host acceptance, not a claim that broad
tooling discovery is wholly passing; no historical assertion was excluded.

Corrected command: `python -I -B state/analysis/P7_motor_expected_metadata_raw/host_driver02.py metadata`.
Owner metadata_corrected_linux02 is consumed. Host acceptance is complete;
prepare a fresh fixed compile-only scope. Checked new artifacts
and actual ABI/entry evidence precede a separately reviewed inhibited run.
The latest flashed image remains D198 source117cc0e7 from D201. No timing gain,
fault repair, WCET, physical qualification or human gate is established here.
