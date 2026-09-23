# D113 single Linux timeout smoke scope

Status: proposed and locally source-reviewed; **not executed**. Root must inspect this fixed runner before invocation. Reused same-model review; no hardware/gate approval. Run only while the coordinator serializes every MCU/upload/reset/transmitter action; ordinary compile-only work does not change this scope.

Target is the already identified UNO Q USB/ADB serial `2629958581` (F-062 and D104 identified run), refreshed by root's `P2_app_build_raw/d114_initial_readonly_inventory.*`; its missing-rsync result does not affect this ADB-only operation. No SSH fallback, discovery selection, privilege escalation or transport repair. The runner uses native Windows Python313 and the existing Arduino ADB32.0.0 executable; SHA256 pins include its three DLLs. ADB `get-state` must return exactly `device` with empty stderr; a mismatch/server diagnostic stops the run.

An exclusive host run directory is named by **one new uuid.uuid4().hex**, generated once per invocation. Before any board command, copy and hash three files into its private tools directory; explicitly select that script/PYTHONPATH and disable bytecode writes:

| File | SHA256 |
|---|---|
| dump_match.py | `5a78257ac02733231958477ff7e139bb3a0987ce0fb893446132cc9b05853717` |
| board_tool.py, from immutable reviewer/board_tool.py.baseline | `cce5ef3baa8430c26192ee6627d093af02a73a80293f87511b2dcca56168387d` |
| validate_csv_bundle.py | `1c4781fdd0f77a610998644db610bf6adf5a2373d4f32f3ec7ca486185ff52f2` |

The baseline transport helper avoids the concurrently changing D114 staging routes. Its six used transport functions, imports, ROOT definition and SSH_OPTIONS are AST-identical to the shared helper at snapshot creation; that comparison's actual full hash is recorded. No staging/compile/upload function is called. The reviewed D113 source and contract37dca22f remain exact.

Sequence in `smoke_runner.py`:

1. Record intent, source/executable hashes and source-copy proof, then one5s ADB identity query. One5s read-only Linux preflight records boot ID/current UID/Python, safe `/tmp`, renameat2 availability, exact router and router-serial service MainPID/start time/NRestarts/active state, and only Monitor-related IPv4 TCP rows from a1MiB/4096-row bounded snapshot. No socket is opened by preflight; current services must be running, their loopback7500 listener and existing established client must exist, and the new ticket path must be absent. The two `systemctl show` unit names are fixed; its subprocess has a2s limit. No root process fd or UART is opened.
2. Launch exactly one private `dump_match.py --connection-ticket T --timeout 12 --output-dir <exclusive-run>/capture`. It alone creates the Linux `/tmp/sumox26-dump-connection-T` directory/receipts and one receive-only TCP127.0.0.1:7500 socket. It sends no application bytes. No transmitter, mon/RPC call, firmware or service action is started.
3. Approximately3s after host capture launch, issue exactly one private `--observe-connection T`. This is one bounded5s board query. A valid PENDING/UNKNOWN/EXPIRED/TERMINAL result here is preserved and makes the smoke inconclusive; it does not trigger another query or a changed delay.
4. Let the original capture complete its own12s deadline,27s host receive bound and one automatic final5s metadata query. Then issue exactly one explicit terminal observation and one matching5s read-only postflight. Thus the smoke adds **three metadata queries total**: live, capture's required final query, and explicit terminal. It never reconnects/retries or removes a ticket.

The one-off host harness uses40s for the capture CLI and10s for each explicit observation CLI as exceptional outer guards; these are not receiver deadline extensions. A guard expiry kills only that local CLI through subprocess.run timeout, records failure/inconclusive, and makes **no claim** that its remote process was killed or its socket closed. No remote kill/recovery follows. Without host/filesystem failure the fixed command wait ceilings total at most65s (live overlaps capture), plus bounded local bookkeeping. No persistent manager or production transport framework is introduced.

Expected evidence: live observation exit0 with CONNECTED; explicit terminal exit0 with TERMINAL/TIMEOUT; their claim/connection identities match. Claim deadline-start equals12,000,000,000ns and terminal closed time is at/after it. Terminal observed bytes and local retained wire are zero. Capture CLI **exit1 is expected**, primary error TRANSPORT, remote receive exit1 without host timeout, exactly one retained `.partial`, no successful CSV/capture bundle. Its automatic query succeeds, but capture's `connection_evidence` has state null/error CONNECTION_METADATA because TIMEOUT does not satisfy END_OBSERVED; this is expected capture-success rejection, not malformed stored metadata. The same terminal record must appear in the separate valid terminal observation.

PASS additionally requires stable Linux boot/UID, unchanged router/socat service identities and restart counts, and every pre-existing Monitor established/listening socket still present with the same endpoints/inode/state. The smoke's own client inode must no longer be established. Every observation retains router_registration UNKNOWN and both permission fields false. No fresh MCU read is added; “unchanged MCU” means this runner issued no MCU action and the coordinator serialized other work, not a new flash/readback proof.

Any source/identity/preflight mismatch stops before capture. Any unexpected byte, early END/EOF, publication/query/transport failure, non-CONNECTED single live observation, outer timeout, changed service/original socket, mismatched claim, or missing/invalid timeout receipt prevents PASS. Preserve actual stdout/stderr, argv, host times, partial wire/error JSON, all observation envelopes, pre/post metadata and a local SHA256 manifest; no cleanup, inferred success or automatic retry. An independently reviewed later attempt would use a new UUID.

No result from this smoke proves registration inside the router, clean UART framing, actual MCU log transmission, a physical sensor or motor, calibrated MCU time, or any human phase gate.
