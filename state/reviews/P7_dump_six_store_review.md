# D235 six-store source and host review

Verdict: **PASS for the scoped source change and retained host evidence.** No
material blocker found. This accepts a bounded candidate for a separately
controlled native attempt; it does not establish that the D233 failure is fixed.

## Reviewed identity

- Base: `77ee8a66efc593d34aa579a5c0625919aa8fa30c`.
- Production checkpoint: `1b2af246cd88e6207e846ee340f8c4e46a5bb980`.
- Sole production change: `src/config.h`, `DUMP_UART_STEP_BYTES`, 8U to 6U.
  Current config SHA256:
  `243cfef511d822cfd2d562b6accee4bce529d185df58bfff8cb36aeef1a11f01`.
- `state/analysis/P7_dump_six_store_raw/closure.json`: 5484 bytes,
  `3c5f9969f02c5926d8853e15641338606823ea0476e6d3fdb6cff978458753e0`.
  All 29 path/size/SHA256 pins independently reconcile to the reviewed files.
- Contract: 5028 bytes,
  `a1f00816bce1ef72bd286bbf645a177d61830248e97e79451e6eeb25134732d9`.
- Validation: 3661 bytes,
  `0e035bb0401d3acdc259099ef57a731572421779028a2ae851ad3338b4c35d16`.

## Source findings

The UART HAL, ownership and readiness checks, FIFO selection, IRQ handling,
80 us step deadline, 100 ms packet deadline, 300000 ms total deadline, abort,
cleanup and D231 first-failure retention are unchanged. No production changes
outside the config literal were found. Locked tests are unchanged.

The revised fixture derives its current profile from the production literal.
The explicit historical-eight profile changes only its staged config copy and
retains the original eight-store branches. Current-six assertions cover exact
packet call counts, six-store progress, FIFO occupancy, final stop-bit completion,
live ownership loss and the real Transfer failure followed by cancel. Existing
read, clock, mask, overflow and foreign-write invariants remain present. Registry
coverage accepts six and rejects an eight-value regression.

The conservative full-capacity model requires 288575 calls with six stores,
leaving 11425 nominal calls within its 300000-call budget. The unchanged model
accounts for 23303 packets, 1156084 payload bytes and 1505629 wire bytes. A
maximum 79-byte packet needs at most 15 modeled calls. These are model bounds,
not measured target throughput, preemption tolerance or WCET.

## Retained host evidence

Accepted evidence is `d235-host03.zip`: 554652 bytes, SHA256
`a6706e4401c830c81629b1bafb39b5bb1843aa4552c5340aabc1c3a938ee9a5b`.
Its member manifest is 114365 bytes, SHA256
`c9b4bec6453be0ddaf74fb551d1c51cd625465378fd38c2c0c7cdc8ef1d51cab`.
All 612 archived members (8902346 uncompressed bytes) independently rehash
exactly. Both 121-file source-copy receipts reconcile, including the explicit
historical config substitution. All 747 recorded compiler/model commands return
zero with empty stderr.

All 30 selected methods pass without skips: two config, twelve current native,
eleven current FIFO, one capacity model and four historical-eight methods.
The retained runs include normal and ASan/UBSan execution. Historical full-stream
tests were not rerun; this is not a complete project-suite claim.

Both current-six D116 profiles retain 532562 payload bytes, 682967 wire bytes,
130252 calls, 5001 frames and eight events. Receiver/CSV validation reports format
integrity and consistency PASS, with hardware acceptance false. Both raw-capacity
profiles retain 1148071 payload bytes, 1496311 wire bytes, 287225 calls, 5001
frames and 4096 events. Independent archive inspection confirms row counts and
CRC. Submitted and emitted byte counts agree, queue maximum is five, and modeled
failures are zero. Raw-capacity invalid enum values are deliberate stress data.

The original host01 archive retains both unchanged receiver `renameat2 EINVAL`
publication failures on `/mnt/c`, including partial output; all 447 members
independently rehash. Host02's console-only PASS is explicitly insufficient for
raw closure because its RAM owner was unavailable before archival. Host03 closes
that evidence gap by verifying the archive before the WSL process exits. The
three fixture-header line-ending corrections preceded the accepted final run.

## Boundary and next action

The earlier TIMEOUT/STORE_DEADLINE record does not distinguish the shared step
and packet deadline predicate. The cleanup READBACK_FAILED cause also remains
unresolved. This change neither identifies those causes nor alters cleanup to
hide them. No claim about an LPUART hardware FIFO restriction follows.

The separate compile and motor-inhibited native delivery attempt require their
own actual receipts. They are not reviewed by this source/host report. No motor
permission, hardware qualification, physical acceptance or phase gate follows.
Reviewer performed only local source/evidence inspection and hashing, with no
test rerun, native action or source/test edit. Only this review file was written.
