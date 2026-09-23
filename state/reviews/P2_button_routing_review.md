# D087 button evidence and routing: independent review

Status: PASS for the bounded D087 software scope. No open review findings.
Reviewed baseline c10f473, contract 6c01bb4 and the evolving D087 source/test diff.
Date: 2026-09-23 Asia/Dubai. Active scope is P2 software development under D051/D075.

Reviewer context is reused from completed D086 because a new reviewer spawn hit
its thread limit. This is a separate same-model reviewer, not a newly fresh-context
or cross-model review. The reviewer authored no implementation or product tests;
ownership is only this report and P2_button_routing_raw. No board, MCU, pin, motor,
upload or human-gate action was performed by this reviewer.

## Scope and findings

Read AGENTS, applicable D051/D075/D087, PLAN schedule, HARDWARE 5.6/SC-A, BEHAVIOR
B3/B13/B15, frozen contract and source audit, public power/ui/Robot/countdown/logframe
interfaces, all changed implementation and new independent test fixtures.

No open BLOCKER, MAJOR or MINOR source finding. Initial LINE event fixtures also
needed independently fresh opponent evidence to isolate LINE 256; this reviewer
reported that fixture contamination before final validation. The independent
author corrected it without changing implementation or old assertions.

## Reviewed behavior

- ui.cpp validates provider shape and configuration before classifying raw counts.
  Canonical absence is distinct from NONE; known provider failure stays INVALID.
  Unconfigured, unmatched and overlapping windows cannot produce a logical release.
  applyButtons changes only RobotInput.buttons, with no I/O, debounce or allocation.
- fsm_buttons.cpp fixes explicit versus legacy mode until reset. It admits bounded
  source duration/age, distinct forward sequence and source time, nonoverlap and
  bounded source/decision gaps. Exact replay does not refresh source age or events;
  malformed identity, stale/missing history, half-range/backward time and mode
  mixing latch BUTTON_CONTRACT. Saturating accumulated age prevents wrap revival.
- Fresh source NONE spans the full debounce before START arming. Boot-held START
  cannot grant a release; fresh boot-held BOTH still follows STOP qualification.
  Fault interruption clears pending gestures/neutral arming and requires reset.
- Shared stepObserved paths use source completion for observed debounce and
  decision time for full START release hold and qualified STOP/MODE anchors.
  Source samples before a decision anchor cannot turn unsigned subtraction into
  an immediate hold. No-new observations preserve pending qualification without
  advancing it; Gate, countdown services and genuine external STOP still progress.
  Fresh release at the STOP/menu deadline keeps existing release precedence.
- Menu final inhibition and non-IDLE disarm still run without fresh input. Selection
  survives interruption. Existing service views, qualified START consumption,
  cancellation ordering and legacy wrapper behavior remain covered.
- Detail 11 admits exactly known mask bits 0..9 with at least bit 8 or bit 9. Detail 7
  retains exactly 1..255. Robot emits new high faults once, in the existing 8-byte
  event and capacity 21 batch; recorder and existing CSV format preserve them.
- The actual MotorGate callback boundary proves nonzero host-enabled duty only
  after the 5100 ms hold, then EN-low and all four PWM-zero writes on invalid,
  expired or production-unconfigured decoder evidence. This is callback evidence,
  not a physical motor result.

## Executed evidence

Independent reviewer executions are under P2_button_routing_raw:

- final_tooling: isolated snapshot, 385 files, no drift at execution; 8 unittest
  methods PASS in 42.347 s. Four complete 14-bit synthetic profiles, six malformed
  configurations, provider shape/status/shutdown coverage and adapter isolation.
  Both MATCH/MOTORS_ALLOWED macro modes prove actual probe global construction,
  setup and 10000 loops produce zero counted native I/O/allocation. All eight upload
  combinations refuse before transport lookup. Existing CSV schema accepts detail 11.
  All 24 captured native compile/execution commands exited 0.
- final_focused_v2: copied and SHA256-identified final host binaries; normal and
  ASan/UBSan each PASS 36 main D087 cases / 113773 assertions and 1 host-enabled MotorGate
  case / 46636 assertions. Source and binary drift lists are empty. This reviewer
  executed these binaries independently; root built them.
- Compared all 222 baseline tracked test files. Only test_p0_config.py changes:
  additive four-declaration allowlist and a new default-policy assertion method.
  No locked or previous behavioral assertion changed. New tests are separate files.
- Root full normal 2/2 PASS in 20.51 s and full ASan/UBSan 2/2 PASS in 28.73 s, each main 1209 cases/
  22954190 assertions plus enabled 38 cases / 3843482 assertions. Root config 18 and
  staging 2 pass. Final existing tooling 25 PASS in 18.392 s, including LF-checkout identity.
  Full-suite source precedes the normalization-only header fix below.

## Source, target and startup identity

Initial target source a4a4b803c2843735fdeb775db22f8dc79dd4eb006af95a30f7fb306179879127
matched all 59 staged files and three ELF receipts. Independent offline verification
checked 36 native and 42 AEABI export bindings; additional fmod/sqrt bindings equal
the canonical functions in base ELF 39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd.

Retained target methods include raw begin/readButtons, decoder/adapter, Robot
admission and observed-time services. setup stores only exercise's address and loop
returns. Reader and Robot are static data; the new-TU initializer performs existing
RouterBridge::HCI data bookkeeping without function calls. The nine initializer
entries retain inherited Bridge/UART/libstdc++ setup. Inherited __loopHook can lock
and update Bridge, and the base static thread remains. Thus the evidence proves no
new project pin/native initialization; it does not prove a globally I/O-free core
runtime, loader acceptance or whole-firmware determinism.

Two existing tooling checks exposed src/core/logframe.h:1 CRLF bytes not surviving
Git LF checkout. Root changed only CRLF to LF and rebuilt. Independent
inert_approval_final.json reconstructs the exact initial header bytes from final
LF bytes and proves every other production file unchanged. Initial target,
approval and all failed receipts remain preserved; this formatting-only change
requires new source identities but does not change executed program semantics.

Only the exact existing five registry keys are approved, via
P2_button_routing_raw/inert_approval_final.json/approved_existing_keys. No new probe
key or upload/run permission is approved. Final registry equality is independently
verified in final_evidence_audit.json, with no extra key.

Final source 557e0e5fe1c30aeda84d4f1aa6171f3aa56e5a67d5df00fcf51173c8c894bf60
matches all 59 current staged files and the final three ELF receipts. Compile output
is 142288 program bytes / 69864 compiler global bytes; this is not runtime free RAM.
Final 36 native / 42 AEABI plus 2 additional math bindings and startup evidence pass
the independent scripts. The upload-format ELF remains byte-identical across the
normalization at 37d9acef0bad1260abb3d9d6d219113b90f3507f260733d4023b74c3e1874c52.
Debug/temp ELF hashes differ and are retained separately; no equality claim is
made for those artifacts. The final focused-source snapshot has no drift; the
earlier decoder snapshot differs only by the exactly proved header normalization.

## Preserved failures and limitations

Root/author initial new-fixture include and STOPPED-status errors, initial event
fixture contamination and repeated premature builds are preserved in
state/analysis/P2_button_routing_failures.md and author/HANDOFF.md. Reviewer-only
scripts also preserved three initial mistakes: an overbroad unchanged-tests check
forgot the additive config test, substring ui matched inherited arduino symbols,
and a closure assertion incorrectly assumed all three ELF artifacts would be
byte-identical. Corrected only reviewer checks/claims to the exact evidence; no
product/test assertion edit. Raw initial failures and both artifact hashes remain.

Windows remain deliberately unconfigured. SC-A START/BOTH electrical ambiguity,
physical A1 readings, sample cadence, full-tick 800 us, SC-AJ/F091 RAM/loader and
inherited Bridge runtime questions remain open. App scheduling/integration,
hardware acceptance, motor-run authorization and phase gates are outside scope.
