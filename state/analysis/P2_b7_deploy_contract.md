# D245 B7 guarded deployment preparation

Under D051 and the explicit D244 B7 exception, prepare the missing deployment
route. No actual upload, MCU operation, setup grant, wiring assumption or human
gate is authorized by this software work. D244 compilation remains unchanged.

Add only `tools/b7_app_upload.py` and `tools/deploy_b7_app.py`, reusing the checked
D227 uploader and caller machinery. Existing D227 files remain byte-identical.
The native adapter admits only the exact string `b7_brownout`, exact built-in
motor integer0/1, and the existing bounded token/source/run-ID grammar. Keep
the commissioning owner/path layout, static/default FQBN, package/export/source
bindings, descriptor protection, payload bounds and result checks unchanged.

The deployment caller exposes the D227 public API/CLI with a new caller,
adapter, contract and owner identity. Command:
`python -I -B tools/deploy_b7_app.py --check-only|--execute --scope RELATIVE_JSON
--reviewed-head FULL_HEAD`. No arbitrary profile, flags, paths or identified
delivery mode is added. Execute is implemented for a future fully qualified
scope, but is not used during this preparation.

Load the exact pinned D227 source into a private namespace and apply bounded
checked substitutions, or an equivalently checked private adapter. Bind the
new compiler `tools/compile_b7_app.py` and policy
`tools/b7_app_static_policy.py`. Preserve complete checked-code Git blob closure;
the compiler's `_checked_base(root)._head_bytes` supplies the already hash-checked
D222 implementation. Never omit a source closure check because the new compiler
lacks a facade method. Private selections cannot mutate legacy module globals.

Only B7 maps to `GATE P1 PASS`. M1 qualification is exactly operation `stand`;
authorization is exactly fresh `STAND OK`, bound to the complete request digest
and existing strict one-hour window. `RING OK` is rejected. Keep all enabled
source-grant evidence, required opponent/ADC/QTR grants, configured nonoverlapping
A1 windows and all eight physical qualification checks. Keep complete source,
configuration and image linkage. M0 must have absent grants and null physical
qualification/authorization; it is not an operational B7 test.

Keep all eleven compile receipt bindings, exact B7 flags, one query/one compiler,
nine successful closing checks, artifact/package metadata and current clean
reviewed HEAD. Preserve refusal of source overrides, boot/UID/tool changes,
active conflicts, existing scratch or consumed owners. Preserve bounded single
upload, child reaping, before/after observations, available closing checks and
original-error precedence. Do not add retry, rollback or scratch cleanup. An
attempted failure remains FAILED/UNKNOWN as applicable with original evidence.

Verification is host-only: independent exact B7 identity/metadata fixtures,
rejection of all other profiles and RING authorization, M0 truth, qualified M1
STAND with each inherited setup/gate/receipt guard retained, compiler Git closure,
private namespace isolation and a controlled upload lifecycle. Freeze those
expectations before executing the new subjects. Independent read-only review
must close material findings. No real deployment scope, board call or upload is
needed to test the new route. Successful future upload would still not prove
actual cycles, electrical behavior, half-charge or uninterrupted uptime.
