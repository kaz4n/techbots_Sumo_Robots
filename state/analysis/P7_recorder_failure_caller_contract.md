# D230 fixed recorder passive capture caller

This completes the second software step while leaving the accepted initial ABI,
remote capture helper and original contract unchanged. No MCU action is part of
this preparation. Root owns native execution after source/host acceptance.

tools/run_recorder_failure_capture.py uses only the D228 source702ad99e,
attempt377911abefabd094 and the initial capture helper13fc387d. It accepts one
fresh file-only ABI whose original four commands and exact12-file identity set,
board/local closing checks and recomputed summary agree. ABI size/offset facts
remain distinct from MCU observations. The accepted ABI hash is an explicit
root input; repeated binding preparation refuses existing owner files.

The offline command is:
`python -B tools/run_recorder_failure_capture.py --prepare-bindings --abi-sha256 <accepted SHA256>`.
It writes exactly three absent-only local files under P7_recorder_failure_raw:
capture_inputs01.json, capture_scope01.json and capture_adapter01.py. The adapter
is the unchanged reviewed helper plus a literal fixed-spec wrapper. It uses no
caller-provided code and remains at most1MiB. Scope/data pin all ABI inputs,
compile records and current caller/helper/contract bytes. Root commits these
mechanically derived files before the same-HEAD check/execute sequence:
`python -B tools/run_recorder_failure_capture.py --check-only --reviewed-head <HEAD>`
then exactly one `--execute --reviewed-head <same HEAD>`.

The local owner is P7_recorder_failure_raw/native_capture01. Remote staging is
/home/arduino/sumox26_codex_build/recorder-377911abefabd094-failure-capture01-adapter/remote.py;
the separate capture owner omits the -adapter suffix. Both are absent-only and
consumed after partial work. There is no cleanup or retry branch.

Reuse D219 CaptureRun and inherited D212 owners privately, retaining staging,
durable intents, fixed ADB/hash/target, ten-transport bound, command allowlist,
baseline prerequisite checks, source/adapter capabilities before and after,
exclusive output/descriptor identity and first/closing error preservation.
Only the pushed local file and sequence result schema are projected in the
D219 source. New narrow overrides bind scope/inputs to the current recorder and
verify/export the small status bundle. The current144 source inputs are checked
against historical compile HEAD004dc7cf and remapped to the109 exact staged
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
