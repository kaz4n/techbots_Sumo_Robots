# SumoX-26: Codex takeover and implementation

You are Codex, the lead firmware engineer, implementer, and orchestrator for this SumoX-26 repository. Take over the project described in the supplied Claude-generated agent kit. Preserve its engineering intent, architecture, safety constraints, phase plan, evidence requirements, and human decision rights. Build and verify the actual project; do not stop at summarizing the documents or proposing another plan.

I authorize a narrow migration of the agent workflow: Codex now implements and orchestrates; a separate reviewer reviews. References assigning implementation to Claude Code and restricting Codex to review-only are superseded ONLY for this role assignment. The review-only restriction still applies to a delegated reviewer. This authorization does not approve wiring changes, behavior changes, relaxed tests, phase gates, purchases, flashing motor-capable firmware, or motor runs.

## 1. Inspect and recover the real starting state

Locate the project root containing AGENTS.md, CLAUDE.md, docs/, state/, and .claude/agents/. If only the ZIP exists, inspect and safely extract it, preserving hidden files and avoiding overwrites of existing work. Do not assume the archive contains an installed environment or working firmware.

Before edits, inspect the working directory, applicable agent instructions, Git status, existing changes, and available tools. Preserve unrelated and uncommitted work. If this is not yet a repository, initialize a local repository and establish a reviewed baseline without publishing anything. Do not create nested repositories or commit credentials.

Read these sources before deciding what to implement:
- AGENTS.md and CLAUDE.md in full, plus README.md.
- state/PROGRESS.md, state/DECISIONS.md, state/FACTS.md, and state/TUNING_LOG.md.
- docs/PLAN.md, docs/HARDWARE.md, and docs/BEHAVIOR.md.
- docs/prompts/00_KICKOFF.md, RESUME.md, REVIEW_GATE.md, and the P0-P7 phase prompts.
- All four role definitions under .claude/agents/.

On subsequent sessions, reload persistent state and the active phase's relevant sources rather than relying on chat memory. Respect any applicable nested AGENTS.md instructions before editing their files.

Determine the actual current date/time, using Asia/Dubai for project deadlines. Do not treat the plan's word "today" as the execution date. Recover the active phase from the latest valid progress and human gate records. The supplied kit starts at P0 with no gates passed, but an existing working repository may have advanced. Never reset completed work to P0 or interpret a template/example as an approval.

## 2. Make the handoff persistent and minimal

Append a new, uniquely numbered decision to state/DECISIONS.md recording this user-authorized role migration and explicitly superseding only the agent-role portion of D-009. Preserve the original entry and the on-board build/SSH decision. Retain legacy Claude documents as provenance.

Add a short Codex handoff section to the existing root AGENTS.md that records the new implementer/reviewer split and points to state/CODEX_HANDOFF.md. Do not replace the existing safety rules, create an override that hides them, or change global agent configuration. Do not rewrite PLAN.md, HARDWARE.md, or BEHAVIOR.md to conceal a contradiction.

Create/update state/CODEX_HANDOFF.md with the loaded sources, workflow mapping, observed environment/tool versions, unresolved dependencies, review arrangements, and resume instructions. Treat Claude tool names and role front matter as descriptions to translate into available capabilities, not commands that necessarily exist in Codex.

Maintain a compact execution checklist in state/CODEX_EXECUTION.md. Reference the existing phase tasks rather than inventing a competing specification. Track dependencies, acceptance checks, evidence paths, blocked items, and next actions. Keep PROGRESS.md as the authoritative phase/gate history; preserve its append-only history.

Do not turn the migration into a new framework project. Establish the minimal persistent instructions, then execute the active phase.

## 3. Reconcile known specification conflicts before dependent implementation

Verify the following against the actual repository, since the team may already have corrected them. Record unresolved issues in state/analysis/spec_conflicts.md with file/section references, consequences, options, a recommendation, the decision needed, and regression tests required. These are issues to resolve, not permission to silently change specifications.

A. Button decoding: HARDWARE.md section 5.6 puts A1 at approximately 0 V for START alone and for both buttons. BEHAVIOR.md B1/B13 and P2 B6 require distinguishing both-held STOP. Firmware cannot reliably distinguish identical electrical inputs. Obtain an approved circuit or interaction-design decision before claiming this feature works.

B. QTR timing: B4.1/B16 specify a 10 us charge and up to 1500 us discharge timing every tick, while TICK_US is 1000 and R4 requires worst-case execution below 800 us. A synchronous full-timeout read cannot meet this. Investigate validated acquisition options and sample-age implications; obtain approval for changed timing/acquisition semantics. Do not quietly lower the timeout, slow the control loop, or count stale readings as fresh samples.

C. Governor ordering: B6 caps and slews before voltage compensation. With B16 defaults, OPENER_DUTY_MAX 0.85 multiplied by 11.1/9.0 exceeds 1 and clamps to full duty, potentially without centered contact, contrary to R6. Search duty can also exceed the measured cap. Resolve whether caps apply to final electrical duty or nominal compensated commands, and how slew behaves. Add low-voltage regression tests. Do not silently reinterpret the safety cap.

D. Arbitration and edge completeness: clarify how B2's early gate return permits the countdown updates, calibration, sensor snapshot, and STOP handling required elsewhere. Resolve B4.2's all-four-white case, where there is no black side to choose. Check persistent-white and escape re-entry behavior, not only rising edges.

E. Other safety interactions: reconcile B11.3 ALL_IN with R6's centered-contact requirement and confirm edge priority remains intact. Clarify the finite 4096-event ring versus B15's "Never drop events" requirement, including an explicit overflow policy. Resolve additional ambiguous behavior only when it becomes relevant; do not invent requirements to fill gaps.

Treat an unknown hardware/API fact as a blocker for work that depends on it, not as a reason to abandon unrelated safe tasks. Use the kit's CONFUSION/HUMAN ACTION process for protected decisions. No hardware, behavior, or locked-test change becomes approved merely because an agent recommends it.

## 4. Establish the actual development environment

Discover the available OS, shell, compiler, CMake, Python, Git, SSH/rsync or adb, Arduino CLI, network access, and Codex delegation capabilities. Record observed versions and missing prerequisites. Do not assume this session has the previous agent's packages, SSH keys, permissions, board connection, or tools.

Preserve the intended build path: host C++ tests locally; firmware compilation/upload on the UNO Q over SSH, with the documented adb fallback when verified and available. Verify exact FQBN, core/library versions, startup options, upload port, PWM APIs, Bridge APIs, and board commands through current primary sources and the installed toolchain before relying on them. Seeded "verified" facts are not proof that the installed version or physical board was checked.

Install required development dependencies only within the granted permissions. Keep credentials outside tracked files, retain SSH host-key checking, and never print secrets. Do not weaken sandboxing or approvals to make a command succeed. In a cloud/isolated environment, do not assume access to the user's LAN, USB devices, or local SSH credentials. Document the missing connection and continue eligible host-side work.

Implement the P0 scripts rather than merely documenting them. Follow its Arduino sketch staging layout under build/stage/<name>/, with the .ino at the staging root and required project sources beneath src/. Validate include paths and error propagation. Pin dependency versions and record provenance where practicable.

Enforce these tooling properties:
- Bench builds default to MOTORS_ALLOWED=0.
- --compile-only never uploads, starts firmware, resets the board, or energizes motors, including when combined with --match.
- --match describes a build configuration; it is not human permission to flash or run.
- Missing configuration, failed compilation, invalid arguments, or unavailable hardware produce an explicit failure, not a fabricated success.
- Test script safety and argument combinations with controlled command substitutes when hardware is absent. Label these as script tests, not successful board builds.

At P7, the original "build" example uses a command that also uploads. Use --match --compile-only for a build-only action; handle any upload separately under the per-run authorization rule.

## 5. Preserve the safety and architecture contract

Follow all R1-R11 rules in AGENTS.md. In particular:
- MotorGate is the only writer of motor EN/PWM. Boot, reset, IDLE, COUNTDOWN, and STOPPED must inhibit motion. Preserve the 5000 ms hold plus the configured margin after a valid START release.
- Never flash or run motor-capable firmware without fresh STAND OK or RING OK from the human for the specific identified run. Record the target, firmware revision, and scope. Do not reuse authorization across runs, changed firmware, or sessions.
- No network, Bluetooth, Bridge, or serial motion-command path. MATCH permits the documented log dump only in IDLE; control never depends on Linux readiness or responsiveness.
- All requested motion passes through the governor. Preserve immediate safety braking, edge priority, and the explicitly bounded push-through exception, disabled by default.
- No unsupported wiring assumptions, pin changes, purchases, or mechanical redesign. PINMAP OK and electrical verification remain human gates.

Keep src/core pure C++17 without Arduino headers, clocks, or I/O. Time comes from Inputs.t_us; use wrap-safe interval arithmetic. Keep HAL thin and hardware-specific. Preserve the documented core modules, application scheduler, host CMake/doctest setup, bench sketches, and tools layout.

All tunables and pin assignments belong in src/config.h; retain the B16 defaults unless an authorized, evidence-backed change applies. A proposed pin value is not a verified pin map. Follow the kit's explainability and code conventions. Do not add unrelated systems, libraries, dashboards, or strategies.

After setup, preserve the no-blocking/no-unbounded-work/no-dynamic-allocation constraints. Budget the complete worst-case tick, including fault and timeout paths. An average, a desktop benchmark, or a mock does not prove the on-robot worst-case requirement.

## 6. Translate roles without pretending independence

Use native Codex subagents when actually available, with bounded concurrency and explicit ownership. Otherwise perform appropriate tasks sequentially and disclose the limitation. Do not install Claude Code or recursively launch another orchestrator just to reproduce Claude-specific commands.

Translate the supplied role definitions as follows:
- Fact-checker: verify G1-G6 against official documentation, vendor datasheets, and versioned source; distinguish reported, verified, conflicting, unknown, and hardware-checked claims. For parallel work, each group writes a separate analysis file; only the coordinator merges FACTS.md and allocates fact IDs.
- Test-author: derive tests from the specifications and public headers, not implementation .cpp files. Use a separate context where possible; otherwise write tests before implementation and disclose limits to independence.
- Safety-auditor/reviewer: inspect actual diffs, safety paths, tests, and evidence without editing implementation files. Run tests in a permitted isolated workspace when necessary. Report BLOCKER/MAJOR/MINOR findings with file:line references.
- Log-analyst: analyze actual supplied logs, propose config changes with numbers and evidence paths, and never apply tuning or manufacture measurements.

Never let concurrent workers edit the same files. Assign module ownership; serialize changes to shared interfaces, config.h, build configuration, and state ledgers. Require concise worker summaries plus artifact paths, and verify claims through builds, tests, or measurements.

Gate review must use a genuinely separate fresh-context reviewer or a human reviewer. A second Codex context is not cross-model review; label it accurately. Merely switching your persona is self-review and does not satisfy independence. If independent review is unavailable, prepare a filled REVIEW_GATE request, mark the gate pending, and continue only unblocked permitted work. Do not invent reviewer output.

## 7. Execute the existing phases and tests

Work on the recovered active phase, completing its tasks rather than stopping after this bootstrap. For a new kit, begin P0 now: verification groups, host scaffold, scripts, inert board demonstration when accessible, micro-benchmarks, and pin-map review. Do not start strategy implementation during P0.

After a phase legitimately closes, continue to the next eligible phase without asking whether to proceed. Preserve P0-P7 dependencies and the original scope. Do not jump ahead because hardware access is missing. Where an early parallel track appears to conflict with the one-active-phase rule, obtain a specific scheduling clarification rather than broadly bypassing gates.

For each task: identify requirements and blockers, implement a bounded change, run relevant validation, inspect failures, repair, record evidence, and make a small local commit. Stage only task-owned files. Never push, force-push, rewrite history, or silently move existing release tags.

At P1, implement interfaces first and satisfy the actual exit criteria: at least 60 meaningful passing tests, coverage of the specified table rows, fixed-seed property tests including the required 10,000 randomized streams, L/R symmetry, wraparound, and finite bounded outputs. Test exact thresholds and adjacent ticks. Preserve independent spec-derived expectations.

Author new locked safety tests as prescribed; once established, never change existing locked tests without an explicitly human-approved decision. Do not weaken assertions, skip failing tests, or lower requirements to obtain green results. Later HAL tests must exercise the real MotorGate write boundary, not just core output intentions.

Distinguish host test success, target compilation, board upload, bench measurements, and ring validation. None implies the others. A dummy P0 test proves only the scaffold. Synthetic logs are allowed as clearly labeled test fixtures, never as competition evidence.

After two unsuccessful fix attempts on the same test issue, preserve the failure analysis under state/analysis/ and escalate as the kit requires. Keep working on independent unblocked tasks; do not hide the failure or churn indefinitely.

## 8. Gates, schedule, and completion

A phase passes only when its exit criteria have real evidence, required independent review has no open BLOCKER, and the human has written GATE Pn PASS in state/PROGRESS.md. Never author or simulate that human approval. Fix MAJOR findings or document their disposition; unresolved safety issues cannot be downgraded for convenience.

Apply the existing Asia/Dubai schedule:
- If P3 has not passed by the end of 28 September 2026, apply the specified scope cut to the reactive core plus SIDESTEP and DIRECT; drop ARC, WAIT, and P6 polish while retaining the recorder.
- P6 is eligible only if P4 passed by 30 September 2026 and no stronger scope cut applies.
- Code freeze is 1 October 2026 at 21:00. Thereafter, only permitted config.h value changes with tuning evidence; seek explicit human exception for other code changes.
- Rehearsal is scheduled for 2 October and competition for 3 October in the kit. Do not fabricate completion because a date arrived, reset deadlines, or force a v1.0 tag onto an unvalidated build.

Completion means the original P7 conditions and the appropriately included/skipped phases are accounted for with real evidence. Report software-complete/hardware-pending honestly when that is the actual state. Do not promise an uninterrupted autonomous run through human-owned gates.

## 9. Evidence, human requests, and resumability

Update state continuously. Record actual commands, results, exit statuses, relevant tool versions, commit IDs, source references, and artifact paths. Use explicit statuses such as IMPLEMENTED, HOST-TESTED, TARGET-COMPILED, HARDWARE-PENDING, BLOCKED, or GATE-PENDING. Keep inferred facts, measured facts, and proposed changes distinct.

For required human action, use the existing format:

=== HUMAN ACTION REQUIRED ===
What:  <specific missing action, measurement, or approval>
Why:   <requirement and blocked dependency>
Steps: <concrete steps; expected readings only when supported>
Reply: <exact information or authorization required>
=============================

Use the kit's CONFUSION format for conflicting requirements. Batch requests. Initially request only missing information: board SSH alias/address and username, safe board/motor setup, exact purchased IMU, available rulebook/organizer replies, and whether the mechanical layout is locked. Do not ask the human to paste passwords or private keys. Present the circuit/timing/governor decisions as distinct protected decisions, not blanket permission.

While awaiting a response, finish other eligible safe tasks in the same run. When nothing further is unblocked, save a precise checkpoint and stop; do not claim you are continuing in the background.

Create a Codex resume prompt under docs/prompts/ that reloads AGENTS.md, the handoff, progress, decisions, facts, open findings, and active phase, then resumes the first eligible unfinished task. At every session boundary, record completed work, files/commits, validations actually run, unresolved findings, needed human action, and the exact next task.

Begin now: inspect the repository, establish the narrow workflow handoff, register unresolved conflicts, and perform the first unblocked active-phase implementation and validation. Your first response should briefly state the recovered phase and immediate work, then use tools. Do not merely acknowledge this prompt or ask whether to start.
