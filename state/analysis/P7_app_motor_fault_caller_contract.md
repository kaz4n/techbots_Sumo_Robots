# Fixed local caller for the inhibited full-app diagnostic

This is the local composition for the exact run and identities in
`P7_app_motor_fault_run_contract.md`. It adds no firmware change or motor grant.
The coordinator creates the actual preparation manifest, fresh scope and reviewed
HEAD only after independent host tests and review. Preparation is not execution.

## Reuse and public interfaces

`P7_app_motor_fault_run_raw/actions.py` privately loads the unchanged
`P7_motor_fault_raw/inert_actions.py` (SHA256
`8ffb65c0f1284f261ae1237bcf260e866176e83433a3538908780962513f1104`).
It keeps bounded canonical JSON/BZ2 framing, exact action sequencing, first-error
and final-check wrappers, with explicit new identity/schema/profile substitutions.
Its public functions are `build_command(action, sources, bindings, adapter_pin)`,
`validate_reply(action, reply)` and `run_actions(operations)`. Action is exactly
`upload` or `capture`; sources are exactly three nonempty byte strings named
`helper`, `support`, `upload` with the pinned original static/upload/capture hashes
from the remote contract. `adapter_pin` is exactly `{path,bytes,sha256}` for the
fixed staging path below; bytes/hash must match the independently reviewed new
adapter recorded in the actual scope. No arbitrary source or staging path exists.

`build_command` does not dispatch. Its result is the isolated `/usr/bin/python3
-I -B` argument list and preserves the 196608-byte decoded payload bound, single
BZ2 member, canonical base64/base85, duplicate-key/nonfinite rejection, payload
hash and source hashes. Including terminating NUL, actual Windows composition
must fit 30000 UTF-16 units. It fails explicitly on overflow. Native action reply
is bounded to 65536 bytes. It admits only exact new schemas/owner/run/source,
one successful upload and, for capture, 26 exact reads/727088 bytes, all four true
flash flags, twelve matching snapshot records, full bracket hashes and a measured
two-second gap. It does not decode callback fields or infer atomicity.

`P7_app_motor_fault_run_raw/run.py` exposes `InertRun(reviewed_head, *, root=None)`
with the inherited public `admit`, `claim`, `local`, `prerequisites`, `intent`,
`action`, `finish`, `run` seams, plus `stage`. CLI accepts exactly one of
`--check-only`/`--execute` and required forty-lowercase-hex `--reviewed-head`;
check-only makes no board call, output owner, upload, reset or staging mutation.
Missing input/scope/review, malformed CLI or failed admission returns failure.

The caller privately loads unchanged `P7_motor_fault_raw/inert_run.py` (SHA256
`8b47b1d6e9073179e4f587e09ce04e1a1c0cfc6797daf3151d0a7126d279f56a`),
`P7_static_startup_raw/startup_run.py`, and its existing `CompileOnce.transport`
with its durable command/raw-output recording. It replaces only private fixed
identities, preparation and immutable allowlist composition, plus the two-command
staging allowance. No historical launcher constructor/run or consumed owner runs.
No new process execution stack, generic board interface or flag is introduced.

## Pinned inputs and immutable admission

Actual scope path: `P7_app_motor_fault_run_raw/inert_run01_scope.json`.
Local exclusive owner: `P7_app_motor_fault_run_raw/native_inert_run01`.
Run: `app-motor-fault-21df6ae8-run01`; board serial `2629958581`; source exactly
`21df6ae82cca4b09dc6b1e0de5bc719cf98ec6887800d5ce8297522e491a7950`.

The coordinator-owned `preparation.json` contains exactly `schema`, `run_id`,
`source_sha256`, `bindings`, `files`. Schema is
`app-motor-fault-run-preparation-v1`; bindings have exactly `upload` and `capture`
using the remote contract; files are exact SHA256/byte pins for required local
provenance. Required provenance includes D188 input manifest, actual compiler
result/artifacts, original ABI plus offline interpretation, successful actual
entry/local closure, adapter, actions and contracts/reviews. The actual scope
pins the preparation, caller, independent tests and review as committed bytes.
Its six fields retain the original scope shape (`schema`, `run_id`, `board`,
`source_sha256`, `expected_identity`, `files`), with schema
`app-motor-fault-native-scope-v1` and the freshly observed canonical boot UUID.
Scope file values are lowercase SHA256 hashes. The caller's own bytes must agree
with its scope entry. No self-referential preparation hash is required.

Reload every one of D188's 127 input pins; require its exact known manifest and
source/boot identities. Preserve local plain-file/reparse/ancestry checks and
unchanged inputs throughout; source projection must still equal D188. Recheck
canonical target source names and bytes through the fixed capability observation.
The actual compilation, ABI and initialization records remain separate evidence;
their failed predecessor cannot be silently rewritten. Root records their
reviewed disposition and exact hashes before native use.

Keep original checked local ADB hash, board identity, reviewed clean tracked HEAD,
committed scope bytes, exclusive local directory, immutable command/binding state
and original per-intent predecessor hash checks. Permit only the fixed attempt's
new evidence after claim. Native invocation always uses the real fixed root,
transport and board; filesystem/executor substitutions are host-test seams only.

## Small fixed staging before actions

Four inline modules plus unchanged bounded bootstrap exceed Windows' 30000-unit
limit: a measured upload payload already consumes 27891 units with an empty
bootstrap; the historical bootstrap adds 3292 characters. Stage only new
`remote.py`, retaining the three original dependencies inline.

Fixed directory:
`/home/arduino/sumox26_codex_build/app-motor-fault-21df6ae8-run01-adapter`.
Fixed file: its `remote.py` child. No existing directory/file may be reused,
overwritten, renamed, cleaned or retried. Before staging, durable local intent
records source hash/size, fresh boot, reviewed HEAD and exact commands. Use the
existing fixed identity preamble and exclusive remote directory creation, then
existing bounded ADB push of the single already pinned local source. Exactly two
staging transport calls are permitted: `adapter-claim` (60 seconds) and
`adapter-push` (60 seconds). A partial/uncertain staging attempt consumes the
outer owner and prevents upload. The first subsequent prerequisite observation
verifies the staged file using descriptor-bound size/hash checks.

Each actual action reads the staged adapter with the pinned static helper,
checks its exact bytes/hash before executing those bytes privately, and checks
the file again during closure. Both action payloads bind its immutable pin.
Capture additionally reads/checks the already installed 18880-byte `p0_capture.py`
SHA256 `885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c`
for `loader_image` and rechecks it on every exit. No recorder_heap or
runtime_capture import/dynamic relocation is needed.

## Per-action prerequisites, dispatch counts and failure handling

Preserve the two exact F166 initialization/builtin inventory commands and
projection comparisons. The third fixed capability command verifies actual
boot/UID/Python `-B`/BZ2/base85, staged adapter identity and canonical source
inventory. All three run before upload, before capture and independently at
closure. No board identity or installed API fact is accepted only from memory.
The fixed allowlist has seven commands: two staging, upload, capture and the
three prerequisites. A successful whole attempt has exactly **13 transports**:
two staging, one upload, one capture, and three executions of each prerequisite.
No command may exceed its fixed per-label count. Upload transport timeout is
195 seconds, capture 630 seconds; prerequisite commands 60 seconds. Remote child
and attempt bounds stay those of the remote contract.

Upload intent must be durably written before native dispatch. Capture is allowed
only after strict validation of the actual successful upload reply and equality
to its retained predecessor hash. A failed/uncertain upload never reaches capture;
partial capture never retries. Preserve first errors while independently running
closing checks and saving final diagnostics. Staging failure also attempts local
and prerequisite closure, with no second staging invocation or action dispatch.

Inherited MINOR: original remote `close()` can stop at its first descriptor-close
error and replace the outward exception after a durable result was written. The
isolated child exits and releases remaining descriptors. The new action envelope
retains that outward error, and separately preserves the exact durable result
when readable at the fixed path. Such a result is marked unproven as belonging
to the failing call; its success flag never overrides an outward error or allows
capture. No retry follows. The launcher must report failure even if a saved
inner report says UPLOADED/COLLECTED but envelope/closing errors remain.

Native checks and tests remain distinct. Independent tests derive from this
contract before implementation execution, freeze their oracle, and exercise
controlled staging, framing, identity drift, allowlists, wrong/failed predecessors,
timeouts, durable original error evidence and closing failures. All first failures
remain recorded; no existing/locked test change or actual target claim follows.

## Exact caller data and test seams

`files` in `preparation.json` maps each required relative filename to exactly
`{bytes: positive integer, sha256: 64 lowercase hexadecimal characters}`.
Its exact key set is the following (prefix `C` means
`state/analysis/P7_app_motor_fault_compile_raw/`; `R` means `state/reviews/`):

- `C inputs_static.json`
- `C native_static01/result.json`
- `C native_static01/artifacts.json`
- `C native_abi_static01/result.json`
- `C native_abi_static01/local_result.json`
- `C abi_static01_interpreted.json`
- `C native_entry_static01/result.json`
- `C native_entry_static01/local_result.json`
- `C native_entry_static01/entry.json`
- `R P7_app_motor_fault_native_actual_review.md`
- `R P7_app_motor_fault_abi_actual_review.md`
- `R P7_app_motor_fault_entry_actual_review.md`

Scope `files` has this exact key set (prefix `N` means
`state/analysis/P7_app_motor_fault_run_raw/`):

- `N preparation.json`
- `N run.py`, `N actions.py`, `N remote.py`
- `N test_run.py`, `N test_actions.py`, `N test_remote.py`
- `state/analysis/P7_app_motor_fault_caller_contract.md`
- `state/analysis/P7_app_motor_fault_run_contract.md`
- `R P7_app_motor_fault_caller_review.md`
- `R P7_app_motor_fault_remote_source_review.md`

These scope values are plain SHA256 strings. The preparation does not hash
itself or the scope; the scope does not hash itself. Additional fixed legacy
source/F166 pins belong to the caller implementation, not editable manifests.
The D188 input manifest's exact SHA256 remains
`d4eae97c1c47a1ce0fa24c9d7e3ae44857a565cd7b85b9c17be45143654d3eb5`.
The staged adapter pin is exactly 10518 bytes and SHA256
`d796489fc812a509f5ef1edbcd487a4a3afe4adc76960a94ba9c1d3ec075e10a`.

Action envelopes retain the old exact ten fields and add only `report_origin`:
`schema`, `action`, `run_id`, `source_sha256`, `report`, `remote_result_path`,
`full_result_bytes`, `full_result_sha256`, `first_error`, `postcheck_errors`,
`report_origin`. Schema is `app-motor-fault-action-v1`. Origin must be `returned`
for success; `durable_unattributed` identifies recovery of an existing durable
report after an outward exception, while absent reports use null. Upload report
omits stdout/stderr in the envelope, but its full-result hash/size bind the complete
durable record. Capture report stays complete and its hash/size are recomputed.
The sequence schema is `app-motor-fault-sequence-v1`; existing FAILED/COMPLETED
semantics and six-operation callback contract remain unchanged.

`root` means repository root (absolute `Path`); default is the caller's actual
repository. The inherited public seams `git`, `head`, `check_scope`, `check_adb`,
`check_output`, `write`, `transport`, `query`, `check_prerequisite`,
`check_capability`, `local`, `prerequisites`, `intent`, `action`, `finish` remain
available for controlled instance/class substitution. `stage(self)` has no
arguments and is invoked once after `admit()` and exclusive `claim()`, before
the original six-callback sequence. It writes `adapter_attempt.json` before its
first dispatch. On staging failure, local and prerequisite closure are attempted
once and final result remains FAILED, with zero upload/capture attempts.

The immutable allowlist retains the existing representation:
`frozenset((native_arguments, timeout_seconds, label), ...)`, where
`native_arguments` is a tuple. Action/prerequisite entries are `('shell','-T',
shlex.join(remote_argv))`. Stage claim uses that same shell representation;
stage push uses `('push', absolute_local_remote_py, fixed_remote_adapter_path)`.
Labels are exactly `adapter-claim`, `adapter-push`, `upload`, `capture`,
`cli-initialization`, `cli-builtin-files`, `capabilities`. `command_counts`
uses these labels. Each staging/action label is limited to one invocation;
each prerequisite is limited to three. Command comparison includes exact timeout.

Capability reply is exactly `{boot_id,uid,no_bytecode,bz2,base85,adapter_bytes,
adapter_sha256,source_sha256,source_files}`. First five fields keep the original
types/requirements; adapter fields equal the fixed pin; source_sha256 equals the
fixed D188 source. `source_files` maps exact projected remote names to
`{bytes,sha256}`; names, actual lengths and hashes match current pinned projected
source bytes. The private unchanged static helper's `source_action` performs the
descriptor-bound before/after tree check and full source digest calculation.
Only its private SOURCE/SKETCH constants change. Capability reply limit is
65536 bytes; each of the other two inventory replies retains 1MiB.

Stage claim reply is exactly `{uid,user,boot_id,cli_sha256,free_bytes,conflicts}`:
integer UID1000, user `arduino`, fresh scope boot, original pinned CLI SHA256,
integer free_bytes at least 1073741824, and empty conflicts list. It is obtained
through the original checked identity preamble followed by exclusive mkdir.
Stage push requires integer returncode0; its raw stdout/stderr are retained as
transport evidence rather than treated as JSON. Module-level `helpers`,
`pinned_file`, `compiler` and `actions` expose the inherited fixture seams;
callers may substitute them only in controlled host tests.

`InertRun.source_inventory(self)` is the public read seam for the unchanged D188
local source-name walk. Its native implementation checks the actual three source
roots and rejects nonplain/reparse entries; tests may substitute the exact names
derived from the real pinned manifest without duplicating its 127 source files.
All 127 individual pin reads and the original source projection/hash check remain
mandatory even with that test-only name-walk substitution.

Direct calls to the public `transport` seam cannot bypass staging order: neither
staging label may dispatch before the durable `adapter_attempt.json` write has
completed. Push additionally requires the exact successful exclusive claim reply.
Each staging label is consumed before delegation to the existing transport, so
an error before or during its native child still forbids a second dispatch.
Final diagnostics add `staging` with boolean `started`, `intent_ready`,
`claim_verified`, `ready` and a sorted `dispatched` list. A completed result
requires both staging labels and all four flags true.
