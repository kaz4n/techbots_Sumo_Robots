# Explicit run02 ownership: host contract

D156/run01 is terminal. D157 fixes the upload file limit but its old ownership
cannot be reused. Extend the existing three modules narrowly; do not clone them.
This contract permits host preparation only, with a separately identified native
scope required after review. The known /tmp/remoteocd fragment still blocks upload.

Remote wrappers gain optional explicit bindings and run_id keywords. Defaults
retain static-fcddbd8e-run01 and the legacy BINDINGS fixture/entry behavior.
The only additional allowed identity is static-fcddbd8e-run02; reject other values,
non-string identities and mismatched output or run binding before any claim.
Exact output names are static-startup-fcddbd8e-runNN-upload/capture beneath the
existing PARENT, with NN either01 or02 matching that instance. Copy validated
bindings per instance; derive its output basename only from that checked identity.
No arbitrary destination, source, packet, command, timeout or policy override.

Public APIs:
- upload_loader(..., bindings=None, run_id='static-fcddbd8e-run01').
- collect(..., bindings=None, run_id='static-fcddbd8e-run01').
- Existing upload(..., bindings=None) remains fixed to legacy run01 and the
  original file cap. Only explicit bindings is additive; no run_id override.

Legacy helpers and tests remain usable unchanged. The collector acquisition,
limits, interpretation and failure semantics do not change. Its source digest
changes only for explicit instance ownership; retain original D153 source in Git.
No new-API use may modify module BINDINGS, OUTPUT_NAME or dependency globals.

The host launcher gains a closed selection:
NativeRun(reviewed_head, *, run='run01'), native_run(reviewed_head, *, run='run01')
and an optional --run argument with exactly run01/run02 choices. Default run01
retains its old scope, local output and old dependency pins, hence must refuse
changed helpers. For run02, use the unchanged original binding files as pinned
inputs; transform only run_id/output in memory. Select upload_loader explicitly.
Use native_run02_scope.json, local native_run02 and remote run02 owners. Retain
same original D144 artifact run, source, board, boot, fixed six command forms,
14 successful-path transport calls, budgets and guarded one-shot orchestration.
The old native scope and evidence remain untouched and cannot be resumed.

Report validation check_upload/check_capture/report_identity and orchestration
accept a keyword run_id defaulting to the legacy identity; validate exact closed
identity and reject cross-run reports before admitting the next action. Expected
identity flows per instance through claims, intents, payloads and report checks.
No global mutation or substitution of a report's identity for validation.

Run02 selects exact current source hashes for only upload_remote/capture_remote,
retaining all other dependency pins. Its scope files bind current launcher,
new independent ownership tests, this contract and the separate code/review
artifact. A committed scope plus exact reviewed HEAD is still required for any
native entry. Do not create that scope as part of this host implementation.
Bootstrap passes explicit bindings/run_id, never reassigns globals; legacy
upload dispatch remains upload(bindings=...), new run02 selects upload_loader(). Capture
uses the same collect API. Payloads remain bounded and command length <=30000.

For independent tests, expose these small pure selection helpers:
- run_profile(run): accept exact strings run01/run02, return a fresh dictionary
  with keys run_id, output_name, scope, dependencies, scope_files. output_name is
  native_run01/native_run02; scope is RAW + native_runNN_scope.json. dependencies
  is a fresh dictionary with the same keys as historical DEPENDENCIES; run01
  values remain historical, run02 changes only uploader and collector digests
  to the current reviewed source. scope_files is the corresponding tuple.
  NativeRun stores this as profile and uses it without mutating module globals.
- project_bindings(action, bindings, *, run_id=RUN_ID): action upload/capture,
  original run01 binding dictionary, exact closed target identity. Return a deep
  copy changing only run_id and output. Require original source/run/output match
  SOURCE, run01 and the exact original action path; remote complete validation
  remains unchanged. Reject invalid action/run or wrong original identities.
- report_identity(report, schema, status, *, run_id=RUN_ID), with check_upload,
  check_capture and orchestrate forwarding their same keyword consistently.
Run02 scope_files is exactly (RAW+'startup_run.py', RAW+'test_run02_ownership.py',
'state/analysis/P7_startup_run02_contract.md',
'state/reviews/P7_startup_run02_review.md'). Legacy SCOPE_FILES is unchanged.
NativeRun constructor validates run before any filesystem/process operation;
output is self.root/RAW/profile['output_name']. Pure helpers do no I/O.

Bootstrap payload JSON keeps sources (helper/support/upload or decoder module
source strings), hashes (same module names to SHA256), bindings (JSON string);
add run_id from the selected profile. Capture also keeps parser_path and
parser_sha256. Bootstrap validates the closed run_id, selects upload for run01
or upload_loader for run02, passing explicit bindings (and run_id only where
accepted). Capture passes bindings/run_id to collect. No scope inferred from
report identity. build_command(action, payload_bytes) retains its original API.
The prior dependency pin baseline is preserved in native_run01/inputs.json
(dependency_pins, excluding the four D144 runs/f0220228320c4b2aa20c3e5e8264c813/
0001.json, 0009.json, 0017.json and 0021.json receipt entries, leaving12 keys);
historical scope_files are the keys of native_run01_scope.json
files. These may serve as source-independent expected data for companion tests.

Tests must derive from this public contract before reading new bodies. Exercise
run02 upload/capture success with controlled commands, reports and distinct owned
paths; simultaneous/alternating instance isolation; consumed-output rejection;
wrong run, output, source and cross-run report rejection; no mutation of legacy
bindings/constants; run02 binding projection changes only two fields; correct
bootstrap/API dispatch, closed launcher scope/output selection and old pins.
Run existing suites unchanged to check legacy behavior. Keep fixture work in
RAM, Python -B and compact evidence; no new binary or source snapshots.

This explicitly permits the narrow ownership parameterization of D153/D154/D155;
all historical source, oracles, scopes and receipts remain evidence in Git.
No cleanup, upload, reset, acquisition, production firmware change or phase gate
is granted by this host contract. Native scope and exact residue disposition
must be reviewed separately; never bypass the preexisting-temp admission guard.
