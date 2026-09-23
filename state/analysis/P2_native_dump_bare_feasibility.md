# Bare UNO Q native dump: bounded feasibility note

Read-only local source/evidence assessment, 2026-09-24. No board command, source
change, test rerun, upload, router RPC or service action. Prior installed-source
observations below are cached evidence, not a fresh claim about running processes
or clean framing. This note proposes the next scope; it adopts no run policy.

**Eligible in principle on the bare UNO Q without extra hardware.** D090 already
implements transmit-only internal LPUART1 notifications through Linux router
Monitor, and D091 already executed explicitly synthetic Robot/Gate/Recorder
records with no motor backend. The unresolved prerequisite is controlled UART
ownership/clean framing/receiver attachment, not an external sensor connection.
User bare-board test authority can support a separately identified inert run;
it does not itself establish the four existing SetupGrant predicates.

| Existing evidence | Consequence for a new run |
|---|---|
| `P2_dump_native_audit.md:95-125`: internal LPUART1, PG7/8 route, PG13 ready, deferred init; router `/dev/ttyHS1`115200 | No external UART wires are needed. Preserve the exact native ownership/readiness checks, including Immediate behavior if that mode is later selected. PG13 high does not prove an attached receiver or clean parser. |
| `src/hal/dump_uart_unoq.h:11-26`; `.cpp:138-178` | All setup_phase/exclusive_uart/ready_pin_owned/framing_clean grants must be substantiated. No default grant widening. Setup-only device_init has known unbounded ACK waits; a timed host failure observation cannot convert that into bounded firmware initialization. |
| `P2_dump_native_audit.md:150-174`; `tools/dump_match.py:288-310` | Existing receiver connects to127.0.0.1:7500 and only receives; it never sends motion/reset data. It must be connected before the first notification. With zero clients the router silently loses bytes. MCU TX-complete means SENT_UNCONFIRMED until host framing/count/CRC/CSV checks pass. |
| `P2_recorder_bench_native_audit.md:95-105` | Router serial close/open creates a new decoder but does not explicitly flush input; open's true reply precedes actual successful reopen. A fresh decoder alone does not establish absence of residual kernel/UART/in-flight bytes. |
| Same audit:99 and `P2_dump_native_audit.md:115-120` | Installed systemd stop/start hooks lower ready and toggle MCU control lines. Restart is a reset-affecting operation, never an automatic or hidden capture recovery. MCU reset alone does not prove Linux decoder recovery. |
| `P2_dump_native_contract.md:30-44` | Partial cancellation poisons the native instance; already shifted bytes cannot be recalled. No resume/retry/finish outside eligible IDLE and no implicit recovery may be added. |
| `P2_recorder_bench_validation.md:7-20`; `bench/recorder_inert/src/recorder_bench.h:99-108` | Actual200s synthetic retained data exists, but D091's Runner terminates after STOP/seal/checksum and exposes only const source. It does not expose a live IDLE/menu transaction for Transfer. Its old no-UART run scope and upload identity cannot be reused for a UART-enabled image. |

The smallest useful next software contract is a **new short synthetic transport
probe**, composed from the existing Robot, inert checked MotorGate callbacks,
AttemptRecorder, Transfer and UnoQDumpPort. Do not use app NativePortFactory,
which initializes the native motor boundary, or invent an IDLE boolean/result.
`recorder_dump.cpp:60-68,115` requires a real fresh inhibited IDLE result with
LOG_DUMP selected, and continues enforcing result/source/time eligibility.

A short synthetic accepted START followed by actual qualified MODE cancellation
before GO is a candidate lifecycle: existing Gate supports this cancellation
(`countdown.cpp:10-20`), and recorder recognizes COUNTDOWN-to-IDLE as termination
(`recorder.cpp:13-18`). Then consume the real tail and drive actual synthetic
menu gestures to LOG_DUMP while continuing real fresh IDLE results. The exact
stimulus schedule, refusal paths and declared incomplete/no-GO meaning still
need a contract and independent tests. All wire records must declare SYNTHETIC;
no frame, menu result or success flag is fabricated. This tests the transport
path without pretending to repeat200s B8 acceptance. A later200s version would
need an explicit post-STOP logical reset/service lifecycle and recorder retention;
do not silently weaken D091's frozen behavior or D103's physical/local policy.

Before proposing execution, resolve these concrete obligations:

1. Refresh read-only installed loader/router/service/process/socket identity and
   identify every MCU UART writer/worker and Linux serial/monitor client. Prove
   the proposed ELF retains the strong empty loop hook and no Bridge worker,
   header motor writes or competing UART owner. Fresh exact sources, target
   startup/imports, ordered loader fit and native binding review are necessary.
2. Specify and independently review a finite clean-framing preparation with
   quiescent MCU TX, completed exclusive serial close, discarded input/in-flight
   residue, verified actual reopen and receiver already attached. Existing
   close/open calls and default setup cannot prove this by themselves. Any
   deliberate restart/reset must be visible in the exact run scope; never hide
   one inside the receive helper or retry automatically after partial output.
3. Make receiver attachment observable before the planned autonomous transmit
   window. Current `LiveCapture` returns captured process output after completion
   (`dump_match.py:315-344`); it has no public armed acknowledgement. A long
   startup delay alone is not proof. Add only a bounded, reviewed host-side
   readiness receipt/rendezvous if necessary, with no inbound MCU control path.
4. Freeze exact image/serial/startup/grants/bench origin, total/call deadlines,
   partial/poison handling and host failure retention. Drive one bounded Transfer
   step per admitted synthetic transaction. Continue actual ready checks; do not
   turn router backpressure into MCU waiting. Retain actual native status and
   partial evidence on setup/readiness/framing/timeout failure.
5. Require valid END, exact session/epoch/count/order/CRC and existing CSV bundle
   validation, plus retained-row comparison to the actual synthetic recorder.
   Bind deployed/source identities separately from origin. Record successful
   delivery and observed call durations separately from full800us WCET,
   oscillator qualification, sensor truth or assembled-robot B8.

This keeps R2 unchanged (transmit-only log data from eligible IDLE), keeps all
existing grants meaningful, and keeps motors disabled with inert callbacks.
No new native transport or remote-control framework is needed. The next eligible
action is the small probe/preparation contract and read-only prerequisite audit;
the currently available evidence is insufficient to assert framing_clean now.

## Read-only connected-board refresh, 2026-09-24

Completed the separately authorized Linux-only refresh on explicit ADB serial
2629958581. Host command interval was2026-09-23T21:08:51.725646Z through
21:10:47Z (2026-09-24 Asia/Dubai). Exact remote/ADB argv, start/end UTC, return
codes, stdout/stderr and hashes are in
`P2_native_dump_bare_raw/read_only/01_*.json` through `12_*.json`, indexed by
`summary.json` and `manifest.json`. All calls use existing board_tool.remote;
the board ran only metadata queries and regular-file reads. No UART open/read,
Monitor/router socket connection, RPC, signal, service action, MCU operation or
config mutation occurred. Twelve command receipts:11 exit0; one retained exit1
was `sudo -n` refusing the read-only proc-fd query because a password is required.
No password was requested/read and no privileged bypass was attempted.

**Fresh observations:**

- Router package remains0.10.0 arm64. `/usr/bin/arduino-router` is6095032bytes,
  SHA256 `3eacd38a9c813209f6985951869105600824e4f7c54a1111a8d48ef094cc1a19`,
  matching the cached D090 identity. All six checked core1.0.0 source/config
  hashes match their original cached receipts. This does not make the separately
  cached matching-tag Go source a reproducible build proof of that executable.
- Router service is active/running, MainPID558, NRestarts0, started
  2026-09-23T16:28:55Z. Current generated10-imola.conf is526bytes/SHA256
  `b94641327302c1795545c83ad2be1aa4fe7dcc7e84630fa8b7106cfddde72430`.
  Its actual ExecStart still selects `/dev/ttyHS1`115200; the ready and MCU-control
  ExecStartPre/ExecStopPost hooks are unchanged. These queries did not run hooks.
- Monitor listens on127.0.0.1:7500. **An existing Monitor client is already
  connected:**127.0.0.1:48746, client inode11017/server inode11018. `ss -ntpe`
  supplies kernel socket cgroups: client belongs to
  `/system.slice/arduino-router-serial.service`, server to router.service.
  Both queues were0 at that observation; this is not a continued-draining proof.
- That serial proxy service and its `.path` unit are active. Public metadata
  identifies root-owned socat PID627 and the actual command
  `socat file:/dev/ttyGS0,raw,echo=0,b9600,crtscts=0 tcp:127.0.0.1:7500`.
  The path unit watches `/dev/ttyGS0`; service Restart=always/RestartSec=3.
  Thus the existing connection is the USB serial Monitor proxy, not a newly
  armed dump receiver. No proxy or USB serial endpoint was opened or stopped.
- The ADB account is UID1000 and a member of group20. `/dev/ttyHS1` is character
  device239:1, mode0660, root:20; metadata-only access checks report read/write
  permission. `/var/run/arduino-router.sock` is root:root/mode0666, with write
  access. These establish potential user-space preparation access, not actual
  exclusivity, an open file, a successful RPC or a clean receive buffer.
- Proc scanning admitted2 of164 process fd directories and denied162. The failed
  sudo query is preserved. Kernel socket cgroups resolve Monitor ownership
  independently, but **the UART fd-holder inventory is incomplete**. Service
  argv does not prove there is no second privileged UART opener.

**What the existing source actually permits us to conclude:** cached, hash-bound
router `main.go:180-269` implements close by signalling its serial loop and waiting
on a condition variable, without a deadline; failed serial-open/reopen paths may
wait/retry. The open RPC acknowledges the request before serial.Open succeeds.
CLI `cmd/arduino-router-cli/main.go:58-79,181-210` adds no explicit connect/request
deadline and prints RPC errors without necessarily making them a nonzero process
exit. A bounded caller therefore needs exact semantic response validation and
an outer deadline; a timeout leaves the operation indeterminate, not canceled or
safe for the next step. No automatic retry/restart follows.

Pinned serial_unix.go:214-294 opens/configures without an explicit input purge;
serial_linux.go:68-70 selects TCSETS and separately defines TCFLSH. Neither proves
that the router invokes a flush. The current socket queue observations concern
TCP Monitor only; they say nothing about UART RX residue or partially consumed
MessagePack state. The refreshed evidence still cannot set framing_clean=true.

**Minimal preparation remains feasible as a separately reviewed task.** The
ordinary account has apparent access to the existing RPC socket and UART node,
so missing external hardware/root password need not be assumed blockers. The
next contract should scope an exact reset-free close/purge/reopen helper with
finite caller deadlines, independently verified quiescent MCU TX, positive close
completion, verified exclusive temporary UART access and a source-justified
input-discard operation, then verified actual router reopen and receiver
attachment before the autonomous transmit window. The purge/ioctl semantics,
failure-indeterminate states, possible competing UART owner and precise evidence
for successful reopen still need review; no such helper or proof exists here.

Account explicitly for the existing socat client. Leaving it in place avoids a
new service mutation but makes the intended dump receiver a second client:
the pinned monitor write path then uses500ms per-client deadlines, whereas a
single client may block indefinitely (`monitor-api.go:133-152`). That is Linux
behavior, never permission for the MCU to wait, and actual end-to-end delivery
still needs bounded capture/CRC validation. Do not silently stop the proxy,
equate its existing connection with the desired capture, or claim it drains data
because the sampled queues were empty. A short synthetic first transport probe
is the smallest reviewable next run after those software prerequisites close;
full200s/native failure-recovery/B8 claims remain separate.
