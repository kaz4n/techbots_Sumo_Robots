# D224 recorder session source and host review

Date: 2026-09-26 (Asia/Dubai). Reviewer: independent fresh-context Codex agent,
review only. Base: `ee1bdcedf412903445c5076cae5980a43e0dc34e` in isolated worktree
`sumox-recorder-session-20260926`. The local date precedes the 1 October freeze;
the schedule's 26 September bench milestone does not constitute a passed gate.

## Findings

No BLOCKER, MAJOR or MINOR finding in the scoped session implementation.

- The actual diff preserves legacy zero-session wire identity and freezes a
  supplied uint64 identity per transfer. Changing the supplied identity cancels
  pending bytes once, before repeated-time suppression. Existing inhibited-IDLE,
  chronology, immutable-source, CRC, deadline and cancellation checks remain.
- `UNTRUSTED_RECEIVE_STREAM` relaxes only `framing_clean`, requires a nonzero
  session and the three existing setup/ownership grants, and rejects unknown
  modes. Native context/device/register/clock/IRQ, FIFO completion, lifetime
  ownership and poison checks are unchanged. The runner copies the session and
  supplies it throughout the transfer without changing its inert motor backend.
- The receiver enforces exact positive uint64 API inputs and canonical decimal
  CLI inputs before capture I/O. BEGIN, every row envelope and END are bound to
  the expected identity. A session mismatch remains terminal across parser
  reuse. Raw bytes and expected/observed/rejected identities survive failed
  publication; counts, CRC, CSV validation and trailing-byte rejection remain.
- The checked-in identity profile is disabled with zero grants. Actual default
  sketch entrypoint evidence covers setup plus 10,000 loops with no native
  clock/setup/ready/write/cancel calls. `src/config.h`, production `src/app`,
  motor HAL and `tests/locked` have no diff. No motion-command path, tick-loop
  blocking operation or heap allocation is introduced by these changes.

## Evidence checked

Read the complete scoped diff, surrounding implementation, independent new test
sources, contract, validation report and raw receipts. Independently recomputed
all 14 first-run input pins, all 7 compatibility pins and all 22 closure receipt
pins: PASS. Closure SHA-256:
`2164a1680510140c7b31a765df6814dadaafc28c6304cb5298e33e383a236354`.
The recorded base HEAD matches the worktree and `git diff --check` passes.

The 141 focused command receipts and 4 compatibility command receipts all
return zero. Their detailed outputs support 136 native UART model cases, 5 C++
cases / 54,034 assertions in each normal and ASan/UBSan profile, and 47 unchanged
C++ cases / 4,191,932 assertions. Receiver receipts support 11 Windows methods,
11 Linux methods and the additional Linux mismatch-reuse method; compatibility
receipts support 58 unchanged Python methods. Tests include independently
constructed stale/mixed wire records with repaired CRCs, full 200-second
synthetic output, all setup grant combinations, partial progress and cancellation.

The initial 13 compatibility setup errors are retained. They failed the
pre-existing external TMPDIR requirement before assertions; the correction
selects those 13 methods with `TMPDIR=/dev/shm`, without source/oracle changes.
The two explicitly excluded historical tooling methods are disclosed in the
validation report. No broad suite was rerun during this review because no new
finding justified it. Review commands were local and read-only; this report is
the reviewer's only written file.

## Verdict

**PASS for the scoped session source and retained host validation.**

This review excludes `tools/run_recorder_delivery.py`, staged enablement,
compile/upload admission and actual delivery. It does not establish loaded
target layout, physical UART framing or throughput, continuous exclusivity,
sensor/motor acceptance, initialized WCET/live RAM, motor-run permission or any
human phase gate. The remaining next action is the separately scoped delivery
caller validation/review and its admitted target execution; this core review
adds no further prerequisite chain.
