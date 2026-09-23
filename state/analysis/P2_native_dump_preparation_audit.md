# Native dump preparation: existing APIs and evidence limits

Read-only audit,2026-09-24. Only cached local artifacts and public Linux API
documentation were read; no board connection, RPC, UART open/read/write, service
action, MCU operation or implementation occurred. This qualifies the earlier
`P2_native_dump_bare_feasibility.md`; it does not adopt a new run policy.

**Result:** the installed router exposes the necessary close/open controls, but
there is no existing API that atomically proves close, exclusive ownership,
input purge, decoder replacement and successful reopen. A narrowly scoped
preparation helper is plausible; it must refuse to claim READY while the present
owner-visibility and installed-driver gaps remain. Extra external hardware is
not the obstacle. Neither D113 CONNECTED nor a successful close/open CLI exit
establishes `SetupGrant::framing_clean`.

## Exact source used

Local source prefixes below are:

- `R=state/analysis/P2_dump_raw/native/router/`, pinned router v0.10.0 commit
  `b92ba75a62781a7b79d4bc0429a499542f939233`. Rehashed `R/main.go` SHA256
  `a19b4188b6b1301385ac95dff269221ba18a19ba27795f49b933c03f1ec45ed8`,
  CLI `R/cmd/arduino-router-cli/main.go`
  `fc411b9b61ce6a6b977371e0f5902fa9441feb142fc4e3f05d7e7470fc92f6a5`.
- `S=state/analysis/P2_recorder_bench_raw/native/`, dependency go-serial v1.6.4.
  Rehashed `S/serial_unix.go`
  `e0095afd13642860b27a2decc2827c346356185acbadc9603dcc55ec21091f1c`;
  `S/serial_linux.go`
  `d3e02e43251c295573efdec91428b7289823aacf2bc1d6df80132ee1079d54a6`.
- `B=state/analysis/P2_native_dump_bare_raw/read_only/`: cached September24
  Linux receipts, not fresh process observations. `05_known_files.json` binds
  `/usr/bin/arduino-router` to `3eacd38a...1a19` and
  `/usr/bin/arduino-router-cli` to `1fd348a0...c76`; matching-tag sources are not
  a reproducible-build proof of those binaries.
- Actual current receiver `tools/dump_match.py` rehashes to
  `5a78257ac02733231958477ff7e139bb3a0987ce0fb893446132cc9b05853717`.
  D113's actual receive-only smoke was CONNECTED then TIMEOUT/zero bytes
  (`P2_dump_receiver_arm_validation.md:42-50`), not native UART delivery.

## What the existing operations actually do

| Operation | Source-level conclusion and limit |
|---|---|
| Local serial close RPC | `R/main.go:204-228`: `$/serial/close` accepts exactly one string matching configured `/dev/ttyHS1`. It closes the signal and waits on a condition variable only when that signal was non-nil. The serial loop closes the port and waits for routerExit before broadcasting closed (`:229-270`). This is useful completion evidence for a single controlled transition; it has no deadline. If the signal is already nil, a second call returns true immediately, even if an earlier close is still pending. Never use a retry after timeout as completion proof. Concurrent open/close clients also invalidate that reasoning. |
| Local serial open RPC | `R/main.go:180-203`: `$/serial/open` sets a signal/broadcasts and replies true. Actual `serial.Open` occurs later in another goroutine (`:239-262`); failure waits/retries and can sleep5s. ACK means request accepted, not fd open or decoder running. No serial-status/holder API is registered here. |
| New decoder | `R/msgpackrpc/connection.go:292-317` creates a new MessagePack decoder for each Connection.Run. Resetting it drops that user-space parser state, not bytes still in Linux/UART buffers. Close/open does not invoke systemd hooks. |
| CLI | `/usr/bin/arduino-router-cli --server /var/run/arduino-router.sock '$/serial/close' '[' 'str:/dev/ttyHS1' ']'`, and the exact corresponding open method, use existing APIs. `R/cmd/arduino-router-cli/main.go:58-79,181-210` has no explicit dial/request timeout and can print an RPC error without exiting nonzero. Check bounded exact output, method/argument echo and one true response, with no RPC error; exit0 alone is insufficient. Use argument arrays, not shell interpolation. |
| Library open/close | `S/serial_unix.go:214-294` opens O_RDWR/O_NOCTTY/O_NDELAY, configures raw1152008N1/no flow control, then switches to blocking. It performs no explicit input purge. At line280 it calls acquireExclusiveAccess **without checking its returned error**. `:461-466` uses TIOCEXCL/TIOCNXCL. Close releases exclusive mode before closing the fd (`:32-58`); errors in the router's close calls are not directly checked. The returned RPC/fd evidence must carry these limitations. |
| Monitor attachment | `R/internal/monitorapi/monitor-api.go:44-60` accepts TCP before inserting it in the client map. D113 proves only the completed TCP connection, with registration UNKNOWN (`P2_dump_receiver_arm_contract.md:96-105`). Existing socat already makes aggregate mon/connected true. Do not send mon/write test data, mon/reset, a registration RPC or any application payload as a hidden check. |
| Service restart | Actual cached `/run/systemd/generator/arduino-router.service.d/10-imola.conf` has ExecStopPost ready-low and MCU control GPIO transitions (`B/05_known_files.json`). Stop/start/restart/signal is not a reset-free alternative to these RPCs; Restart=always also makes killing the daemon inappropriate recovery. |

Linux TIOCEXCL prevents further opens except CAP_SYS_ADMIN; it neither evicts
existing fd holders nor identifies them. TIOCGEXCL reports a flag, not an owner.
Thus even a helper that checks both cannot fill the missing holder inventory.
These are Linux API semantics, not verified installed-driver results.
[Linux exclusive-terminal API](https://man7.org/linux/man-pages/man2/TIOCEXCL.2const.html).

`tcflush(fd, TCIFLUSH)` is the existing input-discard primitive; it discards
received unread input, not future arrivals, a router's old decoder memory or
remote MCU bytes still in flight. Do not substitute tcdrain, a sleep, an empty
FIONREAD observation, or a guessed amount of discard reading. Driver-specific
FIFO/DMA delivery and close/reopen behavior still need qualification against the
actual installed kernel/tty driver. No ioctl number is guessed here.
[Linux tcflush API](https://man7.org/linux/man-pages/man3/tcflush.3.html),
[kernel TTY buffer semantics](https://docs.kernel.org/5.17/tty/tty_buffer.html).

## Minimal sequence, conditional on an adopted run contract

1. **Freeze identity and quiescence before any mutation.** Current last-observed
   D114 COMPLETE image is an ADC-only runner with empty loop hook/no Bridge worker
   (`bench/ui_adc_probe/ui_adc_probe.ino:9-16`,
   `P2_ui_adc_probe_firmware_validation.md:40-44`). Its retained complete capture
   supports a candidate UART-silent baseline, not a fresh electrical TX reading.
   Recheck the exact loader/sketch and relevant source/startup/no-UART-owner
   evidence in a separately admitted passive readout. Any UART register read
   would need its own exact scope; existing D114 RAM/flash permission is not a
   peripheral-read permission. Quiescence must persist through the procedure;
   elapsed silence alone is not its proof.
2. **Establish Linux ownership before the close request.** Bind boot ID,
   router PID/start/executable, unit/drop-in hashes, configured character device
   identity and relevant callers. `B/06_socket_ownership.json` inspected only2
   of164 pid fd directories;162 were denied. `B/07_privileged_socket_ownership.json`
   retains sudo-n failure. Therefore current evidence cannot rule out another
   privileged UART holder. A complete targeted holder observation or another
   independently reviewed equivalent is required; do not bypass denied access,
   infer sole ownership from argv, or add arbitrary service/credential changes.
3. **One close RPC, then verify closed.** Require the exact successful response,
   stable service identity and disappearance of the router's identified UART fd,
   with no other holder. Hold a one-run local coordination lock for this helper;
   it does not control unrelated RPC clients. Any concurrent request, restart,
   timeout or ambiguous state aborts the readiness claim. No second close as a
   repair. No normal MCU payload may begin during this transition.
4. **Exclusive temporary fd and one input purge.** Once the owner proof holds,
   open only `/dev/ttyHS1` with O_NOCTTY/O_NONBLOCK/O_CLOEXEC, validate fstat device
   identity, successfully set/read back exclusive mode and recheck holders.
   Do not alter baud, modem bits or line discipline merely to purge. Perform the
   one admitted TCIFLUSH, save its result and release the temporary fd. This
   step still depends on installed-driver proof that quiescence and purge cover
   pending input at the transfer boundary. Opening/closing a tty is itself an
   action; lack of explicit DTR calls is not evidence of no driver side effects.
5. **One open RPC and positive reopen observation.** After the helper fd is
   closed/released, request open once. Verify that the same router process owns
   the expected new UART fd, no unexpected owner appeared, and the actual open
   succeeded. An accepted RPC, ready GPIO high, process-alive result, socket
   EBUSY or generic journal line alone is insufficient. None distinguishes all
   present failure paths. If decoder readiness cannot be observed, retain that
   qualification instead of declaring it proven.
6. **Fresh receiver, then separately authorized transmission.** Start the
   existing ticketed dump receiver and inspect its D113 live evidence. Keep
   router registration UNKNOWN unless separate evidence establishes it. An
   eventual missing first record is a failed capture, not permission to resend
   or manufacture framing. The preparation-only trial ends here without a new
   MCU image. A later one-shot synthetic UART probe needs its own source/grants,
   target/run review and exact lifecycle: actual inhibited IDLE/LOG_DUMP through
   existing Robot/Gate/Recorder/Transfer/UnoQDumpPort, then validated END/CRC/CSV.

Preparing while the known inert image remains quiescent is the smallest first
trial. A subsequent upload resets/reinitializes the MCU (`P0_installed_debug_contract.md:83-92`)
and changes the identity under which quiescence was established. Do not reuse a
preparation receipt as timeless permission. A transmit plan must either prove
the pinned upload/loader/new image emit no bytes before the clean decoder and
receiver exist, or perform preparation during an explicitly defined autonomous
no-TX setup window. Neither a guessed startup delay nor host data sent to the MCU
is an adopted solution. Default startup and PG13 ready do not acknowledge this
specific preparation.

## Finite failure behavior and next implementation

For a proposed helper contract, use one20s mutation-stage observation budget
(steps3-5 after the separately bounded identity/readout prerequisite),
at most5s for each existing CLI request, and at most16KiB of CLI output per
request; one close, one purge and one open maximum. These are proposed host
limits, not measured constants, MCU tick limits or proof Linux syscalls finish
within them. Bound the Linux child itself as well as outer ADB/SSH collection;
killing a local transport does not cancel a remote RPC. Preserve argv, identity,
monotonic/UTC times, output prefixes, exit/error and the last completed phase.
Any deadline/missing completion is **INDETERMINATE**, never READY.

Close only the helper's own fd on error when possible; record whether that
cleanup completed. Never blindly reopen after a purge/ownership failure, retry
after partial TX, signal/restart the router, reset the MCU or change UART/pin
grants to recover. The intended failure state may leave the router serial link
closed; report that observed/unknown state for a separately reviewed restoration.
This is a bounded caller/observation policy, not a claim to cancel kernel or
daemon work already accepted. Receiver attachment/capture retains its separate
D113 deadline; it is not included in that20s mutation budget.

**Smallest productive next scope:** first obtain a tightly limited, read-only
Linux prerequisite receipt for actual `/sys/class/tty/ttyHS1/device/driver`,
installed kernel/module identity, its input/close/open semantics and complete
targeted UART-holder visibility. Metadata can be collected without opening the
UART; denied/unavailable observations stay explicit. No existing cached record
closes those two gaps. Then freeze one preparation-only helper contract and
independent tests for exact CLI semantic responses, refusal-before-mutation,
owner/restart races, ignored/exclusive ioctl failures, purge failures, premature
open ACK, timeout/cleanup and no UART payload. Reuse the installed CLI and D113
receiver; no new protocol/parser service or firmware controller is needed.

Under this task's read-only authority no action above may execute. Under existing
bare-board permission a separately reviewed inert preparation can be eligible,
but permission alone cannot supply privileged visibility, a clean-framing fact
or successful native delivery. Until the prerequisites close, a helper can
truthfully retain partial diagnostics/refuse; it cannot establish all four D090
setup grants with the presently observed APIs and access.
