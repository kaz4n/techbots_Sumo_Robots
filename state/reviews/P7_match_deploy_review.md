# D183 guarded precompiled MATCH deployment review

Date: 25 September 2026, Dubai. Separate same-model reviewer, initially fresh
context. Scope: the adopted D183 contract, tools/match_deploy.py,
tools/match_payload.py, board_tool.py/flash.sh routing and deployment documentation.
Reviewed implementation through 35e86452; functional repairs are in 69bb9981
and 8a1c8523. No firmware or historical uploader implementation was changed.

The reviewer read source and retained test outputs, consulted on bounded repairs,
and, at the orchestrator's explicit request, authored only the source-aware
supplemental test_realistic_composition.py and this report. That supplemental
test is not the separately authored specification oracle. The reviewer did not
execute tests, compilers, board transports, uploads or motor operations.

## Findings

No open BLOCKER or MAJOR implementation findings remain within this offline scope.

- Resolved MAJOR: successful upload followed by failed outcome saving originally
  raised without attached deployment context and retained ACCEPTED in memory.
  save_outcome now promotes the save failure only when there is no prior error,
  retains the original primary otherwise, records outcome_write, marks a
  dispatched attempt UNKNOWN and attaches deploy_outcome without retrying.
- Resolved MAJOR: local admission originally imported the Linux-only resource
  module from the frozen support source. It now extracts exactly five checked,
  pure definitions into an isolated namespace. The complete remote source and
  its historical hash remain unchanged. Windows support-view preparation and
  the independent no-resource admission regression pass.
- Resolved MAJOR: the checked policy originally reopened its two JSON inputs
  outside the bounded pinned reads. The isolated policy view now replaces
  exactly the two original read expressions with checked strings, rejects
  unexpected replacement counts and preserves the remaining AST. The public
  no-reopen regression passes; no shared module or historical source is mutated.
- Resolved MAJOR: realistic metadata caused Windows command-size rejection
  although the original, unusually compressible fixture passed. The original
  rejection and source-aware regression are retained. Static shortening of
  bootstrap identifiers and error phase labels preserves external field names,
  adapter keyword arguments, all 24 require predicates, framing and limits.
  The frozen realistic regression now passes for both transports.
- Resolved documentation issue: tools/README.md no longer claims that every app
  upload is disabled. It identifies the explicit precompiled route, states that
  upload starts motor-capable firmware, and explains fresh human provenance,
  consumed attempts, UNKNOWN outcomes and the limits of compact reply hashes.

Source tracing found no bypass of the request/qualification/authorization checks.
Current firmware bytes, compile receipts, overlapping compile/runtime hashes,
artifact identity, target and operation are bound before dispatch. Argument
refusals precede the old build route. Claims precede remote calls; prerequisite
failure prevents upload; at most one upload is dispatched; closing checks are
independent. Reply acceptance requires the exact request identity and successful
uploader lifecycle rather than transport exit zero. The inherited uploader owns
native execution; there is no second uploader, compile, staging, repair or retry.

## Evidence and provenance

- Original source 396e3359 and oracle 721e090b produced 59 PASS / 4 FAIL.
  first_test_output.txt has hash 89c96b3d. The new in-process bootstrap fixture
  omitted isolated-interpreter flags, and the ENOSPC fixture patched only
  os.open, missing Path.open/io.open. The narrow fixture corrections preserve
  all expected assertions; production isolation was not weakened. Original
  source, oracle, failures and the independent adjudication remain retained.
- Corrected oracle c98b1873 with source 69bb9981 passed 126 methods: 66 D183
  methods and 60 unchanged compiler/executor/parser regressions, no skips.
  corrected_test_output.txt hash e57795ae. Windows payload tests also passed
  25 methods before the realistic composition issue was discovered.
- windows_composition.json and rejected_composition_sizes.json retain the
  additional realistic rejection: 30303 ADB / 30289 SSH UTF-16 units including
  NUL for that input. The separate frozen source-aware supplement 623150b7
  also rejected both transports before repair; original output hash 3aa66688.
- Functional size repair 8a1c8523, frozen by 77e0db0b, passed all 66 D183 methods
  again on WSL (final_test_output.txt hash b7c3fb7e), plus 25 payload methods and
  the one realistic-composition method on Windows (final_windows_output.txt
  hash ceb86049), no skips. The realistic supplemental commands measure
  29919 ADB / 29904 SSH UTF-16 units including NUL.
- The reviewer independently recomputed hashes of the original, corrected,
  final WSL, final Windows and original supplemental output files; all match
  their result records. Source comparisons confirm src/ and tests/locked/
  remain unchanged relative to 0f3aa531.

The final_freeze.json source_commit label still names the preceding admission
repair 69bb9981. Its payload pin 405b3ae4 identifies the actual tested size repair
8a1c8523; this report explicitly records that provenance correction without
rewriting the frozen record. Commit 35e86452 then adds only two explanatory
comments outside the bootstrap string. The inspected diff and retained
comment_identity.json establish unchanged executable AST and bootstrap wire.
Current match_deploy.py SHA256 is
3acacad6e95aff1012e9d0d1f8ef60905c026ebe865569fdb71384abd607d2a9;
current match_payload.py SHA256 is
7962e8bd30c1fbc9ccb12c98856c47d92d4ed501be6cdc718e9b45e25b82944a.
The unchanged reviewer supplement is 3889 bytes, SHA256
7a094c098fddd341617273ac0a376ef690f9975b05cea16618b516988b796967.

## Limitations

The measured Windows headroom is modest: 81 ADB / 96 SSH units for the tested
realistic input. The unchanged 30000-unit guard evaluates every actual request
with its native transport prefix; other identifiers, metadata, paths or later
source changes may be refused. These measurements are not a universal fit claim.

Fixtures and historical metadata are synthetic preparation evidence, not current
board identity, physical qualification or human permission. File hashes cannot
authenticate a human message or prove physical truth. Real execution still
requires the exact artifact's qualification and a current-session, identified
STAND OK or RING OK statement whose provenance the operator verifies. A local
transport timeout does not prove that remote execution stopped. Compact hashes
cannot independently rehash omitted remote streams.

This review does not establish target compilation of the current firmware,
MotorGate diagnostic success, RAM/WCET, physical acceptance, any human phase
gate, an approved deploy scope or permission to upload/run motors.

## Verdict

PASS for D183 offline software preparation and reviewed host validation only.
No native deployment or phase-gate approval follows.
