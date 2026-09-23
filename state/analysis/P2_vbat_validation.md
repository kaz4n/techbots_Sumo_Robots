# D110 battery bench validation

2026-09-24 Asia/Dubai. Contract/interfaces/config adoptedc3ed3eb after independent
author preflight. First source7b132a2a is preserved; before test execution the
worker moved sample_seen publication before A as the contract requires. Current
Runnerb5fa7eea and complete source/config hashes are in P2_vbat_raw/worker.
Status: IMPLEMENTED/HOST-TESTED/TARGET-COMPILED in both startup profiles;
separate source/test/policy/target review PASS with no open findings.

The named P2 B5 bench retains the first128 accepted battery samples at the
existing10ms cadence. One battery-only Reader supplies actual unfiltered samples;
source and wrapper times, local/cumulative missed releases, native failures and
shutdown status stay explicit. Every poll does at most one read. Closing-clock
failure hides a tentative record; published records never change. Default ADC
grant is false. No A1, motor, matrix, transport or application controller owner
is added. No stop/disable operation is invented for the Reader.

## Independent expectations and build tooling

Separate author and implementer contexts wrote in parallel from the adopted
contract/public API. The author did not read implementation bodies and froze
executable tests before their first run: cases196faa64 and harness34e3a896.
These are reused same-model contexts, not cross-model or human gate review.
Exact frozen bytes and run evidence are under P2_vbat_raw/author.

The coordinator added only the literal VBAT_BENCH_SAMPLES=128 expectation to the
unlocked registry. Removing the exact added bytes restores the previous file
byte-for-byte; the proof and both byte copies are under P2_vbat_raw/registry.
All existing assertions/defaults remain. Production capacity is a software
storage choice, not a physical tuning measurement.

Root-authored seven route fixtures froze before the four literal policy changes.
Initial red result: four failures, two errors, one pass, as the new target was
not admitted yet. The changed route permits only checked inert default/Immediate
compile profiles. Uploads, MATCH and sketch.yaml/yml including dangling symlinks
fail before transport. No upload-manifest entry or generic fallback was added;
all installed-tool/property/library/result/artifact checks remain intact.

Root's first green invocation named a nonexistent old test_app_override_policy
module. Its68 actual methods passed but the import sentinel failed; that complete
failed invocation remains. The separately corrected test_app_build_overrides
invocation passes46 methods. Together114 real methods pass; no source or test
change resolved the command typo. The separate reviewer runs the correctly named
complete set privately. Receipts are P2_app_build_raw/d110_policy_*.

## Evidence limits and checkpoint correction

Target commands only compile/read files on board Linux; no upload/reset/MCU run.
The MCU remains frozen D1042bd817c4. A target compiler exit0 will not by itself
establish exact startup/import/owner/loader acceptance. Physical divider/reference,
ADC timing, SC-AJ clock qualification and0.05V multimeter agreement across
9.5..12.6V remain pending. Stable RAM needs later reviewed capture readout and
physical provenance; simulated clocks and nominal scaling supply neither.

An initial checkpoint edit used Windows' implicit cp1252 decoding and failed
before any write. Explicit subsequent Git commands still made contract commit
c3ed3eb. The checkpoint update was then performed using ASCII byte anchors,
preserving historical bytes; P2_vbat_raw/checkpoint_encoding_correction.json
records the correction. No history or earlier evidence was rewritten.

## Final executed results

All frozen executable expectations pass on first execution against second-source
b5fa7eea; no test amendment or execution-driven source fix was needed. The
separate reviewer reproduces all profiles. Normal/sanitizer scopes are explicit:

| Profile | Cases / assertions per binary |
|---|---|
| Ordinary128, normal and ASan/UBSan | 31 /21,066 |
| Actual Native/default selection, normal and sanitizer | 3 /911 |
| Capacity1, normal and sanitizer | 22 /2,864 |
| Capacity0, normal and sanitizer | 3 /60 |
| Eleven invalid configurations, sanitizer | 3 /60 each |
| Five valid boundary configurations, sanitizer | 1 /10 each |
| Public missed-release saturation, normal and sanitizer | 1 /38 |
| Accumulated source half-range, normal and sanitizer | 1 /24 |

All28 binaries pass with empty stderr; three forbidden flag combinations fail
their required static assertions. The native case selector also matches one
ordinary native-failure case because matching is case-insensitive; observed3/911
includes the two actual binding/default-sketch cases. This is disclosed extra
coverage, not an assertion change. Ninety original registry checks across five
profiles preserve one positive result and four deliberate value rejections.
See author/validation.md, coverage.md and run1_summary.json for all61 commands.
The prior D109 full host run remains applicable to unchanged shared behavior;
only the new unused-by-production count constant was added since that run.

## Exact target and review

Source8e3efb92cc6fb2ea66fdb79c96184279fbee7040ad40d9356be9365b0757c1c8
contains96 staged files. Default receiptf89f7f7cae7e4a37b98b50d45c1e0968 and
Immediate9a49eb8337304454b61e59f4c6363a6f pass checked native policy and exact
collection. Both final ELFs are19,276 bytes and have the same508bedea prefix;
full hashes and all ELF forms/packages are retained in the target directories.
Payload12,333; conditional ordered loader peak13,200 of262,144; remaining
span248,944 and largest payload248,940. No loaded-RAM measurement follows.

Actual target paths use beginProfile(false), acquire(rank9,true), one32-byte
Reader and6280-byte Runner. Startup is passive/default-disabled, with unrelated
owners and transports excluded. Target references to native hardware are not
evidence that the absent grant configured it. The reviewer verifies all331 prior
test files and the prior upload manifest unchanged. Final bound verdict:
state/reviews/P2_vbat_review_raw/final_review.json, SHA256
a6497205ec53c981a9e3a5b65a46f2dc8e7c9936b7aa08e92deceda498febc51.

Root separately verifies28 command receipts, both artifact sets and unchanged
second-source bytes in root_receipt_verification.json. Its initial inline helper
used the previous worker's manifest key and failed before writing a result;
the corrected traversal reads this manifest's files list, with no changed check.
The reviewer's summary-schema correction likewise changed no executed tests.
All software, conditional-model and physical evidence limits above remain.

Local implementation/evidence commit: a0ee402. The final Git whitespace check
reported one extra blank line at tests/tooling/vbat_cases.cc EOF. Root retains
the exact frozen, passing oracle bytes; this is a disclosed formatting-only
limitation, with no changed assertion or production behavior.
