# D115 motor_stand inhibition preparation

IMPLEMENTED / HOST-TESTED / TARGET-COMPILED / SCOPED-REVIEW-PASS.
This is the finite setup/inhibition portion of P2 B4 preparation. It does not
implement directional drive, active brake, powered-output kill, or B7 reversals.

Five new bench files implement one actual MotorGate with one Native port owner.
The ordinary sketch's grant is false: construction, setup, loop and report access
perform no native motor/clock callbacks. Controlled host true-grant cases invoke
actual begin once, retain its immediate bool/fault, then invoke actual halt once
even after failed setup. Every result is preserved; later calls are passive.
No apply/reset, RobotResult, motion token, contact, outer clock or new tunable was
introduced. The existing HAL/core/config and established locked tests are unchanged.
MATCH or MOTORS_ALLOWED nonzero fails compilation.

First implementation7e1b99a4 remains unchanged. Full five-file hashes and original
source copies are in raw/implementer/first_source_freeze.json. The public contract
d8f5fd96 preceded execution; independent tests were derived from it, headers and
the earlier Gate contracts without implementation-body reads. Literal success,
failure, timing and terminal assertions are supplemented by separate real-Gate
comparisons for compatibility of existing cleanup behavior. That comparison is
not claimed as a new independent proof of the pre-existing Gate implementation.

Validation:

- Independent normal and ASan/UBSan:58cases /4,242,601assertions each. These include
  11 ordinary new cases, one isolated allocation-guard case and46 unchanged locked
  Gate/halt cases. Four counted Native/default-sketch binaries and six forbidden
  flag compilations pass. The sole initial Native link failure came from fixture
  name lookup; approved helper-only renaming preserved all assertions and values.
  Original failure, frozen inputs, diff and native-only rerun remain in raw/author.
- Full host normal and ASan/UBSan each:1457main cases /45,984,586assertions plus
  187active-Gate cases /4,536,952assertions, zero failures/skips. Root added only the
  pure Runner source to the ordinary CMake target; the active target is unchanged.
  Actual LastTest logs are in raw/coordinator; argv/UTC/exit receipts are
  P2_app_build_raw/d115_host_normal and d115_host_sanitize.
- All175 controlled policy methods pass:145 earlier policy cases,22 single-run
  guard cases and8 new literal motor-stand cases. Native production bytes remain
  unchanged after the test fixture correction. No script fixture is a board run.
- Board Linux checked compile-only passes for exact95-file source
  `bb3b462aef66f5a0a70ed24849b47e408ef93470d975071d64ad78d4a97260fe`, default/M0,
  fresh receipt a7b05d1e88d242d19bca7129e5cf8e46. No upload/reset/MCU operation.
  ELF `7a9c5cb5a2497e5a879c9c124c159d2c70cb91f83b839ea9c4a49e7aa6e6989d`,25524bytes;
  ZSK `682f3b65ff7c3548af03ee119f2d5bb6dec74c4f8b3aaf7211b29180dc231e18`.
  Three ELFs/ZSK and16 offline command results are preserved with their source and
  checked receipt under raw/target_bb3b462a_bench-default_checked.

Target ABI is observed from that exact debug ELF: Runner120bytes, Native40,
Report24 at Runner+88, HaltResult16 at Report+8, Port44. These are recorded ABI
facts, not a newly invented wire format or a live RAM result. Compiler dynamic
payload5556bytes is distinct from the ordered loader allocation peak6312bytes in
the pristine262144-byte model, leaving span255832/largest payload255828. The review
retains every allocation and its assumptions; this is not measured loaded RAM.
All35 used imports resolve against the pinned installed loader export table.
Final/debug function bytes and temporary relocations/constant sections were
inspected; an overstrict temporary-section audit assertion was corrected and
retained, without changing source, target bytes or tests.

Only literal motor_stand.ino is added to the existing checked build policy.
Default compile-only is allowed; MATCH, Immediate, sketch profiles/dangling links,
every upload and the unrelated D114 run option refuse before staging/transport.
No source allowlist entry, direct compile fallback, command transport or motor
permission was added. Root's first tooling hashes are boarde93ef30c and policy9b8f8639.
The D114 actual-run versions are archived before these subsequent tool changes.

Review and exact source/target findings are in
state/reviews/P2_motor_stand_inhibit_review.md and raw/reviewer. Separate reused
same-model review has no open finding; its private ten-method suite reproduces
the58-case normal/sanitizer runs, four Native binaries, six refusals and eight
policy checks. No human phase gate or cross-model review is claimed. The current MCU
remains D114's completed396bcc45 bare ADC probe. No extra hardware is requested.
Remaining directional B4 authority, B7/R6 policy, actual wiring/measurements,
full-app timing and human phase gates stay explicit; neither an acknowledged
callback nor this compile-only preparation supplies those missing results.

The remaining-task audit is P2_after_D115_checkpoint.md. No completed phase,
stand command-authority exception or clean-framing grant is inferred from this
bounded software closure. Exact next candidate is a narrow native dump ownership/
framing preparation contract; its factual grants remain unproved. Required B4/B7
authority resolution and assembled-robot acceptance stay separate.
