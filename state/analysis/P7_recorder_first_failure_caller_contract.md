D233 fresh-image projection: the historical compile HEAD is
ce4e69390d21d9a91231581a186be4a63213135e; source is
29cb1e76193e4b7c562d1fd842039f61367a82c2651a2303c09518d35a0c7ce9.
Attempt 07f19e32c483cebadecaa63f4d6d720f / session 572412568535289530
uses 145 exact inputs and 110 staged files. The package is 55376 bytes, SHA256
b13a32b5e92993a49f165b907d5d6036fa933e1680bb23ff2738620b294fd584.
The separate collector HEAD is pinned after preparation and review. Execute
from the isolated sumox-recorder-fresh-diagnosis-20260927 worktree; MAIN stays
frozen. Under root's D051 scheduling authorization, reviewed offline ELF queries
on closed compiled files may overlap the bounded receiver. Passive MCU capture
still requires delivery/receiver closure. No MCU, UART, OpenOCD, cleanup, build
or upload effect is permitted in file-only work. A passed compile does not
establish the loaded image.

Only fixed identity/artifact/path/inventory data and layout projections differ
from D230. One fresh FailureRecord window adds reason, site, cleanup,
cleanup_ownership, packet_offset, packet_size, payload_size and
ownership_evaluated. The new FailureSite and CleanupDisposition enums use exact
D231 declarations. Query every type, enum, offset and extent from this image;
reuse no D228 addresses or observed values. First-failure data remains raw and
non-atomic with coherence UNPROVEN. Packet progress is not acknowledged payload;
NOT_ATTEMPTED and ownership_evaluated=false must not imply attempted cleanup.
Full flash checks still precede all SRAM and close afterward. No cause is
inferred before observation. Existing lifecycle, transport, descriptor, owner,
source comparison, budgets and strict invalid-bool/enum behavior are unchanged.

# D233 fixed recorder passive capture caller

This projects the accepted D230 caller to the fresh D233 ABI and capture helper.
Original D230 tools, contracts and evidence remain unchanged. No MCU action is part of
this preparation. Root owns native execution after source/host acceptance.

tools/run_recorder_first_failure_capture.py uses only the D233 source29cb1e76,
attempt07f19e32c483ceba and the initial capture helper576efd49. It accepts one
fresh file-only ABI whose original four commands and exact12-file identity set,
board/local closing checks and recomputed summary agree. ABI size/offset facts
remain distinct from MCU observations. The accepted ABI hash is an explicit
root input; repeated binding preparation refuses existing owner files.

The offline command is:
`python -B tools/run_recorder_first_failure_capture.py --prepare-bindings --abi-sha256 <accepted SHA256>`.
It writes exactly three absent-only local files under P7_recorder_first_failure_raw:
capture_inputs01.json, capture_scope01.json and capture_adapter01.py. The adapter
is the unchanged reviewed helper plus a literal fixed-spec wrapper. It uses no
caller-provided code and remains at most1MiB. Scope/data pin all ABI inputs,
compile records and current caller/helper/contract bytes. Root commits these
mechanically derived files before the same-HEAD check/execute sequence:
`python -B tools/run_recorder_first_failure_capture.py --check-only --reviewed-head <HEAD>`
then exactly one `--execute --reviewed-head <same HEAD>`.

The local owner is P7_recorder_first_failure_raw/native_capture01. Remote staging is
/home/arduino/sumox26_codex_build/recorder-07f19e32c483ceba-failure-capture01-adapter/remote.py;
the separate capture owner omits the -adapter suffix. Both are absent-only and
consumed after partial work. There is no cleanup or retry branch.

Reuse D219 CaptureRun and inherited D212 owners privately, retaining staging,
durable intents, fixed ADB/hash/target, ten-transport bound, command allowlist,
baseline prerequisite checks, source/adapter capabilities before and after,
exclusive output/descriptor identity and first/closing error preservation.
Only the pushed local file and sequence result schema are projected in the
D219 source. New narrow overrides bind scope/inputs to the current recorder and
verify/export the small status bundle. The current145 source inputs are checked
against historical compile HEADce4e6939 and remapped to the110 exact staged
files including the session header; source capabilities use /recorder, not
the older /app path. The collector HEAD remains a separate exact current pin.

The D219 remote bootstrap is reused with fixed run/source/schema/adapter pins;
it reads installed p0_capture and rechecks the staged adapter and installed
parser at closure. The D219 read-only retrieval body is reused with fresh
fixed PLAN/COUNTS and the selected two SRAM snapshots. Its owner/file paths,
identity guards, per-file hashes, independent closing reads and1MiB response
bound remain. Timing separation is validated by the local caller; the original
wait=None predicate is replaced because this capture has two separated samples.
No B4 addresses, old frame decoder or upload action is reachable in the new
command allowlist. Full flash images remain in the durable remote owner;
retrieval returns the checked report and all selected status bytes.

Successful export requires exact envelope/report identities, command/read
counts, valid monotonic timing and two-second bracket, matching flash hashes,
every raw-file hash and a local recomputation equal to the remote analysis.
Raw statuses preserve invalid bool/enum errors and coherence UNPROVEN. An
unsuccessful capture is retained at its remote owner and in returned error
evidence; it cannot become a successful local bundle. No session match or
status value is promoted into a causal, physical, motor or phase-gate claim.
