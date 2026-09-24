# One-shot static probe runner: public host contract

Draft D143, 25 September 2026. Completes the runner portion of the frozen parent
[probe contract](P7_static_link_probe_contract.md); the [earlier runner proposal](P7_static_runner_proposal.md)
is design provenance. D141 policy and D142 structure/package checks are already
host-tested. This draft does not yet authorize implementation or any board command.

## Fixed interface, scope and outputs

Place the scoped implementation in `P7_static_link_probe_raw/run_static_probe.py`.
Use the unchanged `board_tool.remote`, existing D139 `verifiedStage`, applicable
pure/common policy helpers, and the exact D141/D142 files. No global callback
replacement, production-policy edit, restaging, upload/reset/run or deletion.

```python
run_probe(*, compile_only: bool, run_id: str, receipt_dir: Path,
          command: Callable) -> dict
# command(board: str, argv: list[str], *, capture: bool,
#         timeout: int) -> subprocess.CompletedProcess[str]
parse_request(argv: list[str]) -> argparse.Namespace
main(argv=None) -> int
```

`compile_only` must be exactly True; `run_id` is32 lowercase hexadecimal digits.
`command` must be callable and is the only transport substitution seam. It never
replaces a validator or controls the emitted argv. Invalid request types/values
raise ValueError before directory creation, dependency import or command calls.
The local receipt Path must be absolute/canonical, its parent already exist and
be a nonsymlink directory, and its entire ancestry must contain no symlink or
Windows reparse point. The final directory must be absent and is created
exclusively after local pins/stage checks. An existing empty directory also fails.
Do not remove stale data, create arbitrary missing parent directories or retry.

`parse_request` accepts exactly the three tokens `--compile-only --run-id <id>`
in that order. The sole-token `--help` or `-h` returns normal argparse help;
all other token lists, duplicates, abbreviations and invalid IDs fail with
SystemExit2. Parsing performs no filesystem I/O or transport.
`main` parses first, then verifies exact existing environment:
SUMO_TRANSPORT=adb, SUMO_ADB_SERIAL=2629958581 and SUMO_ADB_EXECUTABLE equal to
`C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe`
(ordinary Windows slash/case normalization is allowed for that same absolute
path, not resolution to a different target). Check its exact known SHA256
e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982 and nonsymlink file.
Missing/drifting configuration fails; do not set global/persistent configuration.
The real receipt parent is the pre-created task-owned `P7_static_link_probe_raw/runs/`.
The exact reviewed launcher hash and invocation remain a later coordinator GO.

Success returns exactly these fields, and writes the same JSON as `result.json`:

- `status`: STATIC_COMPILE_COLLECTED (never STATIC_ARTIFACT_PROBE_PASS).
- `source_sha256`: fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2.
- `run_id`, `receipt_dir`, `remote_root`, `build_path`, `artifact_path`.
- `query_attempts`:1 and `compile_attempts`:1.
- `layout`: the complete unchanged D142 structural report.
- `artifacts`: seven canonical filename keys, each with observed bytes/SHA256.
- `final_elf`: local `app.ino.elf` path and its verified bytes/SHA256.

On failure raise the original command exception (or ValueError for admission /
response validation). If a receipt directory was claimed, write `result.json`
with status FAILED or COMPILE_OUTCOME_UNKNOWN, phase, attempt counts, first error
class/message, and an ordered separate `postcheck_errors` list. The first failure
is never replaced by a later postcheck failure. No result asserts target/runtime
or complete native-audit acceptance. A timeout during compile is UNKNOWN: no
retry, output acceptance, cleanup, kill or post-compile remote command follows.

## Immutable local input checks

Every input in the earlier proposal's11-row hash table remains exact, plus:

- D142 static_artifacts.py:
  d30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368.
- D142 artifact contract:
  b6a18e4d27e500d6306587141cbb27bcd7e546ce9bb507f148f28591634bec54.
- This runner contract and the separately reviewed new remote helper/wrapper
  files, with literal hashes frozen before implementation execution.

Check file containment, regular file/no symlink ancestry, and literal SHA256
before importing dependencies or using data. Recheck after a terminal compile.
The module's own hash is recorded; its later production launcher pins that hash
externally to avoid self-hash recursion. Data manifests cannot redefine accepted
hashes. Call the unchanged D139 local stage verifier with the two pinned manifests
before any transport, before compile and after its terminal result. It checks
all103 source/102 stage files and current config, without any staging fallback.

## Exact transport sequence

All calls use board literal2629958581, `capture=True`, and explicit timeout.
Helper actions use the companion's exact per-action timeout table. Other
read/guard calls timeout60s, properties query300s, compile1800s.
One actual compile process only, with --jobs1. A callback must return a genuine
CompletedProcess with integer non-bool returncode and str stdout/stderr on normal
return; other shapes fail. A nonzero normal result is converted to the equivalent
CalledProcessError only after its actual code/text are recorded.

1. Check local pins/stage and claim local receipt directory.
2. Run remote helper inventory: Linux user arduino, architecture aarch64, Python3
   at least3.9, memory/disk observations and no active compiler. Require at least
   512MiB MemAvailable and1GiB free on each of the build-root and /tmp filesystems.
   These are conservative host resource floors, not measured compiler/WCET claims.
   Reject unknown inventory or active arduino-cli/cc1/cc1plus/lto1/arm-zephyr process;
   do not stop another job. Recheck resources immediately before actual compile.
3. Capture `arduino-cli version`, `arduino-cli core list`, and `arduino-cli config
   get directories.data --json` / `directories.user --json`. Use unchanged
   validate_cli/resolved_directory. Require unique installed arduino:zephyr1.0.0,
   exact data=/home/arduino/.arduino15 and user=/home/arduino/Arduino. Unknown core
   rows may be listed but do not satisfy the required row; duplicate required
   rows fail, including conflicting versions.
4. Verify remote source tree S, existing overrides and all26 installed pins.
   Reuse unchanged check_overrides and verify_hashes through the receipt adapter;
   merge18 production plus8 additional paths with no duplicates or removed pins.
5. Atomically claim new U/build and U/artifacts via reviewed helper. U is
   /home/arduino/sumox26_codex_build/_app_builds/static-app-probe-v1/<source>/bench-default/<run_id>.
   S is /home/arduino/sumox26_codex_build/<source>/app. Neither may be caller options.
6. Check all eight outputs absent, then issue the single properties query exactly as the earlier proposal's argv;
   validate through unchanged D141 validate_preflight with exact B/data paths.
7. Recheck local source/pins, remote source/overrides/26pins, resources, run
   ownership/ancestry and absence of all eight fixed output destinations. Source
   or any stale artifact drift stops before compile. Query output cannot count
   as a newly compiled artifact.
8. Issue exactly one actual compiler argv from the proposal. Record observed
   stdout/stderr/code; a well-formed zero transport result permits D141 validation
   and the terminal postcheck group even if that validation fails. A nonzero
   transport result may instead be an ADB disconnect; classify it as unknown
   completion, retaining original output/exception and running local checks only.
   Timeout or any other uncertain completion likewise permits no remote postcheck.
9. Only after successful compile/result/postchecks, bound-check and identify all
   seven canonical build outputs plus selected A/app.ino.bin-zsk.bin. The selected
   export must equal the canonical flat package. Perform D142 validation with
   the exact hash-pinned source plus reviewed I/O wrapper on Linux, emitting only
   the compact report and file identity metadata. Recheck all identities after
   validation and again after fetching the final ELF. Any drift/missing/nonregular
   output fails. Preserve the complete files on Linux.
10. Fetch only the final ELF through base64, strictly decode and compare its
    length/SHA to the bound remote records. Save it with exclusive creation.
    Include the exact D142 report only after verifying its seven identities and
    fixed status, entry and bounds schema; response JSON rejects duplicates and
    all nonfinite numbers. A command substitute can simulate this report for host
    tests; that never establishes target execution. Real use binds transmitted
    helper/validator bytes and observed files, without a validator-replacement callback.

The remote helper/wrapper's exact argv and result schemas are in the separately
reviewed [companion](P7_static_remote_contract_draft.md), finalized before adoption.
Use its bounded compressed-code bootstrap and reject any command exceeding
30,000 UTF-16 code units including NUL after exact existing ADB/Windows quoting,
before transport. All paths/argument templates are
fixed and validated; no caller shell fragment or alternate sketch/build profile.

## Receipts, failures and storage

### Canonical dispatch and attempt accounting

The following is the sole successful command order. `overrides` and `pins` mean
the exact one-command calls emitted by the unchanged common helpers; merge the
18+8 pin maps in their existing insertion order. Helper arguments are those in
the remote companion; no additional inventory or hidden transport call occurs.

1. inventory; CLI version; CLI core list; CLI data directory; CLI user directory.
2. source; overrides; pins; claim; absent; expanded-properties query.
3. Recheck local pins and stage, then source; overrides; pins; inventory; absent.
4. Compile once. On a terminal result, validate its D141 report, then perform
   all postchecks in this order: local pins, local stage, remote postcheck,
   installed pins, overrides. These five checks are independent: retain each
   failure and continue the remaining checks. No artifact collection if any fails.
5. artifacts; layout; read final-ELF chunks in increasing offsets. All eight
   FileRecords must stay identical to the successful first postcheck, including
   metadata and hashes. Each chunk's FileRecord must equal that baseline's ELF.
6. Repeat all five checks from step4 in the same order after collection; the
   second remote postcheck must match all eight baseline FileRecords. Save the
   complete checked ELF only after these checks, by exclusive creation, then
   write success. If a collection command/validation fails, still perform this
   final five-check group once, preserving the collection failure as primary.

Before compile is attempted, fail immediately without the terminal postcheck
group. Increment query_attempts/compile_attempts only after persisting the
planned command receipt and immediately before invoking command. These are
dispatch attempts, not proof of remote process startup. No outcome permits a
second attempt. Other command failures propagate with the actual attempt counts.
After compile dispatch, only a well-formed CompletedProcess with integer non-bool
returncode0 establishes the normal terminal path. Any nonzero returned result or
CalledProcessError may be an ADB transport failure while compilation continues;
it therefore remains unknown rather than proving a remote compiler exit.
TimeoutExpired, OSError, an unexpected callback exception or malformed status leaves
COMPILE_OUTCOME_UNKNOWN: run local pins/stage checks only, with no remote action.
A zero-return compile whose metadata fails D141 validation remains FAILED even
if later postchecks fail. No wrapper or inferred remote-completion marker is added.

Each postcheck error is `{check,class,message}` with check one of `local_pins`,
`local_stage`, `remote_postcheck`, `installed_pins`, `overrides`, in that order.
For an otherwise successful compile/collection, the first postcheck failure is
the primary exception too; retain the whole ordered postcheck_errors list.
Primary error is `{class,message}`. Failure result has exactly status,phase,
query_attempts,compile_attempts,error,postcheck_errors. Phase is the failing
logical command/check name above; use `query`, `compile`, `artifacts`, `layout`,
`read`, `local_admission`, `local_claim` or `result_write` where applicable.

### Host acceptance of returned evidence

Every successful helper envelope and nested object has exactly its companion
keys, correct action/run identity, and no bool in an integer field. All JSON
numbers are finite; hashes are64 lowercase hex characters. Claim IDs must remain
identical to the runner's own first claim; boot identity also equals inventory.
Compare both source checks and postcheck source maps to all102 pinned local-stage
names/hashes and observed local byte lengths, with exact total and SOURCE digest.
All eight successful file records must be nonempty regular files within the
companion bounds. Export size/hash equals its canonical build package; the pinned
helper additionally performs the byte comparison. Metadata integer fields are
nonnegative. Freshness still rests on exclusive claims and absent destinations.

The layout has exactly the D142 result keys/nested fields. Require its fixed status
and entry; flash/RAM starts and upper limits equal D142 constants, end lies within
the region, and remaining equals limit-end. All integer fields are non-bool and
nonnegative. Data-copy source/span lies in flash, destination/span lies in RAM;
the span ends no later than bss_zero.start. BSS zero bytes=end-start and its range
lies within RAM with end<=ram.end. Sections are unique, nonempty, address-sorted
records from D142's named allocation table, with exactly its permitted type/flags,
power-of-two-or-zero alignment and aligned addresses. .text/.data/.bss are required.
Each extent fits its flash/RAM region; flash load_address equals address, .data's
load span fits flash, and only .bss has null load_address. Section extents cannot
overlap. weak_undefined is a sorted unique list of nonempty strings, each at most
4096 characters; it is still pending native-use review. Seven report artifact
identities equal the baseline records. Reject any extra/missing nested fields.
These are report-integrity checks; the exact unchanged remote D142 function is
the structural validator, and full native instruction/ABI acceptance is separate.

Read offsets begin at0 and advance by exactly the decoded length through the
baseline ELF size, using the companion's262144-byte maximum. Canonical base64,
chunk SHA/length/offset/name, FileRecord and Claim must match on every response.
The accumulated ELF hash/length must equal baseline; no partial or repeated chunk
can become success. Record final_elf as exactly `{path,bytes,sha256}`.

### Exact command receipt format

Use `0001.json`, `0002.json`, ... in the exclusive local receipt directory.
A planned record has exactly `sequence,phase,board,argv,timeout,start_utc`;
complete the same owned record with `end_utc,returncode,stdout,stderr,error`.
error is null for a normal process result, or `{class,message}` for an exception.
For exception output only, bytes become `{encoding:"base64",data:<canonical>}`;
str/null remain unchanged. Retain a returned nonzero process as actual output
before converting it to CalledProcessError. A failed receipt write prevents
dispatch; a failed completion write never invents success or allows a retry.

Before every command, persist a monotonically numbered JSON record with planned
argv, board, timeout, phase and UTC start. Complete it with end time, actual
returncode and exact observed stdout/stderr before any response validation.
Exceptions retain class/message and original output: bytes use base64 with an
encoding label, None remains null, strings remain strings. A timeout/launch error
has null returncode, never synthetic zero. Ordinary returned output must be text.
No secret environment dump. Preserve CalledProcessError/TimeoutExpired/OSError;
never continue on an unknown response. Each planned record can only be completed
inside this exclusively claimed directory; no reuse/overwriting old runs.

Source enumeration, pins and compact layout metadata remain small. To satisfy
both complete command capture and storage conservation, do not transfer debug /
temp ELF, raw BIN, both packages and map as large base64 receipt strings. The
reviewed validator wrapper reads them on Linux. Final ELF transfer may retain its
one base64 command capture plus the one decoded checked ELF; this small deliberate
duplicate preserves raw transport evidence. Failure outputs and all7 remote files
remain intact. No cleanup function, build cache or parallel compiler is added.

## Independent host verification before real use

The author derives controlled-command expectations from this public contract,
the frozen helper command templates and prior D141/D142 fixtures, not runner
implementation. Fake commands must return independently built outputs; tests
must reject wrong literal command order/arguments instead of accepting arbitrary
calls. Test request/CLI/pins/stage/source/override/resource/core/properties drift,
stale outputs before compile despite valid bytes/zero packaging exit, each
compiler/transport failure and timeout, postcheck drift, package/report/export
identity failures, exact counts, original failure/bytes retention and success.
Use transient local test receipt directories; preserve only compact results.
Tests may inject local read failures/drift at the filesystem boundary, never
replace validators, relax their constants or edit current source/stage files.

Freeze oracles before first implementation execution. Separate code/command
review and actual host checks precede later coordinator GO for the one target
query/compiler. CLI tests requiring real transport remain unexecuted until that
GO; no full-probe/runtime/phase acceptance can follow from fakes.
