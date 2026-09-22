# SumoX-26 agent kit: Codex handoff review

Reviewed: 22 September 2026. Source: the supplied `sumox26-agent-kit.zip`.

## Scope and conclusion

All 25 non-empty files were inspected. The archive also contains two empty `.gitkeep` files. It is a specification and agent-workflow kit, not an installed development environment: it contains no firmware, host build project, tool scripts, dependency installation, SSH configuration, or completed hardware measurements.

The kit is substantially portable. Its root AGENTS.md already addresses both coding agents; the engineering plan, specifications, phase prompts, and state ledgers are reusable. The necessary migration is a narrow reassignment of the implementer/orchestrator role, an honest replacement for independent review, explicit loading of legacy Claude context, and environment discovery. Technical conflicts must not be silently resolved as part of renaming the agent.

This review does not certify component specifications, competition rules, wiring, electrical safety, firmware correctness, or physical performance. No firmware was available to compile and no robot was tested. Findings below about circuit behavior and timing are deductions from the supplied documents, not measurements. The referenced team rulebook is not included in the ZIP.

## Workflow findings

### 1. Codex is explicitly restricted to reviewing

Sources: CLAUDE.md lines 25-30; state/DECISIONS.md D-009, lines 39-40; docs/PLAN.md line 50; docs/prompts/REVIEW_GATE.md lines 3-7.

Simply pasting the original kickoff into Codex leaves contradictory roles. The new prompt authorizes Codex to implement and orchestrate, while keeping review-only restrictions scoped to actual reviewers. It requires an appended decision superseding only the role portion of D-009, not deletion of the original decision or changes to the board-side build path.

### 2. Existing AGENTS.md should remain the instruction entry point

Sources: AGENTS.md lines 1-3; CLAUDE.md line 1.

The prompt retains root AGENTS.md and explicitly reads CLAUDE.md and all role definitions. It does not rely on Claude's `@AGENTS.md` import mechanism working in Codex. OpenAI documents selecting at most one guidance file per directory, with AGENTS.md ahead of configured fallback names; merely adding CLAUDE.md as a fallback would not cause both files to load from this root.

### 3. Claude role definitions are useful task briefs, not portable runtime configurations

Sources: .claude/agents/*.md; CLAUDE.md lines 10-23.

The prompt translates the four roles into available Codex capabilities. Native delegation is preferred when supported, but not assumed. Sequential work must be labeled honestly, and a self-review cannot masquerade as independent review. A separate Codex context is separate-context review, not cross-model review.

### 4. Parallel fact-checkers would compete for the same file

Sources: CLAUDE.md line 11; docs/prompts/P0_recon_toolchain.md lines 9-16; .claude/agents/fact-checker.md lines 8-12.

The orchestration policy forbids two workers owning one file, but every fact-checker is instructed to write FACTS.md. The handoff assigns per-group analysis files and makes the coordinator the sole merger and fact-ID allocator. Shared configuration, interface files, and progress ledgers also need serialized ownership.

### 5. The kickoff can overwrite a valid resume point

Sources: docs/prompts/00_KICKOFF.md lines 19 and 30-34; state/PROGRESS.md.

The kickoff first says to resume existing progress, then says to set P0. The new prompt recovers the latest valid state and never resets an existing project. The uploaded kit itself has P0 active and no gates passed.

### 6. Human gates cannot become automatic checkboxes

Sources: AGENTS.md lines 132-157; README.md lines 29-33; phase exit criteria.

The kit intentionally separates code work from board access, wiring, measurements, motor runs, explanations, and human sign-off. The prompt preserves those requirements. Without board access, Codex can complete eligible P0 host scaffolding, research, and script tests, but cannot claim that the board round trip, startup measurements, PINMAP OK, or GATE P0 passed. It must not automatically proceed to P1 merely because hardware is unavailable.

### 7. Early P2 work needs a narrow scheduling clarification

Sources: AGENTS.md line 132; docs/prompts/P2_hal_bench.md line 4; docs/PLAN.md lines 64-67.

The global policy says one active phase, while P2 and the schedule permit early driver/bench work. The handoff calls for a specific clarification before using that exception; it does not interpret it as permission to bypass all prerequisites.

## Engineering issues requiring explicit decisions

### E1. The specified circuit cannot distinguish START from both buttons

Sources: docs/HARDWARE.md lines 140-147; docs/BEHAVIOR.md lines 68 and 317; docs/prompts/P2_hal_bench.md line 16.

START directly grounds A1. Pressing MODE simultaneously does not change that grounding. Both cases therefore produce approximately 0 V, yet the firmware is expected to identify both-held STOP separately. This is a specification/circuit conflict, not a decoder implementation detail. An approved circuit or interaction change is required; the prompt does not prescribe a wiring change itself.

### E2. QTR timeout exceeds the control-tick budget

Sources: AGENTS.md line 52; docs/BEHAVIOR.md lines 105 and 353-355; docs/HARDWARE.md line 198.

The documented charge plus maximum discharge window is 10 + 1500 = 1510 us, before other sensor reads or decisions. This cannot fit synchronously inside a 1000 us tick or the required under-800 us worst-case execution budget. An asynchronous design could change when readings are available, so it also requires explicit freshness and latency semantics. Lowering the timeout without validation is not a legitimate silent fix.

### E3. Voltage compensation can produce unauthorized full duty

Sources: AGENTS.md line 54; docs/BEHAVIOR.md lines 175-189 and 382-383, 411.

The specified ordering caps before voltage compensation. With the documented defaults:

```
Opener: 0.85 * 11.1 / 9.0 = 1.048333... -> clamped to 1.0
Search: 0.30 * 11.1 / 9.0 = 0.37
```

The opener result can conflict directly with full duty being reserved for centered contact. Search duty can exceed the value selected from the stopping table. Compensation after slew also raises a question about whether the configured slew limit applies before or after compensation. Resolve the intended invariant explicitly and test the final motor command over the permitted voltage range.

### E4. Arbitration ordering is underspecified around gated states

Sources: docs/BEHAVIOR.md lines 72-98 and 317.

B2 returns early for BOOT/IDLE/COUNTDOWN/STOPPED, while B3 requires countdown progression, calibration, line warnings, and an opponent snapshot. STOP handling is also described separately. This can be resolved by a clear order of input/state updates and output gating, but mechanically translating the numbered arbitration steps could suppress required updates. This is a specification ambiguity, not evidence of an existing code bug.

### E5. All-white escape and ALL_IN need complete safety semantics

Sources: docs/BEHAVIOR.md lines 120, 125-128, 271-273; AGENTS.md lines 53-54.

The 3-or-4-white row says to drive toward sensors that read black; with all four white there are none. Separately, ALL_IN calls for full duty without spelling out how centered-contact eligibility is retained if perception changes. The safe response and transition rules need an approved, testable definition. Persistent white inputs and escape re-entry must be tested as well as newly asserted bits.

### E6. Finite event storage is not an unconditional no-loss guarantee

Source: docs/BEHAVIOR.md lines 338-340.

A 4096-entry event ring has finite capacity, while the specification says never to drop events. The record format, maximum event production, capacity argument, and overflow behavior need to be explicit. Do not silently overwrite events while reporting lossless evidence. Actual available MCU RAM remains a P0/P2 verification item.

### E7. WAIT's intended evasive geometry merits review before P5

Sources: docs/BEHAVIOR.md lines 281-284 and 296-300; docs/PLAN.md line 141.

WAIT invokes SIDESTEP's DRIVE and TURN_IN phases without the initial pivot. DRIVE is specified as straight heading-hold motion. Starting from the normal center-facing orientation, this does not obviously supply the lateral clearance implied by a matador strategy. Treat this as a behavioral-design question for review and physical validation, not permission to invent a new opener.

### E8. The release "build" command also uploads

Sources: AGENTS.md lines 118-123; docs/prompts/P0_recon_toolchain.md lines 19-20; docs/prompts/P7_freeze_matchday.md line 7.

P7 calls `tools/flash.sh app --match` a build, but the script contract includes upload. The handoff separates a match compile-only operation from any upload, which still requires fresh authorization for the specific motor-capable run. Tests must confirm --compile-only wins over upload behavior in every supported flag combination.

## What the new prompt preserves

The original source-of-truth documents, module architecture, C++17 host-testable core, MCU-only control, HAL boundary, MotorGate, R1-R11, B16 defaults pending approved tuning, P0-P7 gates, empirical test targets, separate reviewer requirement, state files, and human-owned physical work remain intact. No specific hardware model, pin assignment, API, or test result is invented.

The date logic uses Asia/Dubai: the P3 scope-cut checkpoint is the end of 28 September 2026; P6 eligibility depends on P4 by 30 September; freeze is 1 October at 21:00. These are dates from the kit, not independently confirmed organizer announcements.

## Current Codex documentation consulted

The following official OpenAI documentation informed only the Codex-specific workflow recommendations. Hardware research remains part of P0.

- Custom instructions with AGENTS.md: `https://developers.openai.com/codex/guides/agents-md`
- Subagents: `https://developers.openai.com/codex/multi-agent`
- Agent approvals and security: `https://learn.chatgpt.com/docs/agent-approvals-security`
- Cloud environments: `https://developers.openai.com/codex/cloud/environments`
- Using PLANS.md for multi-hour problem solving: `https://developers.openai.com/cookbook/articles/codex_exec_plans`

Some Codex documentation URLs currently redirect to OpenAI's ChatGPT Learn documentation. Installed-client capabilities and configuration schemas must still be checked at execution time.

## Bundle integrity

The accompanying handoff ZIP retains every original member's contents unchanged and adds a Codex kickoff prompt, this review, and a start-here note. It does not pre-approve engineering changes or pretend that the development environment has been installed.

Original archive SHA-256:

```
d769f2f912e2ecd61cb4453e3d4ab31b0dc8a299b877228b077816bafe558c2b
```
