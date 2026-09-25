# D179 fixed inert caller: host preparation only

Complete the missing D177 caller while the board is disconnected. No real scope,
owner directory or device operation is created by this task. The eventual caller
requires an explicit committed fresh scope; historical action_preparation.json is
artifact provenance only. No motor-capable firmware, old manifest/global repinning,
compile/stage action, decoder, generic launcher framework or automatic retry.

## Ownership and public API

New implementation: state/analysis/P7_motor_fault_raw/inert_run.py.
Public class InertRun(reviewed_head, *, root=None), methods admit(), claim(),
local(), prerequisites(), intent(action, predecessor), action(name), finish(result),
run(). Public main(argv=None) supports exactly --execute --reviewed-head HEX40 or
--check-only --reviewed-head HEX40; mutually exclusive and required. Check-only
calls admit only: no owner creation or device command. Invalid arguments exit2;
missing/invalid scope or operational failure exits1; success/check-only exits0.
Import and construction may read pinned local Python sources, but never invoke a
process, contact hardware, modify environment/files or execute module __main__.
root defaults to this checkout; optional root supports controlled isolated tests
and verified checkouts, not arbitrary source or command overrides.

Fixed identity: D177 RUN_ID motor-fault-8f592937-run01, SOURCE8f592937...f36 and
BOARD2629958581. Fixed local owner:
state/analysis/P7_motor_fault_raw/native_inert_run01.
Fixed scope: state/analysis/P7_motor_fault_raw/inert_run01_scope.json.
Scope is strict JSON <=65536B, rejects duplicate/nonfinite values, exact keys:
schema='motor-fault-native-scope-v1',run_id,board,source_sha256,expected_identity,files.
files maps exactly these four repository-relative names to lowercase SHA256:
- state/analysis/P7_motor_fault_raw/inert_run.py
- state/analysis/P7_motor_fault_raw/test_inert_run.py
- state/analysis/P7_motor_fault_caller_contract.md
- state/reviews/P7_motor_fault_caller_review.md
The scope is byte-identical to its committed version at reviewed_head, HEAD matches
that lowercase40hex commit, and tracked changes are absent. Untracked owned results
are expected. All scoped/fixed/provenance files must match their pinned bytes.
Expected identity has exactly the same fields and non-boot values as BOTH pinned
CLI baseline identities; boot_id is a nonempty canonical lowercase UUID provided
by later fresh admission. No actual identity or scope is invented during host work.

Reuse pinned startup_run.py helpers safe_path/pinned_file and NativeRun's git,
head,check_scope,check_output,write,local methods where practical by composition
or explicit aliases. Do not inherit/expose or invoke its old native scopes,
admit/claim/payload/action/run/decoder. Its local method can use runner=probe=None
and fixed profile['scope']; maintain its independent local-error checks. Use the
existing check_output/write ownership pattern (device/inode before/after,
exclusive files, flush/fsync). No-follow path/reparse checks are path checks,
not a claim of immunity to malicious concurrent filesystem replacement.

admit is local-only: Python startup -B and current dont_write_bytecode=True,
reviewed commit/scope, exact fixed source bytes and preparation provenance,
plain output ancestry, absent output via lexists, pinned ADB file checked locally,
then prepare bounded immutable command choices. Never mutate SUMO_* or module
BOOT/ROOT/dependency pins. Re-run local pin/HEAD/scope checks before claim/actions.
claim exclusively creates the fixed owner, stores device/inode and writes inputs.json
with actual scope hash, expected identity, all input hashes, exact command hashes,
Windows unit sizes and remote output identities BEFORE any transport. A failed
claim retains partial files, propagates failure and executes no device callbacks.
Repeated claim/run/owner reuse fails; no deletion, overwrite or implicit staging.

## Fixed sources and composition

Pin these observed bytes literally (plus byte counts as useful):
startup_run.py c95888353c9d85c5d9b0e545553a9e9dcde372b5b313102dd14240ce38db4e0c
compile_motor_fault.py 84efd00611b3a6a8129655005930ff58e555221f6bd8d88a23c7fa1c4381ac0d
inert_actions.py 8ffb65c0f1284f261ae1237bcf260e866176e83433a3538908780962513f1104
action_preparation.json 6b5df73026e11914c811ab274054bf4d26ff6b8438e8c9a86ad1ba9bce802835
static_remote.py 8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8
capture_remote.py 95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e
upload_remote.py e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1
cli_initialization_inventory.json aaa2c307b7ed1b8d7e00a737447a03a63a78cd4b7fb2145142b20e9501da1e62
cli_builtin_files_inventory.json a364beb814b36b9c56328b54a9de5fa0f4ad80a67003d40c7cc994a1917ba2cb
Paths are existing paths mapped in P7_motor_fault_capture_plan_notes.md and
D177 contract. Load only hash-checked bytes as non-__main__ modules, registering
before execution. Historical module code/manifests remain untouched.

Verify all six preparation provenance paths/hashes/sizes as local inputs too.
Take exact upload/capture bindings from the pinned preparation via deep copy;
replace ONLY boot_id with the new scope identity. Existing identity/artifact,
UID1000, fixed schemas/run/source/output, file/directory/absence expectations and
limits remain unchanged. Use D177 build_command with actual helper/support/upload
bytes, not substitutes. Each full Windows command must fit30000 UTF16 units
INCLUDING the trailing NUL used by CompileOnce.transport. Inputs unchanged.

## Bounded transport and fresh prerequisites

Reuse CompileOnce.transport UNBOUND on this owner (output,counter) only. Never
construct CompileOnce or invoke its consumed run/stage/local/manifests. Fixed ADB
path/hash/serial remain unchanged. Wrap it with an exact argument/timeout/label
allowlist, output owner checks and maximum11 transport calls; no shell command,
port, filename or target option supplied by a scope. Record full causal exception
chains (at most8 unique links, explicit truncation if more) in transport_errors;
preserve the actual thrown exception, raw outputs and any independent final errors.
A host timeout does not prove remote reap or justify retry.

prerequisites independently tries all three read-only queries, retaining the first
failure and every later failure before raising. Queries repeat before each action
and during final closure under D177, not as retries of a failed native action:
1. Replay the exact argv of cli_initialization_inventory.json.
2. Replay the exact argv of cli_builtin_files_inventory.json.
For each: no stderr, returncode builtin int0, stdout bytes <=1MiB, strict JSON,
status COLLECTED. Require ENTIRE identity==scope.expected_identity. Compare all
remaining result content with the historical baseline via the existing projection
(excludes only mtime_ns/ctime_ns); omit only the already-checked top-level identity.
Require expected non-boot identity values to equal both baselines at admission.
Do not call CompileOnce.prerequisites, which pins a consumed boot.
3. Fixed isolated Python -I -B capability query under D177 env-i prefix; 60s alarm,
read /proc/sys/kernel/random/boot_id, UID, current/startup no-bytecode flags, check
bz2 and canonical base85 roundtrips on a fixed literal. Return exact keys boot_id,
uid,no_bytecode,bz2,base85; require expected boot, int1000 and literal True flags.
No file mutation, child executable, MCU access or configurable code in this query.
Each query uses60s local timeout as existing baseline checks; capability stdout
<=4096B. Native action timeouts remain upload195s/capture630s; reply<=65536B,
no stderr/nonzero return, strict JSON. Allowlist labels are fixed printable slugs.

## One attempt, conditional capture, durable closure

run performs admit,claim, then D177 run_actions with exactly its six callbacks.
intent validates exact action/order and its checked predecessor, writes an exclusive
<action>_attempt.json containing source/scope/command identity and predecessor hash,
then records intent. action rejects missing/repeated intent, marks dispatch consumed
BEFORE transport, and performs the sole fixed selected remote command. D177 validates
the returned envelope; raw transport bytes remain even if JSON/admission fails.
Successful run has exactly11 transports, one upload, one capture. No decode or
claim that COLLECTED means runtime success/atomicity/acceptance is permitted.

finish tries final_checks.json then result.json independently; diagnostic records
contain local/Git/prerequisite/transport errors and counters. Preserve result's
original first_error. A closure/counter/write error marks FAILED and is recorded
as additional evidence before attempting result.json; result cannot be saved as
COMPLETED after a preceding final-check write failure. Keep partial files and
raise first finish error after both writes have been attempted. D177 then attaches
sequence_result on the exception; retain that behavior. Success requires expected
counter/action sets and all postchecks/writes. No blanket retry or repair.

## Host acceptance and limits

Separate test author owns test_inert_run.py from this contract and existing public
helpers/fixture contracts, without reading the new implementation. Freeze before
execution. Controlled transport/Git/ADB substitutes only; small RAM fixtures and
Python-B. Cover scope/commit/pin/identity drift, missing scope before owner/devices,
exclusive claim/reuse/link paths, mutation/intent/command limits, fresh boot vs
non-boot changes, strict bounded prerequisite/capability replies, independent checks,
exact successful sequence, failures at each action/closure, causality/partial outputs
and CLI/check-only. Reuse established fixtures where appropriate; no copied runner
framework. Independent source review required; do not change established assertions.

Actual production command composition is checked locally. No real scope, owner,
board query, upload, capture, firmware rebuild, pin change or gate is authorized
by this host-only preparation. Fresh scope/admission and source review are still
required when hardware returns, including exact active artifact verification.
