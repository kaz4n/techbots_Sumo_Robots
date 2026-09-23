# Native dump prerequisite follow-up review

Verdict: **PASS_SCOPED_READ_ONLY_EVIDENCE**. No open BLOCKER or MAJOR finding in the final report; UART preparation remains blocked on the stated evidence prerequisites.
Reviewed 2026-09-24 by a reused separate same-model, source-aware reviewer; not a human or phase-gate approval.

- **MINOR, closed:** the original report incorrectly claimed changing PID membership. `P2_native_dump_prerequisite_followup.md:33` now correctly records equal 167-PID sets with differing sort order and one vanished fd. Original report/index and `raw/report_correction.json` preserve the correction.
- Final report SHA256: `7189b597c44705242f2e997982170967157a9010f4810786b88f97f57ec8e3b9`.
- Final artifact index SHA256: `7e4c766ae2bc92d878004a0cbc9206a59cbf2726f84846aabfdfc5a07768723e`. Independently rehashed all 18 indexed files plus the report; sizes and hashes match.
- Inventory receipt SHA256: `27983afb9b46448b5dbee20d13fbee0d6047f7d4f2c68050d68abfd466475167`. Verified retained stdout/stderr hashes, embedded program equality, exact ADB serial, 30s outer limit and exit0; inner absent-header exit1 remains visible.
- Access conclusion is supported: character239:1, platform `qcom_geni_serial`, DT `qcom,geni-uart`, matching built-in registration/kernel suffix; UID1000 with zero permitted/effective capabilities; only 2/167 fd directories readable, 165 denied including cached558/627. No claim of zero holders follows.
- Collector source contains metadata/regular-file reads and package lookup, with no UART open/read, socket/RPC, privilege or service/MCU operation. This is a review of retained evidence, not a fresh board observation or universal audit of host activity.

Here `raw` means `state/analysis/P2_native_dump_prerequisite_followup_raw`; source references below are under `raw/kernel_source/`.

- **TCIFLUSH:** `drivers/tty/tty_io.c:2770`, `tty_buffer.c:221`, `tty_ioctl.c:895,975` and `n_tty.c:350,2491` establish flip-buffer plus N_TTY flushing, without an RX-DMA completion guarantee.
- **Last-close:** `tty_port.c:605,695` makes shutdown conditional on the last open reference; `tty_ldisc.c:384` confirms both receive-buffer layers. `serial/serial_core.c:1761,1890` reaches stop_rx, native shutdown and IRQ synchronization. Hidden holders defeat the proposed last-close inference.
- **DMA:** `serial/qcom_geni_serial.c:1636,1838,1853` binds the observed non-console compatible to DMA operations. `:289,820` bounds polling; abort/reset success is not propagated (`:348,838`). Close success cannot establish all hardware cancellation/reset results.
- **Reopen/effects:** `qcom_geni_serial.c:851,1205` can return startup success despite failure inside the void RX preparation callback; `tty_port.c:343` and `qcom_geni_serial.c:231` support HUPCL/manual-RFR changes. No runtime termios, physical-signal or MCU-reset-free behavior is proved.
- **Timing:** `tty_port.c:100,633` supports a default30s output wait, not the proposed5s completion bound. A host/RPC deadline remains only an observation budget; timeout is indeterminate.
- Retained router `state/analysis/P2_dump_raw/native/router/main.go:180,204,229` supports open ACK before actual open and conditional close completion. No TCP connection, ACK or successful syscall is promoted to clean framing or receiver readiness.

The official revision resolution and cached source hashes support source identity, not a reproducible comparison to the running kernel/router binary or a measurement of hardware completion. Complete, race-qualified holder visibility would still require MCU TX quiescence and successful cancellation/reopen evidence; it does not independently authorize mutation.
No new board/network/MCU action, host-test execution, source/tool/test edit or phase-gate claim was made in this review. Evidence-only checks were sufficient; the sole created artifact is this review.
