# D230 independent complete passive caller review

Reviewed2026-09-27. **PASS: frozen source and focused host evidence accepted
for the concrete preparation/check/one-execution workflow below.** No material
blocker was found. The reviewer made no native call, ran no tests, and changed
only this review. Actual capture remains unperformed at this review boundary.
The accepted ABI and unchanged dependencies were not subjected to another
broad review or test campaign.

Frozen identities (SHA256):

- Caller19572B: `c61858ba7cd940499a9a69ea6a9fc92556e32263bfa54abb13dba5f8d577a87e`.
- Contract3861B: `4da6e6eb3e6dade56e9507f55d51f3e061bc6b700c2b1d0ddc6b8d50987b33d3`.
- Tests13962B: `c2ae4d67ba78ba68818c2b7a4bc02fdc7a3518f9f368af49ea95c8ed2a5f5596`.
- caller_windows01.json1119B: `e40149ad9f40c2816f3e682027e9523d6c0659082ef3a28d185543adea2d895c`.
- caller_windows01.stderr1540B: `e96da86363e171ce231cf2ffbe8e00b6339049ffa4355ed46bec46651c051c7f`.

The caller is tools/run_recorder_failure_capture.py; contract and receipts are
under state/analysis/P7_recorder_failure_caller_contract.md and
state/analysis/P7_recorder_failure_raw/. All5 source/raw pins in the receipt
were independently recomputed. The retained stdout is empty. The caller and
contract stayed unchanged through the final focused run.

This completes the previously pending local workflow. Offline preparation
reconciles the accepted ABI with its original four command results, exact12
remote file closures, local closure and recomputed summary. It writes only
three absent-only binding files. The pushed adapter is the unchanged reviewed
capture helper13fc387d plus a literal fixed-spec wrapper. The spec and its
canonical SHA256 derive mechanically from accepted ABI
de0cb0ecb558937a9ad251fd81168fe340bf2440aa9ebd3108a60d7758b89ee9.
No fresh source invention or repeated ABI admission chain is required.

Current recorder source identity remains702ad99ee4f888c58de1715cb91512cb0a174a646d914db6ce9155489ffa63e8,
attempt377911abefabd094971ee6d089326604 and session3997245574426120340.
Historical HEAD004dc7cff534896a851901f9d7d0ba6066cae060 remains distinct from
the exact clean collector HEAD. Real historical admission binds144 source
inputs and109 staged entries including the positive session header. The
capability projection checks /home/arduino/sumox26_codex_build/SOURCE/recorder,
which agrees with the delivery caller's source path. Its whole source mapping
and staged adapter are rechecked before and after capture.

D219's lifecycle retains exclusive local ownership, durable staging/capture/
retrieval intents, fixed ADB executable/hash/serial, immutable command state,
bounded dispatch counts, prerequisite checks and first/closing failure handling.
Only the pushed local adapter path and result schema are substituted in that
caller body. Scope/input and status export overrides are narrow. The actual
allowlist has7 action forms and at most10 transports: two rounds of the two
baselines and capabilities, one adapter claim, one push, one capture and one
retrieval. No upload action is present. Native startup and cleanup logic remain
in the pinned capture lifecycle; motor grants, UART and MCU reset are not added.

Fresh10 windows merge into6 aligned SRAM ranges totaling684B per snapshot.
The fixed plan has24 reads requesting638936B: full263680B loader and55104B
sketch before SRAM, two snapshots separated by at least2 seconds, then both
full flash images again. Initial flash mismatch refuses SRAM. Status decoding
retains strict bool/enum validation and coherence UNPROVEN. The executed remote
bootstrap checks staged adapter bytes and installed p0_capture both before and
at closure. Reuse of the old bootstrap does not reuse B4 addresses or its decoder.

The reply must match exact run/source/schema, COLLECTED status, bounded counts,
every ordered read identity, finite600s monotonic bracket,2s sample separation,
four true flash checks and matching before/after flash hashes. Retrieval returns
the durable report plus12 status files; descriptor reads verify each hash and
independently re-read all13 files before final identity closure. Local export
requires byte equality of the durable and returned report, every raw hash and
an exact local recomputation of analysis. Full flash bytes remain in the durable
remote owner. A failed capture retains its returned/raw command evidence and
remote partial owner; it cannot proceed to successful retrieval/export. This
preserves unsuccessful evidence without describing it as a complete bundle.

The focused Windows suite passed10/10 methods in7.162s, exit0. The reviewer read
the actual fixtures and complete method receipt. They cover accepted-ABI
recomputation, six-range/count identity, hash refusal, real offline owner and
command construction, binding reuse refusal, state mutation refusal, reply
timing/count/flash refusals, raw export and malformed retrieval. Three fixtures
execute the projected bootstrap request/perform through explicit fake descriptor
and Linux-dependency seams, execute the exact retrieval read body with13
independent closing reads and changed-byte refusal, and inject failed capture
plus two closing errors to prove no retrieval/export and preserved first error.
These are host fixtures, not board observations. The controlled owner fixture
substitutes the live HEAD/ADB gate; actual check-only below remains required.
No Linux-wide or inherited-suite repeat was needed for this bounded caller.

Concrete completion sequence after integrating the frozen caller:

1. With the accepted ABI and unchanged current image/source records present,
   run `python -B tools/run_recorder_failure_capture.py --prepare-bindings --abi-sha256 de0cb0ecb558937a9ad251fd81168fe340bf2440aa9ebd3108a60d7758b89ee9`.
2. Commit the mechanically generated capture_inputs01.json,
   capture_scope01.json and capture_adapter01.py under P7_recorder_failure_raw.
   Preserve exact bytes. Use that clean collector HEAD for
   `python -B tools/run_recorder_failure_capture.py --check-only --reviewed-head <HEAD>`.
3. After successful check-only and with active compiler/conflicting native
   work closed, execute once using the same HEAD:
   `python -B tools/run_recorder_failure_capture.py --execute --reviewed-head <HEAD>`.
4. Reconcile its returned report, durable retrieval, raw snapshots, flash
   brackets and closing checks before interpreting status. The fixed local
   owner is native_capture01; remote adapter and capture owners are absent-only
   and remain consumed after partial work. Retain any failure; no retry or
   cleanup branch is admitted here.

Mechanical preparation and same-HEAD check-only need no further recursive
source review. This PASS supersedes only the initial checkpoint's pending
complete-caller boundary. It neither asserts current MCU status nor explains
the prior zero-byte timeout. Actual observations remain non-atomic; equal
snapshots do not establish coherence or earlier causation. No firmware upload,
reset, UART/receiver retry, grant/pin change, motor permission, physical
qualification or phase pass follows.
