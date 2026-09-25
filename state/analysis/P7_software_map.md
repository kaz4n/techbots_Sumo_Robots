# P7 software preparation map

**25 September D180 follow-up:** the map below preserves the24September audit.
The runbook now exists. Item2's configuration binding is implemented and
HOST-TESTED with every grant still disabled; see
[D180 evidence](P7_setup_binding_validation.md). Its changed main app has not
been target-compiled. Physical grant qualification and release acceptance remain
pending; use CODEX_HANDOFF.md for the current task and gate status.

Read-only source/document mapping, 2026-09-24, during D134 validation. Only this
map was added; no implementation, test, board operation, release tag, phase
advance or ledger update. D134's final result is owned by its validation/review
packet, not inferred here. P7 preparation does not depend on P6 eligibility.

## Minimal remaining deliverables

| Existing requirement/artifact | Current state | Smallest useful completion |
|---|---|---|
| P7.2 runbook (`docs/prompts/P7_freeze_matchday.md:8-16`) | `docs/RUNBOOK.md` does not exist. `docs/P0_MANUAL_CHECKLIST.md` is a historical bare-board checklist, not a match-day procedure. | One printable runbook covering the required night-before, pit, ring, between-round, timeout, dump and failure procedures. Link current acceptance packets; mark unverified setup and procedures explicitly. Include the mode card, kit list and small scouting/rehearsal record in this document rather than creating a new documentation system. |
| Mode card and scouting (`docs/PLAN.md:165-178`) | The selection table and scouting fields already exist. D134 adds optional availability; all six are still development defaults. | Reuse the table in the runbook, showing only the enabled and ultimately accepted options for the identified release. Record ARC/WAIT disposition and enabled MODE_DEFAULT from the actual config. Preserve historical IDs. If organizer mode changes are prohibited, PLAN's fixed-mode contingency still needs the real answer. |
| Release identity/checklist (P7.1, PLAN section 3) | Existing checked board-side compile path and receipts exist. No `v1.0` tag was returned by read-only Git lookup. No standalone release checklist exists. | A short release section in the runbook referencing existing compile receipts, source/config/ELF identities, current tests/review, enabled modes, unresolved acceptance and the eventual actual commit/tag. Prepare it with pending fields now; tag only at the real freeze against the final reviewed revision. Do not generate another source archive or build wrapper. |
| Kit and rehearsal (P7.3/7.4, prompt lines17-18) | Required list, three best-of-three rehearsal sets and date are already specified. No completed runbook/rehearsal artifact exists. | Add checkboxes and a compact result table to the runbook; retain actual outcomes and procedural corrections later. Printing, pack inventory, battery-swap practice and rehearsal remain physical tasks. |

The smallest next documentation task is therefore one `docs/RUNBOOK.md`, using
existing PLAN and tooling guidance, with a separate review against actual UI and
release capabilities. Do not add P6 plots, presentation packaging or generic
release scripts just to complete P7's document list.

## Concrete unfinished software/release prerequisites

1. **Match deployment is not implemented by the documented P7 command.**
   P7.1 names `tools/flash.sh app --match`, but the current
   `tools/board_tool.py:460-466` refuses motor-capable uploads and permits only
   identified inert upload paths. `tools/flash.sh` is only a wrapper; it adds no
   authorization. The existing safe build command is
   `tools/flash.sh app --match --compile-only`, subject to its current checked
   board/toolchain prerequisites (`tools/README.md:3-24,91-96`). A later bounded
   source/artifact/run-authorized deployment contract must extend or explicitly
   resolve the existing route; changing a README, passing --match, or refreshing
   an inert hash cannot supply it. This is a genuine release capability gap,
   not an invitation to bypass guards or create a second uploader.

2. **The shipped app intentionally supplies no physical setup grants.**
   `src/app/app.ino:19-20` always calls `runtime.begin(app::SetupGrants{})`.
   Source, ADC/buttons, QTR, IMU, matrix, dump and local-reset capabilities are
   explicitly unconfirmed in `src/app/runtime.h:36-50`; Runtime consumes those
   grants in `runtime.cpp:52-67`. MATCH changes motor/build flags, not these
   facts. A final robot binding must identify which existing grants can truthfully
   be supplied and how the verified config is selected. Hardware facts are
   deferred, but this integration/disposition must be planned before the
   config-only freeze: the current literal empty binding cannot become a working
   qualified match configuration merely by tagging it. Do not set grants true
   from assumed acceptance, or add a default-enabled bypass.

3. **Latest target evidence remains unfinished.**
   `state/CODEX_EXECUTION.md:40-42` and `state/CODEX_HANDOFF.md:41-45` retain D129+
   native compilation/fit/default-compatibility work. D128's historical default
   modeled margin was only16 bytes; it is not a current D134 or live-memory
   result. Reuse checked compilation and existing loader auditing when the board
   build environment is available. Native compilation is software verification
   requiring that environment; full-source timing, loaded stack/RAM and physical
   source behavior still require actual measurements. No new memory framework.

4. **P5.3's native one-tick evidence method is still unresolved.**
   `state/analysis/spec_conflicts.md:723-728` includes both P4 loss and P5 opener
   abort timing. D129 deliberately requires P4 reactive mode, where no opener
   runs (`P4_timing_evidence_contract.md:6-13`). D134 clarifies D034 routing and
   tests software handover, but does not add a native opener stimulus/receipt
   trace. Existing25Hz frames alone do not establish a1ms abort bound. The
   coordinator must choose a bounded evidence method before claiming physical
   P5.3 acceptance; an existing suitable external measurement may be part of
   that decision. Do not automatically add a logger or extend the P4 trace.

Current `CODEX_EXECUTION.md` reports no open scoped defect for D131-D133 and
lists D134 validation in progress. This map finds no basis to rebuild completed
opener algorithms or repeat their solved host work. The four boundaries above
must remain visible when deciding whether software preparation is complete.

## Hardware, external-access and human acceptance still pending

- Preserve the existing P2/P3/P4/P5 acceptance packets rather than duplicating
  their trial matrices. Actual electrical/PINMAP, sensor polarity/range/color,
  button/BOTH distinction, calibrated clock/battery, motor direction/kill,
  dimensional/weight, full-source <800us, loaded RAM/stack and ring-performance
  evidence remain absent at their recorded scopes. Real EXPLAINED and phase
  gates are human records, not software scheduling decisions.
- Native post-match dumping already has a receiver, CSV validator and IDLE
  service path (`tools/README.md:255-278`). D117 resolved the selected FIFO
  cadence design in software despite the old OPEN heading
  (`spec_conflicts.md:693-699`). The remaining blocker is genuine UART holder
  visibility, framing/last-close/reopen proof and measured delivery/service rate;
  see `P2_native_dump_prerequisite_followup.md:87-113`. Another unprivileged
  scan, helper or router restart cannot manufacture these prerequisites.
  Document the existing receiver and retained partial-error behavior; do not
  promise that current app grants can perform a live dump.
- B7 remains the explicit full-reverse versus R6 requirements conflict,
  selected blocked/unaccepted under D121 (`spec_conflicts.md:704-710`;
  `P2_software_acceptance_packet.md:56-68`). A runbook cannot resolve it, and a
  lower-duty sequence is not its replacement. Any dependent implementation
  needs a supported protected resolution before the later authorized trial.
- Organizer answers remain pending at D014 (`state/DECISIONS.md:56-57`):
  orientation, between-round mode changes, radios, arena, START activation,
  scale and blade questions are already in PLAN section5. Preserve the stated
  center-facing and Wi-Fi-off defaults without claiming organizer approval;
  add actual answers when supplied. This mapping sends no external message.
- Freeze remains1October21:00 Dubai, followed by2October rehearsal and3October
  competition (`docs/PLAN.md:72-82`). Actual28September scope cuts and optional
  opener acceptance determine final config. Printing, rehearsal, measured
  performance, identified STAND OK/RING OK and GATE P7 PASS are not completed
  by a prepared document or a local tag. P6's separate gate-date rule does not
  block writing the required P7 runbook.

## Runbook wording must match the implemented UI

P7.2's phrase "confirm READY and battery at or above VBAT_WARN_V on the matrix"
needs a precise mapping, not invented UI behavior. The renderer shows boot,
countdown, service or mode glyphs (`src/hal/ui_display.cpp:163-191`), not a literal
READY screen. Its battery output is a coarse bar with an unavailable pattern
(`:44-52`), plus fault icons; it is not an exact voltage readout. The runbook
should identify the reviewed IDLE/mode/no-fault indication and distinguish it
from motor permission or sensor qualification. An exact10.8V acceptance check
needs calibrated evidence; bar appearance alone must not be described as that
measurement. Use the existing display/error semantics and measured pit practice
instead of adding UI features during documentation work.
