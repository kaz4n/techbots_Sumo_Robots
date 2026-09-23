# Native dump prerequisites: installed driver and current visibility

Read-only follow-up, 2026-09-24. This qualifies
`P2_native_dump_preparation_audit.md`; it does not adopt a preparation procedure.
Only Linux metadata/regular files and public primary source were read. No UART
was opened/read, no socket/RPC or service action occurred, and no privilege,
MCU, firmware, source, configuration or grant was changed. No sudo was attempted.

**Result: source identity is substantially narrowed, but the preparation remains
blocked by incomplete holder visibility and unobserved driver completion.**
Current access cannot establish exclusive last-close, successful hardware purge,
or positive reopen. Another helper cannot manufacture those facts.

## Fresh identity and visibility

`P2_native_dump_prerequisite_followup_raw/01_inventory.json` records exact ADB
argv, the remote program, a 30-second outer limit, actual status and output
hashes. ADB serial was explicitly `2629958581`; command exit was 0. Host receipt
UTC was 2026-09-23 23:46:41; the board independently reported its own UTC.
Receipt SHA256 is
`27983afb9b46448b5dbee20d13fbee0d6047f7d4f2c68050d68abfd466475167`.
Inner package lookup exit1, caused by absent header packages, is retained.

| Observation | Consequence |
|---|---|
| Running kernel `6.16.7-g0dd6551ae96b`, installed matching linux-image package; boot ID `9caf2230-da00-40cd-a7af-792d66e1d05a` | The source revision can be located precisely; this is not a reproducible-build comparison against the running kernel. |
| `/dev/ttyHS1` is character device **239:1**, root:dialout, mode0660 | Metadata identifies the device. Current read/write permission was checked without opening it; permission does not prove exclusive ownership. |
| tty device resolves through serial-base to platform `4a88000.serial`, driver **qcom_geni_serial**, DT compatible `qcom,geni-uart` | The immediate tty `device/driver` is merely `serial-base/port`; the ancestor platform driver supplies the relevant UART implementation. |
| `/proc/tty/drivers` identifies `qcom_geni_uart` at ttyHS major239; `modules.builtin` names `qcom_geni_serial.ko` | This is the built-in non-console UART implementation, not an absent loadable module. |
| `/usr/src` empty; matching `/lib/modules/.../{source,build}` absent | No installed source/header tree was available for comparison. |
| Effective UID1000, effective/permitted capabilities zero; **2 of167** process fd directories readable, **165 denied**, including cached router PID558 and socat PID627 | The scan is incomplete. Its empty visible-holder list is **not** evidence of zero UART holders. Membership in the sudo group is not privilege authority. |

The metadata scan used finite process/fd/time caps, none reached. One fd vanished.
The before/after PID sets are equal (167 each); their list order differs because
the first is lexicographic and the second numeric. Even a fully readable scan
would need explicit race treatment. No proc hidepid mount option was present;
that does not remove ordinary per-process access restrictions. The prior denied
sudo evidence remains historical; no privilege retry or workaround was used.

## Exact primary source conclusion

Official `arduino/linux-qcom` resolves the kernel suffix to full commit
`0dd6551ae96b78024086e72339fefbef6fcc604b`. Download receipts and SHA256s are in
`raw/source_receipts.json` and `raw/source_flush_chain_receipt.json`, with `raw`
meaning `P2_native_dump_prerequisite_followup_raw` here. Exact files are retained
under `raw/kernel_source/`. This is a release/revision identity match, not proof
that the running binary has no local changes, nor a hardware measurement.

1. **TCIFLUSH covers Linux flip and line-discipline buffers, not an RX-DMA
   completion handshake.** `drivers/tty/tty_io.c:2770-2777` first calls
   `tty_buffer_flush(tty, NULL)`; `tty_buffer.c:221-244` discards committed flip
   data. `tty_ioctl.c:895-918` subsequently invokes the line-discipline flush,
   and `n_tty.c:350-358` resets its input indexes. Thus it would be inaccurate to
   describe TCIFLUSH as *only* the line-discipline reset. Neither operation stops
   the GENI RX command or establishes that no DMA/hardware input can arrive
   afterwards. [Exact TTY ioctl dispatch](https://github.com/arduino/linux-qcom/blob/0dd6551ae96b78024086e72339fefbef6fcc604b/drivers/tty/tty_io.c#L2770).
2. **Last-close is material.** `tty_port.c:605-646,695-705` skips shutdown when
   another port reference remains. A real last-close flushes Linux buffers,
   runs shutdown, then flushes again (`tty_ldisc.c:384-391` includes the flip
   buffers). The serial layer calls `stop_rx`, native shutdown and IRQ
   synchronization (`serial_core.c:1761-1789,1890-1910`). An invisible holder
   defeats the assumption that closing the router triggered that path.
3. **DMA stop has bounded polling but no exported success result.** The
   non-console operations select RX DMA (`qcom_geni_serial.c:1636-1651`). Its
   stop routine cancels the secondary command, checks RX_EOT, otherwise aborts
   and resets the RX DMA state machine (`:820-849`). The reset poll result is
   not propagated, and the function returns void. Native shutdown also stops
   TX and cancels its command (`:1138-1148`). A successful close RPC or close
   syscall therefore does not itself prove every hardware cancellation/reset
   succeeded. [Exact GENI DMA stop](https://github.com/arduino/linux-qcom/blob/0dd6551ae96b78024086e72339fefbef6fcc604b/drivers/tty/serial/qcom_geni_serial.c#L820).
4. **Open is not electrically passive or positive receiver readiness.**
   Startup starts RX DMA and enables IRQs (`qcom_geni_serial.c:1205-1222`). RX
   DMA preparation failure is logged and stopped inside a void callback
   (`:851-868`), so the enclosing startup can still return0. Close may lower
   DTR/RTS when HUPCL is set (`tty_port.c:343-359`); the native modem callback
   writes the UART manual-RFR register (`qcom_geni_serial.c:231-246`). These are
   real UART state changes. The inspected path does not itself call the
   router service's MCU-reset GPIO hook; this is not a proof of every physical
   signal effect or the actual current termios. No live termios was queried.

The source defaults `closing_wait` to30s (`tty_port.c:99-100`) and may wait for
output at close (`:633-640`); the live value was not read. Therefore the earlier
proposed 5-second RPC limit is only an observation budget, not a guaranteed
close-completion bound. Timeout remains indeterminate. No runtime delay or
reliability measurement is claimed.

## Exact remaining prerequisite and next action

The earlier router API conclusions remain: close completion is conditional on
one controlled request; open ACK precedes actual open; service restart has MCU
side effects; D113 CONNECTED proves TCP attachment only. This follow-up does
not strengthen any of those into framing-clean or exclusive-ownership grants.

**The next prerequisite is a separately supplied, narrowly scoped privileged
read-only holder receipt**, bound to boot/process start/executable identity and
character device239:1, including denied/vanished entries and races. It must cover
the router's actual UART fd and every other process; another unprivileged scan
with current credentials cannot close this gap. This task neither acquires that
privilege nor requests a service/credential change.

Even complete visibility would be necessary rather than sufficient. Before a
preparation trial, a reviewed plan must bind MCU TX quiescence across the
transition and determine how successful last-close/RX cancellation and actual
router reopen are established, preserving UNKNOWN on timeout or hidden driver
failure. Those are action/evidence prerequisites, not grounds to weaken
`framing_clean`, guess a silence delay, or substitute TIOCEXCL for holder proof.
Source tracing here identifies the limitation; it does not adopt a new driver,
instrumentation service or protocol.

**Recommended current checkpoint:** retain the exact source and access receipt;
do not implement or execute a mutation helper that claims READY with current
observability. D116/D117 compile/host evidence can close independently. Native
UART delivery and clean preparation remain pending these concrete prerequisites.
