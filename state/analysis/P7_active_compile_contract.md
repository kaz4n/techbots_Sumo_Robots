# D171: active diagnostic compile ownership

Extend only the existing P7_motor_fault_raw/compile_motor_fault.py caller.
D167's closed selector gains one exact value `active01`; old compile01/02
behavior, manifests, receipts and assertions stay unchanged. This is host
preparation; a later identified native scope is required for compilation.

Public API: `CompileOnce(*, run_id='compile01')`, exact str values compile01,
compile02 and active01 only. `parse_request` retains both old forms and adds
exactly `['--execute', '--run', 'active01']`; all other spellings/orders/types
remain rejected before constructing an instance or invoking transport.

Each instance keeps its old public paths plus these explicit fields:

| Field | compile01/02 | active01 |
|---|---|---|
| output | unchanged native_compile01/02 | RAW/native_active01 |
| inputs_path | unchanged compile_inputs.json/compile_inputs02.json | RAW/compile_inputs_active01.json |
| remote | unchanged motor-fault-compile01/02 | same remote parent/motor-fault-active01 |
| sketch | remote/motor_fault | remote/motor_fault |
| stage_path | legacy STAGE | ROOT/build/stage/motor-fault-active01/motor_fault |
| stage_attempt | None | motor-fault-active01 |
| stage_owner | legacy STAGE | ROOT/build/stage/motor-fault-active01 |
| flags | -DMATCH=0 -DMOTORS_ALLOWED=0 | -DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1 |

`run` refuses any existing stage_owner before output creation or board contact;
`stage` repeats this check before copying or transport. Active staging calls
`board.stage('bench/motor_fault', attempt='motor-fault-active01')` and verifies
the exact returned stage_path and complete reviewed file map. Legacy calls
retain their existing one-argument form. Existing active owner (file/directory/
link) fails, even when its motor_fault child is absent. Never delete/reuse owners.

Every later local hash check, source hash and push source uses stage_path; every
remote path/receipt/manifest/cache uses its selected instance. Compilation uses
the selected exact flags with unchanged default/dynamic FQBN/startup/project and
checked build policy. Keep per-instance selection isolated; no global rebinding,
new wrapper, flags override, source overlay, upload/reset/read or automatic retry.

Preserve ENV, IDENTITY, REMOTE_CHILD and extracted_wait exactly, together with
all existing input, tool, prerequisite, process, deadline/reap, output-bound,
recipe/artifact and independent final checks. Failed partial attempts/evidence
remain. Old manifests must reject changed caller/source; never repin them.

Independent tests use controlled local fixtures: exact selectors/paths/flags,
legacy compatibility, interleaved instances, owner refusal before contact,
explicit staging route/wrong result/map rejection, source/push/compile routing,
manifest/cache binding and all final checks on failure. Freeze expectations
before execution. Preserve old tests and child machinery hashes. No actual
source stage or board command during host validation.
